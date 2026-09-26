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
                self.assertEqual('executor_started',calls[0][0])
                result_calls=[c for c in calls if c[0]=='executor_result']
                self.assertEqual(2,len(result_calls))
                self.assertFalse(result_calls[0][1]['integration_ready'])
                self.assertTrue(result_calls[1][1]['integration_ready'])
                self.assertTrue(result_calls[0][1]['strict_contract'])
            finally:
                conn.close()


    def test_worker_does_not_execute_if_start_notification_fails(self):
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
                def submit(op,args,key):
                    if op=='executor_started':
                        raise RuntimeError('writer unavailable')
                    raise AssertionError(op)
                with self.assertRaisesRegex(RuntimeError,'writer unavailable'):
                    c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',submit=submit)
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
                conn.commit()
                calls=[]
                def submit(op,args,key):
                    calls.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    if op=='executor_started':
                        c2_scheduler.executor_started(conn,**args)
                    elif op=='complete':
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
                self.assertEqual(['executor_started','complete'],[op for op,_ in calls])
            finally:
                conn.close()
