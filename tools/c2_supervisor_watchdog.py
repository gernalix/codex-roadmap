#!/usr/bin/env python3
"""Deterministic lease watchdog and one-shot browser recovery dispatcher."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import time

from c2_supervisor_lease import DEFAULT_DB, connect, retire_expired, retire_stalled, snapshot
from c2_codex_executor import persist
from c2_browser_recovery import existing_session, open_successor_tab, send_recovery_message

RECEIPT_DIR = Path.home() / '.local/state/c2-supervisor'
SUSPECTED_STALL_SECONDS = 40
FINAL_VERIFICATION_SECONDS = 90
STALLED_SECONDS = 180


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
    message = ('Recover the C2 non-PersonalHub supervisor with the deterministic command: '
               'python3 tools/c2_supervisor_resume.py. The command reads this durable pointer once: '
               + row['recovery_pointer'] + '\n'
               'Do not acquire authority, create a thread/run, or rescan history manually. '
               'For RESUMED or STALE_TAKEOVER execute its Exact next action immediately; '
               'for ALREADY_ACTIVE stop this recovery; for BLOCKED report its concrete blocker. '
               'Preserve every PersonalHub worker and device. Do not request the prior transcript.\n'
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
    now = time.time() if now is None else now
    row = snapshot(db)
    if row and row['state'] == 'active':
        if float(row['lease_expires_at']) <= now:
            row = retire_expired(db, now=now)
        else:
            progress_age = now - float(row['last_progress_at'])
            if progress_age >= STALLED_SECONDS:
                row = retire_stalled(db, stalled_after=STALLED_SECONDS, now=now)
            elif progress_age >= FINAL_VERIFICATION_SECONDS:
                return {'state': 'final_verification', 'progress_age': progress_age}
            elif progress_age >= SUSPECTED_STALL_SECONDS:
                return {'state': 'suspected_stall', 'progress_age': progress_age}
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
