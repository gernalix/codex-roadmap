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


if __name__ == "__main__":
    unittest.main()
