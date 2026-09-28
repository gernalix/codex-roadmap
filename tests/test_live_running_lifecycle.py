from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db
import roadmap_live_watch as live


class LiveRunningLifecycleTests(unittest.TestCase):
    def test_live_scanner_detects_prompt_start_and_terminal_event(self) -> None:
        user = {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "PROMPT_ID=123456\nDo the task"}],
            },
        }
        active, observed, terminal = live._scan_bytes(
            (json.dumps(user) + "\n").encode("utf-8"),
            None,
        )
        self.assertEqual("123456", active)
        self.assertEqual({"123456"}, observed)
        self.assertFalse(terminal)

        done = {
            "type": "event_msg",
            "payload": {"type": "task_complete", "turn_id": "turn-1"},
        }
        active, observed, terminal = live._scan_bytes(
            (json.dumps(done) + "\n").encode("utf-8"),
            active,
        )
        self.assertIsNone(active)
        self.assertEqual(set(), observed)
        self.assertTrue(terminal)

    def test_pass_confirmation_unblocks_all_children(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="parent",
                title="Parent",
                current_path="prompts/parent.md",
                queue_position=1,
            )
            for prompt_id, slug, pos in (
                ("234567", "child-one", 2),
                ("345678", "child-two", 3),
            ):
                db.register_prompt(
                    conn,
                    prompt_id=prompt_id,
                    slug=slug,
                    title=slug,
                    current_path=f"prompts/{slug}.md",
                    queue_position=pos,
                )
                db.add_dependency(conn, prompt_id, "123456")

            db.set_status(conn, "123456", "running", actor="codex", note="launch")
            db.request_terminal(conn, "123456", "completed", actor="codex")
            conn.commit()

            runnable_after_request = {
                row["prompt_id"]
                for row in conn.execute("SELECT prompt_id FROM v_runnable_prompts")
            }
            self.assertIn("234567", runnable_after_request)
            self.assertIn("345678", runnable_after_request)
            self.assertEqual("completed", db.prompt_row(conn, "123456")["status"])

            db.record_execution(
                conn,
                "123456",
                cycle_key="cycle-pass",
                started_at="2026-09-19T00:00:00Z",
                ended_at="2026-09-19T00:01:00Z",
                outcome="PASS",
                source="codex-usage",
                actor="codex-usage",
                allow_running_terminal=True,
            )
            conn.commit()

            runnable = [
                row["prompt_id"]
                for row in conn.execute(
                    "SELECT prompt_id FROM v_runnable_prompts ORDER BY queue_position"
                )
            ]
            self.assertEqual(["234567", "345678"], runnable)
            self.assertEqual("completed", db.prompt_row(conn, "123456")["status"])
            conn.close()

    def test_legacy_running_terminal_request_is_self_healed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="legacy",
                title="Legacy",
                current_path="prompts/legacy.md",
            )
            db.set_status(conn, "123456", "running", actor="codex", note="launch")
            conn.execute(
                """INSERT INTO terminal_requests(
                     prompt_id,requested_status,actor,note,requested_at
                   ) VALUES(?,?,?,?,?)""",
                ("123456", "blocked", "codex", "legacy terminal", db.now_utc()),
            )
            conn.commit()

            self.assertEqual(1, db.reconcile_terminal_requests(conn))
            self.assertEqual("blocked", db.prompt_row(conn, "123456")["status"])
            self.assertEqual(0, db.reconcile_terminal_requests(conn))
            conn.close()

    def test_historical_terminal_request_does_not_replay_after_reactivation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(conn, prompt_id="123456", slug="old", title="Old",
                               current_path="prompts/old.md")
            db.set_status(conn, "123456", "running", actor="codex")
            db.request_terminal(conn, "123456", "blocked", actor="codex")
            request = conn.execute("SELECT running_history_id FROM terminal_requests "
                                   "WHERE prompt_id='123456'").fetchone()[0]
            self.assertIsNotNone(request)
            # The explicit blocked reconciliation preserves the terminal row.
            conn.execute("UPDATE prompts SET status='pending' WHERE prompt_id='123456'")
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','blocked','waiting',?,'test',NULL)""", (db.now_utc(),))
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','waiting','pending',?,'test',NULL)""", (db.now_utc(),))
            db.set_status(conn, "123456", "running", actor="codex")
            self.assertEqual(0, db.reconcile_terminal_requests(conn))
            self.assertEqual("running", db.prompt_row(conn, "123456")["status"])
            self.assertEqual("blocked", conn.execute(
                "SELECT requested_status FROM terminal_requests WHERE prompt_id='123456'"
            ).fetchone()[0])
            conn.close()

    def test_legacy_terminal_request_from_old_run_does_not_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(conn, prompt_id="123456", slug="old", title="Old",
                               current_path="prompts/old.md")
            db.set_status(conn, "123456", "running", actor="codex")
            db.request_terminal(conn, "123456", "blocked", actor="codex")
            conn.execute("UPDATE terminal_requests SET running_history_id=NULL "
                         "WHERE prompt_id='123456'")
            conn.execute("UPDATE prompts SET status='pending' WHERE prompt_id='123456'")
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','blocked','waiting',?,'test',NULL)""", (db.now_utc(),))
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','waiting','pending',?,'test',NULL)""", (db.now_utc(),))
            db.set_status(conn, "123456", "running", actor="codex")
            self.assertEqual(0, db.reconcile_terminal_requests(conn))
            self.assertEqual("running", db.prompt_row(conn, "123456")["status"])
            conn.close()

    def test_later_run_replaces_archived_terminal_request_by_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(conn, prompt_id="123456", slug="later", title="Later",
                               current_path="prompts/later.md")
            db.set_status(conn, "123456", "running", actor="codex", note="first run")
            first_run = conn.execute(
                "SELECT MAX(history_id) FROM status_history WHERE prompt_id='123456' AND new_status='running'"
            ).fetchone()[0]
            db.request_terminal(conn, "123456", "blocked", expected_running_history_id=first_run)

            conn.execute("UPDATE prompts SET status='pending' WHERE prompt_id='123456'")
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','blocked','pending',?,'test','reactivate')""", (db.now_utc(),))
            db.set_status(conn, "123456", "running", actor="codex", note="second run")
            second_run = conn.execute(
                "SELECT MAX(history_id) FROM status_history WHERE prompt_id='123456' AND new_status='running'"
            ).fetchone()[0]
            self.assertNotEqual(first_run, second_run)

            with self.assertRaisesRegex(db.RoadmapDBError, "terminal_request_generation_conflict"):
                db.request_terminal(conn, "123456", "completed",
                                    expected_running_history_id=first_run)
            self.assertEqual(0, conn.execute(
                "SELECT COUNT(*) FROM terminal_request_history"
            ).fetchone()[0])

            # Same target status is valid for a later generation and remains
            # idempotent for retries within that generation.
            db.request_terminal(conn, "123456", "blocked",
                                expected_running_history_id=second_run)
            db.request_terminal(conn, "123456", "blocked",
                                expected_running_history_id=second_run)

            conn.execute("UPDATE prompts SET status='pending' WHERE prompt_id='123456'")
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES('123456','blocked','pending',?,'test','reactivate again')""", (db.now_utc(),))
            db.set_status(conn, "123456", "running", actor="codex", note="third run")
            third_run = conn.execute(
                "SELECT MAX(history_id) FROM status_history WHERE prompt_id='123456' AND new_status='running'"
            ).fetchone()[0]
            # A different target status is also valid after a new run starts.
            db.request_terminal(conn, "123456", "completed",
                                expected_running_history_id=third_run)
            with self.assertRaisesRegex(db.RoadmapDBError, "terminal_request_conflict"):
                db.request_terminal(conn, "123456", "failed",
                                    expected_running_history_id=third_run)

            active = conn.execute("SELECT requested_status,running_history_id FROM terminal_requests "
                                  "WHERE prompt_id='123456'").fetchone()
            self.assertEqual(("completed", third_run), tuple(active))
            archived_rows = conn.execute(
                "SELECT requested_status,running_history_id FROM terminal_request_history "
                "WHERE prompt_id='123456' ORDER BY request_history_id"
            ).fetchall()
            self.assertEqual([("blocked", first_run), ("blocked", second_run)],
                             [tuple(row) for row in archived_rows])
            self.assertEqual(3, conn.execute(
                "SELECT COUNT(*) FROM audit_events WHERE prompt_id='123456' AND event_type='terminal_requested'"
            ).fetchone()[0])
            self.assertEqual("completed", db.prompt_row(conn, "123456")["status"])
            conn.close()


if __name__ == "__main__":
    unittest.main()
