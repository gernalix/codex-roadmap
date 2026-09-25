#!/usr/bin/env python3
"""At-most-once Telegram delivery for a writer-owned C2 milestone."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import subprocess

from c2_codex_executor import persist
from c2_runtime import _open_snapshot, _writer_submit

STATE_ROOT=Path.home()/'.local/state/c2/notifications'
NOTIFIER=Path.home()/'.local/bin/c2-notify'


class NotificationError(RuntimeError):
    pass


def deliver(db_path: Path, event_key: str, *, root=STATE_ROOT, notifier=NOTIFIER,
            submit=_writer_submit, send=None):
    with closing(_open_snapshot(db_path)) as db:
        row=db.execute('SELECT * FROM c2_notification_outbox WHERE event_key=?',(event_key,)).fetchone()
        if not row or row['state'] not in ('sending','sent','uncertain'):
            raise NotificationError('milestone_not_claimed')
        event=dict(row)
    path=Path(root)/(hashlib.sha256(event_key.encode()).hexdigest()+'.json')
    if path.exists():
        receipt=json.loads(path.read_text())
        if receipt['event_key']!=event_key:
            raise NotificationError('milestone_receipt_conflict')
    elif event['state']=='sending':
        receipt={'event_key':event_key,'phase':'attempted'}
        persist(path,receipt)
        if send is None:
            def send(title,message):
                proc=subprocess.run([str(notifier),title,message],capture_output=True,text=True)
                return proc.returncode==0
        try:
            success=bool(send(event['title'],event['message']))
        except Exception:
            success=False
        receipt['phase']='sent' if success else 'uncertain'
        persist(path,receipt)
    else:
        raise NotificationError('delivery_receipt_missing')
    submit('mark_milestone',{'event_key':event_key,'sent':receipt['phase']=='sent',
        'error':None if receipt['phase']=='sent' else 'delivery_unconfirmed'},
        'c2-milestone-confirm-'+hashlib.sha256(event_key.encode()).hexdigest()[:32])
    return receipt['phase']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=Path.home()/'projects/codex-roadmap/roadmap.sqlite')
    parser.add_argument('--event-key',required=True)
    args=parser.parse_args()
    result=deliver(args.db,args.event_key)
    print(json.dumps({'event_key':args.event_key,'phase':result}))
    return 0 if result=='sent' else 2


if __name__=='__main__':
    raise SystemExit(main())
