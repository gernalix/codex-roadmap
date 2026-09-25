from contextlib import closing
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake as intake
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

    def test_adopted_running_is_never_claimed_or_changed(self):
        self.conn.execute("UPDATE work_items SET status='running',repo='repo-a' WHERE prompt_id='123456'")
        before=tuple(self.conn.execute("SELECT * FROM work_items WHERE prompt_id='123456'").fetchone())
        self.add()
        self.assertEqual([],scheduler.schedule(self.conn,event_key='migration',now=1))
        self.assertEqual(before,tuple(self.conn.execute("SELECT * FROM work_items WHERE prompt_id='123456'").fetchone()))

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
