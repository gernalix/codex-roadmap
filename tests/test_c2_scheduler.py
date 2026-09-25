from contextlib import closing
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake as intake
import c2_scheduler as scheduler
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
