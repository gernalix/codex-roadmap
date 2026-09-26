from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c2_supervisor_lease import LeaseError, acquire, connect, snapshot, update
from c2_supervisor_watchdog import watch_once


class SupervisorLeaseTests(unittest.TestCase):
    def test_successor_fences_expired_primary_without_duplicate_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'lease.sqlite3') as db:
                first = acquire(db, owner='first', pointer='/tmp/pointer',
                                supervisor_id='first', now=100, ttl=10)
                self.assertEqual(first['fencing_token'], 1)
                heartbeat = update(db, supervisor_id='first', token=1, now=101, ttl=10)
                self.assertEqual(heartbeat['last_progress_at'], 100)
                progress = update(db, supervisor_id='first', token=1, now=102,
                                  ttl=10, progress=True)
                self.assertEqual(progress['last_progress_at'], 102)
                with self.assertRaisesRegex(LeaseError, 'primary_lease_held'):
                    acquire(db, owner='second', pointer='/tmp/pointer', now=103)
                dispatched = []
                def prepare(row):
                    dispatched.append(row['supervisor_id'])
                    return {'state': 'prepared', 'session_id': 'https://chatgpt.com/c/test'}
                watch_once(db, launch=prepare, now=113)
                watch_once(db, launch=prepare, now=114)
                self.assertEqual(dispatched, ['first'])
                self.assertEqual(snapshot(db)['state'], 'retired')
                with self.assertRaisesRegex(LeaseError, 'supervisor_id_reused'):
                    acquire(db, owner='second', pointer='/tmp/pointer',
                            supervisor_id='first', now=115)
                successor = acquire(db, owner='second', pointer='/tmp/pointer',
                                    supervisor_id='second', now=115)
                self.assertEqual(successor['fencing_token'], 2)
                with self.assertRaisesRegex(LeaseError, 'stale_or_expired_supervisor'):
                    update(db, supervisor_id='first', token=1, now=116)
                self.assertEqual(snapshot(db)['supervisor_id'], 'second')


if __name__ == '__main__':
    unittest.main()
