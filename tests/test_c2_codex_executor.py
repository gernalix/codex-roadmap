from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_codex_executor import dispatch, record_terminal, ExecutorError


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
            self.assertEqual('auto_review',rpc.calls[0][1]['approvalsReviewer'])
            turn_params=next(p for m,p in rpc.calls if m=='turn/start')
            self.assertEqual('Canonical body',turn_params['input'][0]['text'])
            self.assertEqual('auto_review',turn_params['approvalsReviewer'])

    def test_mismatch_does_not_start_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            rpc=RPC(model='fallback')
            with self.assertRaisesRegex(ExecutorError,'metadata_mismatch:model'):
                dispatch(rpc,run_id='run-1',metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'},prompt='Canonical body',receipt=Path(tmp)/'receipt.json')
            self.assertNotIn('turn/start',[method for method,_ in rpc.calls])

    def test_lost_ack_restart_never_duplicates_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            rpc=RPC(lose_ack=True); metadata={'model':'exact','reasoning':'medium',
                'worktree':'/tmp/worktree','goal_mode':True}
            with self.assertRaises(TimeoutError):
                dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            resumed=RPC()
            resumed.goal=rpc.goal
            result=dispatch(resumed,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            self.assertFalse(result['resubmitted'])
            self.assertEqual('started',result['phase'])
            self.assertEqual('turn-1',result['turn_id'])
            self.assertEqual('active',resumed.goal['status'])
            resume_params=next(p for m,p in resumed.calls if m=='thread/resume')
            self.assertEqual('auto_review',resume_params['approvalsReviewer'])
            self.assertNotIn('turn/start',[method for method,_ in resumed.calls])

    def test_lost_ack_without_observed_turn_stays_ambiguous_without_resubmit(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'}
            rpc=RPC(lose_ack=True)
            with self.assertRaises(TimeoutError):
                dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            class EmptyRPC(RPC):
                def __call__(self,method,params):
                    if method=='thread/read':
                        self.calls.append((method,params))
                        return {'thread':{'id':'thread-1','turns':[]}}
                    return super().__call__(method,params)
            empty=EmptyRPC()
            result=dispatch(empty,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            self.assertEqual('starting',result['phase'])
            self.assertIsNone(result['turn_id'])
            self.assertNotIn('turn/start',[method for method,_ in empty.calls])

    def test_terminal_receipt_prevents_turn_resubmission(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'}
            started=dispatch(RPC(),run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            record_terminal(receipt,run_id='run-1',thread_id=started['thread_id'],
                turn_id=started['turn_id'],status='completed')
            resumed=RPC()
            result=dispatch(resumed,run_id='run-1',metadata=metadata,prompt='Canonical body',receipt=receipt)
            self.assertEqual('terminal',result['phase'])
            self.assertEqual('completed',result['turn_status'])
            self.assertEqual([],resumed.calls)
