"""One-time C2 migration inside the serialized GitHub roadmap writer.

The Issue carries a bounded snapshot of only the requested MegaVault tables.
The previous tracked roadmap.sqlite revision remains the durable rollback source.
"""
from __future__ import annotations

import base64
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import zlib

import c2_identity
import work_items_cutover
import work_items_migration
import work_items_state_import

MAX_SNAPSHOT_BYTES = 2_000_000


class C2CutoverError(RuntimeError):
    pass


def build_snapshot(megavault_db: Path) -> dict:
    with closing(c2_identity.connect_db(megavault_db,read_only=True)) as source:
        c2_identity._assert_tables(source)
        if source.execute('PRAGMA quick_check').fetchone()[0]!='ok' or source.execute('PRAGMA foreign_key_check').fetchall():
            raise C2CutoverError('megavault_identity_source_invalid')
        rows={table:[dict(row) for row in source.execute(f'SELECT * FROM "{table}"')]
              for table in c2_identity.IMPORT_TABLES}
    raw=json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    if len(raw)>MAX_SNAPSHOT_BYTES:
        raise C2CutoverError('identity_snapshot_too_large')
    return {'snapshot_sha256':hashlib.sha256(raw).hexdigest(),
            'snapshot_b64':base64.b64encode(zlib.compress(raw,9)).decode('ascii')}


def _sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_snapshot(arguments: dict) -> dict:
    encoded=arguments.get('snapshot_b64')
    expected=arguments.get('snapshot_sha256')
    if not isinstance(encoded,str) or len(encoded)>100_000 or not isinstance(expected,str):
        raise C2CutoverError('bounded_identity_snapshot_required')
    try:
        packed=base64.b64decode(encoded,validate=True)
        inflater=zlib.decompressobj()
        raw=inflater.decompress(packed,MAX_SNAPSHOT_BYTES+1)
        if len(raw)>MAX_SNAPSHOT_BYTES or not inflater.eof or inflater.unused_data:
            raise C2CutoverError('identity_snapshot_size_or_framing_invalid')
        raw+=inflater.flush()
        if len(raw)>MAX_SNAPSHOT_BYTES or hashlib.sha256(raw).hexdigest()!=expected:
            raise C2CutoverError('identity_snapshot_digest_mismatch')
        snapshot=json.loads(raw)
    except (ValueError,zlib.error,json.JSONDecodeError) as exc:
        raise C2CutoverError('identity_snapshot_invalid') from exc
    if not isinstance(snapshot,dict) or set(snapshot)!=set(c2_identity.IMPORT_TABLES):
        raise C2CutoverError('identity_snapshot_tables_mismatch')
    if any(not isinstance(rows,list) or len(rows)>10_000 or
           any(not isinstance(row,dict) for row in rows) for rows in snapshot.values()):
        raise C2CutoverError('identity_snapshot_rows_invalid')
    return snapshot


def _materialize_source(target_db: Path, source_db: Path, snapshot: dict) -> None:
    with closing(sqlite3.connect(target_db)) as target, closing(sqlite3.connect(source_db)) as source:
        target.row_factory=sqlite3.Row
        source.execute('PRAGMA foreign_keys=OFF')
        for table in c2_identity.IMPORT_TABLES:
            schema=target.execute('SELECT sql FROM sqlite_master WHERE type=\'table\' AND name=?',(table,)).fetchone()
            if not schema:
                raise C2CutoverError('target_identity_schema_missing:'+table)
            source.execute(schema[0])
            columns={str(row[1]) for row in target.execute(f'PRAGMA table_info("{table}")')}
            for row in snapshot[table]:
                if not row or not set(row).issubset(columns):
                    raise C2CutoverError('identity_snapshot_columns_invalid:'+table)
                names=list(row)
                quoted=','.join('"'+name+'"' for name in names)
                source.execute(f'INSERT INTO "{table}"({quoted}) VALUES({",".join("?" for _ in names)})',
                    tuple(row[name] for name in names))
        source.commit()
        source.execute('PRAGMA foreign_keys=ON')
        if source.execute('PRAGMA quick_check').fetchone()[0]!='ok' or source.execute('PRAGMA foreign_key_check').fetchall():
            raise C2CutoverError('identity_snapshot_integrity_invalid')


def prepare(repo: Path, arguments: dict) -> dict:
    path=Path(repo).resolve()/'roadmap.sqlite'
    expected_db=arguments.get('expected_db_sha256')
    snapshot=_decode_snapshot(arguments)
    with closing(sqlite3.connect(f'{path.as_uri()}?mode=ro',uri=True)) as before_conn:
        before_conn.row_factory=sqlite3.Row
        if before_conn.execute("SELECT 1 FROM meta WHERE key='work_items_cutover_version'").fetchone():
            prior=before_conn.execute("SELECT value FROM meta WHERE key='c2_cutover_snapshot_sha256'").fetchone()
            if not prior or prior[0]!=arguments['snapshot_sha256']:
                raise C2CutoverError('different_cutover_already_applied')
            return {'idempotent':True}
        if not isinstance(expected_db,str) or _sha256(path)!=expected_db:
            raise C2CutoverError('roadmap_db_precondition_changed')
        running=[dict(row) for row in before_conn.execute("SELECT * FROM prompts WHERE status='running' ORDER BY prompt_id")]
    with tempfile.TemporaryDirectory(prefix='c2-cutover-writer-') as folder:
        root=Path(folder)
        backup=root/'roadmap-before.sqlite'
        backup_info=work_items_migration.create_backup(path,backup)
        try:
            work_items_migration.migrate_database(path)
            source_db=root/'identity.sqlite'
            _materialize_source(path,source_db,snapshot)
            c2_identity.import_megavault_subset(path,source_db)
            with closing(work_items_migration._connect(path)) as conn:
                conn.execute('BEGIN IMMEDIATE')
                conn.execute("INSERT INTO meta(key,value) VALUES('c2_cutover_snapshot_sha256',?)",
                    (arguments['snapshot_sha256'],))
                work_items_state_import.import_state_tree(conn,Path(repo)/'operations/task-state',
                    source_commit=str(arguments.get('source_commit') or 'c2-cutover'))
                conn.commit()
            result=work_items_cutover.cutover_database(path)
            verification=work_items_cutover.verify_cutover(path)
            with closing(sqlite3.connect(f'{path.as_uri()}?mode=ro',uri=True)) as after_conn:
                after_conn.row_factory=sqlite3.Row
                after=[dict(row) for row in after_conn.execute("SELECT * FROM prompts WHERE status='running' ORDER BY prompt_id")]
            if running!=after or not verification['ok']:
                raise C2CutoverError('running_or_cutover_verification_mismatch')
            return {'idempotent':False,'backup_sha256':backup_info['sha256'],
                    'running_preserved':len(running),'cutover':result}
        except Exception:
            work_items_migration.restore_backup(backup,path)
            raise


def confirm(conn: sqlite3.Connection, *, snapshot_sha256: str, **_ignored) -> None:
    marker=conn.execute("SELECT value FROM meta WHERE key='c2_cutover_snapshot_sha256'").fetchone()
    if not marker or marker[0]!=snapshot_sha256:
        raise C2CutoverError('cutover_snapshot_not_confirmed')
