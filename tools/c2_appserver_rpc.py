"""Bounded JSON-RPC transport to the existing Codex app-server daemon.

Uses the documented local proxy; never starts/stops the user's daemon. No model
work is launched by initialization or model discovery.
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
        self.process=subprocess.Popen(command or ['codex','app-server','proxy'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        self.buffer=b''; self.sequence=0
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

    def __call__(self, method, params):
        self.sequence+=1
        request_id=self.sequence
        self._send({'id':request_id,'method':method,'params':params})
        deadline=time.monotonic()+self.timeout
        while True:
            if b'\n' not in self.buffer:
                remaining=deadline-time.monotonic()
                if remaining<=0 or not select.select([self.process.stdout],[],[],remaining)[0]:
                    raise AppServerError('rpc_timeout:'+method)
                chunk=os.read(self.process.stdout.fileno(),65536)
                if not chunk:
                    raise AppServerError('rpc_transport_closed:'+method)
                self.buffer+=chunk
                continue
            line,self.buffer=self.buffer.split(b'\n',1)
            message=json.loads(line)
            if 'method' in message and 'id' in message:
                # Never approve requests as a side effect of transport handling.
                self._send({'id':message['id'],'error':{'code':-32601,'message':'C2 requires explicit approval handling'}})
                raise AppServerError('approval_or_interaction_required')
            if message.get('id')!=request_id:
                continue
            if 'error' in message:
                raise AppServerError('rpc_rejected:'+method+':'+str(message['error'].get('code')))
            return message['result']

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
