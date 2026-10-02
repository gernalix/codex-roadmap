from contextlib import closing
import tempfile
import unittest
from pathlib import Path

import roadmap_db as db
from c3_compact_audit import compact, preserved_fingerprint


class AuditCompactionTests(unittest.TestCase):
    def test_repeated_expected_noops_never_append_audit(self):
        with tempfile.TemporaryDirectory() as tmp, closing(db.connect(Path(tmp))) as conn:
            db.register_prompt(conn, prompt_id='123456', slug='old', title='old', current_path='prompts/old.md')
            conn.execute("INSERT INTO terminal_requests(prompt_id,requested_status,actor,requested_at) VALUES('123456','blocked','test',?)", (db.now_utc(),))
            conn.commit()
            before = conn.total_changes
            for _ in range(100):
                self.assertEqual(0, db.reconcile_terminal_requests(conn))
            self.assertEqual(before, conn.total_changes)

    def test_compaction_preserves_real_events_state_and_aggregates_history(self):
        with tempfile.TemporaryDirectory() as tmp, closing(db.connect(Path(tmp))) as conn:
            db.register_prompt(conn, prompt_id='123456', slug='old', title='old', current_path='prompts/old.md')
            for _ in range(10):
                conn.execute("INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES('123456','terminal_reconcile_skipped','2026','test','{\"current_status\":\"pending\",\"requested_status\":\"blocked\"}')")
            conn.execute("INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES('123456','terminal_outcome_mismatch','2026','test','{}')")
            conn.commit()
            before = preserved_fingerprint(conn)
            conn.execute('BEGIN IMMEDIATE')
            self.assertEqual(10, compact(conn)['removed'])
            self.assertEqual(before, preserved_fingerprint(conn))
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM audit_events WHERE event_type='terminal_outcome_mismatch'").fetchone()[0])
            self.assertEqual(0, compact(conn)['removed'])
            conn.commit()
