from pathlib import Path
import sqlite3
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_mutations
import c2_supervisor_authority as authority


class CanonicalFencingTests(unittest.TestCase):
    def test_queued_old_scheduler_request_rejected_after_takeover(self):
        db = sqlite3.connect(':memory:')
        db.row_factory = sqlite3.Row
        db.execute('CREATE VIEW prompts AS SELECT 1 AS prompt_id')
        db.execute('CREATE TABLE work_items(work_item_id TEXT PRIMARY KEY,status TEXT)')
        authority.install_schema(db)
        now = time.time()
        old = {'supervisor_id': 'old', 'fencing_token': 1,
               'lease_expires_at': now + 120}
        new = {'supervisor_id': 'new', 'fencing_token': 2,
               'lease_expires_at': now + 240}
        authority.claim(db, old, now=now)
        with patch.object(c2_mutations.c2_scheduler, 'schedule', return_value='scheduled') as schedule:
            mutation = {'op': 'c2_schedule', 'arguments': {
                'event_key': 'first', 'supervisor_authority': old}}
            self.assertEqual(c2_mutations.apply(db, mutation), 'scheduled')
            authority.retire(db, old, now=now + 1)
            authority.claim(db, new, now=now + 2)
            with self.assertRaisesRegex(authority.AuthorityError, 'stale_or_expired_supervisor'):
                c2_mutations.apply(db, mutation)
            with self.assertRaisesRegex(authority.AuthorityError, 'supervisor_authority_required'):
                c2_mutations.apply(db, {'op': 'c2_schedule', 'arguments': {'event_key': 'missing'}})
            self.assertEqual(schedule.call_count, 1)
        db.close()


if __name__ == '__main__':
    unittest.main()
