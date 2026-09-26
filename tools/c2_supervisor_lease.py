#!/usr/bin/env python3
"""Local, atomic supervisor lease and recovery state; never writes roadmap.sqlite."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import time
import uuid


DEFAULT_DB = Path.home() / '.local/state/c2-supervisor/lease.sqlite3'
RUNTIME_ENV = Path.home() / '.config/c2-supervisor/runtime.env'


class LeaseError(RuntimeError):
    pass


def connect(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA busy_timeout=10000')
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('''CREATE TABLE IF NOT EXISTS supervisor (
        singleton INTEGER PRIMARY KEY CHECK(singleton=1),
        supervisor_id TEXT NOT NULL, lease_owner TEXT NOT NULL,
        fencing_token INTEGER NOT NULL, lease_expires_at REAL NOT NULL,
        last_heartbeat REAL NOT NULL, last_progress_at REAL NOT NULL,
        acquired_at REAL NOT NULL, last_renewed_at REAL NOT NULL,
        current_action TEXT NOT NULL, current_step TEXT NOT NULL,
        progress_counter INTEGER NOT NULL, state TEXT NOT NULL,
        recovery_pointer TEXT NOT NULL, executor TEXT,
        stall_reason TEXT, retirement_reason TEXT, successor_session_id TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS supervisor_events (
        id INTEGER PRIMARY KEY, at REAL NOT NULL, supervisor_id TEXT NOT NULL,
        fencing_token INTEGER NOT NULL, event TEXT NOT NULL, detail TEXT
    )''')
    return db


def snapshot(db):
    row = db.execute('SELECT * FROM supervisor WHERE singleton=1').fetchone()
    return dict(row) if row else None


def _event(db, row, event, detail=None, now=None):
    db.execute('INSERT INTO supervisor_events(at,supervisor_id,fencing_token,event,detail) VALUES(?,?,?,?,?)',
               (time.time() if now is None else now, row['supervisor_id'], row['fencing_token'], event, detail))


def acquire(db, *, owner, pointer, supervisor_id=None, ttl=180, now=None):
    now = time.time() if now is None else now
    if not owner or not pointer or ttl <= 0:
        raise LeaseError('invalid_acquisition')
    supervisor_id = supervisor_id or str(uuid.uuid4())
    if not re.fullmatch(r'[A-Za-z0-9_.:-]+', supervisor_id):
        raise LeaseError('invalid_supervisor_id')
    db.execute('BEGIN IMMEDIATE')
    try:
        if db.execute('SELECT 1 FROM supervisor_events WHERE supervisor_id=? LIMIT 1',
                      (supervisor_id,)).fetchone():
            raise LeaseError('supervisor_id_reused')
        old = snapshot(db)
        if old and old['state'] == 'active' and old['lease_expires_at'] > now:
            raise LeaseError('primary_lease_held')
        token = old['fencing_token'] + 1 if old else 1
        if old and old['state'] == 'active':
            _event(db, old, 'expired', now=now)
        db.execute('''INSERT INTO supervisor VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(singleton) DO UPDATE SET
            supervisor_id=excluded.supervisor_id,lease_owner=excluded.lease_owner,
            fencing_token=excluded.fencing_token,lease_expires_at=excluded.lease_expires_at,
            last_heartbeat=excluded.last_heartbeat,last_progress_at=excluded.last_progress_at,
            acquired_at=excluded.acquired_at,last_renewed_at=excluded.last_renewed_at,
            current_action=excluded.current_action,current_step=excluded.current_step,
            progress_counter=excluded.progress_counter,state=excluded.state,
            recovery_pointer=excluded.recovery_pointer,executor=excluded.executor,
            stall_reason=excluded.stall_reason,retirement_reason=excluded.retirement_reason,
            successor_session_id=excluded.successor_session_id''',
            (supervisor_id, owner, token, now + ttl, now, now, now, now,
             'acquired', 'read recovery pointer', 0, 'active', pointer,
             None, None, None, None))
        row = snapshot(db)
        _event(db, row, 'acquired', now=now)
        db.commit()
        return row
    except Exception:
        db.rollback()
        raise


def _require(db, supervisor_id, token, now):
    row = snapshot(db)
    if (not row or row['supervisor_id'] != supervisor_id or
            row['fencing_token'] != token or row['state'] != 'active' or
            row['lease_expires_at'] <= now):
        raise LeaseError('stale_or_expired_supervisor')
    return row


def update(db, *, supervisor_id, token, action=None, step=None, progress=False,
           ttl=180, executor=None, stall_reason=None, now=None):
    now = time.time() if now is None else now
    if ttl <= 0:
        raise LeaseError('invalid_ttl')
    db.execute('BEGIN IMMEDIATE')
    try:
        row = _require(db, supervisor_id, token, now)
        db.execute('''UPDATE supervisor SET lease_expires_at=?,last_heartbeat=?,
            last_renewed_at=?,last_progress_at=?,current_action=?,current_step=?,
            progress_counter=?,executor=?,stall_reason=? WHERE singleton=1''',
            (now + ttl, now, now, now if progress else row['last_progress_at'],
             action if action is not None else row['current_action'],
             step if step is not None else row['current_step'],
             row['progress_counter'] + int(progress), executor, stall_reason))
        result = snapshot(db)
        _event(db, result, 'progress' if progress else 'heartbeat', now=now)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def retire_expired(db, *, now=None):
    now = time.time() if now is None else now
    db.execute('BEGIN IMMEDIATE')
    try:
        row = snapshot(db)
        if row and row['state'] == 'active' and row['lease_expires_at'] <= now:
            db.execute("UPDATE supervisor SET state='retired',retirement_reason='lease_expired' WHERE singleton=1")
            _event(db, row, 'retired', 'lease_expired', now)
            row = snapshot(db)
        db.commit()
        return row
    except Exception:
        db.rollback()
        raise


def publish_runtime_identity(row, path=RUNTIME_ENV):
    """Make the current token available to the one local systemd scheduler."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write('C2_SUPERVISOR_ID=' + row['supervisor_id'] + '\n')
            stream.write('C2_FENCING_TOKEN=' + str(row['fencing_token']) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest='command', required=True)
    claim = sub.add_parser('acquire')
    claim.add_argument('--owner', required=True)
    claim.add_argument('--pointer', required=True)
    claim.add_argument('--supervisor-id')
    claim.add_argument('--ttl', type=int, default=180)
    for name in ('heartbeat', 'progress', 'verify'):
        command = sub.add_parser(name)
        command.add_argument('--supervisor-id', required=True)
        command.add_argument('--token', type=int, required=True)
        if name != 'verify':
            command.add_argument('--action')
            command.add_argument('--step')
            command.add_argument('--ttl', type=int, default=180)
    sub.add_parser('watch')
    sub.add_parser('status')
    args = parser.parse_args()
    with connect(args.db) as db:
        if args.command == 'acquire':
            row = acquire(db, owner=args.owner, pointer=args.pointer,
                          supervisor_id=args.supervisor_id, ttl=args.ttl)
            if args.db.expanduser().resolve() == DEFAULT_DB.resolve():
                publish_runtime_identity(row)
        elif args.command in ('heartbeat', 'progress'):
            row = update(db, supervisor_id=args.supervisor_id, token=args.token,
                         action=args.action, step=args.step, ttl=args.ttl,
                         progress=args.command == 'progress')
        elif args.command == 'verify':
            row = _require(db, args.supervisor_id, args.token, time.time())
        elif args.command == 'watch':
            row = retire_expired(db)
        else:
            row = snapshot(db)
    print(json.dumps(row, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except LeaseError as exc:
        raise SystemExit(str(exc))
