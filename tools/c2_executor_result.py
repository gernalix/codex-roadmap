#!/usr/bin/env python3
"""Submit one structured executor terminal result to the canonical C2 writer."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

from submit_mutation import submit_document


def _env(name: str) -> str | None:
    value=os.environ.get(name)
    return value.strip() if value and value.strip() else None


def build_request_key(arguments: dict) -> str:
    """Derive replay identity from the canonical executor-result semantics."""
    encoded=json.dumps(arguments,sort_keys=True,ensure_ascii=False,
                       separators=(',',':')).encode()
    return 'c2-executor-result-'+hashlib.sha256(encoded).hexdigest()[:32]


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',required=True,
        choices=('PASS','BLOCKED','FAIL','CANCELLED'))
    parser.add_argument('--payload',type=Path,required=True,
        help='JSON object: completed, remaining, evidence, blocker, next_action; optional summary')
    parser.add_argument('--run-id')
    parser.add_argument('--work-item-id')
    parser.add_argument('--prompt-id')
    args=parser.parse_args()
    payload=json.loads(args.payload.read_text(encoding='utf-8'))
    if not isinstance(payload,dict):
        parser.error('payload must be a JSON object')
    allowed={'completed','remaining','evidence','blocker','next_action','summary'}
    if set(payload)-allowed:
        parser.error('unsupported payload keys: '+','.join(sorted(set(payload)-allowed)))
    for key in ('completed','remaining','evidence'):
        if key not in payload or not isinstance(payload[key],list):
            parser.error(key+' must be a list')

    run_id=args.run_id or _env('C2_RUN_ID')
    work_item_id=args.work_item_id or _env('C2_WORK_ITEM_ID')
    prompt_id=args.prompt_id or _env('C2_PROMPT_ID')
    if not any((run_id,work_item_id,prompt_id)):
        parser.error('run/work-item/prompt identity required')

    arguments={
        'outcome':args.result,
        'run_id':run_id,
        'work_item_id':work_item_id,
        'prompt_id':prompt_id,
        'strict_contract':True,
        **payload,
    }
    arguments={k:v for k,v in arguments.items() if v is not None}
    identity=run_id or work_item_id or prompt_id
    key=build_request_key(arguments)
    result=submit_document({
        'schema':'codex-roadmap.mutation.v1',
        'actor':'c2-executor',
        'operations':[{'op':'c2_executor_result','arguments':arguments}],
    },request_key=key)
    print(json.dumps({
        'status':'ok',
        'result':args.result,
        'identity':identity,
        **result,
    },sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
