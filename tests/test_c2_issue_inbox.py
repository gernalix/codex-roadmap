from contextlib import closing
from pathlib import Path
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import c2_intake
import c2_issue_inbox
import c2_scheduler
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


if __name__ == "__main__":
    unittest.main()
