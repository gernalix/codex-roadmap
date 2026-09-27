from contextlib import closing
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import c2_intake
import c2_issue_inbox
import c2_manual_order
import c2_scheduler
import c2_issue_capture
import c2_runtime
import c2_supervisor_authority
import roadmap_db
from test_c2_intake import C2IntakeTests


class IssueInboxTests(unittest.TestCase):
    def make_conn(self, root: Path):
        path = C2IntakeTests().make_cutover_db(root)
        conn = c2_intake._connect(path)
        c2_scheduler.install_schema(conn)
        return path, conn

    def test_capture_is_append_only_and_requires_no_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                first = c2_issue_inbox.capture(
                    conn, description="Same observation", observed_at_ms=1000
                )
                second = c2_issue_inbox.capture(
                    conn, description="Same observation", observed_at_ms=1001
                )
                self.assertNotEqual(first["issue_id"], second["issue_id"])
                self.assertEqual(2, conn.execute(
                    "SELECT COUNT(*) FROM issue_inbox"
                ).fetchone()[0])
            finally:
                conn.close()

    def test_pending_readback_uses_manual_order_then_observed_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                first = c2_issue_inbox.capture(
                    conn, description="First", observed_at_ms=1000
                )["issue_id"]
                second = c2_issue_inbox.capture(
                    conn, description="Second", observed_at_ms=2000
                )["issue_id"]
                third = c2_issue_inbox.capture(
                    conn, description="Third", observed_at_ms=3000
                )["issue_id"]
                c2_manual_order.set_manual_order(
                    conn, scope="inbox", ordered_ids=[third, first, second],
                    source="workflowy", source_modified_at="opaque-inbox"
                )
                rows = c2_issue_inbox.pending_issues(conn)
                self.assertEqual([third, first, second], [row["issue_id"] for row in rows])
                self.assertEqual([0, 1, 2], [row["manual_rank"] for row in rows])
                self.assertTrue(all(
                    row["manual_order_source"] == "workflowy"
                    and row["manual_order_source_modified_at"] == "opaque-inbox"
                    for row in rows
                ))
            finally:
                conn.close()

    def test_task_id_resolves_bound_chat_without_executor_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                item = c2_intake.add_work_item(
                    conn,
                    title="Semantic source",
                    objective="Do source task",
                    acceptance=["done"],
                    execution={
                        "activity": "semantic",
                        "project_url": "https://chatgpt.com/g/g-p-test/project",
                    },
                )
                run = c2_scheduler.schedule(conn, event_key="bind", now=10)[0]
                c2_scheduler.acknowledge(
                    conn,
                    run["run_id"],
                    worker_ref="c2-run:" + run["run_id"],
                    metadata=run["metadata"],
                    now=11,
                )
                c2_scheduler.bind_executor(
                    conn,
                    run["run_id"],
                    executor_ref="https://chatgpt.com/c/test-chat",
                    chat_url="https://chatgpt.com/c/test-chat",
                    now=12,
                )
                issue = c2_issue_inbox.capture(
                    conn,
                    description="Observed while working",
                    task_id=item["work_item_id"],
                    observed_at_ms=13000,
                )
                self.assertEqual(item["work_item_id"], issue["origin_work_item_id"])
                self.assertEqual(run["run_id"], issue["origin_run_id"])
                self.assertEqual("https://chatgpt.com/c/test-chat", issue["chat_url"])
                self.assertEqual("https://chatgpt.com/c/test-chat", issue["executor_ref"])
            finally:
                conn.close()

    def test_completed_match_cannot_be_discarded_and_reopens_as_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                fixed = c2_intake.add_work_item(
                    conn, title="Previously fixed", repo="repo", sort_order=7
                )
                conn.execute(
                    "UPDATE work_items SET status='completed' WHERE work_item_id=?",
                    (fixed["work_item_id"],),
                )
                issue = c2_issue_inbox.capture(
                    conn,
                    description="The fixed bug happened again",
                    task_id=fixed["work_item_id"],
                    observed_at_ms=2000,
                )
                with self.assertRaisesRegex(
                    c2_issue_inbox.IssueInboxError,
                    "requires_regression",
                ):
                    c2_issue_inbox.discard(
                        conn,
                        issue_id=issue["issue_id"],
                        matched_work_item_id=fixed["work_item_id"],
                        reason="already fixed",
                        triaged_by="test",
                    )

                result = c2_issue_inbox.promote(
                    conn,
                    issue_id=issue["issue_id"],
                    matched_work_item_id=fixed["work_item_id"],
                    reason="fresh reproduction",
                    triaged_by="test",
                )
                self.assertTrue(result["regression"])
                self.assertNotEqual(
                    fixed["work_item_id"], result["promoted_work_item_id"]
                )
                reopened = conn.execute(
                    "SELECT status,repo,sort_order FROM work_items WHERE work_item_id=?",
                    (result["promoted_work_item_id"],),
                ).fetchone()
                self.assertEqual(("pending", "repo", 7), tuple(reopened))
                relation = conn.execute(
                    """SELECT relation_type FROM work_item_relations
                       WHERE from_work_item_id=? AND to_work_item_id=?""",
                    (result["promoted_work_item_id"], fixed["work_item_id"]),
                ).fetchone()
                self.assertEqual("regression_of", relation[0])
                self.assertEqual(
                    "promoted",
                    conn.execute(
                        "SELECT state FROM issue_inbox WHERE issue_id=?",
                        (issue["issue_id"],),
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_active_duplicate_is_promoted_into_existing_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                active = c2_intake.add_work_item(conn, title="Existing active")
                issue = c2_issue_inbox.capture(
                    conn, description="Same active problem", observed_at_ms=3000
                )
                before = conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]
                result = c2_issue_inbox.promote(
                    conn,
                    issue_id=issue["issue_id"],
                    matched_work_item_id=active["work_item_id"],
                    reason="duplicate observation of relevant active work",
                    triaged_by="test",
                )
                after = conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]
                self.assertEqual(before, after)
                self.assertEqual(active["work_item_id"], result["promoted_work_item_id"])
                self.assertEqual(1, conn.execute(
                    """SELECT COUNT(*) FROM work_item_evidence
                       WHERE work_item_id=? AND evidence_kind='issue_inbox'""",
                    (active["work_item_id"],),
                ).fetchone()[0])
            finally:
                conn.close()

    def test_capture_is_unfenced_but_triage_requires_supervisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_capture_issue",
                        "arguments": {
                            "description": "Cheap capture",
                            "observed_at_ms": 4000,
                        },
                    },
                )
                issue_id = conn.execute(
                    "SELECT issue_id FROM issue_inbox"
                ).fetchone()[0]
                with self.assertRaisesRegex(Exception, "supervisor_authority_required"):
                    roadmap_db.apply_mutation(
                        conn,
                        {
                            "op": "c2_discard_issue",
                            "arguments": {
                                "issue_id": issue_id,
                                "reason": "irrelevant",
                                "triaged_by": "test",
                            },
                        },
                    )

                authority = {
                    "supervisor_id": "test-supervisor",
                    "fencing_token": 1,
                    "lease_expires_at": time.time() + 120,
                }
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_claim_supervisor",
                        "arguments": {"supervisor_authority": authority},
                    },
                )
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_discard_issue",
                        "arguments": {
                            "issue_id": issue_id,
                            "reason": "irrelevant",
                            "triaged_by": "test-supervisor",
                            "supervisor_authority": authority,
                        },
                    },
                )
                self.assertEqual(
                    "discarded",
                    conn.execute(
                        "SELECT state FROM issue_inbox WHERE issue_id=?",
                        (issue_id,),
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_capture_cli_uses_only_description_and_run_environment(self):
        submitted = []
        with patch.dict('os.environ', {'C2_TASK_ID': 'wi:known', 'C2_RUN_ID': 'run-known'}, clear=True), \
             patch('sys.argv', ['c2_issue_capture.py', 'Incidental failure']), \
             patch.object(c2_issue_capture, 'submit_document',
                          side_effect=lambda doc, **kw: submitted.append((doc, kw)) or {'status': 'queued'}):
            self.assertEqual(0, c2_issue_capture.main())
        args = submitted[0][0]['operations'][0]['arguments']
        self.assertEqual('Incidental failure', args['description'])
        self.assertEqual('wi:known', args['task_id'])
        self.assertEqual('run-known', args['run_id'])
        self.assertNotIn('repo', args)
        self.assertNotIn('code_location', args)

    def test_manual_start_receipt_resolves_executor_without_run_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(conn, title='Manual source')
                c2_scheduler.executor_started(conn, work_item_id=item['work_item_id'],
                    executor='codex', executor_ref='thread-manual',
                    chat_url='codex://threads/thread-manual', now=2)
                issue = c2_issue_inbox.capture(conn, description='Manual incidental',
                    task_id=item['work_item_id'])
                self.assertEqual('codex', issue['executor'])
                self.assertEqual('thread-manual', issue['executor_ref'])
                self.assertEqual('codex://threads/thread-manual', issue['chat_url'])
                self.assertIsNone(issue['origin_run_id'])
            finally:
                conn.close()

    def test_codex_binding_is_idempotent_and_conflicts_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(conn, title='Codex source')
                conn.execute('''INSERT INTO work_item_runs
                  (run_id,work_item_id,event_key,attempt,executor,state,lease_until,
                   worker_ref,checkpoint_commit,metadata_json,created_at)
                  VALUES(?,?,?,1,'codex','running',1000,NULL,NULL,'{}',1)''',
                  ('run-codex', item['work_item_id'], 'test'))
                issue = c2_issue_inbox.capture(conn, description='Found in thread', run_id='run-codex')
                self.assertIsNone(issue['chat_url'])
                first = c2_scheduler.bind_executor(conn, 'run-codex',
                    executor_ref='thread-123', chat_url='codex://threads/thread-123', now=2)
                self.assertEqual(first, c2_scheduler.bind_executor(conn, 'run-codex',
                    executor_ref='thread-123', chat_url='codex://threads/thread-123', now=3))
                self.assertEqual('codex://threads/thread-123', conn.execute(
                    'SELECT chat_url FROM issue_inbox WHERE issue_id=?', (issue['issue_id'],)).fetchone()[0])
                with self.assertRaisesRegex(c2_scheduler.SchedulingError, 'executor_binding_conflict'):
                    c2_scheduler.bind_executor(conn, 'run-codex', executor_ref='other',
                                               chat_url='codex://threads/other')
            finally:
                conn.close()

    def test_one_triage_and_new_batch_after_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                c2_issue_inbox.capture(conn, description='First')
                url = c2_runtime.C2_TRIAGE_PROJECT_URL
                first = c2_issue_inbox.ensure_triage(conn, project_url=url)
                self.assertEqual('created', first['state'])
                self.assertEqual(first['work_item_id'], c2_issue_inbox.ensure_triage(
                    conn, project_url=url)['work_item_id'])
                conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",
                             (first['work_item_id'],))
                second = c2_issue_inbox.ensure_triage(conn, project_url=url)
                self.assertEqual('created', second['state'])
                self.assertNotEqual(first['work_item_id'], second['work_item_id'])
                self.assertEqual('semantic', conn.execute(
                    'SELECT activity FROM work_item_execution_specs WHERE work_item_id=?',
                    (second['work_item_id'],)).fetchone()[0])
            finally:
                conn.close()

    def test_runtime_requests_atomic_triage_once_per_nonterminal_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                c2_issue_inbox.capture(conn, description='Needs triage')
                calls = []
                def submit(op, arguments, key):
                    calls.append((op, arguments, key))
                    if op == 'ensure_issue_triage':
                        c2_issue_inbox.ensure_triage(conn, **arguments)
                c2_runtime.advance(conn, submit=submit, launch=lambda _: None,
                    triage_project_url=c2_runtime.C2_TRIAGE_PROJECT_URL)
                self.assertEqual('ensure_issue_triage', calls[0][0])
                c2_runtime.advance(conn, submit=submit, launch=lambda _: None,
                    triage_project_url=c2_runtime.C2_TRIAGE_PROJECT_URL)
                self.assertEqual(1, sum(op == 'ensure_issue_triage' for op, _, _ in calls))
                first_key = calls[0][2]
                triage_id = conn.execute("""SELECT w.work_item_id FROM work_items w
                    JOIN work_item_tags t USING(work_item_id)
                    WHERE t.tag='c2:issue-triage'""").fetchone()[0]
                conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (triage_id,))
                c2_runtime.advance(conn, submit=submit, launch=lambda _: None,
                    triage_project_url=c2_runtime.C2_TRIAGE_PROJECT_URL)
                triage_calls = [entry for entry in calls if entry[0] == 'ensure_issue_triage']
                self.assertEqual(2, len(triage_calls))
                self.assertNotEqual(first_key, triage_calls[1][2])
            finally:
                conn.close()

    def test_triage_cannot_finish_while_pending_rows_remain(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                c2_issue_inbox.capture(conn, description='Unresolved')
                item = c2_issue_inbox.ensure_triage(
                    conn, project_url=c2_runtime.C2_TRIAGE_PROJECT_URL)
                run = c2_scheduler.schedule(conn, event_key='triage-schedule', now=10)[0]
                c2_scheduler.acknowledge(conn, run['run_id'], worker_ref='c2-run:'+run['run_id'],
                    metadata=run['metadata'], now=11)
                with self.assertRaisesRegex(c2_scheduler.SchedulingError, 'issue_triage_pending_rows'):
                    c2_scheduler.finish_browser_work_item(conn, item['work_item_id'],
                        evidence=['claimed complete'])
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
