#!/usr/bin/env python3
"""Notify C2 that an executor has actually started handling a running work item."""
from __future__ import annotations

import argparse
import hashlib
import json
import os

from submit_mutation import MutationSubmitError, submit_document


def _env(name: str) -> str | None:
    value=os.environ.get(name)
    return value.strip() if value and value.strip() else None


def submit_start(*, run_id=None, work_item_id=None, prompt_id=None,
                 executor=None, executor_ref=None, chat_url=None):
    run_id=run_id or _env('C2_RUN_ID')
    work_item_id=work_item_id or _env('C2_WORK_ITEM_ID')
    prompt_id=prompt_id or _env('C2_PROMPT_ID')
    executor_ref=executor_ref or _env('C2_EXECUTOR_REF')
    chat_url=chat_url or _env('CHATGPT_CONVERSATION_URL')
    thread_id=_env('CODEX_THREAD_ID')
    if not executor_ref and thread_id:
        executor_ref=thread_id
    if not chat_url and thread_id:
        chat_url='codex://threads/'+thread_id
    executor=executor or _env('C2_EXECUTOR')
    if not executor and thread_id:
        executor='codex'
    if not any((run_id,work_item_id,prompt_id)):
        raise ValueError('run/work-item/prompt identity required')
    if not executor and not run_id:
        raise ValueError('executor required when run_id is unavailable')
    arguments={
        'run_id':run_id,'work_item_id':work_item_id,'prompt_id':prompt_id,
        'executor':executor,'executor_ref':executor_ref,'chat_url':chat_url,
    }
    arguments={k:v for k,v in arguments.items() if v is not None}
    # Request identity must include optional binding fields. The canonical
    # executor_started receipt remains keyed by run/work-item+executor inside
    # the writer, so a later call may safely enrich executor_ref/chat_url.
    # Reusing one transport key for both the unbound and bound documents makes
    # submit_mutation reject the legitimate enrichment as a key conflict.
    encoded=json.dumps(arguments,sort_keys=True,ensure_ascii=False,
                       separators=(',',':')).encode()
    key='c2-executor-start-'+hashlib.sha256(encoded).hexdigest()[:32]
    return submit_document({
        'schema':'codex-roadmap.mutation.v1',
        'actor':'c2-executor-start',
        'operations':[{'op':'c2_executor_started','arguments':arguments}],
    },request_key=key)
def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id')
    parser.add_argument('--work-item-id')
    parser.add_argument('--prompt-id')
    parser.add_argument('--executor')
    parser.add_argument('--executor-ref')
    parser.add_argument('--chat-url')
    args=parser.parse_args()
    try:
        result=submit_start(run_id=args.run_id,work_item_id=args.work_item_id,
            prompt_id=args.prompt_id,executor=args.executor,
            executor_ref=args.executor_ref,chat_url=args.chat_url)
    except (ValueError,OSError,MutationSubmitError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},sort_keys=True))
        return 2
    print(json.dumps({'status':'ok',**result},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
