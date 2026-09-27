from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_codex_executor import dispatch, record_terminal, parse_terminal_result, ExecutorError
from c2_goal_objective import compact_goal_objective
from c2_codex_sandbox import git_metadata_writable_roots


class RPC:
    def __init__(self,model='exact',lose_ack=False,cwd='/tmp/worktree'):
        self.model=model; self.lose_ack=lose_ack; self.cwd=cwd; self.calls=[]; self.goal=None
    def __call__(self,method,params):
        self.calls.append((method,params))
        if method in ('thread/start','thread/resume'):
            return {'thread':{'id':'thread-1'},'model':self.model,'reasoningEffort':'medium','cwd':self.cwd}
        if method=='thread/goal/set':
            self.goal={**(self.goal or {}),**params}; return {}
        if method=='thread/goal/get': return {'goal':self.goal}
        if method=='turn/start':
            if self.lose_ack: raise TimeoutError('ack lost')
            return {'turn':{'id':'turn-1'}}
        if method=='thread/read': return {'thread':{'id':'thread-1','turns':[{'id':'turn-1'}]}}
        raise AssertionError(method)


class CodexExecutorTests(unittest.TestCase):
    def setUp(self):
        self.sandbox_patch=patch('c2_codex_executor.workspace_write_policy',return_value={
            'type':'workspaceWrite','writableRoots':[],'networkAccess':False})
        self.sandbox_patch.start()
        self.addCleanup(self.sandbox_patch.stop)

    def test_external_linked_worktree_gets_only_its_git_metadata_root(self):
        self.sandbox_patch.stop()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            repository=root/'repository'
            worktree=root/'assigned-worktree'
            subprocess.run(['git','init','--initial-branch=main',str(repository)],check=True,
                           stdout=subprocess.DEVNULL)
            (repository/'base.txt').write_text('base\n')
            subprocess.run(['git','-C',str(repository),'add','base.txt'],check=True)
            subprocess.run(['git','-C',str(repository),'-c','user.name=C2 Test',
                            '-c','user.email=c2@example.invalid','commit','-m','base'],
                           check=True,stdout=subprocess.DEVNULL)
            subprocess.run(['git','-C',str(repository),'worktree','add','-b','task/test',
                            str(worktree)],check=True,stdout=subprocess.DEVNULL)
            roots=git_metadata_writable_roots(worktree)
            self.assertEqual([str((repository/'.git').resolve())],roots)
            self.assertNotIn(str(root.resolve()),roots)
            rpc=RPC(cwd=str(worktree))
            dispatch(rpc,run_id='run-external',metadata={
                'model':'exact','reasoning':'medium','worktree':str(worktree)},
                prompt='Commit and finish.',receipt=root/'receipt.json')
            start=next(params for method,params in rpc.calls if method=='thread/start')
            self.assertEqual('workspace-write',start['sandbox'])
            self.assertEqual({'type':'workspaceWrite','writableRoots':roots,
                              'networkAccess':False},next(
                params for method,params in rpc.calls if method=='turn/start')['sandboxPolicy'])
            (worktree/'change.txt').write_text('change\n')
            subprocess.run(['git','-C',str(worktree),'add','change.txt'],check=True)
            subprocess.run(['git','-C',str(worktree),'-c','user.name=C2 Test',
                            '-c','user.email=c2@example.invalid','commit','-m','change'],
                           check=True,stdout=subprocess.DEVNULL)
            self.assertEqual('',subprocess.run(['git','-C',str(worktree),'status','--porcelain'],
                                               text=True,capture_output=True,check=True).stdout)
        self.sandbox_patch.start()

    def test_strict_terminal_contract_parses_structured_receipt(self):
        text='PROMPT_ID=123456\nRESULT=PASS\nC2_RESULT={"completed":["A"],"remaining":[],"evidence":["pytest PASS"],"blocker":null,"next_action":null}'
        turn={'items':[{'type':'agentMessage','phase':'final_answer','text':text}]}
        result=parse_terminal_result(turn,'123456')
        self.assertTrue(result['strict_contract'])
        self.assertEqual('PASS',result['outcome'])
        self.assertEqual(['pytest PASS'],result['evidence'])

    def test_legacy_terminal_report_is_recoverable(self):
        text='PROMPT_ID=123456\nRESULT=PASS\n\nTests PASS; commit abc.'
        turn={'items':[{'type':'agentMessage','phase':'final_answer','text':text}]}
        result=parse_terminal_result(turn,'123456')
        self.assertFalse(result['strict_contract'])
        self.assertEqual([text],result['evidence'])

    def test_malformed_structured_terminal_contract_fails_closed(self):
        text='PROMPT_ID=123456\nRESULT=PASS\nC2_RESULT={"completed":[]}'
        turn={'items':[{'type':'agentMessage','phase':'final_answer','text':text}]}
        with self.assertRaisesRegex(ExecutorError,'invalid_c2_result_remaining'):
            parse_terminal_result(turn,'123456')


    def test_thread_binding_precedes_first_turn_and_failure_blocks_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            rpc=RPC()
            metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree'}
            def bind(thread_id):
                self.assertEqual('thread-1',thread_id)
                self.assertNotIn('turn/start',[method for method,_ in rpc.calls])
                raise RuntimeError('binding unavailable')
            with self.assertRaisesRegex(RuntimeError,'binding unavailable'):
                dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',
                    receipt=Path(tmp)/'receipt.json',on_thread_created=bind)
            self.assertNotIn('turn/start',[method for method,_ in rpc.calls])

    def test_goal_and_metadata_are_structured_and_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            rpc=RPC(); metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree','goal_mode':True}
            result=dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',
                goal_objective='Compact goal',receipt=Path(tmp)/'receipt.json')
            self.assertEqual('started',result['phase'])
            self.assertEqual('Compact goal',rpc.goal['objective'])
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
                dispatch(rpc,run_id='run-1',metadata=metadata,prompt='Canonical body',
                    goal_objective='Compact goal',receipt=receipt)
            resumed=RPC()
            resumed.goal=rpc.goal
            result=dispatch(resumed,run_id='run-1',metadata=metadata,prompt='Canonical body',
                goal_objective='Compact goal',receipt=receipt)
            self.assertFalse(result['resubmitted'])
            self.assertEqual('started',result['phase'])
            self.assertEqual('turn-1',result['turn_id'])
            self.assertEqual('active',resumed.goal['status'])
            resume_params=next(p for m,p in resumed.calls if m=='thread/resume')
            self.assertEqual('auto_review',resume_params['approvalsReviewer'])
            self.assertNotIn('turn/start',[method for method,_ in resumed.calls])

    def test_goal_contract_preserves_scope_and_invariants_without_history(self):
        body='Pasted metadata and long history\n# Goal\nFinish the release.\n# Scope\nOnly service A.\n# Invariants\nKeep existing data.\n# Starting point\nOld history to avoid.\n# Acceptance\nLive check passes.'
        objective=compact_goal_objective(prompt_id='123456',title='Release',prompt=body)
        self.assertIn('Only service A.',objective)
        self.assertIn('Keep existing data.',objective)
        self.assertIn('Live check passes.',objective)
        self.assertIn('operations/task-state/123456.md',objective)
        self.assertNotIn('Old history to avoid.',objective)

    def test_goal_dispatch_requires_compact_objective(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ExecutorError,'compact_goal_objective_required'):
                dispatch(RPC(),run_id='run-1',metadata={'model':'exact','reasoning':'medium',
                    'worktree':'/tmp/worktree','goal_mode':True},prompt='Canonical body',
                    receipt=Path(tmp)/'receipt.json')

    def test_plain_text_goal_contract_and_legacy_goal_upgrade(self):
        body='PROMPT_ID=123456\n\nFinish the release.\n\nHard constraints:\n- Keep data.\n\nAcceptance:\n- Live check passes.'
        objective=compact_goal_objective(prompt_id='123456',title='Release',prompt=body)
        self.assertIn('Finish the release.',objective)
        self.assertIn('Keep data.',objective)
        self.assertIn('Live check passes.',objective)
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            metadata={'model':'exact','reasoning':'medium','worktree':'/tmp/worktree','goal_mode':True}
            rpc=RPC()
            dispatch(rpc,run_id='run-1',metadata=metadata,prompt=body,
                goal_objective=objective,receipt=receipt)
            rpc.goal['objective']=body  # Existing thread from the older full-prompt implementation.
            resumed=dispatch(rpc,run_id='run-1',metadata=metadata,prompt=body,
                goal_objective=objective,receipt=receipt)
            self.assertFalse(resumed['resubmitted'])
            self.assertEqual(objective,rpc.goal['objective'])

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
