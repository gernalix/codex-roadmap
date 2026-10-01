from contextlib import closing
from pathlib import Path
import json
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import apply_issue_mutation
import c2_intake
import c2_supervisor_authority
import c2_scheduler
import roadmap_db
import test_c2_intake


class C2WriterTests(unittest.TestCase):
    def test_retired_workflowy_order_operations_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                conn.execute('BEGIN IMMEDIATE')
                for operation in ('c2_set_manual_order', 'c2_clear_manual_order'):
                    with self.assertRaisesRegex(ValueError, 'unknown_c2_operation'):
                        roadmap_db.apply_mutation(conn, {'op':operation,'arguments':{}})

    def test_override_set_replay_clear_requires_current_fence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                conn.execute('BEGIN IMMEDIATE')
                current={'supervisor_id':'test-supervisor','fencing_token':1,
                         'lease_expires_at':time.time()+120}
                roadmap_db.apply_mutation(conn,{'op':'c2_claim_supervisor',
                    'arguments':{'supervisor_authority':current}})
                op={'op':'c2_set_execution_override','arguments':{
                    'selector':'tag','value':'focus:ph','supervisor_authority':current}}
                roadmap_db.apply_mutation(conn,op)
                first=c2_scheduler.read_override(conn)
                roadmap_db.apply_mutation(conn,op)
                self.assertEqual(first,c2_scheduler.read_override(conn))
                self.assertEqual('focus:ph',c2_scheduler.read_override(conn)['value'])
                with self.assertRaisesRegex(c2_supervisor_authority.AuthorityError,'supervisor_authority_required'):
                    roadmap_db.apply_mutation(conn,{'op':'c2_clear_execution_override','arguments':{}})
                roadmap_db.apply_mutation(conn,{'op':'c2_clear_execution_override',
                    'arguments':{'supervisor_authority':current}})
                self.assertIsNone(c2_scheduler.read_override(conn))

    def test_auto_configure_existing_item_through_fenced_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                conn.execute('BEGIN IMMEDIATE')
                authority={'supervisor_id':'test-supervisor','fencing_token':1,
                           'lease_expires_at':time.time()+120}
                roadmap_db.apply_mutation(conn,{'op':'c2_claim_supervisor',
                    'arguments':{'supervisor_authority':authority}})
                roadmap_db.apply_mutation(conn,{'op':'c2_intake','arguments':{
                    'title':'Needs context','supervisor_authority':authority}})
                work_item_id=conn.execute("SELECT work_item_id FROM work_items WHERE title='Needs context'").fetchone()[0]
                self.assertEqual(0,conn.execute('SELECT COUNT(*) FROM work_item_execution_specs WHERE work_item_id=?',
                                                (work_item_id,)).fetchone()[0])
                roadmap_db.apply_mutation(conn,{'op':'c2_auto_configure','arguments':{
                    'work_item_id':work_item_id,
                    'execution':{'command':['/usr/bin/true']},
                    'supervisor_authority':authority}})
                self.assertEqual('native',conn.execute(
                    'SELECT activity FROM work_item_execution_specs WHERE work_item_id=?',
                    (work_item_id,)).fetchone()[0])


    def test_prompt_result_receipt_waits_for_pass_integration_then_reconciles_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                roadmap_db.set_status(conn,'123456','running',actor='test')
                conn.execute("""INSERT INTO work_item_runs VALUES(
                    'run-result','prompt:123456','event',1,'codex','running',100,
                    'c2-run:run-result',NULL,'{}',1)""")
                base={'op':'c2_executor_result','arguments':{
                    'run_id':'run-result','prompt_id':'123456','outcome':'PASS',
                    'completed':[],'remaining':[],'evidence':['legacy final report'],
                    'strict_contract':False,'integration_ready':False}}
                roadmap_db.apply_mutation(conn,base)
                self.assertEqual('running',conn.execute(
                    "SELECT status FROM work_items WHERE prompt_id='123456'").fetchone()[0])
                final={'op':'c2_executor_result','arguments':{
                    **base['arguments'],'integration_ready':True}}
                roadmap_db.apply_mutation(conn,final)
                self.assertEqual('completed',conn.execute(
                    "SELECT status FROM work_items WHERE prompt_id='123456'").fetchone()[0])
                self.assertEqual('completed',conn.execute(
                    "SELECT state FROM work_item_runs WHERE run_id='run-result'").fetchone()[0])
                self.assertEqual(1,conn.execute(
                    "SELECT COUNT(*) FROM work_item_result_receipts WHERE run_id='run-result'").fetchone()[0])

    def test_nonpass_prompt_result_terminalizes_without_integration_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                roadmap_db.set_status(conn,'123456','running',actor='test')
                conn.execute("""INSERT INTO work_item_runs VALUES(
                    'run-blocked','prompt:123456','event',1,'codex','running',100,
                    'c2-run:run-blocked',NULL,'{}',1)""")
                roadmap_db.apply_mutation(conn,{'op':'c2_executor_result','arguments':{
                    'run_id':'run-blocked','prompt_id':'123456','outcome':'BLOCKED',
                    'completed':[],'remaining':['retry'],'evidence':['final report'],
                    'blocker':'external blocker','next_action':'retry later',
                    'strict_contract':True,'integration_ready':False}})
                self.assertEqual('blocked',conn.execute(
                    "SELECT status FROM work_items WHERE prompt_id='123456'").fetchone()[0])
                self.assertEqual('failed',conn.execute(
                    "SELECT state FROM work_item_runs WHERE run_id='run-blocked'").fetchone()[0])


    def test_executor_started_mutation_records_canonical_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                roadmap_db.set_status(conn,'123456','running',actor='test')
                roadmap_db.apply_mutation(conn,{'op':'c2_executor_started','arguments':{
                    'prompt_id':'123456','executor':'codex',
                    'executor_ref':'thread-1','chat_url':'codex://threads/thread-1'}})
                row=conn.execute(
                    "SELECT * FROM work_item_executor_starts WHERE prompt_id='123456'").fetchone()
                self.assertEqual('codex',row['executor'])
                self.assertEqual('thread-1',row['executor_ref'])

    def test_issue_replay_does_not_duplicate_intake(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            event=Path(tmp)/'event.json'
            authority={'supervisor_id':'test-supervisor','fencing_token':1,
                       'lease_expires_at':time.time()+120}
            document={'schema':'codex-roadmap.mutation.v1','actor':'test','operations':[
                {'op':'c2_claim_supervisor','arguments':{'supervisor_authority':authority}},
                {'op':'c2_intake','arguments':{'title':'One canonical task','executor_policy':'human',
                                              'supervisor_authority':authority}}]}
            event.write_text(json.dumps({'issue':{'number':42,'title':'[roadmap-mutation] c2-test-intake',
                'body':json.dumps(document)}}))
            first=apply_issue_mutation.apply_issue(path.parent,event,render_views=False)
            second=apply_issue_mutation.apply_issue(path.parent,event,render_views=False)
            self.assertFalse(first['idempotent']); self.assertTrue(second['idempotent'])
            with closing(c2_intake._connect(path)) as conn:
                self.assertEqual(1,conn.execute("SELECT COUNT(*) FROM work_items WHERE title='One canonical task'").fetchone()[0])
                self.assertEqual([],conn.execute('PRAGMA foreign_key_check').fetchall())

    def test_multi_operation_failure_rolls_back_intake(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as conn:
                conn.execute('BEGIN IMMEDIATE')
                authority={'supervisor_id':'test-supervisor','fencing_token':1,
                           'lease_expires_at':time.time()+120}
                roadmap_db.apply_mutation(conn,{'op':'c2_claim_supervisor',
                                                'arguments':{'supervisor_authority':authority}})
                roadmap_db.apply_mutation(conn,{'op':'c2_intake','arguments':{
                    'title':'Rollback','supervisor_authority':authority}})
                with self.assertRaisesRegex(ValueError,'unknown_c2'):
                    roadmap_db.apply_mutation(conn,{'op':'c2_invalid'})
                conn.rollback()
                self.assertEqual(0,conn.execute("SELECT COUNT(*) FROM work_items WHERE title='Rollback'").fetchone()[0])
