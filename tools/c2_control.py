#!/usr/bin/env python3
"""Submit C2 commands to the one canonical writer; never open the live DB writable."""
import argparse
import json
from pathlib import Path
from submit_mutation import submit_document
from c2_supervisor_lease import DEFAULT_DB, connect, _require, record_activity
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-key',required=True)
    parser.add_argument('--operation',required=True,choices=(
        'claim_supervisor','renew_supervisor','retire_supervisor',
        'intake','prepare_codex','configure','auto_configure','schedule','acknowledge','checkpoint','record_checkpoint','recover','quarantine_browser','finish_work_item','verify_work_item','complete','reconcile_run','milestone','claim_milestone','mark_milestone','reimport_terminal_state','repair_prompt_materialization','reconcile_item','executor_started','bind_executor','promote_issue','discard_issue','ensure_issue_triage','set_manual_order','clear_manual_order'))
    parser.add_argument('--arguments',type=Path,required=True,help='JSON object with structured arguments')
    parser.add_argument('--supervisor-id',required=True)
    parser.add_argument('--fencing-token',type=int,required=True)
    args=parser.parse_args()
    arguments=json.loads(args.arguments.read_text())
    if not isinstance(arguments,dict):
        parser.error('arguments must be an object')
    with connect(DEFAULT_DB) as lease:
        row=_require(lease,args.supervisor_id,args.fencing_token,time.time())
        row=record_activity(lease,supervisor_id=row['supervisor_id'],
                            token=row['fencing_token'],
                            operation='control:'+args.operation)
        arguments['supervisor_authority']={
            'supervisor_id':row['supervisor_id'],
            'fencing_token':row['fencing_token'],
            'lease_expires_at':row['lease_expires_at'],
        }
    result=submit_document({'schema':'codex-roadmap.mutation.v1','actor':'c2-control',
        'operations':[{'op':'c2_'+args.operation,'arguments':arguments}]},request_key=args.request_key)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
