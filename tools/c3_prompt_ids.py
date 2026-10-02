"""C3 prompt identity authority and backed-up MegaVault registry cutover."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

import c2_identity as identity
from roadmap_db import materialization_hash


def import_registry(conn, source_path):
    if not conn.in_transaction:
        raise ValueError('prompt_id_import_transaction_required')
    if conn.execute("SELECT 1 FROM meta WHERE key='prompt_id_authority' AND value='C3'").fetchone():
        return {'status': 'already_imported'}
    with closing(identity.connect_db(source_path, read_only=True)) as source:
        source.execute('BEGIN')
        registry = [dict(row) for row in source.execute('SELECT * FROM prompt_id_registry ORDER BY prompt_id')]
        events = [dict(row) for row in source.execute('SELECT * FROM prompt_id_events ORDER BY event_id')]
        requests = [dict(row) for row in source.execute('SELECT * FROM prompt_id_allocation_requests ORDER BY request_id')]
    inserted, enriched = [], []
    guard = conn.execute("SELECT sql FROM sqlite_master WHERE name='prompt_id_identity_immutable'").fetchone()
    if guard:
        conn.execute('DROP TRIGGER prompt_id_identity_immutable')
    conn.execute('PRAGMA defer_foreign_keys=ON')
    for incoming in registry:
        pid = incoming['prompt_id']
        existing = conn.execute('SELECT * FROM prompt_id_registry WHERE prompt_id=?', (pid,)).fetchone()
        if existing:
            previous = dict(existing)
            if previous == incoming:
                continue
            # C3's historical rows reserve IDs but have no allocator provenance.
            # Enrich only those placeholders; actual allocation conflicts close.
            if previous['source'] != 'historical-roadmap' or previous['status'] != 'allocated' or previous['content_sha256'] is not None:
                raise ValueError('prompt_registry_conflict:' + str(pid))
            names = [name for name in incoming if name != 'prompt_id']
            conn.execute(f'UPDATE prompt_id_registry SET {",".join(name+"=?" for name in names)} WHERE prompt_id=?',
                         tuple(incoming[name] for name in names) + (pid,))
            enriched.append({'prompt_id': pid, 'previous': previous})
        else:
            names = list(incoming)
            conn.execute(f'INSERT INTO prompt_id_registry({",".join(names)}) VALUES({",".join("?" for _ in names)})', tuple(incoming.values()))
            inserted.append(pid)
    if guard:
        conn.execute(guard[0])
    events_added = 0
    for event in events:
        values = tuple(event[name] for name in ('prompt_id', 'event_type', 'event_at_utc', 'detail'))
        if conn.execute('''SELECT 1 FROM prompt_id_events WHERE prompt_id=? AND event_type=?
            AND event_at_utc=? AND detail IS ?''', values).fetchone():
            continue
        conn.execute('INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail) VALUES(?,?,?,?)', values)
        events_added += 1
    requests_added = 0
    reconciled_requests = []
    for incoming in requests:
        existing = conn.execute('SELECT * FROM prompt_id_allocation_requests WHERE request_id=?', (incoming['request_id'],)).fetchone()
        if existing:
            if dict(existing) != incoming:
                previous = dict(existing)
                same_arguments = all(previous[name] == incoming[name] for name in ('source', 'project_id', 'parent_prompt_id'))
                replacement = conn.execute('''SELECT 1 FROM prompt_relations r
                    JOIN prompts p ON p.prompt_id=r.from_prompt_id
                    WHERE r.from_prompt_id=? AND r.to_prompt_id=? AND r.relation_type='replacement'
                      AND p.status IN ('superseded','cancelled')''',
                    (str(previous['prompt_id']), str(incoming['prompt_id']))).fetchone()
                if not same_arguments or not replacement:
                    raise ValueError('prompt_allocation_request_conflict:' + incoming['request_id'])
                # Explicit historical replacement evidence resolves the old
                # split-allocator receipt. Both IDs stay permanently reserved.
                request_guard = conn.execute("SELECT sql FROM sqlite_master WHERE name='prompt_id_allocation_requests_no_update'").fetchone()
                if request_guard:
                    conn.execute('DROP TRIGGER prompt_id_allocation_requests_no_update')
                conn.execute('UPDATE prompt_id_allocation_requests SET prompt_id=?,created_at_utc=? WHERE request_id=?',
                             (incoming['prompt_id'], incoming['created_at_utc'], incoming['request_id']))
                if request_guard:
                    conn.execute(request_guard[0])
                reconciled_requests.append({'previous': previous, 'canonical_prompt_id': incoming['prompt_id']})
            continue
        names = list(incoming)
        conn.execute(f'INSERT INTO prompt_id_allocation_requests({",".join(names)}) VALUES({",".join("?" for _ in names)})', tuple(incoming.values()))
        requests_added += 1
    historical_reserved = identity.reserve_existing_roadmap_prompt_ids(conn)
    result = {'inserted_ids': inserted, 'enriched_reservations': enriched,
              'reconciled_requests': reconciled_requests,
              'events_imported': events_added, 'requests_imported': requests_added,
              'historical_reserved': historical_reserved}
    conn.execute("INSERT INTO meta(key,value) VALUES('prompt_id_authority','C3')")
    conn.execute('INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(NULL,?,?,?,?)',
                 ('prompt_id_authority_cutover', identity.utc_now(), 'architecture-migration', json.dumps(result, sort_keys=True)))
    return result


def register(conn, operation):
    pid = int(operation['prompt_id'])
    row = identity._registry_row(conn, pid)
    if row['status'] != 'allocated' or str(row['source']).startswith('historical-'):
        raise ValueError('prompt_id_not_new_reservation:' + str(pid))
    supplied_project = operation.get('project_id')
    supplied_project = int(supplied_project) if supplied_project is not None else None
    if supplied_project != row['project_id']:
        raise ValueError('prompt_id_project_mismatch:' + str(pid))
    if not operation.get('prompt_text'):
        raise ValueError('canonical_prompt_body_required')
    identity.materialize_prompt_id(conn, pid, content_sha256=materialization_hash(operation['prompt_text']))


def allocate(conn, operation):
    arguments = dict(operation.get('arguments') or {})
    if not arguments.get('request_id'):
        raise ValueError('prompt_id_request_id_required')
    return identity.allocate_prompt_id(conn, **arguments)


def allocation_result(conn, operations):
    allocations = [op for op in operations if op.get('op') == 'prompt_id_allocate']
    if not allocations:
        return {}
    result = []
    for op in allocations:
        request_id = op['arguments']['request_id']
        row = conn.execute('SELECT prompt_id FROM prompt_id_allocation_requests WHERE request_id=?', (request_id,)).fetchone()
        if not row:
            raise ValueError('allocation_receipt_missing')
        result.append({'request_id': request_id, 'prompt_id': row[0]})
    return {'allocations': result}


def reconcile_used(conn):
    rows = conn.execute('''SELECT r.prompt_id,r.status,m.body FROM prompt_id_registry r
        JOIN work_items w ON CAST(w.prompt_id AS INTEGER)=r.prompt_id
        JOIN prompt_materializations m ON m.prompt_id=w.prompt_id
        WHERE w.status='running' AND r.status IN ('allocated','materialized')
          AND r.source NOT LIKE 'historical-%' ''').fetchall()
    for row in rows:
        if row['status'] == 'allocated':
            identity.materialize_prompt_id(conn, row['prompt_id'], content_sha256=materialization_hash(row['body']))
        identity.mark_prompt_id_used(conn, row['prompt_id'])


def migrate():
    import fcntl
    from c3_storage import CANONICAL_DB, verified_backup
    from c3_projects import SOURCE
    with (CANONICAL_DB.parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = verified_backup(CANONICAL_DB, CANONICAL_DB.parent / 'backups')
        with closing(identity.connect_db(CANONICAL_DB)) as conn:
            conn.execute('BEGIN IMMEDIATE')
            try:
                result = import_registry(conn, SOURCE)
                if conn.execute('PRAGMA foreign_key_check').fetchall() or conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError('prompt_import_integrity_failed')
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    return {'backup': backup, 'result': result}


if __name__ == '__main__':
    print(json.dumps(migrate(), sort_keys=True))
