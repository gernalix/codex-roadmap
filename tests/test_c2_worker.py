from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake,c2_scheduler,c2_worker
from test_c2_intake import C2IntakeTests


class WorkerTests(unittest.TestCase):

    def test_issue_triage_uses_codex_fallback_when_chat_lane_is_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(conn,title='Triage C2 issue inbox')
                conn.execute("INSERT INTO work_item_tags(work_item_id,tag) VALUES(?, 'c2:issue-triage')",
                    (item['work_item_id'],))
                conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",
                    (item['work_item_id'],))
                metadata={'activity':'semantic','project_url':'https://chatgpt.com/g/g-p-test/project'}
                conn.execute("""INSERT INTO work_item_runs VALUES(
                  'triage-fallback',?,'event',1,'chatgpt','running',100,
                  'c2-run:triage-fallback',NULL,?,1)""",
                  (item['work_item_id'],json.dumps(metadata)))
                c2_scheduler.executor_started(conn,run_id='triage-fallback',now=2)
                conn.commit()
                fallback={'state':'progress','before':20,'after':10,'returncode':0}
                kill_switch=root/'disable-chat-supervisor'; kill_switch.write_text('')
                with patch.object(c2_worker,'lane_degraded',return_value=False), \
                     patch.object(c2_worker,'KILL_SWITCH',kill_switch), \
                     patch.object(c2_worker,'execute_inbox_codex',return_value=fallback) as execute:
                    result=c2_worker.run_once(path,'triage-fallback',state_root=root/'receipts',
                        submit=lambda *_:self.fail('fallback should own its fenced writes'))
                self.assertEqual('codex-fallback',result['executor'])
                self.assertEqual('progress',result['phase'])
                self.assertEqual(10,result['after'])
                execute.assert_called_once()
            finally:
                conn.close()

    def test_terminal_codex_output_auto_submits_receipt_and_safe_pass_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                conn.execute("INSERT OR REPLACE INTO prompt_materializations(prompt_id,body,sha256,created_at,actor) VALUES(?,?,?,?,?)",
                    ('123456','PROMPT_ID=123456\nDo the task.','fixture-sha','2026-01-01T00:00:00Z','test'))
                metadata={'activity':'coding','model':'exact','reasoning':'medium',
                    'worktree':'/tmp/worktree','prompt_id':'123456',
                    'work_item_id':'prompt:123456','goal_mode':0}
                conn.execute("""INSERT INTO work_item_runs VALUES(
                  'auto-result','prompt:123456','event',1,'codex','running',100,
                  'c2-run:auto-result',NULL,?,1)""",(json.dumps(metadata),))
                c2_scheduler.executor_started(conn,run_id='auto-result',now=2)
                conn.commit()
                turn={'id':'turn-1','status':'completed','items':[{
                    'type':'agentMessage','phase':'final_answer','text':
                    'PROMPT_ID=123456\nRESULT=PASS\n'
                    'C2_RESULT={"completed":[],"remaining":[],"evidence":["tests PASS"],'
                    '"blocker":null,"next_action":null}'}]}
                class RPC:
                    def __enter__(self): return self
                    def __exit__(self,*args): pass
                    def __call__(self,method,params):
                        if method=='model/list':
                            return {'data':[{'model':'exact','id':'exact','displayName':'exact',
                                'supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}],
                                'nextCursor':None}
                        if method=='thread/read':
                            return {'thread':{'turns':[turn]}}
                        raise AssertionError(method)
                calls=[]
                def submit(op,args,key):
                    calls.append((op,args,key)); return {'submission':'queued'}
                fake={'thread_id':'thread-1','turn_id':'turn-1',
                      'phase':'terminal','turn_status':'completed'}
                with patch.object(c2_worker,'dispatch_codex',return_value=fake), \
                     patch.object(c2_worker,'_queue_repo_integration',return_value=('merged',True)):
                    result=c2_worker.run_once(path,'auto-result',
                        state_root=root/'receipts',submit=submit,rpc_factory=RPC)
                self.assertEqual('completed',result['phase'])
                result_calls=[c for c in calls if c[0]=='executor_result']
                self.assertEqual(2,len(result_calls))
                self.assertFalse(result_calls[0][1]['integration_ready'])
                self.assertTrue(result_calls[1][1]['integration_ready'])
                self.assertTrue(result_calls[0][1]['strict_contract'])
            finally:
                conn.close()

    def test_failed_codex_turn_without_contract_submits_fail_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                conn.execute("INSERT OR REPLACE INTO prompt_materializations(prompt_id,body,sha256,created_at,actor) VALUES(?,?,?,?,?)",
                    ('123456','PROMPT_ID=123456\nDo the task.','fixture-sha','2026-01-01T00:00:00Z','test'))
                metadata={'activity':'coding','model':'exact','reasoning':'medium',
                    'worktree':'/tmp/worktree','prompt_id':'123456',
                    'work_item_id':'prompt:123456','goal_mode':0}
                conn.execute("""INSERT INTO work_item_runs VALUES(
                  'failed-result','prompt:123456','event',1,'codex','running',100,
                  'c2-run:failed-result',NULL,?,1)""",(json.dumps(metadata),))
                c2_scheduler.executor_started(conn,run_id='failed-result',now=2)
                conn.commit()
                turn={'id':'turn-failed','status':'failed','items':[]}
                class RPC:
                    def __enter__(self): return self
                    def __exit__(self,*args): pass
                    def __call__(self,method,params):
                        if method=='model/list':
                            return {'data':[{'model':'exact','id':'exact','displayName':'exact',
                                'supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}],
                                'nextCursor':None}
                        if method=='thread/read':
                            return {'thread':{'turns':[turn]}}
                        raise AssertionError(method)
                calls=[]
                def submit(op,args,key):
                    calls.append((op,args,key)); return {'submission':'queued'}
                fake={'thread_id':'thread-1','turn_id':'turn-failed',
                      'phase':'terminal','turn_status':'failed'}
                with patch.object(c2_worker,'dispatch_codex',return_value=fake):
                    result=c2_worker.run_once(path,'failed-result',
                        state_root=root/'receipts',submit=submit,rpc_factory=RPC)
                self.assertEqual('failed',result['phase'])
                result_calls=[c for c in calls if c[0]=='executor_result']
                self.assertEqual(1,len(result_calls))
                self.assertEqual('FAIL',result_calls[0][1]['outcome'])
                self.assertIn('ended failed',result_calls[0][1]['blocker'])
                self.assertFalse(result_calls[0][1]['integration_ready'])
            finally:
                conn.close()

    def test_orphaned_codex_turn_submits_blocked_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                conn.execute("""INSERT OR REPLACE INTO prompt_materializations(
                  prompt_id,body,sha256,created_at,actor) VALUES(?,?,?,?,?)""",
                    ('123456','PROMPT_ID=123456\nDo the task.','fixture-sha',
                     '2026-01-01T00:00:00Z','test'))
                metadata={'activity':'coding','model':'exact','reasoning':'medium',
                    'worktree':'/tmp/worktree','prompt_id':'123456',
                    'work_item_id':'prompt:123456','goal_mode':0}
                conn.execute("""INSERT INTO work_item_runs VALUES(
                  'orphan-result','prompt:123456','event',1,'codex','running',100,
                  'c2-run:orphan-result',NULL,?,1)""",(json.dumps(metadata),))
                c2_scheduler.executor_started(conn,run_id='orphan-result',now=2)
                conn.commit()
                class RPC:
                    def __enter__(self): return self
                    def __exit__(self,*args): pass
                    def __call__(self,method,params):
                        if method=='model/list':
                            return {'data':[{'model':'exact','id':'exact','displayName':'exact',
                                'supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}],
                                'nextCursor':None}
                        raise AssertionError(method)
                    def wait_for_turn(self,*_):
                        raise c2_worker.AppServerError('orphaned_turn_requires_recovery')
                calls=[]
                fake={'thread_id':'thread-1','turn_id':'turn-orphan','phase':'started'}
                with patch.object(c2_worker,'dispatch_codex',return_value=fake), \
                     patch.object(c2_worker,'record_terminal'):
                    result=c2_worker.run_once(path,'orphan-result',
                        state_root=root/'receipts',rpc_factory=RPC,
                        submit=lambda op,args,key:calls.append((op,args,key)))
                self.assertEqual('interrupted',result['phase'])
                result_call=next(call for call in calls if call[0]=='executor_result')
                self.assertEqual('BLOCKED',result_call[1]['outcome'])
                self.assertEqual('Retry from the existing checkpoint or create a follow-up run.',
                    result_call[1]['next_action'])
            finally:
                conn.close()


    def test_worker_does_not_execute_before_start_receipt_is_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                marker=root/'must-not-exist'
                item=c2_intake.add_work_item(conn,title='Start fail closed',repo='fixture')
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',
                    command=[sys.executable,'-c',f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')"])
                run=c2_scheduler.schedule(conn,event_key='start-fail',now=10)[0]
                c2_scheduler.acknowledge(conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
                    metadata=run['metadata'],now=11)
                conn.commit()
                with self.assertRaisesRegex(c2_worker.WorkerError,'executor_start_receipt_missing'):
                    c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',
                        submit=lambda *_:self.fail('worker submitted before start receipt'))
                self.assertFalse(marker.exists())
            finally:
                conn.close()

    def test_native_end_to_end_single_run_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                marker=root/'marker'
                item=c2_intake.add_work_item(conn,title='Native proof',repo='fixture')
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',
                    command=[sys.executable,'-c',f"from pathlib import Path; Path({str(marker)!r}).write_text('done')"])
                run=c2_scheduler.schedule(conn,event_key='synthetic-intake',now=10)[0]
                c2_scheduler.acknowledge(conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
                    metadata=run['metadata'],now=11)
                c2_scheduler.executor_started(conn,run_id=run['run_id'],now=12)
                conn.commit()
                calls=[]
                def submit(op,args,key):
                    calls.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    if op=='complete':
                        c2_scheduler.complete(conn,**args)
                    else:
                        raise AssertionError(op)
                    conn.commit()
                result=c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',submit=submit)
                self.assertEqual('completed',result['state'])
                self.assertEqual('done',marker.read_text())
                self.assertEqual('completed',conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0])
                with self.assertRaisesRegex(c2_worker.WorkerError,'run_not_claimed'):
                    c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',submit=submit)
                self.assertEqual(['complete'],[op for op,_ in calls])
            finally:
                conn.close()
