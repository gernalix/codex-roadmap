from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c2_supervisor_lease import LeaseError, acquire, connect, record_activity, snapshot, update
from c2_supervisor_watchdog import watch_once


class SupervisorLeaseTests(unittest.TestCase):
    def test_real_activity_renews_lease_and_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'lease.sqlite3') as db:
                acquire(db,owner='runtime',pointer='/tmp/pointer',
                        supervisor_id='runtime',now=100,ttl=180)
                row=record_activity(db,supervisor_id='runtime',token=1,
                                    operation='writer:schedule',now=150,ttl=180)
                self.assertEqual(330,row['lease_expires_at'])
                self.assertEqual(150,row['last_heartbeat'])
                self.assertEqual(150,row['last_progress_at'])
                self.assertEqual(1,row['progress_counter'])
                self.assertEqual('writer:schedule',row['current_action'])

    def test_short_activity_and_heartbeat_never_shorten_long_live_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'lease.sqlite3') as db:
                acquire(db, owner='runtime', pointer='/tmp/pointer',
                        supervisor_id='runtime', now=100, ttl=1800)
                activity = record_activity(
                    db, supervisor_id='runtime', token=1,
                    operation='control:clear_manual_order', now=150,
                )
                self.assertEqual(1900, activity['lease_expires_at'])
                heartbeat = update(
                    db, supervisor_id='runtime', token=1, now=200, ttl=180,
                )
                self.assertEqual(1900, heartbeat['lease_expires_at'])
                with self.assertRaisesRegex(
                    LeaseError, 'stale_or_expired_supervisor'
                ):
                    update(
                        db, supervisor_id='runtime', token=1,
                        now=1900, ttl=1800,
                    )

    def test_watchdog_encodes_bounded_stall_thresholds(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'lease.sqlite3') as db:
                acquire(db,owner='runtime',pointer='/tmp/pointer',
                        supervisor_id='runtime',now=0,ttl=1000)
                self.assertEqual('suspected_stall',watch_once(db,now=40)['state'])
                self.assertEqual('final_verification',watch_once(db,now=90)['state'])
                result=watch_once(db,now=180)
                self.assertEqual('recovery_required',result['state'])
                self.assertEqual('progress_stalled',result['reason'])

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
                self.assertEqual('recovery_required', watch_once(db, now=113)['state'])
                self.assertEqual('recovery_required', watch_once(db, now=114)['state'])
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
