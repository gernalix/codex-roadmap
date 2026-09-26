"""Canonical writer-side supervisor fencing for C2 control operations."""
from __future__ import annotations

import re
import time


SCHEMA = '''CREATE TABLE IF NOT EXISTS c2_supervisor_authority (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 supervisor_id TEXT NOT NULL, fencing_token INTEGER NOT NULL,
 lease_expires_at REAL NOT NULL, claimed_at REAL NOT NULL,
 renewed_at REAL NOT NULL
)'''


class AuthorityError(ValueError):
    pass


def install_schema(conn):
    conn.execute(SCHEMA)


def _fields(authority):
    if not isinstance(authority, dict):
        raise AuthorityError('supervisor_authority_required')
    supervisor_id = authority.get('supervisor_id')
    token = authority.get('fencing_token')
    expires = authority.get('lease_expires_at')
    if (not isinstance(supervisor_id, str) or
            not re.fullmatch(r'[A-Za-z0-9_.:-]+', supervisor_id) or
            type(token) is not int or token < 1 or
            type(expires) not in (int, float)):
        raise AuthorityError('invalid_supervisor_authority')
    return supervisor_id, token, float(expires)


def claim(conn, authority, *, now=None):
    now = time.time() if now is None else now
    supervisor_id, token, expires = _fields(authority)
    if expires <= now:
        raise AuthorityError('supervisor_lease_expired')
    row = conn.execute('SELECT * FROM c2_supervisor_authority WHERE singleton=1').fetchone()
    if row:
        if token <= row['fencing_token'] or supervisor_id == row['supervisor_id']:
            raise AuthorityError('stale_or_reused_supervisor')
        if row['lease_expires_at'] > now:
            raise AuthorityError('canonical_primary_lease_held')
    conn.execute('''INSERT INTO c2_supervisor_authority VALUES(1,?,?,?,?,?)
        ON CONFLICT(singleton) DO UPDATE SET supervisor_id=excluded.supervisor_id,
        fencing_token=excluded.fencing_token,lease_expires_at=excluded.lease_expires_at,
        claimed_at=excluded.claimed_at,renewed_at=excluded.renewed_at''',
        (supervisor_id, token, expires, now, now))
    return {'supervisor_id': supervisor_id, 'fencing_token': token}


def require(conn, authority, *, now=None):
    now = time.time() if now is None else now
    supervisor_id, token, expires = _fields(authority)
    row = conn.execute('SELECT * FROM c2_supervisor_authority WHERE singleton=1').fetchone()
    if (not row or row['supervisor_id'] != supervisor_id or
            row['fencing_token'] != token or row['lease_expires_at'] <= now or
            expires <= now):
        raise AuthorityError('stale_or_expired_supervisor')
    return row


def renew(conn, authority, *, now=None):
    now = time.time() if now is None else now
    supervisor_id, token, expires = _fields(authority)
    row = conn.execute('SELECT * FROM c2_supervisor_authority WHERE singleton=1').fetchone()
    if (not row or row['supervisor_id'] != supervisor_id or
            row['fencing_token'] != token or expires <= now):
        raise AuthorityError('stale_or_expired_supervisor')
    if expires < row['lease_expires_at']:
        raise AuthorityError('lease_cannot_shorten')
    conn.execute('UPDATE c2_supervisor_authority SET lease_expires_at=?,renewed_at=? WHERE singleton=1',
                 (expires, now))
    return {'supervisor_id': row['supervisor_id'], 'fencing_token': row['fencing_token']}


def retire(conn, authority, *, now=None):
    now = time.time() if now is None else now
    row = require(conn, authority, now=now)
    conn.execute('UPDATE c2_supervisor_authority SET lease_expires_at=?,renewed_at=? WHERE singleton=1',
                 (now, now))
    return {'supervisor_id': row['supervisor_id'], 'fencing_token': row['fencing_token']}
