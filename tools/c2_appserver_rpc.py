"""JSON-RPC transport for a dedicated Codex app-server stdio process.

The worker owns this process and keeps it connected through turn completion.
Initialization and model discovery do not launch model work.
"""
from __future__ import annotations

import json
import os
import select
import subprocess
import time


class AppServerError(RuntimeError):
    pass


class AppServerRPC:
    def __init__(self, command=None, timeout=30):
        self.timeout=timeout
        self.process=subprocess.Popen(command or ['codex','app-server'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        self.buffer=b''; self.sequence=0; self.notifications=[]
        try:
            self('initialize',{'clientInfo':{'name':'c2-control-plane','version':'1'},
                               'capabilities':{'experimentalApi':True}})
            self._send({'method':'initialized'})
        except Exception:
            self.close()
            raise

    def _send(self, document):
        self.process.stdin.write((json.dumps(document)+'\n').encode())
        self.process.stdin.flush()

    def _receive(self, timeout):
        deadline=time.monotonic()+timeout
        while True:
            if b'\n' not in self.buffer:
                remaining=deadline-time.monotonic()
                if remaining<=0 or not select.select([self.process.stdout],[],[],remaining)[0]:
                    return None
                chunk=os.read(self.process.stdout.fileno(),65536)
                if not chunk:
                    raise AppServerError('rpc_transport_closed')
                self.buffer+=chunk
                continue
            line,self.buffer=self.buffer.split(b'\n',1)
            message=json.loads(line)
            if 'method' in message and 'id' in message:
                # Never approve requests as a side effect of transport handling.
                self._send({'id':message['id'],'error':{'code':-32601,'message':'C2 requires explicit approval handling'}})
                raise AppServerError('approval_or_interaction_required')
            return message

    def __call__(self, method, params):
        self.sequence+=1
        request_id=self.sequence
        self._send({'id':request_id,'method':method,'params':params})
        deadline=time.monotonic()+self.timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:
                raise AppServerError('rpc_timeout:'+method)
            message=self._receive(remaining)
            if message is None:
                raise AppServerError('rpc_timeout:'+method)
            if 'method' in message:
                if message['method']=='turn/completed':
                    self.notifications.append(message)
                continue
            if message.get('id')!=request_id:
                continue
            if 'error' in message:
                raise AppServerError('rpc_rejected:'+method+':'+str(message['error'].get('code')))
            return message['result']

    def wait_for_turn(self, thread_id, turn_id, *, idle_check=30):
        """Keep the owning stdio server alive until this turn is terminal."""
        while True:
            while self.notifications:
                message=self.notifications.pop(0)
                if message.get('method')=='turn/completed':
                    params=message.get('params') or {}
                    turn=params.get('turn') or {}
                    if params.get('threadId') in (None,thread_id) and turn.get('id')==turn_id:
                        return turn
            message=self._receive(idle_check)
            if message is None:
                observed=self('thread/read',{'threadId':thread_id,'includeTurns':True})
                thread=observed.get('thread',{})
                for turn in thread.get('turns',[]):
                    if turn.get('id')==turn_id and turn.get('status') in ('completed','interrupted','failed'):
                        return turn
                    if turn.get('id')==turn_id and (thread.get('status') or {}).get('type') in ('idle','notLoaded','systemError'):
                        raise AppServerError('orphaned_turn_requires_recovery')
            elif message.get('method')=='turn/completed':
                self.notifications.append(message)

    def close(self):
        if self.process.stdin:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=3)
        if self.process.stdout:
            self.process.stdout.close()

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()


def resolve_model(rpc, requested, reasoning):
    # Roadmap labels use spaces; the catalog uses hyphens. Normalize only
    # these spelling separators, never model families or version numbers.
    normalize=lambda value: str(value or '').casefold().replace(' ', '-')
    matches=[]; cursor=None
    while True:
        response=rpc('model/list',{'cursor':cursor,'limit':100})
        matches.extend(m for m in response['data'] if normalize(requested) in {normalize(m.get(k)) for k in ('id','model','displayName')})
        cursor=response.get('nextCursor')
        if not cursor:
            break
    if len(matches)!=1:
        raise AppServerError('exact_model_not_available:'+requested)
    match=matches[0]
    if reasoning not in [r['reasoningEffort'] for r in match.get('supportedReasoningEfforts',[])]:
        raise AppServerError('exact_reasoning_not_available:'+reasoning)
    return match['model']
