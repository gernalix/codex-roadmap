import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c3_retire_pre_migration as retirement
import test_c2_intake
from c3_local_writer import LocalWriter


class RetirementTests(unittest.TestCase):
    def test_retirement_clears_ownership_preserves_unfinished_work_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = test_c2_intake.C2IntakeTests().make_cutover_db(Path(directory))
            writer = LocalWriter(path.parent)
            conn = writer.conn
            conn.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
            wid = conn.execute("SELECT work_item_id FROM work_items WHERE prompt_id='123456'").fetchone()[0]
            conn.execute('INSERT INTO work_item_runs VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                         ('old', wid, 'old-event', 1, 'chatgpt', 'running', 9999999999, 'legacy-worker', retirement.HISTORICAL_M1, '{}', 1))
            conn.execute('INSERT INTO work_item_resource_leases VALUES(?,?)', ('legacy-resource', 'old'))
            conn.commit()
            try:
                result = retirement.retire(conn)
                self.assertEqual(result['decisions'][0]['status'], 'pending')
                self.assertEqual(tuple(conn.execute('SELECT state,lease_until,worker_ref,checkpoint_commit FROM work_item_runs').fetchone()),
                                 ('failed', 0, None, None))
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM work_item_resource_leases').fetchone()[0], 0)
                self.assertEqual(retirement.retire(conn), {'status': 'already_retired'})
                document = {'schema': 'codex-roadmap.mutation.v1', 'actor': 'c2-supervisor-resume',
                            'operations': [{'op': 'c2_claim_supervisor', 'arguments': {}}]}
                with self.assertRaisesRegex(ValueError, 'pre_migration_component_retired'):
                    writer.apply(document, 'must-not-reactivate')
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM mutation_receipts').fetchone()[0], 0)
            finally:
                writer.close()
