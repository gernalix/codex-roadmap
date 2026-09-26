#!/usr/bin/env python3
"""Event-triggered C2 bridge from a verified roadmap snapshot to the one writer.

This process never writes roadmap.sqlite. A systemd path/timer can call it after
an accepted roadmap pull; Issue receipts and the next pull drive the next step.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from submit_mutation import submit_document
from c2_supervisor_lease import DEFAULT_DB as SUPERVISOR_DB, connect as connect_supervisor, _require as require_supervisor, snapshot as supervisor_snapshot
from c2_mutations import SUPERVISOR_OPERATIONS


class RuntimeErrorC2(RuntimeError):
    pass


def _open_snapshot(path: Path) -> sqlite3.Connection:
    resolved=Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise RuntimeErrorC2('roadmap_snapshot_missing')
    conn=sqlite3.connect(f'{resolved.as_uri()}?mode=ro',uri=True)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA query_only=ON')
    marker=conn.execute("SELECT value FROM meta WHERE key='work_items_cutover_version'").fetchone()
    if not marker:
        conn.close()
        raise RuntimeErrorC2('c2_cutover_not_active')
    return conn


def _key(prefix: str, data) -> str:
    value=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return prefix+'-'+hashlib.sha256(value.encode()).hexdigest()[:32]


def _writer_submit(operation: str, arguments: dict, key: str):
    arguments=dict(arguments)
    if operation in SUPERVISOR_OPERATIONS or operation in ('claim_supervisor','renew_supervisor','retire_supervisor'):
        with closing(connect_supervisor(SUPERVISOR_DB)) as lease:
            row=supervisor_snapshot(lease)
            if not row:
                raise RuntimeErrorC2('supervisor_lease_missing')
            require_supervisor(lease,row['supervisor_id'],row['fencing_token'],time.time())
            arguments['supervisor_authority']={
                'supervisor_id':row['supervisor_id'],
                'fencing_token':row['fencing_token'],
                'lease_expires_at':row['lease_expires_at'],
            }
    return submit_document({'schema':'codex-roadmap.mutation.v1','actor':'c2-runtime',
        'operations':[{'op':'c2_'+operation,'arguments':arguments}]},request_key=key)


def _launch_worker(run_id: str):
    command=[sys.executable,str(Path(__file__).with_name('c2_worker.py')),
        '--run-id',run_id]
    result=subprocess.run(['systemd-run','--user','--collect',
        '--unit=c2-run-'+run_id,*command],capture_output=True,text=True)
    if result.returncode and 'already exists' not in result.stderr.lower():
        raise RuntimeErrorC2('worker_launch_failed:'+str(result.returncode))


def _launch_notify(event_key: str):
    run_hash=hashlib.sha256(event_key.encode()).hexdigest()[:24]
    command=[sys.executable,str(Path(__file__).with_name('c2_notify_worker.py')),
        '--event-key',event_key]
    result=subprocess.run(['systemd-run','--user','--collect',
        '--unit=c2-notify-'+run_hash,*command],capture_output=True,text=True)
    if result.returncode and 'already exists' not in result.stderr.lower():
        raise RuntimeErrorC2('notification_launch_failed:'+str(result.returncode))


def advance(db: sqlite3.Connection, *, submit=_writer_submit, launch=_launch_worker,
            launch_notify=_launch_notify,
            now: float | None=None, max_parallel: int=3,
            supervisor_expiry: float | None=None) -> dict:
    now=time.time() if now is None else now
    events=[]
    if supervisor_expiry is not None and db.execute("SELECT 1 FROM sqlite_master WHERE name='c2_supervisor_authority'").fetchone():
        authority=db.execute('SELECT fencing_token,lease_expires_at FROM c2_supervisor_authority WHERE singleton=1').fetchone()
        if (authority and authority['lease_expires_at'] <= now+300 and
                supervisor_expiry > authority['lease_expires_at']+1):
            key=_key('c2-renew-supervisor',{'token':authority['fencing_token'],
                                           'expires':supervisor_expiry})
            submit('renew_supervisor',{},key)
            return {'events':[('renew_supervisor',str(authority['fencing_token']))],
                    'ready':0,'active':0}
    for notice in db.execute("SELECT event_key,state FROM c2_notification_outbox WHERE state IN ('pending','sending') ORDER BY created_at,event_key"):
        key=str(notice['event_key'])
        if notice['state']=='pending':
            submit('claim_milestone',{'event_key':key},'c2-claim-milestone-'+hashlib.sha256(key.encode()).hexdigest()[:32])
            events.append(('claim_milestone',key))
        else:
            launch_notify(key)
            events.append(('notify',key))
    active=[dict(r) for r in db.execute("""SELECT r.* FROM work_item_runs r
       JOIN work_items w USING(work_item_id)
       WHERE r.state IN ('claimed','running','recovering')
       AND w.status='running' ORDER BY r.created_at,r.run_id""")]
    terminal_runs=db.execute('''SELECT r.run_id FROM work_item_runs r
       JOIN work_items w USING(work_item_id)
       WHERE r.executor='codex' AND r.state IN ('claimed','running','recovering')
       AND w.status IN ('completed','failed','blocked','cancelled')''').fetchall()
    for row in terminal_runs:
        run_id=str(row['run_id'])
        submit('reconcile_run',{'run_id':run_id},'c2-reconcile-'+run_id)
        events.append(('reconcile_run',run_id))
    for run in active:
        if run['state'] in ('claimed','recovering'):
            metadata=json.loads(run['metadata_json'])
            key=_key('c2-ack',{'run_id':run['run_id'],'metadata':metadata,
                               'state':run['state'],'lease_until':run['lease_until']})
            submit('acknowledge',{'run_id':run['run_id'],'worker_ref':'c2-run:'+run['run_id'],
                'metadata':metadata},key)
            events.append(('acknowledge',run['run_id']))
        elif run['worker_ref']=='c2-run:'+run['run_id']:
            launch(run['run_id'])
            events.append(('launch',run['run_id']))
    expired=[r for r in active if r['state'] in ('claimed','running') and r['lease_until']<=now]
    if expired:
        key=_key('c2-recover',sorted((r['run_id'],r['lease_until']) for r in expired))
        submit('recover',{},key)
        events.append(('recover',str(len(expired))))
    ready=[dict(r) for r in db.execute('''SELECT w.work_item_id,w.status,w.sort_order,w.repo,w.updated_at,
            s.activity,s.model,s.reasoning,s.worktree,s.project_url,s.resources_json
          FROM v_work_item_runnable w
          JOIN work_item_execution_specs s USING(work_item_id)
          ORDER BY CASE
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p0') THEN 0
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p1') THEN 1
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p2') THEN 2
            ELSE 3 END,
            COALESCE(w.sort_order,2147483647),w.work_item_id''')]
    statuses=[tuple(r) for r in db.execute('''SELECT w.work_item_id,w.status FROM work_items w
       WHERE w.status='running' AND (w.prompt_id IS NOT NULL OR EXISTS(
         SELECT 1 FROM work_item_runs r WHERE r.work_item_id=w.work_item_id
         AND r.state IN ('claimed','running','recovering')))
       ORDER BY w.work_item_id''')]
    dependencies=[tuple(r) for r in db.execute('''SELECT d.work_item_id,d.depends_on_work_item_id,w.status
          FROM work_item_dependencies d JOIN work_items w ON w.work_item_id=d.depends_on_work_item_id
          ORDER BY d.work_item_id,d.depends_on_work_item_id''')]
    if ready and len(statuses)<max_parallel:
        key=_key('c2-schedule',{'ready':ready,'running':statuses,'dependencies':dependencies,'limit':max_parallel})
        submit('schedule',{'event_key':key,'max_parallel':max_parallel},key)
        events.append(('schedule',str(len(ready))))
    return {'events':events,'ready':len(ready),'active':len(active)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=Path.home()/'projects/codex-roadmap/roadmap.sqlite')
    parser.add_argument('--max-parallel',type=int,default=3)
    parser.add_argument('--supervisor-id',required=True)
    parser.add_argument('--fencing-token',type=int,required=True)
    args=parser.parse_args()
    with closing(connect_supervisor(SUPERVISOR_DB)) as supervisor:
        def guard():
            return require_supervisor(supervisor,args.supervisor_id,args.fencing_token,time.time())
        def guarded_submit(*values):
            guard()
            return _writer_submit(*values)
        def guarded_launch(*values):
            guard()
            return _launch_worker(*values)
        def guarded_notify(*values):
            guard()
            return _launch_notify(*values)
        current=guard()
        with closing(_open_snapshot(args.db)) as db:
            result=advance(db,submit=guarded_submit,launch=guarded_launch,
                           launch_notify=guarded_notify,max_parallel=args.max_parallel,
                           supervisor_expiry=current['lease_expires_at'])
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
