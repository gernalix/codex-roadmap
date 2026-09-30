#!/usr/bin/env python3
"""Detect and fence a stalled C2 lease; never launch a browser or recovery chat."""
from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
import time

from c2_supervisor_lease import DEFAULT_DB, connect, retire_expired, retire_stalled, snapshot

STATE_DIR = Path.home() / '.local/state/c2-supervisor'
SUSPECTED_STALL_SECONDS = 40
FINAL_VERIFICATION_SECONDS = 90
STALLED_SECONDS = 180


def watch_once(db, *, now=None):
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
    return {'state': 'recovery_required',
            'recovery_id': row['supervisor_id'] + ':' + str(row['fencing_token']),
            'reason': row['retirement_reason']}


def main():
    from c3_retirement import require_not_retired
    require_not_retired()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / 'watchdog.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with connect(args.db) as db:
            result = watch_once(db)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
