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
import roadmap_db
import test_c2_intake


class C2WriterTests(unittest.TestCase):
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
