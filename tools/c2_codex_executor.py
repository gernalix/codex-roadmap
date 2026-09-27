"""Exact, restart-safe Codex app-server handoff for a canonical C2 run.

The injected RPC transport owns connectivity. The receipt owns only transport
identity; work status remains in the C2 writer database.
"""
from __future__ import annotations

import json
import re
import os
from pathlib import Path
import tempfile

from c2_codex_sandbox import workspace_write_policy


class ExecutorError(RuntimeError):
    pass


def persist(path: Path, data: dict):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd, temporary=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.')
    try:
        with os.fdopen(fd,'w') as stream:
            json.dump(data,stream,sort_keys=True)
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary,path)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _validate_response(response, metadata):
    for field, expected in [('model',metadata.get('model_id',metadata['model'])),('reasoningEffort',metadata['reasoning']),
                            ('cwd',metadata['worktree'])]:
        if response.get(field) != expected:
            raise ExecutorError('codex_exact_metadata_mismatch:'+field)


def record_terminal(receipt: Path, *, run_id: str, thread_id: str,
                    turn_id: str, status: str):
    if status not in ('completed','interrupted','failed'):
        raise ExecutorError('invalid_terminal_turn_status')
    state=json.loads(receipt.read_text())
    if (state.get('run_id')!=run_id or state.get('thread_id')!=thread_id or
            state.get('turn_id')!=turn_id or state.get('phase') not in ('started','terminal')):
        raise ExecutorError('terminal_turn_identity_mismatch')
    if state['phase']=='terminal' and state.get('turn_status')!=status:
        raise ExecutorError('terminal_turn_status_conflict')
    state.update(phase='terminal',turn_status=status)
    persist(receipt,state)



def parse_terminal_result(turn: dict, expected_prompt_id: str) -> dict | None:
    """Parse the compact C2 terminal contract; legacy RESULT reports remain recoverable."""
    finals=[item.get('text','') for item in (turn.get('items') or [])
            if item.get('type')=='agentMessage' and item.get('phase')=='final_answer']
    if not finals:
        return None
    text=str(finals[-1]).strip()
    lines=text.splitlines()
    if len(lines)<2 or lines[0].strip()!=f'PROMPT_ID={expected_prompt_id}':
        return None
    match=re.fullmatch(r'RESULT=(PASS|BLOCKED|FAIL|CANCELLED)',lines[1].strip())
    if not match:
        return None
    outcome=match.group(1)
    contract_line=next((line.strip() for line in lines[2:] if line.strip().startswith('C2_RESULT=')),None)
    if contract_line:
        try:
            payload=json.loads(contract_line.removeprefix('C2_RESULT='))
        except json.JSONDecodeError as exc:
            raise ExecutorError('invalid_c2_result_json') from exc
        if not isinstance(payload,dict):
            raise ExecutorError('invalid_c2_result_payload')
        allowed={'completed','remaining','evidence','blocker','next_action','summary'}
        if set(payload)-allowed:
            raise ExecutorError('invalid_c2_result_keys')
        for key in ('completed','remaining','evidence'):
            if key not in payload or not isinstance(payload[key],list):
                raise ExecutorError('invalid_c2_result_'+key)
        return {'outcome':outcome,'summary':payload.get('summary'),
                'completed':payload['completed'],'remaining':payload['remaining'],
                'evidence':payload['evidence'],'blocker':payload.get('blocker'),
                'next_action':payload.get('next_action'),'strict_contract':True}
    # Backward-compatible recovery: an explicit legacy RESULT line is still
    # authoritative enough to prevent "work done, C2 still running" drift.
    blocker=None; next_action=None
    if outcome=='BLOCKED':
        blocker='Executor reported BLOCKED; see final report evidence.'
        next_action='Resolve the reported blocker and resume or create a follow-up.'
    return {'outcome':outcome,'summary':None,'completed':[],'remaining':[],
            'evidence':[text],'blocker':blocker,'next_action':next_action,
            'strict_contract':False}


def dispatch(rpc, *, run_id: str, metadata: dict, prompt: str, receipt: Path,
             on_thread_created=None):
    if not run_id or not prompt or not all(metadata.get(k) for k in ('model','reasoning','worktree')):
        raise ExecutorError('canonical_execution_metadata_required')
    if receipt.exists():
        state=json.loads(receipt.read_text())
        if state['run_id']!=run_id or state['metadata']!=metadata:
            raise ExecutorError('dispatch_identity_conflict')
        if state['phase']=='terminal':
            return {'thread_id':state['thread_id'],'turn_id':state['turn_id'],
                    'phase':'terminal','turn_status':state['turn_status'],
                    'resubmitted':False}
    else:
        state={'run_id':run_id,'metadata':metadata,'phase':'new'}
        persist(receipt,state)
    sandbox=workspace_write_policy(metadata['worktree'])
    if state['phase']=='new':
        response=rpc('thread/start',{
            'model':metadata.get('model_id',metadata['model']),'cwd':metadata['worktree'],
            'config':{'model_reasoning_effort':metadata['reasoning']},
            'allowProviderModelFallback':False,'ephemeral':False,
            'approvalPolicy':'on-request','approvalsReviewer':'auto_review',
            'sandbox':'workspace-write',
        })
        # A lost thread/start acknowledgement may leave an empty thread, but no
        # work starts until its verified identity is durably recorded here.
        state.update(thread_id=response['thread']['id'],phase='created')
        persist(receipt,state)
        _validate_response(response,metadata)
    else:
        response=rpc('thread/resume',{'threadId':state['thread_id'],
            'model':metadata.get('model_id',metadata['model']),'cwd':metadata['worktree'],
            'config':{'model_reasoning_effort':metadata['reasoning']},
            'approvalPolicy':'on-request','approvalsReviewer':'auto_review',
            'sandbox':'workspace-write'})
        _validate_response(response,metadata)
    thread_id=state['thread_id']
    if on_thread_created is not None:
        on_thread_created(thread_id)
    if state['phase'] in ('starting','started'):
        # Never resubmit an ambiguously acknowledged turn. Inspect the existing
        # thread; the supervisor can reconcile completion or resume that worker.
        observed=rpc('thread/read',{'threadId':thread_id,'includeTurns':True})
        if state['phase']=='starting':
            turns=(observed.get('thread') or {}).get('turns') or []
            if len(turns)>1:
                raise ExecutorError('ambiguous_turn_history')
            if len(turns)==1:
                turn_id=turns[0].get('id')
                if not turn_id:
                    raise ExecutorError('observed_turn_identity_missing')
                state.update(phase='started',turn_id=turn_id)
                persist(receipt,state)
        if state['phase']=='started' and metadata.get('goal_mode'):
            goal=rpc('thread/goal/get',{'threadId':thread_id}).get('goal')
            if not goal or goal.get('objective')!=prompt:
                raise ExecutorError('codex_goal_readback_mismatch')
            if goal['status']=='paused':
                rpc('thread/goal/set',{'threadId':thread_id,'status':'active'})
        return {'thread_id':thread_id,'turn_id':state.get('turn_id'),
                'phase':state['phase'],'observed':observed,'resubmitted':False}
    if metadata.get('goal_mode'):
        # Set the objective paused so it cannot race the explicit first turn.
        rpc('thread/goal/set',{'threadId':thread_id,'objective':prompt,'status':'paused'})
        goal=rpc('thread/goal/get',{'threadId':thread_id}).get('goal')
        if not goal or goal.get('objective')!=prompt or goal.get('status')!='paused':
            raise ExecutorError('codex_goal_readback_mismatch')
    state['phase']='starting'; persist(receipt,state)
    result=rpc('turn/start',{'threadId':thread_id,
        'input':[{'type':'text','text':prompt,'text_elements':[]}],
        'model':metadata.get('model_id',metadata['model']),'effort':metadata['reasoning'],
        'cwd':metadata['worktree'],'approvalPolicy':'on-request',
        'approvalsReviewer':'auto_review','sandboxPolicy':sandbox,
        'clientUserMessageId':'c2-'+run_id})
    state.update(phase='started',turn_id=result['turn']['id'])
    persist(receipt,state)
    if metadata.get('goal_mode'):
        rpc('thread/goal/set',{'threadId':thread_id,'status':'active'})
    return {'thread_id':thread_id,'turn_id':state['turn_id'],'phase':'started','resubmitted':False}
