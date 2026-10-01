from contextlib import closing
from pathlib import Path
import tempfile
import unittest
import time

import c2_intake
import c2_issue_inbox as inbox
import c3_inbox_maintenance as job
from test_c2_intake import C2IntakeTests
from c3_local_writer import LocalWriter


class TechnicalInboxTests(unittest.TestCase):
    def test_exact_decision_reuse_is_atomic_bounded_and_nonrecursive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as db:
                db.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(db, title='Known failure')['work_item_id']
                original = inbox.capture(db, description='Exact failure', observed_at_ms=100)['issue_id']
                inbox.promote(db, issue_id=original, matched_work_item_id=item,
                              reason='Verified target', triaged_by='operator')
                duplicates = [inbox.capture(db, description='Exact failure', observed_at_ms=101+n)['issue_id']
                              for n in range(30)]
                ambiguous = inbox.capture(db, description='Different failure', observed_at_ms=200)['issue_id']
                db.commit()
                items_before = db.execute('SELECT COUNT(*) FROM work_items').fetchone()[0]
                current = job.plan(db)
                self.assertEqual(25, len(current['decisions']))
                db.execute('BEGIN IMMEDIATE')
                result = job.apply(db, expected_digest=current['digest'])
                self.assertEqual(25, result['changed'])
                db.rollback()
                self.assertEqual('pending', db.execute('SELECT state FROM issue_inbox WHERE issue_id=?', (duplicates[0],)).fetchone()[0])
                db.execute('BEGIN IMMEDIATE')
                job.apply(db, expected_digest=current['digest'])
                db.commit()
                self.assertEqual(items_before, db.execute('SELECT COUNT(*) FROM work_items').fetchone()[0])
                self.assertEqual(0, db.execute('SELECT COUNT(*) FROM work_item_runs').fetchone()[0])
                self.assertEqual('pending', db.execute('SELECT state FROM issue_inbox WHERE issue_id=?', (ambiguous,)).fetchone()[0])
                self.assertEqual(5, len(job.plan(db)['decisions']))

    def test_ambiguous_and_terminal_targets_stay_pending_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as db:
                db.execute('BEGIN IMMEDIATE')
                for n in range(2):
                    item = c2_intake.add_work_item(db, title='Distinct target ' + str(n))['work_item_id']
                    prior = inbox.capture(db, description='Ambiguous shared observation', observed_at_ms=100+n)['issue_id']
                    inbox.promote(db, issue_id=prior, matched_work_item_id=item, reason='Explicit decision', triaged_by='operator')
                inbox.capture(db, description='Ambiguous shared observation', observed_at_ms=200)
                terminal = c2_intake.add_work_item(db, title='Already fixed')['work_item_id']
                prior = inbox.capture(db, description='Possible regression', observed_at_ms=100)['issue_id']
                inbox.promote(db, issue_id=prior, matched_work_item_id=terminal, reason='Explicit decision', triaged_by='operator')
                db.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (terminal,))
                inbox.capture(db, description='Possible regression', observed_at_ms=200)
                inbox.capture(db, description='Needs a decision')
                db.commit()
                before = db.total_changes
                submitted = []
                self.assertEqual({'changed': 0, 'pending': 3}, job.run(db, lambda *args: submitted.append(args)))
                self.assertEqual(submitted, [])
                self.assertEqual(before, db.total_changes)
                with self.assertRaisesRegex(ValueError, 'precondition_changed'):
                    db.execute('BEGIN IMMEDIATE')
                    job.apply(db, expected_digest='stale')
                db.rollback()
                with self.assertRaisesRegex(ValueError, 'limit_invalid'):
                    job.plan(db, batch_limit=26)

    def test_single_writer_requires_fence_and_replays_one_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = C2IntakeTests().make_cutover_db(root)
            with closing(c2_intake._connect(path)) as db:
                db.execute('BEGIN IMMEDIATE')
                target = c2_intake.add_work_item(db, title='Known')['work_item_id']
                original = inbox.capture(db, description='Same', observed_at_ms=100)['issue_id']
                inbox.promote(db, issue_id=original, matched_work_item_id=target, reason='Verified', triaged_by='operator')
                duplicate = inbox.capture(db, description='Same', observed_at_ms=200)['issue_id']
                db.commit()
            writer = LocalWriter(path.parent)
            try:
                digest = job.plan(writer.conn)['digest']
                arguments = {'expected_digest': digest}
                document = {'schema': 'codex-roadmap.mutation.v1', 'actor': 'c2-runtime',
                            'operations': [{'op': 'c2_maintain_issue_inbox', 'arguments': arguments}]}
                with self.assertRaisesRegex(Exception, 'supervisor_authority_required'):
                    writer.apply(document, 'unfenced')
                authority = {'supervisor_id': 'test', 'fencing_token': 1, 'lease_expires_at': time.time()+120}
                writer.apply({'schema': document['schema'], 'actor': 'test', 'operations':
                    [{'op': 'c2_claim_supervisor', 'arguments': {'supervisor_authority': authority}}]}, 'claim')
                arguments['supervisor_authority'] = authority
                writer.apply(document, 'bounded')
                self.assertTrue(writer.apply(document, 'bounded')['idempotent'])
                self.assertEqual('promoted', writer.conn.execute('SELECT state FROM issue_inbox WHERE issue_id=?', (duplicate,)).fetchone()[0])
                self.assertEqual(1, writer.conn.execute('SELECT COUNT(*) FROM issue_reconciliation_batches').fetchone()[0])
                self.assertEqual(0, writer.conn.execute('SELECT COUNT(*) FROM work_item_runs').fetchone()[0])
            finally:
                writer.close()
