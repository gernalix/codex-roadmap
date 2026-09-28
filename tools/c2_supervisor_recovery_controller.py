#!/usr/bin/env python3
"""The sole fenced controller allowed to prepare a C2 supervisor recovery chat."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

from c2_codex_executor import persist
from c2_browser_recovery import existing_session, open_successor_tab, send_recovery_message, _json
from c2_supervisor_lease import DEFAULT_DB, connect, snapshot

STATE_DIR = Path.home() / '.local/state/c2-supervisor'
KILL_SWITCH = Path.home() / '.config/c2/disable-chat-supervisor'


def ensure_browser(*, run=subprocess.run):
    """Observe browser health without ever starting or restarting Chrome."""
    try:
        _json('/json/version')
        return 'healthy'
    except Exception:
        active = run(['systemctl', '--user', 'is-active', '--quiet',
                      'chatgpt-rdc-browser.service'], capture_output=True)
        if active.returncode == 0:
            return 'active_browser_unhealthy'
        if KILL_SWITCH.exists():
            return 'kill_switch_active'
        return 'browser_manual_start_required'


def ensure_supervisor(*, run=subprocess.run):
    """Start a missing daemon without interrupting an active worker."""
    active = run(['systemctl', '--user', 'is-active', '--quiet',
                  'chatgpt-rdc-supervisor.service'], capture_output=True)
    if active.returncode == 0:
        return 'healthy'
    if KILL_SWITCH.exists():
        return 'kill_switch_active'
    started = run(['systemctl', '--user', 'start', 'chatgpt-rdc-supervisor.service'],
                  capture_output=True)
    return 'started' if started.returncode == 0 else 'supervisor_start_failed'


def prepare_successor(row, *, open_tab=open_successor_tab,
                      send=send_recovery_message, find=existing_session):
    if not row or row['state'] != 'retired':
        return {'state': 'healthy'}
    if row['successor_session_id']:
        return {'state': 'successor_prepared', 'session_id': row['successor_session_id']}
    recovery_id = row['supervisor_id'] + ':' + str(row['fencing_token'])
    receipt = STATE_DIR / ('recovery-' + hashlib.sha256(recovery_id.encode()).hexdigest()[:24] + '.json')
    if receipt.exists():
        prior = json.loads(receipt.read_text())
        if prior.get('recovery_id') != recovery_id:
            raise RuntimeError('recovery_receipt_identity_conflict')
        if prior['state'] == 'starting' and prior.get('browser_target'):
            url = find(prior['browser_target'])
            if url:
                prior.update(state='prepared', session_id=url)
                persist(receipt, prior)
        return {'state': prior['state'], 'session_id': prior.get('session_id')}
    if KILL_SWITCH.exists():
        return {'state': 'kill_switch_active'}
    message = ('Recover the C2 non-PersonalHub supervisor with the deterministic command: '
               'python3 tools/c2_supervisor_resume.py. The command reads this durable pointer once: '
               + row['recovery_pointer'] + '\n'
               'Do not acquire authority, create a thread/run, or rescan history manually. '
               'For RESUMED or STALE_TAKEOVER execute its Exact next action immediately; '
               'for ALREADY_ACTIVE stop this recovery; for BLOCKED report its concrete blocker. '
               'Preserve every PersonalHub worker and device. Do not request the prior transcript.\n'
               'SUPERVISOR_RECOVERY_ID=' + recovery_id)
    # A crash after this reservation can leave one unused tab, but cannot resend.
    prior = {'recovery_id': recovery_id, 'state': 'reserved'}
    persist(receipt, prior)
    target, page = open_tab()
    try:
        prior.update(state='starting', browser_target=target)
        persist(receipt, prior)
        url = send(page, message)
        prior.update(state='prepared', session_id=url)
        persist(receipt, prior)
        return {'state': 'prepared', 'session_id': url}
    finally:
        page.close()


def recover_once(db, *, prepare=prepare_successor, browser=ensure_browser,
                 supervisor=ensure_supervisor):
    if KILL_SWITCH.exists():
        return {'state': 'kill_switch_active'}
    row = snapshot(db)
    if not row or row['state'] != 'retired':
        return {'state': 'healthy'}
    if row['successor_session_id']:
        return {'state': 'successor_prepared', 'session_id': row['successor_session_id']}
    browser_state = browser()
    if browser_state != 'healthy':
        return {'state': browser_state}
    supervisor_state = supervisor()
    if supervisor_state not in ('healthy', 'started'):
        return {'state': supervisor_state}
    result = prepare(row)
    if result.get('session_id'):
        db.execute('BEGIN IMMEDIATE')
        try:
            current = snapshot(db)
            if (current['supervisor_id'] == row['supervisor_id'] and
                    current['fencing_token'] == row['fencing_token'] and
                    current['state'] == 'retired'):
                db.execute('UPDATE supervisor SET successor_session_id=? WHERE singleton=1',
                           (result['session_id'],))
            db.commit()
        except Exception:
            db.rollback()
            raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    if KILL_SWITCH.exists():
        print(json.dumps({'state': 'kill_switch_active'}))
        return
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / 'recovery-controller.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with connect(args.db) as db:
            result = recover_once(db)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
