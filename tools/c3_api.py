"""Loopback C3 API: canonical projections and synchronous user overrides."""
from __future__ import annotations
import argparse
from contextlib import closing
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import sqlite3
import subprocess
import threading
import time

import c2_snapshot_sync
import c3_override
from c2_runtime import _user_systemd_environment
from roadmap_start import _wait_issue_applied
from submit_mutation import submit_document


class ControlError(RuntimeError):
    pass


class Control:
    def __init__(self, repo, snapshot, *, refresh=True, timeout=120):
        self.repo, self.snapshot = Path(repo), Path(snapshot)
        self.refresh, self.timeout = refresh, timeout
        self.lock = threading.RLock()
        self.last_refresh = 0

    def connect(self, *, force=False):
        if self.refresh and (force or time.monotonic() - self.last_refresh > 3):
            c2_snapshot_sync.sync(self.repo, self.snapshot)
            self.last_refresh = time.monotonic()
        conn = sqlite3.connect(self.snapshot.resolve().as_uri() + '?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def state(self):
        with self.lock, closing(self.connect()) as conn:
            items = [dict(r) for r in conn.execute('SELECT * FROM v_work_item_summary')]
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            overrides = {r['work_item_id']: dict(r) for r in conn.execute('SELECT * FROM c3_user_state')} if 'c3_user_state' in names else {}
            tags = {}
            for r in conn.execute('SELECT work_item_id,tag FROM work_item_tags'):
                tags.setdefault(r[0], []).append(r[1])
            order = dict(conn.execute('SELECT work_item_id,rank FROM c3_user_order')) if 'c3_user_order' in names else {}
            for item in items:
                item['tags'] = tags.get(item['work_item_id'], [])
                item['priority'] = next((t.split(':')[1] for t in item['tags'] if t.startswith('priority:')), 'normal')
                item['paused'] = bool(overrides.get(item['work_item_id'], {}).get('paused'))
                item['deleted'] = bool(overrides.get(item['work_item_id'], {}).get('deleted'))
                item['user_rank'] = order.get(item['work_item_id'])
                item['display_state'] = 'paused' if item['paused'] else item['status']
            items.sort(key=c3_override.order_key(conn))
            events = [dict(r) for r in conn.execute('SELECT * FROM c3_user_events ORDER BY created_at DESC LIMIT 20')] if 'c3_user_events' in names else []
            return {'items': [i for i in items if not i['deleted']],
                    'dependencies': [dict(r) for r in conn.execute('SELECT * FROM work_item_dependencies')],
                    'events': events, 'authority': 'origin/main:roadmap.sqlite'}

    def preview(self, wid, action):
        with self.lock, closing(self.connect(force=True)) as conn:
            return c3_override.preview(conn, wid, action)

    def executor_control(self, runs, action):
        effects = []
        for run in runs:
            # Refuse unknown/manual executors rather than claim an interruption.
            rid = run['run_id']
            if not re.fullmatch(r'[A-Za-z0-9:_-]+', rid) or run['worker_ref'] != 'c3-run:' + rid:
                raise ControlError('unsupported_executor_control:' + rid)
            units = ['c3-run-' + rid + '.service']
            with closing(self.connect()) as conn:
                if conn.execute("SELECT 1 FROM work_item_resource_leases WHERE run_id=? AND resource='symphony:backend'", (rid,)).fetchone():
                    units.append('c3-symphony.service')
            for unit in units:
                if action in ('pause', 'resume'):
                    signal = 'SIGSTOP' if action == 'pause' else 'SIGCONT'
                    subprocess.run(['systemctl', '--user', 'kill', '--kill-whom=all', '--signal=' + signal, unit], check=True, capture_output=True, env=_user_systemd_environment())
                    # Signal acceptance alone is insufficient: verify every task in
                    # the owning cgroup reflects the requested stopped state.
                    cg = subprocess.run(['systemctl', '--user', 'show', unit, '-p', 'ControlGroup', '--value'], check=True, capture_output=True, text=True, env=_user_systemd_environment()).stdout.strip()
                    if not cg.startswith('/') or '..' in cg:
                        raise ControlError('executor_cgroup_missing')
                    task_file = Path('/sys/fs/cgroup') / cg.lstrip('/') / 'cgroup.procs'
                    pids = task_file.read_text().split()
                    if not pids:
                        raise ControlError('executor_cgroup_empty')
                    for pid in pids:
                        state = next(line.split()[1] for line in Path('/proc', pid, 'status').read_text().splitlines() if line.startswith('State:'))
                        if (action == 'pause') != (state in ('T', 't')):
                            raise ControlError('executor_signal_readback_failed')
                else:
                    subprocess.run(['systemctl', '--user', 'stop', unit], check=True, capture_output=True, env=_user_systemd_environment())
                    active = subprocess.run(['systemctl', '--user', 'is-active', '--quiet', unit], capture_output=True, env=_user_systemd_environment())
                    if active.returncode == 0:
                        raise ControlError('executor_stop_readback_failed')
            effects.append({'run_id': rid, 'worker_ref': run['worker_ref'],
                            'effect': {'pause': 'paused', 'resume': 'resumed'}.get(action, 'stopped')})
        return effects

    def override(self, args):
        with self.lock:
            args = dict(args)
            if not re.fullmatch(r'[A-Za-z0-9._-]{1,128}', str(args.get('request_id', ''))):
                raise ControlError('invalid_user_request_id')
            wid, action = args['work_item_id'], args['action']
            with closing(self.connect(force=True)) as conn:
                if conn.execute("SELECT 1 FROM sqlite_master WHERE name='c3_user_events'").fetchone():
                    prior = conn.execute('SELECT result_json FROM c3_user_events WHERE request_id=?', (args['request_id'],)).fetchone()
                    if prior:
                        result = json.loads(prior[0])
                        if result['work_item_id'] != wid or result['action'] != action or result['precondition'] != args.get('precondition'):
                            raise ControlError('user_request_id_conflict')
                        return {'result': result, 'state': self.state()}
            plan = self.preview(wid, action)
            if args.get('precondition') != plan['precondition']:
                raise ControlError('control_precondition_changed; preview again')
            destructive = action in c3_override.DESTRUCTIVE_ACTIONS
            if destructive and args.get('confirmed_affected') != plan['affected']:
                raise ControlError('explicit_dependency_confirmation_required')
            # Fail closed before any side effects on invalid move/priority.
            with closing(self.connect()) as conn:
                if action == 'move':
                    c3_override.legal_move(conn, wid, args.get('position'))
                if action == 'force-priority' and args.get('priority') not in ('p0', 'p1', 'p2'):
                    raise ControlError('invalid_priority')
            with closing(self.connect()) as conn:
                items, _ = c3_override.graph(conn)
                controlled = {r['work_item_id'] for r in plan['runs']}
                if action in ('pause', 'resume', 'stop', 'cancel', 'delete') and any(items[i]['status'] == 'running' and i not in controlled for i in plan['affected']):
                    raise ControlError('uncontrolled_manual_executor')
            args['intent'] = 'explicit-user'
            if action in ('pause', 'resume', 'stop', 'cancel', 'delete'):
                args['executor_effects'] = self.executor_control(plan['runs'], action)
            document = {'schema': 'codex-roadmap.mutation.v1', 'actor': 'c3-user-control',
                        'operations': [{'op': 'c3_destructive_override' if destructive else 'c3_user_override', 'arguments': args}]}
            key = 'c3-user-' + args['request_id']
            try:
                submitted = submit_document(document, request_key=key)
                _wait_issue_applied('gernalix/codex-roadmap', submitted['issue_number'], self.timeout)
                with closing(self.connect(force=True)) as conn:
                    receipt = conn.execute('SELECT issue_number FROM mutation_receipts WHERE request_key=?', (key,)).fetchone()
                    event = conn.execute('SELECT result_json FROM c3_user_events WHERE request_id=?', (args['request_id'],)).fetchone()
                    if not receipt or str(receipt[0]) != submitted['issue_number'] or not event:
                        raise ControlError('canonical_override_readback_missing')
                    result = json.loads(event[0])
            except Exception:
                if action == 'resume':
                    self.executor_control(plan['runs'], 'pause')
                raise
            return {'result': result, 'state': self.state()}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.headers.get('Host') not in self.server.allowed_hosts:
            self.reply(403, {'error': 'loopback_host_required'})
            return
        try:
            if self.path == '/api/state':
                self.reply(200, self.server.control.state())
            elif self.path == '/api/health':
                self.server.control.state()
                self.reply(200, {'status': 'ok'})
            else:
                asset = self.path.split('?', 1)[0]
                names = {'/': 'index.html', '/index.html': 'index.html', '/style.css': 'style.css', '/app.mjs': 'app.mjs', '/model.mjs': 'model.mjs'}
                if asset not in names:
                    self.reply(404, {'error': 'not_found'})
                    return
                root = Path(__file__).resolve().parents[1] / 'web' / 'dist'
                data = (root / names[asset]).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(names[asset])[0] or 'application/octet-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except Exception as exc:
            self.reply(503, {'error': str(exc)})

    def do_POST(self):
        # Loopback bind plus exact same-origin fetch protects local user intent
        # against cross-site forms, DNS rebinding and cross-origin scripts.
        expected = 'http://' + self.headers.get('Host', '')
        if self.headers.get('Host') not in self.server.allowed_hosts or self.headers.get('Origin') != expected or self.headers.get('X-C3-Intent') != 'explicit-user':
            self.reply(403, {'error': 'same_origin_user_intent_required'})
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 32768:
                raise ValueError('invalid_body_size')
            args = json.loads(self.rfile.read(size))
            if not isinstance(args, dict):
                raise ValueError('body_must_be_object')
            if self.path == '/api/preview':
                result = self.server.control.preview(args['work_item_id'], args['action'])
            elif self.path == '/api/override':
                result = self.server.control.override(args)
            else:
                self.reply(404, {'error': 'not_found'})
                return
            self.reply(200, result)
        except (ValueError, KeyError, ControlError) as exc:
            self.reply(409, {'error': str(exc)})
        except Exception as exc:
            self.reply(503, {'error': str(exc), 'recovery': 'Refresh canonical state and inspect the user mutation receipt before retrying. Executors may remain safely paused/stopped.'})


def serve(control, port=8767):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.control = control
    server.allowed_hosts = {f'127.0.0.1:{server.server_port}', f'localhost:{server.server_port}'}
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=c2_snapshot_sync.DEFAULT_REPO)
    parser.add_argument('--snapshot', type=Path, default=Path.home() / '.local/state/c3-control/web-snapshot.sqlite3')
    parser.add_argument('--port', type=int, default=8767)
    args = parser.parse_args()
    serve(Control(args.repo, args.snapshot), args.port).serve_forever()


if __name__ == '__main__':
    main()
