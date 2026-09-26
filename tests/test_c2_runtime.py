from pathlib import Path
from contextlib import closing
import sys
import tempfile
import unittest
from unittest.mock import patch
import subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake
import c2_scheduler
import c2_runtime
import c2_supervisor_authority
from test_c2_intake import C2IntakeTests


class RuntimeTests(unittest.TestCase):
    def _pass_receipt_snapshot(self, root):
        path=C2IntakeTests().make_cutover_db(root)
        with closing(c2_intake._connect(path)) as writer:
            c2_scheduler.install_schema(writer)
            writer.execute('BEGIN IMMEDIATE')
            writer.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
            writer.execute("""INSERT INTO work_item_runs VALUES(
                'pass-run','prompt:123456','event',1,'codex','running',999,
                'c2-run:pass-run',NULL,'{}',1)""")
            c2_scheduler.executor_result(writer,run_id='pass-run',prompt_id='123456',
                outcome='PASS',completed=['acceptance'],evidence=['verified'],strict_contract=True)
            writer.commit()
        return path

    def test_merged_repo_reconciles_only_valid_pass_receipt_and_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._pass_receipt_snapshot(Path(tmp))
            calls=[]
            merged={'status':'merged','integration_state':'merged','merge_sha':'abc123'}
            for _ in range(2):
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=lambda op,args,key:calls.append((op,args,key)),
                        repo_task_status=lambda _:merged,
                        launch=lambda _:None,launch_notify=lambda _:None,now=1)
            self.assertEqual(2,len(calls))
            self.assertEqual(calls[0][2],calls[1][2])
            from c2_mutations import apply
            with closing(c2_intake._connect(path)) as db:
                for op,args,_ in calls:
                    db.execute('BEGIN IMMEDIATE')
                    apply(db,{'op':'c2_'+op,'arguments':args})
                    db.commit()
                self.assertEqual('completed',db.execute(
                    "SELECT status FROM work_items WHERE prompt_id='123456'").fetchone()[0])
                self.assertEqual(1,db.execute('SELECT COUNT(*) FROM work_item_result_receipts').fetchone()[0])

    def test_unmerged_pass_receipt_is_not_finalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._pass_receipt_snapshot(Path(tmp))
            calls=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                c2_runtime.advance(snapshot,submit=lambda *args:calls.append(args),
                    repo_task_status=lambda _: {'status':'queued','integration_state':'queued'},
                    launch=lambda _:None,launch_notify=lambda _:None,now=1)
            self.assertFalse(any(call[0]=='executor_result' for call in calls))

    def test_missing_receipt_never_infers_completion_from_merged_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                writer.commit()
            calls=[]; statuses=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                c2_runtime.advance(snapshot,submit=lambda *args:calls.append(args),
                    repo_task_status=lambda prompt:(statuses.append(prompt) or
                        {'status':'merged','integration_state':'merged'}),
                    launch=lambda _:None,launch_notify=lambda _:None,now=1)
            self.assertFalse(statuses)
            self.assertFalse(any(call[0]=='executor_result' for call in calls))

    def _authority_db(self, tmp, supervisor_id, token, expiry):
        path=C2IntakeTests().make_cutover_db(Path(tmp))
        with closing(c2_intake._connect(path)) as writer:
            c2_supervisor_authority.install_schema(writer)
            writer.execute(
                "INSERT INTO c2_supervisor_authority VALUES(1,?,?,?,?,?)",
                (supervisor_id,token,expiry,1,1),
            )
            writer.commit()
        return path

    def test_expired_different_authority_claims_successor_before_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._authority_db(tmp,'old',1,90)
            submitted=[]; launched=[]
            current={'supervisor_id':'new','fencing_token':2,'lease_expires_at':500}
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(
                    snapshot,
                    submit=lambda op,args,key:submitted.append((op,args,key)),
                    launch=launched.append,
                    launch_notify=lambda _:None,
                    now=100,
                    supervisor_authority=current,
                )
            self.assertEqual(['claim_supervisor'],[op for op,_,_ in submitted])
            self.assertEqual([('claim_supervisor','2')],result['events'])
            self.assertEqual([],launched)

    def test_matching_authority_renews_before_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._authority_db(tmp,'same',3,150)
            submitted=[]; launched=[]
            current={'supervisor_id':'same','fencing_token':3,'lease_expires_at':500}
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(
                    snapshot,
                    submit=lambda op,args,key:submitted.append((op,args,key)),
                    launch=launched.append,
                    launch_notify=lambda _:None,
                    now=100,
                    supervisor_authority=current,
                )
            self.assertEqual(['renew_supervisor'],[op for op,_,_ in submitted])
            self.assertEqual([('renew_supervisor','3')],result['events'])
            self.assertEqual([],launched)

    def test_unexpired_different_authority_fences_without_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._authority_db(tmp,'other',4,500)
            submitted=[]; launched=[]
            current={'supervisor_id':'new','fencing_token':5,'lease_expires_at':600}
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(
                    snapshot,
                    submit=lambda op,args,key:submitted.append((op,args,key)),
                    launch=launched.append,
                    launch_notify=lambda _:None,
                    now=100,
                    supervisor_authority=current,
                )
            self.assertEqual([],submitted)
            self.assertEqual([('supervisor_fenced','4')],result['events'])
            self.assertEqual([],launched)

    def test_personalhub_spec_is_scheduled(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(writer,title='External PH',repo='gernalix/PersonalHub')
                writer.execute("INSERT INTO work_item_execution_specs(work_item_id,activity,command_json) VALUES(?,'native','[\"true\"]')",
                               (item['work_item_id'],))
                writer.commit()
            submitted=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(snapshot,submit=lambda op,args,key:submitted.append(op),
                    launch=lambda _:None,launch_notify=lambda _:None,now=1)
            self.assertEqual(1,result['ready'])
            self.assertEqual(['schedule'],submitted)

    def test_override_readback_and_fallback_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                c2_scheduler.set_override(writer,selector='tag',value='focus:ph',now=1)
                item=c2_intake.add_work_item(writer,title='Normal',repo='other')
                c2_scheduler.configure(writer,item['work_item_id'],activity='native',command=['true'])
                writer.commit()
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(snapshot,submit=lambda *_:None,
                    launch=lambda _:None,launch_notify=lambda _:None,now=2)
            self.assertEqual('focus:ph',result['execution_override']['value'])
            self.assertFalse(result['override_draining'])
            self.assertIn(('execution_override','tag:focus:ph:fallback'),result['events'])

    def test_existing_live_worker_unit_is_not_relaunched(self):
        failed_launch=subprocess.CompletedProcess([],1,stderr='Unit already loaded')
        active_unit=subprocess.CompletedProcess([],0)
        with patch.object(c2_runtime.subprocess,'run',side_effect=[failed_launch,active_unit]) as run:
            c2_runtime._launch_worker('same-run',Path('/tmp/snapshot.sqlite3'))
        self.assertEqual(2,run.call_count)
        self.assertEqual(['systemctl','--user','is-active','--quiet','c2-run-same-run'],
            run.call_args.args[0])

    def test_failed_inactive_worker_launch_is_reported(self):
        failed=subprocess.CompletedProcess([],1,stderr='Unit conflict')
        with patch.object(c2_runtime.subprocess,'run',side_effect=[failed,failed]):
            with self.assertRaisesRegex(c2_runtime.RuntimeErrorC2,'worker_launch_failed'):
                c2_runtime._launch_worker('same-run',Path('/tmp/snapshot.sqlite3'))

    def test_imported_running_state_does_not_block_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                writer.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                for n in range(3):
                    orphan=c2_intake.add_work_item(writer,title='Imported '+str(n),repo='imported-'+str(n))
                    writer.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",
                        (orphan['work_item_id'],))
                item=c2_intake.add_work_item(writer,title='Ready',repo='independent')
                c2_scheduler.configure(writer,item['work_item_id'],activity='native',command=['true'])
                writer.commit()
            submitted=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(snapshot,submit=lambda op,args,key:submitted.append(op),
                    launch=lambda _:None,launch_notify=lambda _:None,now=1,max_parallel=2)
            self.assertEqual(1,result['ready'])
            self.assertEqual(['schedule'],submitted)

    def test_schedule_key_changes_when_same_repo_imported_lock_clears(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                blocker=c2_intake.add_work_item(conn,title='Imported blocker',repo='shared')
                conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",
                    (blocker['work_item_id'],))
                item=c2_intake.add_work_item(conn,title='Ready',repo='shared')
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',command=['true'])
                conn.commit()
                submitted=[]
                def submit(op,args,key):
                    submitted.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    if op=='schedule':
                        c2_scheduler.schedule(conn,now=10,**args)
                    conn.commit()
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=lambda _:None,now=10,max_parallel=1)
                self.assertEqual('pending',conn.execute(
                    'SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)
                ).fetchone()[0])
                conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",
                    (blocker['work_item_id'],))
                conn.commit()
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=lambda _:None,now=11,max_parallel=1)
                schedule_keys=[key for op,key in submitted if op=='schedule']
                self.assertEqual(2,len(schedule_keys))
                self.assertNotEqual(schedule_keys[0],schedule_keys[1])
                self.assertEqual('running',conn.execute(
                    'SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)
                ).fetchone()[0])
            finally:
                conn.close()

    def test_snapshot_to_writer_then_worker_without_duplicate_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(conn,title='Native',repo='repo',sort_order=1)
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',command=['true'])
                conn.commit()
                submitted=[]; launched=[]
                def submit(op,args,key):
                    submitted.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    if op=='schedule': c2_scheduler.schedule(conn,now=10,**args)
                    elif op=='acknowledge': c2_scheduler.acknowledge(conn,now=11,**args)
                    conn.commit()
                # Read connection is independent of the writer connection to
                # model accepted remote snapshots between events.
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=10)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=11)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=12)
                self.assertEqual(['schedule','acknowledge'],[op for op,_ in submitted])
                self.assertEqual(1,len(launched))
                self.assertEqual('running',conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0])
            finally:
                conn.close()
