import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_intake
import c3_retire_workflowy
import test_c2_intake


class RetirementTests(unittest.TestCase):
    def test_removes_legacy_order_preserves_canonical_items_and_replays(self):
        with tempfile.TemporaryDirectory() as directory:
            path = test_c2_intake.C2IntakeTests().make_cutover_db(Path(directory))
            conn = c2_intake._connect(path)
            try:
                conn.execute('CREATE TABLE manual_order_overrides(entity_id TEXT,rank INTEGER)')
                conn.execute("INSERT INTO manual_order_overrides VALUES('historical',0)")
                before = conn.execute('SELECT COUNT(*) FROM work_items').fetchone()[0]
                conn.commit()
                self.assertEqual(c3_retire_workflowy.retire(conn)['historical_order_rows'], 1)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM v_work_item_summary').fetchone()[0], before)
                self.assertIsNone(conn.execute("SELECT 1 FROM sqlite_master WHERE name='manual_order_overrides'").fetchone())
                self.assertEqual(c3_retire_workflowy.retire(conn), {'status': 'already_retired'})
            finally:
                conn.close()
