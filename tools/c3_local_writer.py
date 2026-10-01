#!/usr/bin/env python3
"""Serialized local mutation authority, exposed over a private Unix socket."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import http.client
import json
import os
import re
import socket
import socketserver
import sqlite3
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from apply_issue_mutation import canonical_bytes
from roadmap_db import apply_mutation, connect, db_path, now_utc

DEFAULT_SOCKET = Path.home() / '.local/state/c3-control/writer.sock'
MAX_REQUEST = 8 * 1024 * 1024


class LocalWriter:
    def __init__(self, repo: Path, *, projects_source=None):
        self.repo = Path(repo).resolve()
        path = db_path(self.repo)
        if path.exists():
            from c3_storage import verified_backup
            verified_backup(path, path.parent / 'backups')
        self.conn = connect(self.repo)
        self.conn.c3_writer_owned = True
        self.conn.commit()
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA synchronous=FULL')
        self.conn.execute('PRAGMA busy_timeout=30000')
        from c3_storage import REPO
        from c3_projects import SOURCE, CACHE_TABLES
        self.projects_source = projects_source or (SOURCE if self.repo == REPO.resolve() else None)
        self.syncing_projects = False
        if self.projects_source:
            def authorize(action, table, column, database, trigger):
                if action in (sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE) and table in CACHE_TABLES and not self.syncing_projects:
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK
            self.authorize = authorize
            self.conn.set_authorizer(self.authorize)

    def close(self):
        self.conn.close()

    def apply(self, document: dict, request_key: str, *, issue_number=None):
        if not isinstance(document, dict) or document.get('schema') != 'codex-roadmap.mutation.v1':
            raise ValueError('invalid_mutation_schema')
        if not isinstance(request_key, str) or not re.fullmatch(r'[A-Za-z0-9._-]+', request_key):
            raise ValueError('invalid_request_key')
        operations = document.get('operations')
        if not isinstance(operations, list) or not operations or any(not isinstance(op, dict) for op in operations):
            raise ValueError('invalid_operations')
        overrides = [op for op in operations if op.get('op') in ('c3_user_override', 'c3_destructive_override')]
        if overrides and (len(operations) != 1 or request_key != 'c3-user-' + str(overrides[0].get('arguments', {}).get('request_id', ''))):
            raise ValueError('user_override_transport_identity_mismatch')
        if any(op.get('op') == 'c2_cutover' for op in operations):
            raise ValueError('legacy_cutover_not_supported')
        payload_hash = hashlib.sha256(canonical_bytes(document)).hexdigest()
        actor = str(document.get('actor') or 'unknown')
        conn = self.conn
        retired = conn.execute("SELECT 1 FROM meta WHERE key='pre_migration_execution_retired'").fetchone()
        if retired and (actor in ('c2-supervisor-resume', 'c2-workflowy-order') or
                        any(op.get('op') in ('c2_ensure_issue_triage', 'c2_set_manual_order', 'c2_clear_manual_order') for op in operations)):
            raise ValueError('pre_migration_component_retired')
        try:
            conn.execute('BEGIN IMMEDIATE')
            receipt = conn.execute('SELECT * FROM mutation_receipts WHERE request_key=?', (request_key,)).fetchone()
            if receipt:
                if receipt['payload_sha256'] != payload_hash:
                    raise ValueError('request_key_conflict:' + request_key)
                conn.rollback()
                from c3_prompt_ids import allocation_result
                return {'status': 'ok', 'submission': 'applied', 'request_key': request_key,
                        'issue_number': str(receipt['issue_number']), 'idempotent': True,
                        **allocation_result(conn, operations)}
            # Existing receipts use positive GitHub issue numbers. Reserve the
            # negative namespace for local receipts without another registry.
            if issue_number is None:
                issue_number = conn.execute('SELECT MIN(COALESCE(MIN(issue_number),0),0)-1 FROM mutation_receipts').fetchone()[0]
            elif not isinstance(issue_number, int) or issue_number <= 0:
                raise ValueError('invalid_issue_number')
            if self.projects_source:
                from c3_projects import synchronize
                self.syncing_projects = True
                conn.set_authorizer(self.authorize)
                try:
                    synchronize(conn, self.projects_source)
                finally:
                    self.syncing_projects = False
                    conn.set_authorizer(self.authorize)
            for operation in operations:
                if conn.execute("SELECT 1 FROM meta WHERE key='prompt_id_authority' AND value='C3'").fetchone() and operation.get('op') == 'register':
                    from c3_prompt_ids import register
                    register(conn, operation)
                apply_mutation(conn, operation, default_actor=actor)
            if conn.execute("SELECT 1 FROM meta WHERE key='prompt_id_authority' AND value='C3'").fetchone():
                from c3_prompt_ids import reconcile_used
                reconcile_used(conn)
            if self.projects_source:
                from c3_projects import validate_references
                validate_references(conn)
            conn.execute('INSERT INTO mutation_receipts(request_key,issue_number,payload_sha256,actor,applied_at) VALUES(?,?,?,?,?)',
                         (request_key, issue_number, payload_hash, actor, now_utc()))
            conn.commit()
            # Autonomous maintenance must not wake itself recursively. External
            # intake, executor transitions and explicit UI actions wake runtime.
            if actor != 'c2-runtime':
                (db_path(self.repo).parent / 'state.changed').touch()
        except Exception:
            conn.rollback()
            raise
        from c3_prompt_ids import allocation_result
        return {'status': 'ok', 'submission': 'applied', 'request_key': request_key,
                'issue_number': str(issue_number), 'idempotent': False,
                **allocation_result(conn, operations)}


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path, timeout=120):
        super().__init__('localhost', timeout=timeout)
        self.path = str(path)

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def submit_local(document, *, request_key, socket_path=None, issue_number=None):
    connection = UnixConnection(socket_path or os.environ.get('C3_WRITER_SOCKET', str(DEFAULT_SOCKET)))
    try:
        connection.request('POST', '/mutations', json.dumps({'document': document, 'request_key': request_key, 'issue_number': issue_number}),
                           {'Content-Type': 'application/json'})
        response = connection.getresponse()
        result = json.loads(response.read())
        if response.status != 200:
            raise ValueError(result.get('error', 'local_writer_rejected'))
        return result
    finally:
        connection.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path != '/health':
            self.send_error(404)
            return
        body = json.dumps({'status': 'ok', 'authority': str(db_path(self.server.writer.repo)),
                           'journal_mode': self.server.writer.conn.execute('PRAGMA journal_mode').fetchone()[0]}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if self.path != '/mutations' or not 0 < size <= MAX_REQUEST:
                raise ValueError('invalid_request')
            payload = json.loads(self.rfile.read(size))
            result = self.server.writer.apply(payload['document'], payload['request_key'], issue_number=payload.get('issue_number'))
            status = 200
        except Exception as exc:
            result, status = {'status': 'blocked', 'error': str(exc)}, 409
        body = json.dumps(result).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(repo, socket_path):
    socket_path = Path(socket_path)
    socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # The lock belongs to the DB, so using another socket cannot create a
    # second service for the same canonical database.
    with (db_path(Path(repo)).parent / '.c3-writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        socket_path.unlink(missing_ok=True)
        writer = LocalWriter(Path(repo))
        try:
            with socketserver.UnixStreamServer(str(socket_path), Handler) as server:
                os.chmod(socket_path, 0o600)
                server.writer = writer
                server.serve_forever()
        finally:
            writer.close()
            socket_path.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--socket', type=Path, default=DEFAULT_SOCKET)
    args = parser.parse_args()
    serve(args.repo.resolve(), args.socket)
