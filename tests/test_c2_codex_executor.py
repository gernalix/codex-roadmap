from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_codex_executor import dispatch, ExecutorError


class RPC:
    def __init__(self,model='exact',lose_ack=False):
        self.model=model; self.lose_ack=lose_ack; self.calls=[]; self.goal=None
    def __call__(self,method,params):
        self.calls.append((method,params))
        if method in ('thread/start','thread/resume'):
            return {'thread':{'id':'thread-1'},'model':self.model,'reasoningEffort':'medium','cwd':'/tmp/worktree'}
        if method=='thread/goal/set':
            self.goal={**(self.goal or {}),**params}; return {}
        if method=='thread/goal/get': return {'goal':self.goal}
        if method=='turn/start':
            if self.lose_ack: raise TimeoutError('ack lost')
            return {'turn':{'id':'turn-1'}}
        if method=='thread/read': return {'thread':{'id':'thread-1','turns':[{'id':'turn-1'}]}}
        raise AssertionError(method)


class CodexExecutorTests(unittest.TestCase):
    def test_goal_and_metadata_are_structured_and_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            rpc=RPC(); metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree','goal_mode':True}
            result=dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=Path(tmp)/'receipt.json')
            self.assertEqual('started',result['phase'])
            self.assertEqual('Canonical body',rpc.goal['objective'])
            self.assertFalse(rpc.calls[0][1]['allowProviderModelFallback'])
            self.assertEqual('Canonical body',next(p for m,p in rpc.calls if m=='turn/start')['input'][0]['text'])

    def test_mismatch_does_not_start_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            rpc=RPC(model='fallback')
            with self.assertRaisesRegex(ExecutorError,'metadata_mismatch:model'):
                dispatch(rpc,run_id='run-1',metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'},prompt='Canonical body',receipt=Path(tmp)/'receipt.json')
            self.assertNotIn('turn/start',[method for method,_ in rpc.calls])

    def test_lost_ack_restart_never_duplicates_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            rpc=RPC(lose_ack=True); metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'}
            with self.assertRaises(TimeoutError):
                dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            resumed=RPC()
            result=dispatch(resumed,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            self.assertFalse(result['resubmitted'])
            self.assertNotIn('turn/start',[method for method,_ in resumed.calls])
