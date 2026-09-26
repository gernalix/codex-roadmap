#!/usr/bin/env python3
"""Deterministic lease watchdog and one-shot browser recovery dispatcher."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path

from c2_supervisor_lease import DEFAULT_DB, connect, retire_expired, snapshot
from c2_codex_executor import persist
from c2_browser_recovery import existing_session, open_successor_tab, send_recovery_message

RECEIPT_DIR = Path.home() / '.local/state/c2-supervisor'


def prepare_successor(row, *, open_tab=open_successor_tab, send=send_recovery_message):
    """A receipt prevents a second send if browser acknowledgement is lost."""
    if not row or row['state'] != 'retired' or row['retirement_reason'] != 'lease_expired':
        return {'state': 'healthy'}
    if row['successor_session_id']:
        return {'state': 'successor_prepared', 'session_id': row['successor_session_id']}
    identity = row['supervisor_id'] + ':' + str(row['fencing_token'])
    receipt = RECEIPT_DIR / ('recovery-' + hashlib.sha256(identity.encode()).hexdigest()[:24] + '.json')
    if receipt.exists():
        prior = json.loads(receipt.read_text())
        if prior['supervisor_id'] != row['supervisor_id']:
            raise RuntimeError('recovery_receipt_identity_conflict')
        if prior['state'] == 'starting' and prior.get('browser_target'):
            url = existing_session(prior['browser_target'])
            if url:
                prior.update(state='prepared', session_id=url)
                persist(receipt, prior)
        return {'state': prior['state'], 'session_id': prior.get('session_id')}
    message = ('Recover the C2 non-PersonalHub supervisor. Read only this durable recovery pointer first: '
               + row['recovery_pointer'] + '\n'
               'Acquire a new supervisor lease with a NEW unique supervisor_id '
               '(omit --supervisor-id to generate it) and a fencing token above '
               + str(row['fencing_token']) + ' before any scheduling. '
               'Reconcile live executors, preserve every PersonalHub worker and device, '
               'then continue the Next action. Do not request the prior transcript.\n'
               'SUPERVISOR_RECOVERY_ID=' + row['supervisor_id'] + ':' + str(row['fencing_token']))
    target, page = open_tab()
    try:
        persist(receipt, {'supervisor_id': row['supervisor_id'],
                          'fencing_token': row['fencing_token'], 'state': 'starting',
                          'browser_target': target})
        url = send(page, message)
        persist(receipt, {'supervisor_id': row['supervisor_id'],
                          'fencing_token': row['fencing_token'], 'state': 'prepared',
                          'session_id': url})
        return {'state': 'prepared', 'session_id': url}
    finally:
        page.close()


def watch_once(db, *, launch=prepare_successor, now=None):
    row = retire_expired(db, now=now)
    if not row or row['state'] != 'retired':
        return {'state': 'healthy'}
    if row['successor_session_id']:
        return {'state': 'successor_prepared', 'session_id': row['successor_session_id']}
    result = launch(row)
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
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    with (RECEIPT_DIR / 'watchdog.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with connect(args.db) as db:
            result = watch_once(db)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
