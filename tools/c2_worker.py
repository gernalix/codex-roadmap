#!/usr/bin/env python3
"""Execute a claimed C2 run from the read-only canonical snapshot."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys

from c2_appserver_rpc import AppServerRPC, resolve_model
from c2_codex_executor import dispatch as dispatch_codex
from c2_native_executor import execute as execute_native
from c2_runtime import _open_snapshot, _writer_submit

STATE_ROOT=Path.home()/'.local/state/c2/runs'
DEFAULT_DB=Path.home()/'projects/codex-roadmap/roadmap.sqlite'


class WorkerError(RuntimeError):
    pass


def run_once(db_path: Path, run_id: str, *, state_root=STATE_ROOT, submit=_writer_submit,
             rpc_factory=AppServerRPC):
    with closing(_open_snapshot(db_path)) as conn:
        run=conn.execute('''SELECT r.*,w.status AS item_status,w.prompt_id
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
        if executor=='codex':
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
    with rpc_factory() as rpc:
        model_id=resolve_model(rpc,metadata['model'],metadata['reasoning'])
        exact_metadata={**metadata,'model_id':model_id}
        result=dispatch_codex(rpc,run_id=run_id,metadata=exact_metadata,
            prompt=prompt,receipt=Path(state_root)/f'{run_id}.codex.json')
    return {'run_id':run_id,'executor':'codex','thread_id':result['thread_id'],'phase':result['phase']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    try:
        result=run_once(args.db,args.run_id)
    except (OSError,sqlite3.Error,WorkerError,ValueError,KeyError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},sort_keys=True))
        return 2
    print(json.dumps({'status':'ok','result':result},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
