#!/usr/bin/env python3
"""Submit C2 commands to the one canonical writer; never open the live DB writable."""
import argparse
import json
from pathlib import Path
from submit_mutation import submit_document
from c2_supervisor_lease import DEFAULT_DB, connect, _require, record_activity
import time


OPERATIONS = (
    'claim_supervisor','renew_supervisor','retire_supervisor',
    'intake','prepare_codex','configure','auto_configure','schedule','acknowledge',
    'checkpoint','record_checkpoint','recover','quarantine_browser','finish_work_item',
    'verify_work_item','complete','reconcile_run','milestone','claim_milestone',
    'mark_milestone','reimport_terminal_state','repair_prompt_materialization',
    'reconcile_item','reconcile_blocked','reconcile_blocked_safety_net',
    'executor_started','bind_executor','promote_issue','discard_issue',
    'edit_issue','void_issue',
    'ensure_issue_triage','set_manual_order','clear_manual_order','set_human_copy',
)


def submit_controls(*, operations, request_key, supervisor_id, fencing_token,
                    actor='c2-control-batch', canonical_renew=False):
    """Submit a bounded set of fenced C2 operations in one writer transaction."""
    if not isinstance(operations, list) or not operations or len(operations) > 50:
        raise ValueError('operations_must_be_nonempty_bounded_list')
    normalized=[]
    for entry in operations:
        if not isinstance(entry, dict):
            raise ValueError('batch_operation_must_be_object')
        operation=entry.get('operation')
        arguments=entry.get('arguments')
        if operation not in OPERATIONS:
            raise ValueError('invalid_c2_control_operation')
        if not isinstance(arguments, dict):
            raise ValueError('arguments_must_be_object')
        normalized.append((operation, dict(arguments)))
    with connect(DEFAULT_DB) as lease:
        row=_require(lease,supervisor_id,int(fencing_token),time.time())
        row=record_activity(lease,supervisor_id=row['supervisor_id'],
                            token=row['fencing_token'],operation='control:batch')
        authority={
            'supervisor_id':row['supervisor_id'],
            'fencing_token':row['fencing_token'],
            'lease_expires_at':row['lease_expires_at'],
        }
    writer_ops=[]
    if canonical_renew:
        writer_ops.append({'op':'c2_renew_supervisor','arguments':{
            'supervisor_authority':dict(authority),
        }})
    for operation,arguments in normalized:
        arguments['supervisor_authority']=dict(authority)
        writer_ops.append({'op':'c2_'+operation,'arguments':arguments})
    return submit_document({'schema':'codex-roadmap.mutation.v1','actor':actor,
        'operations':writer_ops},request_key=request_key)


def submit_control(*, operation, arguments, request_key, supervisor_id,
                   fencing_token, actor='c2-control', canonical_renew=False):
    """Submit one command after validating and renewing the current local fence.

    ``canonical_renew`` atomically prepends a writer-side lease renewal. It is
    intended for asynchronously applied Workflowy control mutations, where the
    canonical lease can otherwise expire between enqueue and writer apply.
    """
    if operation not in OPERATIONS:
        raise ValueError('invalid_c2_control_operation')
    if not isinstance(arguments,dict):
        raise ValueError('arguments_must_be_object')
    arguments=dict(arguments)
    with connect(DEFAULT_DB) as lease:
        row=_require(lease,supervisor_id,int(fencing_token),time.time())
        row=record_activity(lease,supervisor_id=row['supervisor_id'],
                            token=row['fencing_token'],
                            operation='control:'+operation)
        full_authority={
            'supervisor_id':row['supervisor_id'],
            'fencing_token':row['fencing_token'],
            'lease_expires_at':row['lease_expires_at'],
        }
        arguments['supervisor_authority']={
            'supervisor_id':row['supervisor_id'],
            'fencing_token':row['fencing_token'],
        }
        stable_authority = (
            operation == 'clear_manual_order' and actor == 'c2-workflowy-order'
            and not canonical_renew
        )
        if not stable_authority:
            arguments['supervisor_authority']['lease_expires_at'] = row['lease_expires_at']
    operations=[]
    if canonical_renew:
        operations.append({'op':'c2_renew_supervisor','arguments':{
            'supervisor_authority':full_authority,
        }})
    operations.append({'op':'c2_'+operation,'arguments':arguments})
    return submit_document({'schema':'codex-roadmap.mutation.v1','actor':actor,
        'operations':operations},request_key=request_key)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-key',required=True)
    parser.add_argument('--operation',required=True,choices=OPERATIONS)
    parser.add_argument('--arguments',type=Path,required=True,help='JSON object with structured arguments')
    parser.add_argument('--supervisor-id',required=True)
    parser.add_argument('--fencing-token',type=int,required=True)
    args=parser.parse_args(argv)
    arguments=json.loads(args.arguments.read_text())
    if not isinstance(arguments,dict):
        parser.error('arguments must be an object')
    result=submit_control(operation=args.operation,arguments=arguments,
        request_key=args.request_key,supervisor_id=args.supervisor_id,
        fencing_token=args.fencing_token)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
