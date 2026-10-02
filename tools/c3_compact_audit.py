#!/usr/bin/env python3
"""Back up and compact only repetitive terminal-reconciliation no-op audit."""
from contextlib import closing
import fcntl
import hashlib
import json
import sqlite3

from c3_storage import CANONICAL_DB, verified_backup
from roadmap_db import now_utc


def compact(conn):
    if not conn.in_transaction:
        raise ValueError('audit_compaction_transaction_required')
    groups = conn.execute('''SELECT prompt_id,payload_json,COUNT(*),MIN(event_at),MAX(event_at)
        FROM audit_events WHERE event_type='terminal_reconcile_skipped'
        GROUP BY prompt_id,payload_json ORDER BY prompt_id,payload_json''').fetchall()
    removed = sum(row[2] for row in groups)
    if not removed:
        return {'removed': 0}
    summary = [{'prompt_id': r[0], 'decision': json.loads(r[1]), 'count': r[2],
                'first_seen': r[3], 'last_seen': r[4]} for r in groups]
    conn.execute("DELETE FROM audit_events WHERE event_type='terminal_reconcile_skipped'")
    conn.execute('INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(NULL,?,?,?,?)',
                 ('terminal_reconcile_noops_compacted', now_utc(), 'architecture-migration',
                  json.dumps({'removed_rows': removed, 'historical_summary': summary}, sort_keys=True)))
    return {'removed': removed, 'aggregated_decisions': len(summary)}


def preserved_fingerprint(conn):
    digest = hashlib.sha256()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name<>'audit_events' ORDER BY name")]
    for table in tables:
        digest.update(table.encode())
        rows = sorted(json.dumps(list(r), sort_keys=True, default=str) for r in conn.execute(f'SELECT * FROM "{table}"'))
        for row in rows:
            digest.update(row.encode())
            digest.update(b'\n')
    # Every non-noop audit record is equally protected.
    rows = conn.execute("SELECT * FROM audit_events WHERE event_type NOT IN ('terminal_reconcile_skipped','terminal_reconcile_noops_compacted') ORDER BY event_id")
    for row in rows:
        digest.update(json.dumps(list(row), default=str).encode())
        digest.update(b'\n')
    return digest.hexdigest()


def migrate():
    with (CANONICAL_DB.parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = verified_backup(CANONICAL_DB, CANONICAL_DB.parent / 'backups')
        with closing(sqlite3.connect(CANONICAL_DB)) as conn:
            before = preserved_fingerprint(conn)
            bytes_before = conn.execute('PRAGMA page_count').fetchone()[0] * conn.execute('PRAGMA page_size').fetchone()[0]
            rows_before = conn.execute('SELECT COUNT(*) FROM audit_events').fetchone()[0]
            conn.execute('BEGIN IMMEDIATE')
            try:
                result = compact(conn)
                if preserved_fingerprint(conn) != before:
                    raise ValueError('compaction_changed_canonical_or_relevant_audit')
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            conn.execute('VACUUM')
            conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            if preserved_fingerprint(conn) != before or conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or conn.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('vacuum_verification_failed')
            result.update({'rows_before': rows_before, 'rows_after': conn.execute('SELECT COUNT(*) FROM audit_events').fetchone()[0],
                           'bytes_before': bytes_before, 'bytes_after': CANONICAL_DB.stat().st_size,
                           'preserved_state_sha256': before})
        return {'backup': backup, 'result': result}


if __name__ == '__main__':
    print(json.dumps(migrate(), sort_keys=True))
