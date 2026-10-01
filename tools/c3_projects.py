"""MegaVault project/inventory read-through cache; no C3 identity allocator."""
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3

from c2_identity import connect_db, utc_now

SOURCE = Path.home() / 'MegaVault/megavault.sqlite'
CACHE_TABLES = ('projects', 'project_aliases', 'repositories', 'project_components', 'project_operations')


@contextmanager
def project_catalog(conn):
    """Local helpers resolve identity from MegaVault, never a stale C3 copy."""
    from c3_storage import CANONICAL_DB
    filename = conn.execute('PRAGMA database_list').fetchone()[2]
    if filename and Path(filename).resolve() == CANONICAL_DB.resolve():
        with closing(connect_db(SOURCE, read_only=True)) as source:
            source.execute('BEGIN')
            yield source
    else:
        yield conn


def synchronize(conn, source_path=SOURCE):
    if not conn.in_transaction:
        raise ValueError('project_sync_transaction_required')
    with closing(connect_db(source_path, read_only=True)) as source:
        source.execute('BEGIN')
        snapshot = {}
        columns = {}
        for table in CACHE_TABLES:
            target_cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
            columns[table] = [r[1] for r in source.execute(f'PRAGMA table_info("{table}")') if r[1] in target_cols]
            if not columns[table]:
                raise ValueError('project_source_missing:' + table)
            snapshot[table] = [tuple(row) for row in source.execute(
                f'SELECT {",".join(columns[table])} FROM "{table}" ORDER BY 1')]
    digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
    old_digest = conn.execute("SELECT value FROM meta WHERE key='c3_project_cache_digest'").fetchone()
    request_mismatches = conn.execute('''SELECT COUNT(*) FROM prompt_id_allocation_requests a
        JOIN prompt_id_registry p USING(prompt_id) WHERE a.project_id IS NOT p.project_id''').fetchone()[0]
    if old_digest and old_digest[0] == digest and not request_mismatches:
        return {'changed': False}
    index = columns['projects'].index('slug')
    desired = {row[index]: row[columns['projects'].index('project_id')] for row in snapshot['projects']}
    current = dict(conn.execute('SELECT slug,project_id FROM projects'))
    missing = set(current) - set(desired)
    if missing:
        raise ValueError('project_identity_missing_in_megavault:' + ','.join(sorted(missing)))
    remapped = {int(old): int(desired[slug]) for slug, old in current.items() if old != desired[slug]}
    conn.execute('PRAGMA defer_foreign_keys=ON')
    identity_guard = conn.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='prompt_id_identity_immutable'").fetchone()
    if remapped and identity_guard:
        # Only the exact identity correction may move historical project FKs.
        # Prompt IDs/content remain unchanged; restore the guard before commit.
        conn.execute('DROP TRIGGER prompt_id_identity_immutable')
    # Temporary IDs handle swaps without colliding; FK references follow the
    # project row, while untyped lifecycle references are moved explicitly.
    for old in remapped:
        conn.execute('UPDATE projects SET project_id=? WHERE project_id=?', (-old, old))
        conn.execute('UPDATE work_items SET project_id=? WHERE project_id=?', (str(-old), str(old)))
    for old, new in remapped.items():
        conn.execute('UPDATE projects SET project_id=? WHERE project_id=?', (new, -old))
        conn.execute('UPDATE work_items SET project_id=? WHERE project_id=?', (str(new), str(-old)))
    if remapped and identity_guard:
        conn.execute(identity_guard[0])
    # Allocation receipts use an untyped historical project column rather than
    # a project FK. Follow their immutable prompt identity, not the reused number.
    conn.execute('''UPDATE prompt_id_allocation_requests AS a SET project_id=(
        SELECT p.project_id FROM prompt_id_registry p WHERE p.prompt_id=a.prompt_id)
        WHERE EXISTS(SELECT 1 FROM prompt_id_registry p WHERE p.prompt_id=a.prompt_id
                     AND a.project_id IS NOT p.project_id)''')
    names = columns['projects']
    for row in snapshot['projects']:
        update = ','.join(f'{name}=excluded.{name}' for name in names if name != 'project_id')
        conn.execute(f'INSERT INTO projects({",".join(names)}) VALUES({",".join("?" for _ in names)}) '
                     f'ON CONFLICT(project_id) DO UPDATE SET {update}', row)
    for table in CACHE_TABLES[1:]:
        conn.execute(f'DELETE FROM "{table}"')
        names = columns[table]
        conn.executemany(f'INSERT INTO "{table}"({",".join(names)}) VALUES({",".join("?" for _ in names)})', snapshot[table])
    conn.execute("INSERT INTO meta(key,value) VALUES('c3_project_cache_digest',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (digest,))
    conn.execute("INSERT INTO meta(key,value) VALUES('project_identity_authority','MegaVault') ON CONFLICT(key) DO UPDATE SET value=excluded.value")
    conn.execute('INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(NULL,?,?,?,?)',
                 ('megavault_project_cache_changed', utc_now(), 'MegaVault-read-through', json.dumps({'remapped_ids': remapped, 'allocation_receipts_reconciled': request_mismatches, 'digest': digest})))
    return {'changed': True, 'remapped_ids': remapped, 'projects': len(desired)}


def validate_references(conn):
    invalid = conn.execute('''SELECT DISTINCT project_id FROM work_items WHERE project_id IS NOT NULL
        AND CAST(project_id AS TEXT) NOT IN (SELECT CAST(project_id AS TEXT) FROM projects)''').fetchall()
    if invalid:
        raise ValueError('noncanonical_project_reference:' + ','.join(str(row[0]) for row in invalid))


def migrate():
    import fcntl
    from c3_storage import CANONICAL_DB, verified_backup
    with (CANONICAL_DB.parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = verified_backup(CANONICAL_DB, CANONICAL_DB.parent / 'backups')
        with sqlite3.connect(CANONICAL_DB) as conn:
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('BEGIN IMMEDIATE')
            result = synchronize(conn)
            validate_references(conn)
            if conn.execute('PRAGMA foreign_key_check').fetchall() or conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('project_migration_integrity_failed')
        return {'backup': backup, 'result': result}


if __name__ == '__main__':
    print(json.dumps(migrate(), sort_keys=True))
