"""Exact, restart-safe Codex app-server handoff for a canonical C2 run.

The injected RPC transport owns connectivity. The receipt owns only transport
identity; work status remains in the C2 writer database.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile


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
    for field, expected in [('model',metadata['model']),('reasoningEffort',metadata['reasoning']),
                            ('cwd',metadata['worktree'])]:
        if response.get(field) != expected:
            raise ExecutorError('codex_exact_metadata_mismatch:'+field)


def dispatch(rpc, *, run_id: str, metadata: dict, prompt: str, receipt: Path):
    if not run_id or not prompt or not all(metadata.get(k) for k in ('model','reasoning','worktree')):
        raise ExecutorError('canonical_execution_metadata_required')
    if receipt.exists():
        state=json.loads(receipt.read_text())
        if state['run_id']!=run_id or state['metadata']!=metadata:
            raise ExecutorError('dispatch_identity_conflict')
    else:
        state={'run_id':run_id,'metadata':metadata,'phase':'new'}
        persist(receipt,state)
    if state['phase']=='new':
        response=rpc('thread/start',{
            'model':metadata['model'],'cwd':metadata['worktree'],
            'config':{'model_reasoning_effort':metadata['reasoning']},
            'allowProviderModelFallback':False,'ephemeral':False,
            'approvalPolicy':'on-request','sandbox':'workspace-write',
        })
        # A lost thread/start acknowledgement may leave an empty thread, but no
        # work starts until its verified identity is durably recorded here.
        state.update(thread_id=response['thread']['id'],phase='created')
        persist(receipt,state)
        _validate_response(response,metadata)
    else:
        response=rpc('thread/resume',{'threadId':state['thread_id'],
            'model':metadata['model'],'cwd':metadata['worktree'],
            'config':{'model_reasoning_effort':metadata['reasoning']}})
        _validate_response(response,metadata)
    thread_id=state['thread_id']
    if state['phase'] in ('starting','started'):
        # Never resubmit an ambiguously acknowledged turn. Inspect the existing
        # thread; the supervisor can reconcile completion or resume that worker.
        observed=rpc('thread/read',{'threadId':thread_id,'includeTurns':True})
        return {'thread_id':thread_id,'phase':state['phase'],'observed':observed,'resubmitted':False}
    if metadata.get('goal_mode'):
        # Set the objective paused so it cannot race the explicit first turn.
        rpc('thread/goal/set',{'threadId':thread_id,'objective':prompt,'status':'paused'})
        goal=rpc('thread/goal/get',{'threadId':thread_id}).get('goal')
        if not goal or goal.get('objective')!=prompt or goal.get('status')!='paused':
            raise ExecutorError('codex_goal_readback_mismatch')
    state['phase']='starting'; persist(receipt,state)
    result=rpc('turn/start',{'threadId':thread_id,
        'input':[{'type':'text','text':prompt,'text_elements':[]}],
        'model':metadata['model'],'effort':metadata['reasoning'],
        'cwd':metadata['worktree'],'clientUserMessageId':'c2-'+run_id})
    state.update(phase='started',turn_id=result['turn']['id'])
    persist(receipt,state)
    if metadata.get('goal_mode'):
        rpc('thread/goal/set',{'threadId':thread_id,'status':'active'})
    return {'thread_id':thread_id,'turn_id':state['turn_id'],'phase':'started','resubmitted':False}
