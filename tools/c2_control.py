#!/usr/bin/env python3
"""Submit C2 commands to the one canonical writer; never open the live DB writable."""
import argparse
import json
from pathlib import Path
from submit_mutation import submit_document


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-key',required=True)
    parser.add_argument('--operation',required=True,choices=(
        'intake','prepare_codex','configure','schedule','acknowledge','checkpoint','recover','complete'))
    parser.add_argument('--arguments',type=Path,required=True,help='JSON object with structured arguments')
    args=parser.parse_args()
    arguments=json.loads(args.arguments.read_text())
    if not isinstance(arguments,dict):
        parser.error('arguments must be an object')
    result=submit_document({'schema':'codex-roadmap.mutation.v1','actor':'c2-control',
        'operations':[{'op':'c2_'+args.operation,'arguments':arguments}]},request_key=args.request_key)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
