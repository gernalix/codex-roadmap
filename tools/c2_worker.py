#!/usr/bin/env python3
"""Execute a claimed C2 run from the read-only canonical snapshot."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import sys

from c2_appserver_rpc import AppServerRPC, AppServerError, resolve_model
from c2_chatgpt_executor import dispatch as dispatch_browser, lane_degraded, KILL_SWITCH
from c2_codex_executor import dispatch as dispatch_codex, record_terminal, parse_terminal_result, ExecutorError
from c2_goal_objective import compact_goal_objective
from roadmap_finish import _queue_repo_integration
from roadmap_result import RoadmapResultError
from c2_native_executor import execute as execute_native
from c2_inbox_codex_executor import execute as execute_inbox_codex
from c2_runtime import _open_snapshot, _writer_submit
from c3_symphony_route import (routing_mode, eligible as symphony_eligible,
                               dispatch as dispatch_symphony, ownership_path, RouteError)
from c3_symphony_bridge import BridgeError
from c3_symphony_backend import BackendError

STATE_ROOT=Path.home()/'.local/state/c2/runs'
DEFAULT_DB=Path.home()/'projects/codex-roadmap/roadmap.sqlite'


class WorkerError(RuntimeError):
    pass


def run_once(db_path: Path, run_id: str, *, state_root=STATE_ROOT, submit=_writer_submit,
             rpc_factory=AppServerRPC):
    with closing(_open_snapshot(db_path)) as conn:
        run=conn.execute('''SELECT r.*,w.status AS item_status,w.prompt_id,w.repo,w.executor_policy,
          w.title AS item_title,w.objective,w.acceptance_json,w.next_action
          FROM work_item_runs r JOIN work_items w USING(work_item_id)
          WHERE r.run_id=?''',(run_id,)).fetchone()
        if not run or run['state'] not in ('running','recovering') or run['item_status']!='running':
            raise WorkerError('run_not_claimed_and_acknowledged')
        if run['worker_ref']!='c2-run:'+run_id:
            raise WorkerError('worker_identity_mismatch')
        if not conn.execute('''SELECT 1 FROM work_item_executor_starts
              WHERE run_id=? LIMIT 1''',(run_id,)).fetchone():
            raise WorkerError('executor_start_receipt_missing')
        metadata=json.loads(run['metadata_json'])
        executor=run['executor']
        if executor=='symphony':
            routing=routing_mode()
            expected=metadata.get('symphony_route') or {}
            if (expected.get('mode')!=routing.mode
                    or expected.get('tracker_repo')!=routing.tracker_repo
                    or set(expected.get('source_repos',()))!=routing.source_repos
                    or not symphony_eligible(routing,
                        activity=str(metadata.get('activity') or ''),
                        policy=str(run['executor_policy']),repo=run['repo'])):
                raise WorkerError('symphony_claim_route_changed')
            return dispatch_symphony(db_path,run_id,str(run['work_item_id']),routing,
                                     submit=submit)
        if (executor=='codex' and metadata.get('activity')=='coding'
                and re.fullmatch(r'wi:[a-f0-9]{32}',str(run['work_item_id']))
                and ownership_path(str(run['work_item_id'])).exists()):
            raise WorkerError('symphony_ownership_requires_reconciliation')
        is_issue_triage=bool(conn.execute('''SELECT 1 FROM work_item_tags
              WHERE work_item_id=? AND tag='c2:issue-triage' LIMIT 1''',
              (run['work_item_id'],)).fetchone())
        browser_lane_unavailable = lane_degraded() or KILL_SWITCH.exists()
        if executor in ('rdc','chatgpt') and metadata.get('activity') in ('gui','semantic') and browser_lane_unavailable:
            if is_issue_triage and metadata.get('activity')=='semantic':
                result=execute_inbox_codex(run_id=run_id,
                    work_item_id=str(run['work_item_id']),db_path=db_path)
                return {'run_id':run_id,'executor':'codex-fallback',
                        'phase':result['state'],'before':result['before'],'after':result['after']}
            return {'run_id':run_id,'executor':executor,'phase':'suspended'}
        if executor=='rdc' and metadata.get('activity')=='native':
            receipt=Path(state_root)/f'{run_id}.native.json'
            result=execute_native(run_id=run_id,metadata=metadata,receipt=receipt)
            if result['state'] in ('completed','failed'):
                submit('complete',{'run_id':run_id,'succeeded':result['state']=='completed',
                    'worker_ref':run['worker_ref']},'c2-complete-'+run_id)
            return {'run_id':run_id,'state':result['state'],'executor':'native'}
        if executor in ('rdc','chatgpt') and metadata.get('activity') in ('gui','semantic'):
            acceptance=json.loads(run['acceptance_json'] or '[]')
            lines=[str(run['objective'] or run['item_title'])]
            if acceptance:
                lines += ['Acceptance:']+['- '+str(a) for a in acceptance]
            if run['next_action']:
                lines += ['Next action: '+str(run['next_action'])]
            lines += [
                'C2 control: progress checkpoints are optional and only for recovery while work is ongoing.',
                'For the terminal outcome use exactly one structured call to tools/c2_executor_result.py.',
                'Write a small JSON payload with completed, remaining, evidence, blocker, next_action',
                'and call it with --result PASS|BLOCKED|FAIL|CANCELLED --run-id '+run_id+
                ' --work-item-id '+str(run['work_item_id'])+'.',
                'Do not separately mutate C2 status; the writer validates and applies the receipt.',
            ]
            prompt='\n'.join(lines)
            work_item_id=str(run['work_item_id'])
        elif executor=='codex':
            prompt_id=run['prompt_id']
            if not prompt_id or metadata.get('prompt_id')!=prompt_id:
                raise WorkerError('canonical_prompt_identity_mismatch')
            body=conn.execute('''SELECT body FROM prompt_materializations
                WHERE prompt_id=? ORDER BY created_at DESC LIMIT 1''',(prompt_id,)).fetchone()
            if not body:
                raise WorkerError('canonical_prompt_body_missing')
            prompt=body['body']
            goal_objective=(compact_goal_objective(prompt_id=prompt_id,
                title=str(run['item_title']),prompt=prompt)
                if metadata.get('goal_mode') else None)
        else:
            raise WorkerError('executor_adapter_unavailable:'+executor)
    prompt += ('\nC2_RUN_ID='+run_id+'\nC2_WORK_ITEM_ID='+str(run['work_item_id'])+
        '\nIncidental issue: immediately submit only its description with '
        'python3 tools/c2_issue_capture.py "description". Use C2_TASK_ID/C2_RUN_ID '
        'from this run context if shell environment is available; otherwise pass '
        '--task-id and --run-id shown here. Do not investigate or triage it; '
        'continue the original task immediately.')
    if executor=='codex':
        if goal_objective:
            prompt += ('\nC2 Goal recovery: before substantive work, create or update '
                f'operations/task-state/{prompt_id}.md with a compact, self-contained '
                'objective, mandatory scope and invariants, verified progress, remaining '
                'work, and exactly one next action. Keep it current at meaningful '
                'milestones. On resumption read that checkpoint first, then current '
                'canonical C2 state; do not replay this full prompt or chat history.')
        prompt += (
            '\nC2 terminal contract: the final response must have line 1 PROMPT_ID=<id>, '
            'line 2 RESULT=PASS|BLOCKED|FAIL|CANCELLED, and line 3 exactly '
            'C2_RESULT=<one-line JSON>. JSON keys: completed(list of exact acceptance '
            'criteria satisfied), remaining(list), evidence(list of concise concrete '
            'proof such as tests/commit/PR/device verification), blocker(string|null), '
            'next_action(string|null); optional summary. PASS requires remaining=[], '
            'blocker=null and nonempty evidence. Do not repeat run/task/chat IDs in JSON.'
        )
    if executor in ('rdc','chatgpt'):
        result=dispatch_browser(run_id=run_id,work_item_id=work_item_id,
            metadata=metadata,prompt=prompt,db_path=db_path,
            receipt=Path(state_root)/f'{run_id}.chatgpt.json')
        if result.get('chat_url'):
            submit('bind_executor',{
                'run_id':run_id,'executor_ref':result['chat_url'],
                'chat_url':result['chat_url']},'c2-bind-'+run_id)
        if result['phase']=='starting':
            submit('quarantine_browser',{'run_id':run_id,
                'reason':'Browser delivery uncertain; inspect the existing session before recovery'},
                'c2-quarantine-'+run_id)
        return {'run_id':run_id,'executor':executor,'phase':result['phase']}
    with rpc_factory() as rpc:
        model_id=resolve_model(rpc,metadata['model'],metadata['reasoning'])
        exact_metadata={**metadata,'model_id':model_id}
        receipt=Path(state_root)/f'{run_id}.codex.json'
        def bind_thread(thread_id):
            submit('bind_executor',{'run_id':run_id,'executor_ref':thread_id,
                'chat_url':'codex://threads/'+thread_id},'c2-bind-'+run_id)
        result=dispatch_codex(rpc,run_id=run_id,metadata=exact_metadata,
            prompt=prompt,goal_objective=goal_objective,receipt=receipt,
            on_thread_created=bind_thread)
        terminal=None
        if result['phase']=='terminal':
            observed=rpc('thread/read',{'threadId':result['thread_id'],'includeTurns':True})
            terminal=next((turn for turn in (observed.get('thread') or {}).get('turns',[])
                           if turn.get('id')==result.get('turn_id')),None)
            if terminal is None:
                raise WorkerError('codex_terminal_turn_missing')
            result['phase']=result['turn_status']
        elif result['phase']=='started':
            turn_id=result.get('turn_id')
            if not turn_id:
                raise WorkerError('codex_started_turn_identity_missing')
            try:
                terminal=rpc.wait_for_turn(result['thread_id'],turn_id)
            except AppServerError as exc:
                if str(exc)!='orphaned_turn_requires_recovery':
                    raise
                terminal={'id':turn_id,'status':'interrupted','items':[]}
            record_terminal(receipt,run_id=run_id,thread_id=result['thread_id'],
                turn_id=turn_id,status=terminal['status'])
            result['phase']=terminal['status']
        if terminal is not None:
            parsed=parse_terminal_result(terminal,prompt_id)
            terminal_status=str(terminal.get('status') or '')
            if parsed is None and terminal_status=='completed':
                raise WorkerError('codex_terminal_contract_missing')
            if parsed is None and terminal_status in ('failed','cancelled','interrupted'):
                outcome=('FAIL' if terminal_status=='failed' else
                         'BLOCKED' if terminal_status=='interrupted' else 'CANCELLED')
                parsed={
                    'outcome':outcome,
                    'summary':'Codex turn terminated before producing the C2 terminal contract',
                    'completed':[],
                    'remaining':['Task did not complete'],
                    'evidence':['Codex turn '+str(result.get('turn_id'))+' ended '+terminal_status],
                    'blocker':'Codex turn ended '+terminal_status+' before a terminal result was produced',
                    'next_action':'Retry from the existing checkpoint or create a follow-up run.',
                    'strict_contract':True,
                }
            if parsed is not None:
                base_args={'run_id':run_id,'prompt_id':prompt_id,**parsed,
                           'integration_ready':False}
                submit('executor_result',base_args,'c2-executor-result-'+run_id)
                if parsed['outcome']=='PASS':
                    try:
                        _,integrated=_queue_repo_integration(prompt_id,Path(str(metadata['worktree'])))
                    except RoadmapResultError as exc:
                        raise WorkerError(str(exc)) from exc
                    if integrated:
                        final_args={**base_args,'integration_ready':True}
                        submit('executor_result',final_args,
                               'c2-executor-result-final-'+run_id)
    return {'run_id':run_id,'executor':'codex','thread_id':result['thread_id'],'phase':result['phase']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    try:
        result=run_once(args.db,args.run_id)
    except (OSError,sqlite3.Error,WorkerError,AppServerError,ExecutorError,RouteError,
            BridgeError,BackendError,
            ValueError,KeyError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},sort_keys=True))
        return 2
    print(json.dumps({'status':'ok','result':result},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
