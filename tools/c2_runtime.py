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
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from submit_mutation import submit_document
from c2_supervisor_lease import DEFAULT_DB as SUPERVISOR_DB, connect as connect_supervisor, _require as require_supervisor, snapshot as supervisor_snapshot, record_activity
from c2_mutations import SUPERVISOR_OPERATIONS
from c2_scheduler import read_override, override_matches, dispatchable, inbox_drain_state, inbox_gate_exempt
from c2_chatgpt_executor import lane_degraded
from c2_repository_integration import integration_status, prompt_repository

C2_TRIAGE_PROJECT_URL = 'https://chatgpt.com/g/g-p-6ab69fbdbaf88191a39a75ff5c9e3d70/project'
class RuntimeErrorC2(RuntimeError):
    pass


def _user_systemd_environment() -> dict[str, str]:
    """Recover the conventional user bus environment omitted by headless callers."""
    env = os.environ.copy()
    runtime_dir = Path(env.get('XDG_RUNTIME_DIR') or f'/run/user/{os.getuid()}')
    if not env.get('XDG_RUNTIME_DIR') and runtime_dir.is_dir():
        env['XDG_RUNTIME_DIR'] = str(runtime_dir)
    bus = runtime_dir / 'bus'
    if not env.get('DBUS_SESSION_BUS_ADDRESS') and bus.is_socket():
        env['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path={bus}'
    return env


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
            row=record_activity(lease,supervisor_id=row['supervisor_id'],
                                token=row['fencing_token'],
                                operation='writer:'+operation)
            arguments['supervisor_authority']={
                'supervisor_id':row['supervisor_id'],
                'fencing_token':row['fencing_token'],
                'lease_expires_at':row['lease_expires_at'],
            }
            if operation == 'acknowledge':
                # The same snapshot can be replayed after a lease renewal.
                # Its fenced document changes, so its Issue identity must too.
                key = _key('c2-ack-authorized', {
                    'request_key':key,
                    'authority':arguments['supervisor_authority'],
                })
    return submit_document({'schema':'codex-roadmap.mutation.v1','actor':'c2-runtime',
        'operations':[{'op':'c2_'+operation,'arguments':arguments}]},request_key=key)


def _launch_worker(run_id: str, db_path: Path):
    unit='c2-run-'+run_id
    command=[sys.executable,str(Path(__file__).with_name('c2_worker.py')),
        '--run-id',run_id,'--db',str(db_path)]
    env = _user_systemd_environment()
    result=subprocess.run(['systemd-run','--user','--collect',
        '--unit='+unit,*command],capture_output=True,text=True,env=env)
    if result.returncode:
        active=subprocess.run(['systemctl','--user','is-active','--quiet',unit],
            capture_output=True,env=env)
        if active.returncode:
            raise RuntimeErrorC2('worker_launch_failed:'+str(result.returncode))


def _launch_notify(event_key: str):
    run_hash=hashlib.sha256(event_key.encode()).hexdigest()[:24]
    command=[sys.executable,str(Path(__file__).with_name('c2_notify_worker.py')),
        '--event-key',event_key]
    result=subprocess.run(['systemd-run','--user','--collect',
        '--unit=c2-notify-'+run_hash,*command],capture_output=True,text=True)
    if result.returncode and 'already exists' not in result.stderr.lower():
        raise RuntimeErrorC2('notification_launch_failed:'+str(result.returncode))


def _repo_task_status(prompt_id: str) -> dict:
    try:
        repository=prompt_repository(Path.home()/'projects/codex-roadmap/roadmap.sqlite',prompt_id)
        return integration_status(prompt_id,repository)
    except Exception as exc:
        raise RuntimeErrorC2('repo_task_status_failed:'+str(exc)) from exc


def advance(db: sqlite3.Connection, *, submit=_writer_submit, launch=_launch_worker,
            launch_notify=_launch_notify,
            repo_task_status=_repo_task_status,
            now: float | None=None, max_parallel: int=3,
            supervisor_expiry: float | None=None,
            supervisor_authority: dict | None=None,
            triage_project_url: str | None=None) -> dict:
    now=time.time() if now is None else now
    events=[]
    has_issue_inbox = bool(db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='issue_inbox'"
    ).fetchone())
    has_manual_order = bool(db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='manual_order_overrides'"
    ).fetchone())
    pending_issue_inbox = (
        int(db.execute("SELECT COUNT(*) FROM issue_inbox WHERE state='pending'").fetchone()[0])
        if has_issue_inbox else 0
    )
    if pending_issue_inbox:
        events.append(('issue_inbox_pending', str(pending_issue_inbox)))
    if supervisor_authority is not None and db.execute("SELECT 1 FROM sqlite_master WHERE name='c2_supervisor_authority'").fetchone():
        current_id=str(supervisor_authority['supervisor_id'])
        current_token=int(supervisor_authority['fencing_token'])
        current_expiry=float(supervisor_authority['lease_expires_at'])
        authority=db.execute(
            'SELECT supervisor_id,fencing_token,lease_expires_at FROM c2_supervisor_authority WHERE singleton=1'
        ).fetchone()
        same=bool(authority and str(authority['supervisor_id'])==current_id
                  and int(authority['fencing_token'])==current_token)
        if not same:
            if authority and float(authority['lease_expires_at'])>now:
                return {'events':[('supervisor_fenced',str(authority['fencing_token']))],
                        'ready':0,'active':0}
            key=_key('c2-claim-supervisor',{'supervisor_id':current_id,
                                            'token':current_token,
                                            'expires':current_expiry})
            submit('claim_supervisor',{},key)
            return {'events':[('claim_supervisor',str(current_token))],
                    'ready':0,'active':0}
        if (float(authority['lease_expires_at']) <= now+300 and
                current_expiry > float(authority['lease_expires_at'])+1):
            key=_key('c2-renew-supervisor',{'token':current_token,
                                           'expires':current_expiry})
            submit('renew_supervisor',{},key)
            return {'events':[('renew_supervisor',str(current_token))],
                    'ready':0,'active':0}
    elif supervisor_expiry is not None and db.execute("SELECT 1 FROM sqlite_master WHERE name='c2_supervisor_authority'").fetchone():
        authority=db.execute('SELECT fencing_token,lease_expires_at FROM c2_supervisor_authority WHERE singleton=1').fetchone()
        if (authority and authority['lease_expires_at'] <= now+300 and
                supervisor_expiry > authority['lease_expires_at']+1):
            key=_key('c2-renew-supervisor',{'token':authority['fencing_token'],
                                           'expires':supervisor_expiry})
            submit('renew_supervisor',{},key)
            return {'events':[('renew_supervisor',str(authority['fencing_token']))],
                    'ready':0,'active':0}
    if pending_issue_inbox and triage_project_url:
        triage = db.execute("""SELECT w.work_item_id,w.status FROM work_items w
            JOIN work_item_tags t USING(work_item_id) WHERE t.tag='c2:issue-triage'
            ORDER BY w.created_at DESC,w.work_item_id DESC LIMIT 1""").fetchone()
        if triage is None or triage['status'] in ('completed','failed','cancelled','superseded','waived'):
            pending_ids = [
                str(row[0]) for row in db.execute(
                    """SELECT i.issue_id FROM issue_inbox i
                       LEFT JOIN manual_order_overrides o
                         ON o.scope='inbox' AND o.entity_id=i.issue_id
                       WHERE i.state='pending'
                       ORDER BY CASE WHEN o.rank IS NULL THEN 1 ELSE 0 END,
                                o.rank,i.observed_at_ms,i.issue_id"""
                    if has_manual_order else
                    "SELECT issue_id FROM issue_inbox WHERE state='pending' ORDER BY observed_at_ms,issue_id"
                )
            ]
            key=_key('c2-issue-triage-intake',{'pending':pending_ids,
                'previous':str(triage['work_item_id']) if triage else None})
            submit('ensure_issue_triage',{'project_url':triage_project_url},key)
            events.append(('issue_triage_intake',str(pending_issue_inbox)))
            return {'events':events,'ready':0,'active':0,
                    'issue_inbox_pending':pending_issue_inbox}
        events.append(('issue_triage_active',str(triage['work_item_id'])))
    elif pending_issue_inbox:
        events.append(('issue_triage_unconfigured',str(pending_issue_inbox)))

    # Recover missed terminal delivery natively; a PASS receipt and canonical
    # repository merge are both required before the writer replays finalization.
    pass_receipts=db.execute('''SELECT rr.* FROM work_item_result_receipts rr
        JOIN work_items w USING(work_item_id)
        WHERE rr.outcome='PASS' AND rr.prompt_id IS NOT NULL AND w.status='running'
        ORDER BY rr.captured_at,rr.receipt_id''').fetchall()
    for receipt in pass_receipts:
        prompt_id=str(receipt['prompt_id'])
        integration=repo_task_status(prompt_id)
        if integration.get('status')!='merged' or integration.get('integration_state')!='merged':
            continue
        arguments={
            'prompt_id':prompt_id,'run_id':receipt['run_id'],'outcome':'PASS',
            'summary':receipt['summary'],'completed':json.loads(receipt['completed_json']),
            'remaining':json.loads(receipt['remaining_json']),
            'evidence':json.loads(receipt['evidence_json']),'blocker':receipt['blocker'],
            'next_action':receipt['next_action'],'strict_contract':bool(receipt['strict_contract']),
            'integration_ready':True,
        }
        key='c2-replay-executor-result-'+hashlib.sha256(
            (str(receipt['receipt_id'])+':'+str(receipt['payload_sha256'])+':'+
             str(integration.get('merge_sha') or '')).encode()).hexdigest()[:32]
        submit('executor_result',arguments,key)
        events.append(('reconcile_executor_result',prompt_id))

    for notice in db.execute("SELECT event_key,state FROM c2_notification_outbox WHERE state IN ('pending','sending') ORDER BY created_at,event_key"):
        key=str(notice['event_key'])
        if notice['state']=='pending':
            submit('claim_milestone',{'event_key':key},'c2-claim-milestone-'+hashlib.sha256(key.encode()).hexdigest()[:32])
            events.append(('claim_milestone',key))
        else:
            launch_notify(key)
            events.append(('notify',key))
    chatgpt_suspended=lane_degraded()
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
        metadata=json.loads(run['metadata_json'])
        if chatgpt_suspended and metadata.get('activity') in ('gui','semantic'):
            continue
        if run['state'] in ('claimed','recovering'):
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
    ready_query='''SELECT w.*,
            s.activity,s.model,s.reasoning,s.worktree,s.project_url,s.resources_json'''
    if has_manual_order:
        ready_query+=''',o.rank AS manual_rank,o.source AS manual_order_source,
            o.source_modified_at AS manual_order_source_modified_at'''
    ready_query+=''' FROM v_work_item_runnable w
          JOIN work_item_execution_specs s USING(work_item_id)'''
    if has_manual_order:
        ready_query+=""" LEFT JOIN manual_order_overrides o
          ON o.scope='roadmap' AND o.entity_id=w.work_item_id"""
        ready_query+=""" ORDER BY CASE WHEN o.rank IS NULL THEN 1 ELSE 0 END,o.rank,"""
    else:
        ready_query+=''' ORDER BY '''
    ready_query+='''CASE
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p0') THEN 0
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p1') THEN 1
            WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p2') THEN 2
            ELSE 3 END,
            COALESCE(w.sort_order,2147483647),w.created_at,w.work_item_id'''
    ready=[dict(r) for r in db.execute(ready_query)]
    inbox_gate=inbox_drain_state(db)
    if inbox_gate:
        ready=[r for r in ready if inbox_gate_exempt(db,r)]
        events.append(('issue_inbox_drain',inbox_gate))
    if chatgpt_suspended:
        ready=[r for r in ready if r['activity'] not in ('gui','semantic')]
    override=read_override(db)
    scoped_ready=[r for r in ready if override and override_matches(db,r,override)
                  and dispatchable(db,r)]
    if scoped_ready:
        ready=scoped_ready
    if override:
        events.append(('execution_override',override['selector']+':'+override['value']+':'+
                       ('draining' if scoped_ready else 'fallback')))
    statuses=[tuple(r) for r in db.execute('''SELECT w.work_item_id,w.status FROM work_items w
       WHERE w.status='running' AND (w.prompt_id IS NOT NULL OR EXISTS(
         SELECT 1 FROM work_item_runs r WHERE r.work_item_id=w.work_item_id
         AND r.state IN ('claimed','running','recovering')))
       ORDER BY w.work_item_id''')]
    lock_context=[
        tuple(r) for r in db.execute('''SELECT w.work_item_id,w.status,w.repo,w.project_name,
              COALESCE(s.worktree,'') AS worktree
           FROM work_items w LEFT JOIN work_item_execution_specs s USING(work_item_id)
           WHERE w.status='running' AND w.repo IS NOT NULL
           ORDER BY w.work_item_id''')
    ]
    dependencies=[tuple(r) for r in db.execute('''SELECT d.work_item_id,d.depends_on_work_item_id,w.status
          FROM work_item_dependencies d JOIN work_items w ON w.work_item_id=d.depends_on_work_item_id
          ORDER BY d.work_item_id,d.depends_on_work_item_id''')]
    if ready and len(statuses)<max_parallel:
        key=_key('c2-schedule',{'ready':ready,'chatgpt_lane_degraded':chatgpt_suspended,
                                  'running':statuses,'lock_context':lock_context,
                                  'dependencies':dependencies,'override':override,'limit':max_parallel})
        submit('schedule',{'event_key':key,'max_parallel':max_parallel,
                           'chatgpt_lane_degraded':chatgpt_suspended},key)
        events.append(('schedule',str(len(ready))))
    return {'events':events,'ready':len(ready),'active':len(active),
            'execution_override':override,'override_draining':bool(scoped_ready),
            'issue_inbox_pending':pending_issue_inbox}


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
            current=guard()
            result=_launch_worker(*values,args.db)
            record_activity(supervisor,supervisor_id=current['supervisor_id'],
                            token=current['fencing_token'],
                            operation='executor:launch',step=str(values[0]))
            return result
        def guarded_notify(*values):
            current=guard()
            result=_launch_notify(*values)
            record_activity(supervisor,supervisor_id=current['supervisor_id'],
                            token=current['fencing_token'],
                            operation='notification:launch',step=str(values[0]))
            return result
        current=guard()
        with closing(_open_snapshot(args.db)) as db:
            result=advance(db,submit=guarded_submit,launch=guarded_launch,
                           launch_notify=guarded_notify,max_parallel=args.max_parallel,
                           triage_project_url=C2_TRIAGE_PROJECT_URL,
                           supervisor_authority={
                               'supervisor_id':current['supervisor_id'],
                               'fencing_token':current['fencing_token'],
                               'lease_expires_at':current['lease_expires_at'],
                           })
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
