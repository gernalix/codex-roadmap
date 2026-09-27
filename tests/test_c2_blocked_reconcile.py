from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_blocked_reconcile as blocked
import c2_intake
import c2_scheduler
import c2_mutations
import c2_runtime
from test_c2_intake import C2IntakeTests


class BlockedReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        path = C2IntakeTests().make_cutover_db(Path(self.tmp.name))
        self.db = c2_intake._connect(path)
        c2_scheduler.install_schema(self.db)
        self.db.execute("BEGIN IMMEDIATE")
        self.root = c2_intake.add_work_item(self.db, title="Root")['work_item_id']
        self.child = c2_intake.add_work_item(self.db, title="Child", parent_id=self.root)['work_item_id']
        for item in (self.root, self.child, 'prompt:123456'):
            self.db.execute("UPDATE work_items SET status='blocked',blocker='external',updated_at='old' WHERE work_item_id=?", (item,))

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def _reconcile(self, item, **overrides):
        args = dict(expected_updated_at='old', disposition='WAITING',
                    evidence=['Canonical prerequisite resolved at commit abc123'],
                    next_action='Resume review')
        args.update(overrides)
        return blocked.reconcile(self.db, item, **args)

    def test_root_child_prompt_waiting_preserves_historical_receipts(self):
        self.db.execute("""INSERT INTO work_item_result_receipts
            (receipt_id,work_item_id,outcome,completed_json,remaining_json,evidence_json,
             payload_sha256,captured_at) VALUES('prior',?,'BLOCKED','[]','[]','[]','hash',1)""",
            (self.child,))
        self.db.execute("""INSERT INTO terminal_requests
            (prompt_id,requested_status,actor,note,requested_at)
            VALUES('123456','blocked','historical','prior result','old')""")
        for item in (self.root, self.child, 'prompt:123456'):
            result = self._reconcile(item)
            self.assertEqual('waiting', result['new_status'])
            self.assertEqual(('waiting', None), tuple(self.db.execute(
                'SELECT status,blocker FROM work_items WHERE work_item_id=?', (item,)).fetchone()))
        self.assertEqual(1, self.db.execute("SELECT count(*) FROM status_history WHERE prompt_id='123456' AND new_status='waiting'").fetchone()[0])
        self.assertEqual('blocked', self.db.execute("SELECT requested_status FROM terminal_requests WHERE prompt_id='123456'").fetchone()[0])
        self.assertEqual(1, self.db.execute("SELECT count(*) FROM work_item_result_receipts WHERE receipt_id='prior'").fetchone()[0])
        self.assertEqual(3, self.db.execute("SELECT count(*) FROM work_item_scheduler_events WHERE event_key LIKE 'blocked-reconcile:%'").fetchone()[0])

    def test_stale_updated_at_and_active_run_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'blocked_item_changed'):
            self._reconcile(self.root, expected_updated_at='stale')
        self.db.execute("""INSERT INTO work_item_runs VALUES(
            'run',?,'event',1,'codex','running',100,'worker',NULL,'{}',1)""", (self.root,))
        with self.assertRaisesRegex(ValueError, 'active_run_requires_normal_lifecycle'):
            self._reconcile(self.root)
        self.assertEqual('blocked', self.db.execute('SELECT status FROM work_items WHERE work_item_id=?', (self.root,)).fetchone()[0])

    def test_ambiguous_blocker_requires_recovery_condition(self):
        with self.assertRaisesRegex(ValueError, 'blocker_and_recovery_condition_required'):
            self._reconcile(self.child, disposition='BLOCKED', blocker='External source missing')
        self._reconcile(self.child, disposition='BLOCKED', blocker='External source missing',
                        recovery_condition='Source archive includes session cycles')
        self.assertEqual('External source missing', self.db.execute(
            'SELECT blocker FROM work_items WHERE work_item_id=?', (self.child,)).fetchone()[0])

    def test_terminal_prompt_history_and_safety_net_replay(self):
        successor = c2_intake.add_work_item(self.db, title='Successor')['work_item_id']
        self.db.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (successor,))
        self.db.execute("""INSERT INTO work_item_relations VALUES(
            'prompt:123456',?,'resolved_by','now','test','canonical')""", (successor,))
        expected = blocked.automatic_candidates(self.db)
        self.assertEqual([('prompt:123456', 'resolved_by')],
                         [(x['work_item_id'], x['kind']) for x in expected])
        result = blocked.safety_net(self.db, expected=expected)
        self.assertEqual('superseded', result[0]['new_status'])
        self.assertEqual([], blocked.safety_net(self.db, expected=expected))
        self.assertEqual(1, self.db.execute("SELECT count(*) FROM status_history WHERE prompt_id='123456' AND new_status='superseded'").fetchone()[0])

    def test_safety_net_dependency_requires_explicit_marker_and_all_dependencies(self):
        dependency = c2_intake.add_work_item(self.db, title='Dependency')['work_item_id']
        self.db.execute("INSERT INTO work_item_dependencies(work_item_id,depends_on_work_item_id,required) VALUES(?,?,1)",
                        (self.child, dependency))
        self.db.execute("UPDATE work_items SET blocker=? WHERE work_item_id=?", ('dependency:' + dependency, self.child))
        self.assertEqual([], blocked.automatic_candidates(self.db))
        self.db.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (dependency,))
        expected = blocked.automatic_candidates(self.db)
        self.assertEqual('dependency', expected[0]['kind'])
        self.assertEqual('waiting', blocked.safety_net(self.db, expected=expected)[0]['new_status'])
        self.assertEqual([], blocked.safety_net(self.db, expected=expected))

    def test_single_writer_route_and_replay_fail_closed(self):
        args = dict(work_item_id=self.child, expected_updated_at='old',
                    disposition='WAITING', evidence=['canonical dependency completed'],
                    next_action='Resume child', supervisor_authority={'supervisor_id': 'fixture'})
        with patch('c2_supervisor_authority.require'):
            result = c2_mutations.apply(self.db, {'op': 'c2_reconcile_blocked', 'arguments': args})
        self.assertEqual('waiting', result['new_status'])
        with patch('c2_supervisor_authority.require'):
            with self.assertRaisesRegex(ValueError, 'blocked_item_required'):
                c2_mutations.apply(self.db, {'op': 'c2_reconcile_blocked', 'arguments': args})

    def test_runtime_periodic_tick_submits_only_structured_candidate(self):
        successor = c2_intake.add_work_item(self.db, title='Successor')['work_item_id']
        self.db.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (successor,))
        self.db.execute("""INSERT INTO work_item_relations VALUES(
            ?,?,'resolved_by','now','test','canonical')""", (self.child, successor))
        calls = []
        c2_runtime.advance(self.db, submit=lambda *args: calls.append(args),
                           repo_task_status=lambda _: {}, launch=lambda _: None,
                           launch_notify=lambda _: None, now=10)
        self.assertEqual(1, len([c for c in calls if c[0] == 'reconcile_blocked_safety_net']))
        self.assertEqual(self.child, [c for c in calls if c[0] == 'reconcile_blocked_safety_net'][0][1]['expected'][0]['work_item_id'])


if __name__ == '__main__':
    unittest.main()
