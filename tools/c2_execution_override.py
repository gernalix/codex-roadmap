#!/usr/bin/env python3
"""Read or request a fenced canonical temporary C2 execution override."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json

from c2_prepare_codex import _current_authority
from c2_runtime import _open_snapshot
from c2_scheduler import read_override
from c3_storage import CANONICAL_DB
from submit_mutation import submit_document


def _canonical_document_bytes(document: dict) -> bytes:
    return (json.dumps(document, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


def _request_key(document: dict) -> str:
    digest = hashlib.sha256(_canonical_document_bytes(document)).hexdigest()[:32]
    return 'c2-execution-override-' + digest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db')
    sub = parser.add_subparsers(dest='action', required=True)
    setter = sub.add_parser('set')
    setter.add_argument('--selector', choices=('project','repo','tag'), required=True)
    setter.add_argument('--value', required=True)
    sub.add_parser('clear')
    sub.add_parser('read')
    args = parser.parse_args(argv)
    if args.action == 'read':
        from pathlib import Path
        with closing(_open_snapshot(Path(args.db) if args.db else CANONICAL_DB)) as db:
            print(json.dumps({'execution_override': read_override(db)}, sort_keys=True))
        return 0
    authority = _current_authority('execution_override:'+args.action)
    arguments = {'supervisor_authority': authority}
    if args.action == 'set':
        arguments.update(selector=args.selector, value=args.value, mode='drain_first')
    operation = 'c2_set_execution_override' if args.action == 'set' else 'c2_clear_execution_override'
    payload = {'schema':'codex-roadmap.mutation.v1','actor':'c2-execution-override',
               'operations':[{'op':operation,'arguments':arguments}]}
    result = submit_document(payload, request_key=_request_key(payload))
    print(json.dumps({'status':'queued', **result}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
