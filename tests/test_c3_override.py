from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_intake
import c2_scheduler
import c3_override as override
import c3_api
import test_c2_intake


class OverrideTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = test_c2_intake.C2IntakeTests().make_cutover_db(Path(self.tmp.name))
        self.conn = c2_intake._connect(self.path)
        c2_scheduler.install_schema(self.conn)
        override.install_schema(self.conn)
        self.conn.commit()
        self.conn.execute('BEGIN IMMEDIATE')
        self.a = self.add('A')
        self.b = self.add('B')
        self.c = self.add('C')
        self.conn.execute('INSERT INTO work_item_dependencies VALUES(?,?,1,NULL)', (self.b, self.a))
        self.conn.execute('INSERT INTO work_item_dependencies VALUES(?,?,1,NULL)', (self.c, self.b))

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def add(self, title, **kw):
        return c2_intake.add_work_item(self.conn, title=title, sort_order=100 + self.conn.execute('SELECT COUNT(*) FROM work_items').fetchone()[0], **kw)['work_item_id']

    def command(self, wid, action, **kw):
        p = override.preview(self.conn, wid, action)
        args = {'work_item_id': wid, 'action': action, 'request_id': action + wid,
                'precondition': p['precondition'], 'intent': 'explicit-user', **kw}
        return {'op': 'c3_destructive_override' if action in override.DESTRUCTIVE_ACTIONS else 'c3_user_override', 'arguments': args}

    def apply(self, command):
        return override.apply(self.conn, command, 'c3-user-control')

    def test_pause_resume_and_stop_block_dispatch(self):
        self.apply(self.command(self.a, 'pause'))
        self.assertFalse(self.conn.execute('SELECT 1 FROM v_work_item_runnable WHERE work_item_id=?', (self.a,)).fetchone())
        self.apply(self.command(self.a, 'resume'))
        self.assertTrue(self.conn.execute('SELECT 1 FROM v_work_item_runnable WHERE work_item_id=?', (self.a,)).fetchone())
        self.apply(self.command(self.b, 'stop'))
        self.assertEqual('blocked', self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (self.b,)).fetchone()[0])

    def test_destructive_exact_transitive_confirmation_and_history(self):
        p = override.preview(self.conn, self.a, 'delete')
        self.assertEqual(sorted([self.a, self.b, self.c]), p['affected'])
        cmd = self.command(self.a, 'delete', confirmed_affected=[self.a])
        with self.assertRaisesRegex(ValueError, 'confirmation'):
            self.apply(cmd)
        self.apply(self.command(self.a, 'delete', confirmed_affected=p['affected']))
        self.assertEqual(3, self.conn.execute('SELECT COUNT(*) FROM c3_user_state WHERE deleted=1').fetchone()[0])
        self.assertEqual('cancelled', self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (self.c,)).fetchone()[0])
        self.assertTrue(self.conn.execute('SELECT 1 FROM work_items WHERE work_item_id=?', (self.a,)).fetchone())

    def test_cancel_and_force_priority(self):
        self.apply(self.command(self.c, 'cancel', confirmed_affected=[self.c]))
        self.apply(self.command(self.a, 'force-priority', priority='p0'))
        self.assertTrue(self.conn.execute("SELECT 1 FROM work_item_tags WHERE work_item_id=? AND tag='priority:p0'", (self.a,)).fetchone())

    def test_move_clamps_to_exact_prerequisite(self):
        result = self.apply(self.command(self.c, 'move', position=0))
        order = result['ordered_ids']
        self.assertLess(order.index(self.a), order.index(self.b))
        self.assertLess(order.index(self.b), order.index(self.c))
        self.assertIn(self.b, result['blocking_prerequisites'])
        self.assertGreater(result['applied_position'], 0)

    def test_move_uses_the_displayed_canonical_manual_order(self):
        self.conn.execute('DELETE FROM work_item_dependencies')
        self.conn.execute("INSERT INTO manual_order_overrides VALUES('roadmap',?,0,'workflowy','x','x')", (self.c,))
        self.conn.execute("INSERT INTO manual_order_overrides VALUES('roadmap',?,1,'workflowy','x','x')", (self.a,))
        self.conn.execute("INSERT INTO manual_order_overrides VALUES('roadmap',?,2,'workflowy','x','x')", (self.b,))
        result = self.apply(self.command(self.b, 'move', position=1))
        self.assertEqual([self.c, self.b, self.a], result['ordered_ids'][:3])
        key = override.order_key(self.conn)
        items, _ = override.graph(self.conn)
        self.assertEqual(result['ordered_ids'], sorted(result['ordered_ids'], key=lambda i: key(items[i])))

    def test_move_keeps_running_prerequisite_visible_before_dependent(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?", (self.a,))
        original = self.conn.execute('SELECT sort_order FROM work_items WHERE work_item_id=?', (self.a,)).fetchone()[0]
        result = self.apply(self.command(self.c, 'move', position=0))
        items, _ = override.graph(self.conn)
        order = sorted(result['ordered_ids'], key=lambda i: override.order_key(self.conn)(items[i]))
        self.assertLess(order.index(self.a), order.index(self.b))
        self.assertLess(order.index(self.b), order.index(self.c))
        self.assertEqual(original, items[self.a]['sort_order'])

    def test_graph_change_fails_closed(self):
        cmd = self.command(self.a, 'cancel', confirmed_affected=sorted([self.a, self.b, self.c]))
        self.add('new dependent', parent_id=self.a)
        with self.assertRaisesRegex(ValueError, 'precondition'):
            self.apply(cmd)
        self.assertEqual('pending', self.conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (self.a,)).fetchone()[0])

    def test_wrong_class_and_ordinary_authority_rejected(self):
        cmd = self.command(self.a, 'pause')
        cmd['op'] = 'c3_destructive_override'
        with self.assertRaisesRegex(ValueError, 'wrong_override_class'):
            self.apply(cmd)
        with self.assertRaisesRegex(ValueError, 'authority'):
            override.apply(self.conn, self.command(self.a, 'pause'), 'c2-runtime')

    def test_live_executor_requires_ack_and_releases_lease_on_stop(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?", (self.a,))
        self.conn.execute("INSERT INTO work_item_runs VALUES('r',?,'e',1,'native','running',100,'c3-run:r',NULL,'{}',1)", (self.a,))
        self.conn.execute("INSERT INTO work_item_resource_leases VALUES('test','r')")
        with self.assertRaisesRegex(ValueError, 'not_acknowledged'):
            self.apply(self.command(self.a, 'stop'))
        self.apply(self.command(self.a, 'stop', executor_effects=[{'run_id': 'r', 'worker_ref': 'c3-run:r', 'effect': 'stopped'}]))
        self.assertEqual('failed', self.conn.execute("SELECT state FROM work_item_runs WHERE run_id='r'").fetchone()[0])
        self.assertEqual(0, self.conn.execute('SELECT COUNT(*) FROM work_item_resource_leases').fetchone()[0])

    def test_manual_executor_fails_closed(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?", (self.a,))
        with self.assertRaisesRegex(ValueError, 'uncontrolled_manual'):
            self.apply(self.command(self.a, 'pause'))

    def test_api_reads_canonical_projection_and_refuses_unknown_executor(self):
        self.conn.commit()
        control = c3_api.Control('.', self.path, refresh=False)
        state = control.state()
        self.assertIn(self.a, [i['work_item_id'] for i in state['items']])
        with self.assertRaisesRegex(c3_api.ControlError, 'unsupported_executor'):
            control.executor_control([{'run_id': 'r', 'worker_ref': 'unknown'}], 'stop')

    def test_resume_failure_repauses_executor(self):
        self.conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?", (self.a,))
        self.conn.execute("INSERT INTO work_item_runs VALUES('r',?,'e',1,'native','running',100,'c3-run:r',NULL,'{}',1)", (self.a,))
        self.conn.commit()
        control = c3_api.Control('.', self.path, refresh=False)
        plan = control.preview(self.a, 'resume')
        with mock.patch.object(control, 'executor_control', return_value=[]) as effects, mock.patch.object(c3_api, 'submit_document', side_effect=RuntimeError('offline')):
            with self.assertRaisesRegex(RuntimeError, 'offline'):
                control.override({**plan, 'request_id': 'resume-test'})
        self.assertEqual(['resume', 'pause'], [c.args[1] for c in effects.call_args_list])


if __name__ == '__main__':
    unittest.main()
