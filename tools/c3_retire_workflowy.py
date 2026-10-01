#!/usr/bin/env python3
"""Retire Workflowy ordering from C3's canonical database, offline and backed up."""
import fcntl
import json
import sqlite3

from c3_storage import CANONICAL_DB, verified_backup
from roadmap_db import now_utc


def retire(conn):
    if conn.execute("SELECT 1 FROM meta WHERE key='workflowy_control_plane_retired'").fetchone():
        return {'status': 'already_retired'}
    conn.execute('BEGIN IMMEDIATE')
    try:
        exists = conn.execute("SELECT 1 FROM sqlite_master WHERE name='manual_order_overrides'").fetchone()
        count = conn.execute('SELECT COUNT(*) FROM manual_order_overrides').fetchone()[0] if exists else 0
        conn.execute('DROP VIEW IF EXISTS v_work_item_summary')
        conn.execute('DROP VIEW IF EXISTS v_roadmap_manual_order')
        conn.execute('DROP VIEW IF EXISTS v_issue_inbox_pending_ordered')
        conn.execute('DROP TABLE IF EXISTS manual_order_overrides')
        conn.execute('''CREATE VIEW v_work_item_summary AS
            SELECT w.*,p.total_actionable,p.completed_actionable,p.progress_percent
            FROM work_items w JOIN v_work_item_progress p USING(work_item_id)''')
        conn.execute('''CREATE VIEW v_issue_inbox_pending_ordered AS
            SELECT i.* FROM issue_inbox i WHERE i.state='pending'
            ORDER BY i.observed_at_ms,i.issue_id''')
        conn.execute("INSERT INTO meta(key,value) VALUES('workflowy_control_plane_retired',?)", (now_utc(),))
        conn.execute('INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(NULL,?,?,?,?)',
                     ('workflowy_control_plane_retired', now_utc(), 'architecture-migration', json.dumps({'historical_order_rows': count})))
        conn.commit()
        return {'status': 'retired', 'historical_order_rows': count}
    except Exception:
        conn.rollback()
        raise


if __name__ == '__main__':
    with (CANONICAL_DB.parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = verified_backup(CANONICAL_DB, CANONICAL_DB.parent / 'backups')
        with sqlite3.connect(CANONICAL_DB) as conn:
            result = retire(conn)
            if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('workflowy_retirement_integrity_failed')
        print(json.dumps({'backup': backup, 'result': result}, sort_keys=True))
