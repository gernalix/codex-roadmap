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
import c2_supervisor_lease
from test_c2_intake import C2IntakeTests


class RuntimeTests(unittest.TestCase):
    def test_adaptive_wave_and_completed_slot_backfill(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                for index in range(5):
                    item=c2_intake.add_work_item(writer,title=f'Independent {index}',
                                                 repo=f'repo-{index}')
                    c2_scheduler.configure(writer,item['work_item_id'],
                                           activity='native',command=['true'])
                writer.commit()
            submitted=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                c2_runtime.advance(snapshot,
                    submit=lambda op,args,key:submitted.append((op,args)),
                    launch=lambda _:None,launch_notify=lambda _:None,now=10)
            schedule=[args for op,args in submitted if op=='schedule'][0]
            self.assertEqual(5,schedule['max_parallel'])
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                runs=c2_scheduler.schedule(writer,now=10,**schedule)
                self.assertEqual(5,len(runs))
                c2_scheduler.acknowledge(writer,runs[0]['run_id'],
                    worker_ref='c2-run:'+runs[0]['run_id'],
                    metadata=runs[0]['metadata'],now=10)
                c2_scheduler.complete(writer,runs[0]['run_id'],succeeded=True,
                                      worker_ref='c2-run:'+runs[0]['run_id'])
                item=c2_intake.add_work_item(writer,title='Backfill',repo='repo-new')
                c2_scheduler.configure(writer,item['work_item_id'],
                                       activity='native',command=['true'])
                writer.commit()
            submitted=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                c2_runtime.advance(snapshot,
                    submit=lambda op,args,key:submitted.append((op,args)),
                    launch=lambda _:None,launch_notify=lambda _:None,now=11)
            schedule=[args for op,args in submitted if op=='schedule'][0]
            self.assertEqual(5,schedule['max_parallel'])

    def test_parallel_cap_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                with self.assertRaisesRegex(c2_runtime.RuntimeErrorC2,
                                            'parallel_cap_out_of_range'):
                    c2_runtime.advance(snapshot,max_parallel=17)

    def test_supervisor_writer_operation_automatically_records_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            lease_path=Path(tmp)/'lease.sqlite3'
            with c2_supervisor_lease.connect(lease_path) as lease:
                c2_supervisor_lease.acquire(lease,owner='runtime',pointer='/tmp/pointer',
                                            supervisor_id='runtime',now=100,ttl=10000000000)
            captured=[]
            with patch.object(c2_runtime,'SUPERVISOR_DB',lease_path), \
                    patch.object(c2_runtime,'submit_document',side_effect=lambda document,request_key:
                                 (captured.append((document,request_key)) or {'issue_number':'1'})), \
                    patch.object(c2_runtime.time,'time',return_value=150):
                c2_runtime._writer_submit('schedule',{'event_key':'event'},'key')
            with c2_supervisor_lease.connect(lease_path) as lease:
                row=c2_supervisor_lease.snapshot(lease)
            self.assertEqual(1,row['progress_counter'])
            self.assertEqual(150,row['last_progress_at'])
            self.assertEqual('writer:schedule',row['current_action'])
            authority=captured[0][0]['operations'][0]['arguments']['supervisor_authority']
            self.assertEqual(row['lease_expires_at'],authority['lease_expires_at'])

    def test_ack_request_identity_changes_with_renewed_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            lease_path=Path(tmp)/'lease.sqlite3'
            with c2_supervisor_lease.connect(lease_path) as lease:
                c2_supervisor_lease.acquire(lease,owner='runtime',pointer='/tmp/pointer',
                                            supervisor_id='runtime',now=100,ttl=1000)
            captured=[]
            with patch.object(c2_runtime,'SUPERVISOR_DB',lease_path), \
                    patch.object(c2_runtime,'submit_document',side_effect=lambda document,request_key:
                                 (captured.append((document,request_key)) or {'issue_number':'1'})), \
                    patch.object(c2_runtime.time,'time',return_value=150):
                args={'run_id':'run-1','worker_ref':'c2-run:run-1','metadata':{}}
                c2_runtime._writer_submit('acknowledge',args,'c2-ack-original')
                c2_runtime._writer_submit('acknowledge',args,'c2-ack-original')
                with c2_supervisor_lease.connect(lease_path) as lease:
                    lease.execute('UPDATE supervisor SET lease_expires_at=2000 WHERE singleton=1')
                c2_runtime._writer_submit('acknowledge',args,'c2-ack-original')
            self.assertEqual(captured[0][1],captured[1][1])
            self.assertNotEqual(captured[0][1],captured[2][1])
            self.assertNotEqual(
                captured[0][0]['operations'][0]['arguments']['supervisor_authority'],
                captured[2][0]['operations'][0]['arguments']['supervisor_authority'])

    @patch("c2_runtime.integration_status", return_value={"status":"merged","integration_state":"merged","merge_sha":"b"*40})
    @patch("c2_runtime.prompt_repository", return_value="gernalix/codex-roadmap")
    def test_runtime_routes_self_repo_status_through_shared_helper(self, repository, integration):
        result=c2_runtime._repo_task_status("123456")
        self.assertEqual("merged",result["status"])
        integration.assert_called_once_with("123456","gernalix/codex-roadmap")

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
            c2_scheduler.executor_started(writer,run_id='pass-run',now=2)
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

    def test_matching_authority_renews_without_starving_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self._authority_db(tmp,'same',3,150)
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(writer,title='Ready while renewing',repo='fixture')
                writer.execute("INSERT INTO work_item_execution_specs(work_item_id,activity,command_json) VALUES(?,'native','[\"true\"]')",
                               (item['work_item_id'],))
                writer.commit()
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
            self.assertEqual(['renew_supervisor','schedule'],[op for op,_,_ in submitted])
            self.assertIn(('renew_supervisor','3'),result['events'])
            self.assertEqual(1,result['ready'])
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

    def test_degraded_chatgpt_lane_keeps_codex_and_native_running(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                chat=c2_intake.add_work_item(writer,title='Chat',repo='chat-repo')
                c2_scheduler.configure(writer,chat['work_item_id'],activity='semantic',
                    project_url='https://chatgpt.com/g/g-p-fixture')
                native=c2_intake.add_work_item(writer,title='Native',repo='native-repo')
                c2_scheduler.configure(writer,native['work_item_id'],activity='native',command=['true'])
                writer.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                writer.execute("""INSERT INTO work_item_runs VALUES(
                    'codex-live','prompt:123456','event',1,'codex','running',999,
                    'c2-run:codex-live',NULL,'{}',1)""")
                c2_scheduler.executor_started(writer,run_id='codex-live',now=2)
                writer.commit()
            submitted=[]; launched=[]
            with patch('c2_runtime.lane_degraded',return_value=True):
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    result=c2_runtime.advance(snapshot,
                        submit=lambda op,args,key:submitted.append((op,args)),
                        launch=launched.append,launch_notify=lambda _:None,now=1)
            self.assertEqual(['codex-live'],launched)
            self.assertEqual(1,result['ready'])
            schedule_args=[args for op,args in submitted if op=='schedule']
            self.assertEqual(1,len(schedule_args))
            self.assertTrue(schedule_args[0]['chatgpt_lane_degraded'])
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                runs=c2_scheduler.schedule(writer,now=1,**schedule_args[0])
                self.assertEqual([native['work_item_id']],[r['work_item_id'] for r in runs])
                self.assertEqual('pending',writer.execute(
                    'SELECT status FROM work_items WHERE work_item_id=?',
                    (chat['work_item_id'],)).fetchone()[0])

    def test_expired_live_worker_is_not_recovered_until_unit_is_dead(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(writer,title='Live worker',repo='live-worker')
                c2_scheduler.configure(writer,item['work_item_id'],activity='native',command=['true'])
                run=c2_scheduler.schedule(writer,event_key='live-worker',now=1)[0]
                c2_scheduler.acknowledge(writer,run['run_id'],
                    worker_ref='c2-run:'+run['run_id'],metadata=run['metadata'],now=2)
                c2_scheduler.executor_started(writer,run_id=run['run_id'],now=2)
                writer.execute('UPDATE work_item_runs SET lease_until=3 WHERE run_id=?',
                               (run['run_id'],))
                writer.commit()
            for alive, should_recover in ((True, False), (False, True)):
                submitted=[]
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(
                        snapshot,
                        submit=lambda op,args,key: submitted.append(op),
                        launch=lambda _: None,
                        launch_notify=lambda _: None,
                        worker_active=lambda _run_id, value=alive: value,
                        now=1000,
                    )
                self.assertEqual(should_recover, 'recover' in submitted)

    def test_existing_chatgpt_run_is_held_then_launched_after_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                c2_scheduler.install_schema(writer)
                writer.execute('BEGIN IMMEDIATE')
                chat=c2_intake.add_work_item(writer,title='Chat',repo='chat-repo')
                c2_scheduler.configure(writer,chat['work_item_id'],activity='semantic',
                    project_url='https://chatgpt.com/g/g-p-fixture')
                run=c2_scheduler.schedule(writer,event_key='chat-start',now=1)[0]
                c2_scheduler.acknowledge(writer,run['run_id'],
                    worker_ref='c2-run:'+run['run_id'],metadata=run['metadata'],now=2)
                c2_scheduler.executor_started(writer,run_id=run['run_id'],now=2)
                writer.commit()
            for degraded, expected in ((True, []), (False, [run['run_id']])):
                launched=[]
                with patch('c2_runtime.lane_degraded',return_value=degraded):
                    with closing(c2_runtime._open_snapshot(path)) as snapshot:
                        c2_runtime.advance(snapshot,submit=lambda *_:None,
                            launch=launched.append,launch_notify=lambda _:None,now=3)
                self.assertEqual(expected,launched)
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                state=snapshot.execute('SELECT state FROM work_item_runs WHERE run_id=?',
                                       (run['run_id'],)).fetchone()[0]
                self.assertEqual('running',state)

    def test_worker_launch_waits_for_applied_executor_start_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(writer,title='Start gate',repo='gate')
                c2_scheduler.configure(writer,item['work_item_id'],activity='native',command=['true'])
                run=c2_scheduler.schedule(writer,event_key='start-gate',now=1)[0]
                c2_scheduler.acknowledge(writer,run['run_id'],
                    worker_ref='c2-run:'+run['run_id'],metadata=run['metadata'],now=2)
                writer.commit()
            submitted=[]; launched=[]
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                first=c2_runtime.advance(snapshot,
                    submit=lambda op,args,key:submitted.append((op,args,key)),
                    launch=launched.append,launch_notify=lambda _:None,now=3)
            self.assertEqual(['executor_started'],[op for op,_,_ in submitted])
            self.assertEqual([],launched)
            self.assertIn(('executor_started',run['run_id']),first['events'])
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                c2_scheduler.executor_started(writer,run_id=run['run_id'],now=4)
                writer.commit()
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                second=c2_runtime.advance(snapshot,submit=lambda *_:None,
                    launch=launched.append,launch_notify=lambda _:None,now=5)
            self.assertEqual([run['run_id']],launched)
            self.assertIn(('launch',run['run_id']),second['events'])

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

    def test_override_readback_falls_back_for_leased_device(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                holder=c2_intake.add_work_item(writer,title='Device holder',repo='holder')
                c2_scheduler.configure(writer,holder['work_item_id'],activity='native',command=['true'],resources=['device:pixel'])
                c2_scheduler.schedule(writer,event_key='holder',now=1,max_parallel=1)
                scoped=c2_intake.add_work_item(writer,title='PH',repo='gernalix/PersonalHub')
                c2_scheduler.configure(writer,scoped['work_item_id'],activity='native',command=['true'],resources=['device:pixel'])
                other=c2_intake.add_work_item(writer,title='Other',repo='other')
                c2_scheduler.configure(writer,other['work_item_id'],activity='native',command=['true'])
                c2_scheduler.set_override(writer,selector='repo',value='gernalix/PersonalHub',now=2)
                writer.commit()
            with closing(c2_runtime._open_snapshot(path)) as snapshot:
                result=c2_runtime.advance(snapshot,submit=lambda *_:None,
                    launch=lambda _:None,launch_notify=lambda _:None,now=3)
            self.assertFalse(result['override_draining'])
            self.assertIn(('execution_override','repo:gernalix/PersonalHub:fallback'),result['events'])

    def test_existing_live_worker_unit_is_not_relaunched(self):
        failed_launch=subprocess.CompletedProcess([],1,stderr='Unit already loaded')
        active_unit=subprocess.CompletedProcess([],0)
        with patch.object(c2_runtime.subprocess,'run',side_effect=[failed_launch,active_unit]) as run:
            c2_runtime._launch_worker('same-run',Path('/tmp/snapshot.sqlite3'))
        self.assertEqual(2,run.call_count)
        self.assertEqual(['systemctl','--user','is-active','--quiet','c2-run-same-run'],
            run.call_args.args[0])

    def test_user_systemd_environment_recovers_missing_session_bus(self):
        with patch.dict(c2_runtime.os.environ,{},clear=True), \
                patch.object(c2_runtime.os,'getuid',return_value=4242), \
                patch.object(Path,'is_dir',return_value=True), \
                patch.object(Path,'is_socket',return_value=True):
            env=c2_runtime._user_systemd_environment()
        self.assertEqual('/run/user/4242',env['XDG_RUNTIME_DIR'])
        self.assertEqual('unix:path=/run/user/4242/bus',env['DBUS_SESSION_BUS_ADDRESS'])

    def test_worker_launch_passes_recovered_user_systemd_environment(self):
        env={'XDG_RUNTIME_DIR':'/run/user/4242',
             'DBUS_SESSION_BUS_ADDRESS':'unix:path=/run/user/4242/bus'}
        with patch.object(c2_runtime,'_user_systemd_environment',return_value=env), \
                patch.object(c2_runtime.subprocess,'run',
                             return_value=subprocess.CompletedProcess([],0)) as run:
            c2_runtime._launch_worker('same-run',Path('/tmp/snapshot.sqlite3'))
        self.assertEqual(env,run.call_args.kwargs['env'])

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

    def test_same_repo_imported_state_without_writer_does_not_block_schedule(self):
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
                self.assertEqual('running',conn.execute(
                    'SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)
                ).fetchone()[0])
                schedule_keys=[key for op,key in submitted if op=='schedule']
                self.assertEqual(1,len(schedule_keys))
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
                    elif op=='executor_started': c2_scheduler.executor_started(conn,now=12,**args)
                    conn.commit()
                # Read connection is independent of the writer connection to
                # model accepted remote snapshots between events.
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=10)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=11)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=12)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=13)
                self.assertEqual(['schedule','acknowledge','executor_started'],
                    [op for op,_ in submitted])
                self.assertEqual(1,len(launched))
                self.assertEqual('running',conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0])
            finally:
                conn.close()
