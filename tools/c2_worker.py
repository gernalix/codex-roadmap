#!/usr/bin/env python3
"""Execute a claimed C2 run from the read-only canonical snapshot."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys

from c2_appserver_rpc import AppServerRPC, AppServerError, resolve_model
from c2_chatgpt_executor import dispatch as dispatch_browser
from c2_codex_executor import dispatch as dispatch_codex, record_terminal, ExecutorError
from c2_native_executor import execute as execute_native
from c2_runtime import _open_snapshot, _writer_submit

STATE_ROOT=Path.home()/'.local/state/c2/runs'
DEFAULT_DB=Path.home()/'projects/codex-roadmap/roadmap.sqlite'


class WorkerError(RuntimeError):
    pass


def run_once(db_path: Path, run_id: str, *, state_root=STATE_ROOT, submit=_writer_submit,
             rpc_factory=AppServerRPC):
    with closing(_open_snapshot(db_path)) as conn:
        run=conn.execute('''SELECT r.*,w.status AS item_status,w.prompt_id,
          w.title AS item_title,w.objective,w.acceptance_json,w.next_action
          FROM work_item_runs r JOIN work_items w USING(work_item_id)
          WHERE r.run_id=?''',(run_id,)).fetchone()
        if not run or run['state'] not in ('running','recovering') or run['item_status']!='running':
            raise WorkerError('run_not_claimed_and_acknowledged')
        if run['worker_ref']!='c2-run:'+run_id:
            raise WorkerError('worker_identity_mismatch')
        metadata=json.loads(run['metadata_json'])
        executor=run['executor']
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
                'C2 control: record progress and evidence through the canonical roadmap writer',
                'using tools/c2_control.py --operation record_checkpoint with this TASK_ID.',
                'Before claiming completion, record a checkpoint with remaining=[] and no blocker.',
                'Then submit --operation finish_work_item with the TASK_ID and nonempty acceptance evidence.',
                'Use a unique --request-key and a JSON --arguments file for each operation.',
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
        else:
            raise WorkerError('executor_adapter_unavailable:'+executor)
    if executor in ('rdc','chatgpt'):
        result=dispatch_browser(run_id=run_id,work_item_id=work_item_id,
            metadata=metadata,prompt=prompt,db_path=db_path,
            receipt=Path(state_root)/f'{run_id}.chatgpt.json')
        if result['phase']=='starting':
            submit('quarantine_browser',{'run_id':run_id,
                'reason':'Browser delivery uncertain; inspect the existing session before recovery'},
                'c2-quarantine-'+run_id)
        return {'run_id':run_id,'executor':executor,'phase':result['phase']}
    with rpc_factory() as rpc:
        model_id=resolve_model(rpc,metadata['model'],metadata['reasoning'])
        exact_metadata={**metadata,'model_id':model_id}
        receipt=Path(state_root)/f'{run_id}.codex.json'
        result=dispatch_codex(rpc,run_id=run_id,metadata=exact_metadata,
            prompt=prompt,receipt=receipt)
        if result['phase']=='terminal':
            result['phase']=result['turn_status']
        if result['phase']=='started':
            turn_id=result.get('turn_id')
            if not turn_id:
                raise WorkerError('codex_started_turn_identity_missing')
            terminal=rpc.wait_for_turn(result['thread_id'],turn_id)
            record_terminal(receipt,run_id=run_id,thread_id=result['thread_id'],
                turn_id=turn_id,status=terminal['status'])
            result['phase']=terminal['status']
    return {'run_id':run_id,'executor':'codex','thread_id':result['thread_id'],'phase':result['phase']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    try:
        result=run_once(args.db,args.run_id)
    except (OSError,sqlite3.Error,WorkerError,AppServerError,ExecutorError,ValueError,KeyError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},sort_keys=True))
        return 2
    print(json.dumps({'status':'ok','result':result},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
