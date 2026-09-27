from contextlib import closing
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake as intake
import c2_manual_order
import c2_scheduler as scheduler
import roadmap_db
import test_c2_intake


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(self.tmp.name))
        self.conn=intake._connect(self.path)
        scheduler.install_schema(self.conn)
        self.conn.execute('BEGIN IMMEDIATE')

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def add(self, repo='repo-a', **kwargs):
        row=intake.add_work_item(self.conn,title='Check',repo=repo,sort_order=self.conn.execute('SELECT COUNT(*) FROM work_items').fetchone()[0],**kwargs)
        scheduler.configure(self.conn,row['work_item_id'],activity='native',command=['true'])
        return row['work_item_id']

    def test_verified_external_completion_requires_clear_checkpoint(self):
        item=self.add()
        commit='a'*40
        with self.assertRaisesRegex(scheduler.SchedulingError,'acceptance_checkpoint_incomplete'):
            scheduler.complete_verified(self.conn,item,source_commit=commit,evidence=['proof'])
        scheduler.record_checkpoint(self.conn,item,current_step='Done',next_action='Close',
            remaining=['pending'],evidence=['proof'],source_commit=commit)
        with self.assertRaisesRegex(scheduler.SchedulingError,'acceptance_checkpoint_incomplete'):
            scheduler.complete_verified(self.conn,item,source_commit=commit,evidence=['proof'])
        scheduler.record_checkpoint(self.conn,item,current_step='Done',next_action='Close',
            remaining=[],evidence=['proof'],source_commit=commit)
        scheduler.complete_verified(self.conn,item,source_commit=commit,evidence=['proof'])
        scheduler.complete_verified(self.conn,item,source_commit=commit,evidence=['proof'])
        self.assertEqual('completed',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(item,)).fetchone()[0])
        self.assertEqual(1,self.conn.execute(
            "SELECT COUNT(*) FROM work_item_evidence WHERE work_item_id=? AND evidence_kind='completion'",
            (item,)).fetchone()[0])


    def test_executor_result_receipt_is_idempotent_and_pass_fails_closed(self):
        self.conn.execute("UPDATE work_items SET status='running', acceptance_json=? WHERE prompt_id='123456'", ('["A"]',))
        self.conn.execute("""INSERT INTO work_item_runs VALUES(
            'result-run','prompt:123456','event',1,'codex','running',100,
            'c2-run:result-run',NULL,'{}',1)""")
        with self.assertRaisesRegex(scheduler.SchedulingError,'pass_requires_no_remaining'):
            scheduler.executor_result(self.conn,run_id='result-run',prompt_id='123456',
                outcome='PASS',completed=['A'],remaining=['B'],evidence=['proof'],
                strict_contract=True)
        receipt=scheduler.executor_result(self.conn,run_id='result-run',prompt_id='123456',
            outcome='PASS',completed=['A'],remaining=[],evidence=['proof'],
            strict_contract=True)
        replay=scheduler.executor_result(self.conn,run_id='result-run',prompt_id='123456',
            outcome='PASS',completed=['A'],remaining=[],evidence=['proof'],
            strict_contract=True)
        self.assertFalse(receipt['idempotent']); self.assertTrue(replay['idempotent'])
        self.assertEqual('running',self.conn.execute(
            "SELECT status FROM work_items WHERE prompt_id='123456'").fetchone()[0])
        self.assertEqual(1,self.conn.execute(
            "SELECT COUNT(*) FROM work_item_result_receipts WHERE run_id='result-run'").fetchone()[0])

    def test_manual_result_allows_later_lifecycle_submission_with_new_receipt(self):
        item=intake.add_work_item(self.conn,title='Manual result',repo='manual-result')
        wid=item['work_item_id']
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(wid,))
        blocked=scheduler.executor_result(self.conn,work_item_id=wid,outcome='BLOCKED',
            completed=[],remaining=['wait'],evidence=['first report'],blocker='wait',
            next_action='resume',strict_contract=True)
        passed=scheduler.executor_result(self.conn,work_item_id=wid,outcome='PASS',
            completed=['done'],remaining=[],evidence=['second report'],strict_contract=True)
        self.assertNotEqual(blocked['receipt_id'],passed['receipt_id'])
        self.assertEqual('completed',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(wid,)).fetchone()[0])
        self.assertEqual(2,self.conn.execute(
            'SELECT COUNT(*) FROM work_item_result_receipts WHERE work_item_id=?',(wid,)).fetchone()[0])

    def test_manual_takeover_result_preserves_failed_scheduled_run(self):
        item=intake.add_work_item(self.conn,title='Recovered triage',repo='manual-recovery',
            acceptance=['drained'])
        wid=item['work_item_id']
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(wid,))
        self.conn.execute("""INSERT INTO work_item_runs(
            run_id,work_item_id,event_key,attempt,executor,state,lease_until,
            worker_ref,checkpoint_commit,metadata_json,created_at)
            VALUES('failed-run',?,'event',1,'chatgpt','failed',100,
                   'c2-run:failed-run',NULL,'{}',10)""",(wid,))
        self.conn.execute("""INSERT INTO work_item_executor_starts(
            receipt_id,work_item_id,run_id,prompt_id,executor,executor_ref,chat_url,started_at)
            VALUES('manual-start',?,NULL,NULL,'codex','thread','codex://threads/thread',20)""",(wid,))

        result=scheduler.executor_result(self.conn,work_item_id=wid,outcome='PASS',
            completed=['drained'],remaining=[],evidence=['canonical Inbox zero'],
            strict_contract=True)

        self.assertIsNone(result['run_id'])
        self.assertEqual('failed',self.conn.execute(
            "SELECT state FROM work_item_runs WHERE run_id='failed-run'").fetchone()[0])
        self.assertEqual('completed',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(wid,)).fetchone()[0])

    def test_new_manual_result_cannot_bypass_terminal_lifecycle(self):
        item=intake.add_work_item(self.conn,title='Terminal result',repo='terminal-result')
        wid=item['work_item_id']
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(wid,))
        scheduler.executor_result(self.conn,work_item_id=wid,outcome='PASS',
            completed=['done'],remaining=[],evidence=['proof'],strict_contract=True)
        with self.assertRaisesRegex(scheduler.SchedulingError,'executor_result_item_state_conflict'):
            scheduler.executor_result(self.conn,work_item_id=wid,outcome='BLOCKED',
                completed=[],remaining=['reopen'],evidence=['different report'],blocker='new blocker',
                next_action='do not reopen',strict_contract=True)
        self.assertEqual(1,self.conn.execute(
            'SELECT COUNT(*) FROM work_item_result_receipts WHERE work_item_id=?',(wid,)).fetchone()[0])

    def test_manual_nonprompt_start_claims_runnable_pending_item(self):
        item=intake.add_work_item(self.conn,title='Manual runnable',repo='manual',
            executor_policy='auto')
        wid=item['work_item_id']
        receipt=scheduler.executor_started(self.conn,work_item_id=wid,executor='codex',
            executor_ref='thread-1',chat_url='codex://threads/thread-1',now=12)
        self.assertEqual('running',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(wid,)).fetchone()[0])
        self.assertEqual(wid,receipt['work_item_id'])

    def test_manual_start_ignores_status_only_same_repo_orchestration(self):
        supervisor=intake.add_work_item(self.conn,title='Supervisor',repo='shared')
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",
            (supervisor['work_item_id'],))
        item=intake.add_work_item(self.conn,title='Isolated task',repo='shared',
            executor_policy='auto')
        wid=item['work_item_id']
        scheduler.configure(self.conn,wid,activity='native',command=['true'],
            worktree='/tmp/isolated-task')

        receipt=scheduler.executor_started(self.conn,work_item_id=wid,executor='codex')

        self.assertEqual(wid,receipt['work_item_id'])
        self.assertEqual('running',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(wid,)).fetchone()[0])

    def test_manual_start_still_blocks_real_active_same_repo_run(self):
        holder=self.add('shared')
        run=scheduler.schedule(self.conn,event_key='active-writer',now=10,max_parallel=1)[0]
        self.assertEqual(holder,run['work_item_id'])
        candidate=self.add('shared')

        with self.assertRaisesRegex(scheduler.SchedulingError,'executor_start_repo_conflict'):
            scheduler.executor_started(self.conn,work_item_id=candidate,executor='codex')

    def test_manual_start_still_blocks_prompt_writer_with_worktree(self):
        writer=self.conn.execute(
            "SELECT work_item_id FROM work_items WHERE prompt_id='123456'").fetchone()[0]
        self.conn.execute("UPDATE work_items SET repo='shared' WHERE work_item_id=?",(writer,))
        scheduler.configure(self.conn,writer,activity='coding',model='GPT-5',reasoning='high',
            worktree='/tmp/prompt-writer')
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(writer,))
        candidate=self.add('shared')

        with self.assertRaisesRegex(scheduler.SchedulingError,'executor_start_repo_conflict'):
            scheduler.executor_started(self.conn,work_item_id=candidate,executor='codex')

    def test_manual_prompt_start_cannot_bypass_roadmap_start(self):
        with self.assertRaisesRegex(scheduler.SchedulingError,'prompt_requires_roadmap_start'):
            scheduler.executor_started(self.conn,prompt_id='123456',executor='codex',
                executor_ref='thread-1',chat_url='codex://threads/thread-1')

    def test_executor_started_is_distinct_idempotent_and_binding_enriches_it(self):
        item=intake.add_work_item(self.conn,title='Start receipt',repo='browser',
            executor_policy='chatgpt')
        wid=item['work_item_id']
        scheduler.configure(self.conn,wid,activity='semantic',
            project_url='https://chatgpt.com/g/g-p-fixture')
        run=scheduler.schedule(self.conn,event_key='start-receipt',now=10)[0]
        with self.assertRaisesRegex(scheduler.SchedulingError,'executor_start_run_not_active'):
            scheduler.executor_started(self.conn,run_id=run['run_id'])
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
            metadata=run['metadata'],now=11)
        first=scheduler.executor_started(self.conn,run_id=run['run_id'],now=12)
        replay=scheduler.executor_started(self.conn,run_id=run['run_id'],now=13)
        self.assertEqual(first['receipt_id'],replay['receipt_id'])
        self.assertIsNone(first['chat_url'])
        scheduler.bind_executor(self.conn,run['run_id'],
            executor_ref='https://chatgpt.com/c/test',chat_url='https://chatgpt.com/c/test',now=14)
        enriched=self.conn.execute(
            'SELECT * FROM work_item_executor_starts WHERE run_id=?',(run['run_id'],)).fetchone()
        self.assertEqual('https://chatgpt.com/c/test',enriched['chat_url'])
        self.assertEqual('chatgpt',enriched['executor'])
        self.assertEqual(1,self.conn.execute(
            'SELECT COUNT(*) FROM work_item_executor_starts WHERE run_id=?',(run['run_id'],)).fetchone()[0])

    def test_structured_nonprompt_result_replaces_two_step_terminal_sequence(self):
        item=intake.add_work_item(self.conn,title='One result call',repo='browser',
            acceptance=['A'],executor_policy='chatgpt')
        wid=item['work_item_id']
        scheduler.configure(self.conn,wid,activity='semantic',
            project_url='https://chatgpt.com/g/g-p-fixture')
        run=scheduler.schedule(self.conn,event_key='one-result',now=10)[0]
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
            metadata=run['metadata'],now=11)
        scheduler.executor_result(self.conn,run_id=run['run_id'],outcome='PASS',
            completed=['A'],remaining=[],evidence=['verified'],strict_contract=True)
        self.assertEqual('completed',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(wid,)).fetchone()[0])
        self.assertEqual('completed',self.conn.execute(
            'SELECT state FROM work_item_runs WHERE run_id=?',(run['run_id'],)).fetchone()[0])


    def test_parallelism_and_same_repo_collision(self):
        a=self.add(); b=self.add(); c=self.add('repo-b')
        runs=scheduler.schedule(self.conn,event_key='intake-1',now=10,max_parallel=3)
        self.assertEqual({a,c},{r['work_item_id'] for r in runs})
        self.assertEqual(runs,scheduler.schedule(self.conn,event_key='intake-1',now=11,max_parallel=3))
        self.assertEqual(2,self.conn.execute('SELECT COUNT(*) FROM work_item_runs').fetchone()[0])

    def test_explicit_priority_tag_precedes_sort_order(self):
        normal=self.add('normal')
        urgent=self.add('urgent')
        self.conn.execute("INSERT INTO work_item_tags(work_item_id,tag) VALUES(?,'priority:p0')",(urgent,))
        self.assertEqual(urgent,scheduler.schedule(self.conn,event_key='priority',now=1,max_parallel=1)[0]['work_item_id'])

    def test_manual_rank_obeys_dependency_and_blocker_eligibility(self):
        dependency=self.add('dependency')
        dependent=self.add('dependent',depends_on=[dependency])
        blocked=self.add('blocked')
        self.conn.execute("UPDATE work_items SET status='blocked',blocker='external' WHERE work_item_id=?",(blocked,))
        c2_manual_order.set_manual_order(self.conn,scope='roadmap',
            ordered_ids=[dependent,blocked,dependency],source='workflowy',
            source_modified_at='wf-1')
        run=scheduler.schedule(self.conn,event_key='manual-hard-gates',now=1,max_parallel=1)[0]
        self.assertEqual(dependency,run['work_item_id'])
        self.assertEqual('blocked',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(blocked,)).fetchone()[0])

    def test_manual_rank_precedes_ai_priority_and_reset_restores_ai_order(self):
        p0=self.add('p0')
        p1=self.add('p1')
        self.conn.execute("INSERT INTO work_item_tags VALUES(?,'priority:p0')",(p0,))
        self.conn.execute("INSERT INTO work_item_tags VALUES(?,'priority:p1')",(p1,))
        c2_manual_order.set_manual_order(self.conn,scope='roadmap',ordered_ids=[p1,p0],
            source='workflowy',source_modified_at='wf-2')
        readback=self.conn.execute(
            'SELECT manual_rank,manual_order_source,ai_priority_rank,sort_order,status '
            'FROM v_work_item_summary WHERE work_item_id=?',(p1,)).fetchone()
        self.assertEqual((0,'workflowy',1,2,'pending'),tuple(readback))
        self.assertEqual(p1,scheduler.schedule(
            self.conn,event_key='manual-priority',now=1,max_parallel=1)[0]['work_item_id'])

        self.conn.execute("UPDATE work_items SET status='pending' WHERE work_item_id=?",(p1,))
        self.conn.execute('DELETE FROM work_item_resource_leases')
        self.conn.execute('DELETE FROM work_item_runs')
        c2_manual_order.clear_manual_order(self.conn,scope='roadmap')
        self.assertEqual(p0,scheduler.schedule(
            self.conn,event_key='ai-priority-restored',now=2,max_parallel=1)[0]['work_item_id'])

    def test_blocked_item_retains_rank_and_leads_after_becoming_runnable(self):
        blocked=self.add('blocked-first')
        ready=self.add('ready-second')
        fallback=self.add('fallback-third')
        self.conn.execute("UPDATE work_items SET status='blocked',blocker='wait' WHERE work_item_id=?",(blocked,))
        c2_manual_order.set_manual_order(self.conn,scope='roadmap',
            ordered_ids=[blocked,ready,fallback],source='workflowy',
            source_modified_at='wf-3')
        self.assertEqual(ready,scheduler.schedule(
            self.conn,event_key='while-blocked',now=1,max_parallel=1)[0]['work_item_id'])
        self.assertEqual(0,self.conn.execute(
            "SELECT rank FROM manual_order_overrides WHERE scope='roadmap' AND entity_id=?",
            (blocked,)).fetchone()[0])

        self.conn.execute("UPDATE work_items SET status='pending',blocker=NULL WHERE work_item_id=?",(blocked,))
        self.assertEqual(blocked,scheduler.schedule(
            self.conn,event_key='after-unblock',now=2,max_parallel=2)[0]['work_item_id'])

    def test_override_selectors_replay_clear_and_semantic_order(self):
        normal=self.add('normal')
        scoped=self.add('gernalix/PersonalHub')
        self.conn.execute("UPDATE work_items SET project_name='PersonalHub' WHERE work_item_id=?",(scoped,))
        self.conn.execute("INSERT INTO work_item_tags(work_item_id,tag) VALUES(?,'focus:ph')",(scoped,))
        self.conn.execute("INSERT INTO work_item_tags(work_item_id,tag) VALUES(?,'priority:p0')",(normal,))
        before=[tuple(r) for r in self.conn.execute('SELECT work_item_id,sort_order FROM work_items WHERE work_item_id IN (?,?)',(normal,scoped))]
        for selector,value in [('project','PersonalHub'),('repo','gernalix/PersonalHub'),('tag','focus:ph')]:
            first=scheduler.set_override(self.conn,selector=selector,value=value,now=1)
            self.assertEqual(first,scheduler.set_override(self.conn,selector=selector,value=value,now=1))
            self.assertEqual(scoped,scheduler.schedule(self.conn,event_key='scope-'+selector,now=2,max_parallel=1)[0]['work_item_id'])
            self.conn.execute("UPDATE work_items SET status='pending' WHERE work_item_id=?",(scoped,))
            self.conn.execute('DELETE FROM work_item_resource_leases')
            self.conn.execute('DELETE FROM work_item_runs')
            scheduler.clear_override(self.conn)
            self.assertIsNone(scheduler.read_override(self.conn))
        self.assertEqual(before,[tuple(r) for r in self.conn.execute('SELECT work_item_id,sort_order FROM work_items WHERE work_item_id IN (?,?)',(normal,scoped))])
        self.assertEqual(normal,scheduler.schedule(self.conn,event_key='cleared',now=3,max_parallel=1)[0]['work_item_id'])

    def test_override_falls_back_for_nonrunnable_or_empty_scope(self):
        normal=self.add('normal')
        blocked=self.add('target',depends_on=[normal])
        scheduler.set_override(self.conn,selector='repo',value='target',now=1)
        self.assertEqual(normal,scheduler.schedule(self.conn,event_key='dependency-fallback',now=2,max_parallel=1)[0]['work_item_id'])
        self.assertEqual('pending',self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(blocked,)).fetchone()[0])

    def test_override_honors_parallelism_and_device_lock(self):
        one=self.add('ph-one')
        two=self.add('ph-two')
        other=self.add('other')
        self.conn.execute("UPDATE work_items SET project_name='PersonalHub' WHERE work_item_id IN (?,?)",(one,two))
        for wid in (one,two):
            self.conn.execute("UPDATE work_item_execution_specs SET resources_json='[\"device:pixel\"]' WHERE work_item_id=?",(wid,))
        scheduler.set_override(self.conn,selector='project',value='PersonalHub',now=1)
        runs=scheduler.schedule(self.conn,event_key='device',now=2,max_parallel=3)
        self.assertEqual([one],[r['work_item_id'] for r in runs])
        self.assertEqual('pending',self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(other,)).fetchone()[0])

    def test_override_falls_back_when_scoped_device_is_leased(self):
        holder=self.add('holder')
        self.conn.execute("UPDATE work_item_execution_specs SET resources_json='[\"device:pixel\"]' WHERE work_item_id=?",(holder,))
        scheduler.schedule(self.conn,event_key='holder',now=1,max_parallel=1)
        scoped=self.add('gernalix/PersonalHub')
        other=self.add('other')
        self.conn.execute("UPDATE work_item_execution_specs SET resources_json='[\"device:pixel\"]' WHERE work_item_id=?",(scoped,))
        scheduler.set_override(self.conn,selector='repo',value='gernalix/PersonalHub',now=2)
        runs=scheduler.schedule(self.conn,event_key='locked-fallback',now=3,max_parallel=3)
        self.assertEqual([other],[r['work_item_id'] for r in runs])
        self.assertEqual('pending',self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(scoped,)).fetchone()[0])

    def test_crash_recovery_reuses_identity_and_locks(self):
        a=self.add(); self.add()
        run=scheduler.schedule(self.conn,event_key='first',now=10)[0]
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='worker-1',metadata=run['metadata'],now=11)
        scheduler.checkpoint(self.conn,run['run_id'],'a'*40)
        self.conn.commit(); self.conn.close()
        self.conn=intake._connect(self.path); self.conn.execute('BEGIN IMMEDIATE')
        recovered=scheduler.recover(self.conn,now=999)
        self.assertEqual(run['run_id'],recovered[0]['run_id'])
        self.assertEqual('a'*40,recovered[0]['checkpoint_commit'])
        self.assertEqual([],scheduler.schedule(self.conn,event_key='restart',now=999))
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='worker-1',metadata=run['metadata'],now=1000)
        scheduler.complete(self.conn,run['run_id'],succeeded=True,worker_ref='worker-1')
        scheduler.complete(self.conn,run['run_id'],succeeded=True,worker_ref='worker-1')
        self.assertEqual(1,len(scheduler.schedule(self.conn,event_key='completion',now=1001)))

    def test_adopted_prompt_writer_is_never_claimed_or_changed(self):
        writer=self.conn.execute(
            "SELECT work_item_id FROM work_items WHERE prompt_id='123456'").fetchone()[0]
        self.conn.execute("UPDATE work_items SET repo='repo-a' WHERE work_item_id=?",(writer,))
        scheduler.configure(self.conn,writer,activity='coding',model='GPT-5',reasoning='high',
            worktree='/tmp/adopted-writer')
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(writer,))
        before=tuple(self.conn.execute("SELECT * FROM work_items WHERE prompt_id='123456'").fetchone())
        self.add()
        self.assertEqual([],scheduler.schedule(self.conn,event_key='migration',now=1))
        self.assertEqual(before,tuple(self.conn.execute("SELECT * FROM work_items WHERE prompt_id='123456'").fetchone()))

    def test_imported_running_state_without_worker_does_not_consume_capacity(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
        for n in range(3):
            orphan=self.add('imported-'+str(n))
            self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(orphan,))
        candidate=self.add('live-gate')
        runs=scheduler.schedule(self.conn,event_key='capacity',now=1,max_parallel=2)
        self.assertEqual([candidate],[run['work_item_id'] for run in runs])

    def test_dependencies_and_required_gate(self):
        parent=self.add('parent')
        child=self.add('child',parent_id=parent)
        other=self.add('other',depends_on=[parent])
        runs=scheduler.schedule(self.conn,event_key='start',now=1)
        self.assertEqual([parent],[r['work_item_id'] for r in runs])
        run=runs[0]
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='w',metadata=run['metadata'],now=2)
        with self.assertRaisesRegex(scheduler.SchedulingError,'required_children'):
            scheduler.complete(self.conn,run['run_id'],succeeded=True,worker_ref='w')
        self.conn.execute("UPDATE work_items SET status='waived' WHERE work_item_id=?",(child,))
        scheduler.complete(self.conn,run['run_id'],succeeded=True,worker_ref='w')
        self.assertEqual(other,scheduler.schedule(self.conn,event_key='done',now=3)[0]['work_item_id'])

    def test_exact_metadata_fails_closed(self):
        a=self.add()
        run=scheduler.schedule(self.conn,event_key='start',now=1)[0]
        bad=dict(run['metadata'],model='silently-changed')
        with self.assertRaisesRegex(scheduler.SchedulingError,'metadata_mismatch'):
            scheduler.acknowledge(self.conn,run['run_id'],worker_ref='w',metadata=bad,now=2)
        with self.assertRaisesRegex(scheduler.SchedulingError,'only_pending'):
            scheduler.configure(self.conn,a,activity='coding')

    def test_executor_policy_is_deterministic(self):
        expected={'coding':'codex','diagnostic':'codex','gui':'rdc','native':'rdc',
                  'semantic':'chatgpt','external':None,'human':'human'}
        for activity,executor in expected.items():
            self.assertEqual(executor,scheduler.choose_executor('auto',activity))

    def test_degraded_lane_suspends_chatgpt_but_keeps_native_dispatchable(self):
        chat=intake.add_work_item(self.conn,title='Chat',repo='chat-repo',executor_policy='auto')['work_item_id']
        scheduler.configure(self.conn,chat,activity='semantic',
                            project_url='https://chatgpt.com/g/g-p-fixture')
        native=self.add('native-repo')
        runs=scheduler.schedule(self.conn,event_key='degraded',now=10,max_parallel=2,
                                chatgpt_lane_degraded=True)
        self.assertEqual([native],[r['work_item_id'] for r in runs])
        self.assertEqual('pending',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(chat,)).fetchone()[0])
        resumed=scheduler.schedule(self.conn,event_key='recovered',now=11,max_parallel=2,
                                   chatgpt_lane_degraded=False)
        self.assertEqual([chat],[r['work_item_id'] for r in resumed])

    def test_codex_run_reconciles_only_after_canonical_terminal(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
        self.conn.execute("""INSERT INTO work_item_runs VALUES(
            'r','prompt:123456','event',1,'codex','running',100,'c2-run:r',NULL,'{}',1)""")
        self.conn.execute("INSERT INTO work_item_resource_leases VALUES('repo:roadmap','r')")
        with self.assertRaisesRegex(scheduler.SchedulingError,'canonical_terminal'):
            scheduler.reconcile_terminal_run(self.conn,'r')
        self.conn.execute("UPDATE work_items SET status='completed' WHERE prompt_id='123456'")
        scheduler.reconcile_terminal_run(self.conn,'r')
        scheduler.reconcile_terminal_run(self.conn,'r')
        self.assertEqual('completed',self.conn.execute(
            "SELECT state FROM work_item_runs WHERE run_id='r'").fetchone()[0])
        self.assertEqual(0,self.conn.execute('SELECT COUNT(*) FROM work_item_resource_leases').fetchone()[0])

    def test_canonical_goal_terminal_enqueues_one_milestone(self):
        self.conn.execute("UPDATE work_items SET kind='goal' WHERE prompt_id='123456'")
        roadmap_db.set_status(self.conn,'123456','running',actor='test')
        roadmap_db.set_status(self.conn,'123456','completed',actor='test',allow_running_terminal=True)
        roadmap_db.set_status(self.conn,'123456','completed',actor='test',allow_running_terminal=True)
        self.assertEqual(1,self.conn.execute('''SELECT COUNT(*) FROM c2_notification_outbox
          WHERE event_key='work-item:prompt:123456:completed' AND state='pending' ''').fetchone()[0])

    def test_browser_completion_requires_checkpoint_evidence_and_completed_children(self):
        item=intake.add_work_item(self.conn,title='Browser acceptance',repo='browser',
            sort_order=0,kind='goal',executor_policy='chatgpt')
        work_item_id=item['work_item_id']
        scheduler.configure(self.conn,work_item_id,activity='semantic',
            project_url='https://chatgpt.com/g/g-p-fixture')
        child=intake.add_work_item(self.conn,title='Required child',repo='child',
            sort_order=1,parent_id=work_item_id)
        run=scheduler.schedule(self.conn,event_key='browser',now=10)[0]
        scheduler.acknowledge(self.conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
            metadata=run['metadata'],now=11)
        with self.assertRaisesRegex(scheduler.SchedulingError,'acceptance_checkpoint_incomplete'):
            scheduler.finish_browser_work_item(self.conn,work_item_id,evidence=['proof'])
        scheduler.record_checkpoint(self.conn,work_item_id,current_step='Done',
            next_action='Close',remaining=[],evidence=['proof'])
        with self.assertRaisesRegex(scheduler.SchedulingError,'required_children_incomplete'):
            scheduler.finish_browser_work_item(self.conn,work_item_id,evidence=['proof'])
        self.conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",
            (child['work_item_id'],))
        scheduler.finish_browser_work_item(self.conn,work_item_id,evidence=['proof'])
        scheduler.finish_browser_work_item(self.conn,work_item_id,evidence=['proof'])
        self.assertEqual('completed',self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?',
            (work_item_id,)).fetchone()[0])
        self.assertEqual(1,self.conn.execute('SELECT COUNT(*) FROM c2_notification_outbox WHERE work_item_id=?',
            (work_item_id,)).fetchone()[0])

    def test_verified_nonprompt_closure_requires_every_acceptance_criterion(self):
        item=intake.add_work_item(self.conn,title='Verified repair',repo='roadmap',
            acceptance=['A','B'])
        work_item_id=item['work_item_id']
        scheduler.record_checkpoint(self.conn,work_item_id,current_step='Partial',
            next_action='Verify B',completed=['A'],remaining=[])
        with self.assertRaisesRegex(scheduler.SchedulingError,'acceptance_criteria_not_verified'):
            scheduler.verify_work_item(self.conn,work_item_id,evidence=['proof'])
        scheduler.record_checkpoint(self.conn,work_item_id,current_step='Verified',
            next_action='Close item',completed=['A','B'],remaining=[],evidence=['proof'])
        scheduler.verify_work_item(self.conn,work_item_id,evidence=['proof'])
        self.assertEqual('completed',self.conn.execute(
            'SELECT status FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()[0])
        self.assertEqual(1,self.conn.execute(
            "SELECT COUNT(*) FROM work_item_evidence WHERE work_item_id=? AND evidence_kind='completion'",
            (work_item_id,)).fetchone()[0])
