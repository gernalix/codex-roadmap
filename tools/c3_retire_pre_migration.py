#!/usr/bin/env python3
"""Offline, backed-up retirement of pre-migration execution ownership."""
import argparse
import fcntl
import json
import sqlite3
from pathlib import Path

from c3_storage import CANONICAL_DB, verified_backup
from roadmap_db import now_utc

HISTORICAL_M1 = '0c7d1f9ce8ecf48eb39387a30dcb79a34745f54e'


def relocate_runtime_lease():
    source = Path.home() / '.local/state/c2-supervisor/lease.sqlite3'
    target = CANONICAL_DB.parent / 'runtime-lease.sqlite3'
    if target.exists() or not source.exists():
        return
    verified_backup(source, CANONICAL_DB.parent / 'backups')
    with sqlite3.connect(source) as old:
        with sqlite3.connect(target) as new:
            old.backup(new)
            new.execute("UPDATE supervisor SET lease_owner='c3-runtime',recovery_pointer='c3-control',executor=NULL,successor_session_id=NULL")
        old.execute("UPDATE supervisor SET state='retired',lease_expires_at=0,recovery_pointer='',executor=NULL,successor_session_id=NULL,retirement_reason='pre-migration / retired'")
    target.chmod(0o600)


def plan(conn):
    conn.row_factory = sqlite3.Row
    decisions = []
    for item in conn.execute("SELECT * FROM work_items WHERE status='running'"):
        if item['title'] == 'Triage roadmap issue inbox':
            status, reason = 'superseded', 'recursive triage replaced by bounded technical Inbox maintenance'
        elif item['work_item_id'] == 'wi:c5bdf708a71d40c5a9902838ab8d8021':
            status, reason = 'superseded', 'legacy audit replaced by the user-authorized direct architecture migration'
        else:
            # No completion may be inferred from a stale worker, session or lease.
            status, reason = 'pending', 'pre-migration executor retired; unfinished work remains available'
        decisions.append({'work_item_id': item['work_item_id'], 'status': status, 'reason': reason})
    return decisions


def retire(conn):
    conn.row_factory = sqlite3.Row
    previous = conn.execute("SELECT value FROM meta WHERE key='pre_migration_execution_retired'").fetchone()
    if previous:
        return {'status': 'already_retired'}
    decisions = plan(conn)
    conn.execute('BEGIN IMMEDIATE')
    try:
        for decision in decisions:
            wid = decision['work_item_id']
            conn.execute('UPDATE work_items SET status=?,current_action=NULL,next_action=NULL,blocker=NULL,updated_at=? WHERE work_item_id=?',
                         (decision['status'], now_utc(), wid))
            prompt = conn.execute('SELECT prompt_id FROM work_items WHERE work_item_id=?', (wid,)).fetchone()[0]
            if prompt:
                conn.execute('INSERT INTO status_history(prompt_id,old_status,new_status,changed_at,actor,note) VALUES(?,?,?,?,?,?)',
                             (prompt, 'running', decision['status'], now_utc(), 'architecture-migration', decision['reason']))
        changed_runs = 0
        for run in conn.execute("SELECT * FROM work_item_runs WHERE state IN ('claimed','running','recovering') OR worker_ref IS NOT NULL OR lease_until>0 OR checkpoint_commit IS NOT NULL").fetchall():
            metadata = json.loads(run['metadata_json'])
            metadata['pre_migration_retirement'] = {
                'classification': 'historical-only', 'worker_ref': run['worker_ref'],
                'lease_until': run['lease_until'], 'checkpoint_commit': run['checkpoint_commit'],
                'previous_state': run['state'],
            }
            state = run['state']
            if state in ('claimed', 'running', 'recovering'):
                state = 'failed'
                metadata['pre_migration_retirement']['outcome'] = 'CANCELLED'
            conn.execute('UPDATE work_item_runs SET state=?,worker_ref=NULL,lease_until=0,checkpoint_commit=NULL,metadata_json=? WHERE run_id=?',
                         (state, json.dumps(metadata, sort_keys=True), run['run_id']))
            changed_runs += 1
        bindings = conn.execute('SELECT COUNT(*) FROM work_item_executor_bindings').fetchone()[0]
        # Original binding history remains in the verified migration backup;
        # executor-start/result receipts remain canonical historical evidence.
        conn.execute('DELETE FROM work_item_executor_bindings')
        conn.execute('DELETE FROM work_item_resource_leases')
        conn.execute("UPDATE work_item_checkpoints SET next_action=NULL,blocker='pre-migration / retired: historical evidence only'")
        record = {'m1': {'commit': HISTORICAL_M1, 'status': 'pre-migration / retired', 'executable': False},
                  'decisions': decisions, 'runs_retired': changed_runs, 'bindings_retired': bindings}
        conn.execute('INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(NULL,?,?,?,?)',
                     ('pre_migration_execution_retired', now_utc(), 'architecture-migration', json.dumps(record, sort_keys=True)))
        conn.execute("INSERT INTO meta(key,value) VALUES('pre_migration_execution_retired',?)", (now_utc(),))
        conn.commit()
        return record
    except Exception:
        conn.rollback()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=CANONICAL_DB)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not args.apply:
        with sqlite3.connect(args.db.resolve().as_uri() + '?mode=ro', uri=True) as conn:
            print(json.dumps(plan(conn), sort_keys=True))
        return
    with (args.db.parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = verified_backup(args.db, args.db.parent / 'backups')
        with sqlite3.connect(args.db) as conn:
            result = retire(conn)
            if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('retirement_integrity_failed')
        if args.db == CANONICAL_DB:
            relocate_runtime_lease()
        print(json.dumps({'backup': backup, 'result': result}, sort_keys=True))


if __name__ == '__main__':
    main()
