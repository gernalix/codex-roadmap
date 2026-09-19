from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db


class WorkflowyHumanOutcomeTests(unittest.TestCase):
    def test_pass_closes_running_and_unblocks_dependents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="parent",
                title="Parent",
                current_path="prompts/parent.md",
            )
            db.register_prompt(
                conn,
                prompt_id="654321",
                slug="child",
                title="Child",
                current_path="prompts/child.md",
            )
            db.add_dependency(conn, "654321", "123456")
            db.set_status(
                conn,
                "123456",
                "running",
                actor="workflowy",
                note="explicit running",
            )
            db.apply_mutation(
                conn,
                {
                    "op": "human_execution",
                    "prompt_id": "123456",
                    "outcome": "PASS",
                    "actor": "workflowy",
                    "source": "workflowy-human",
                    "cycle_key": "workflowy:123456:node:pass",
                    "ended_at": "2026-09-19T01:00:00Z",
                },
            )
            conn.commit()

            self.assertEqual(
                "completed",
                db.prompt_row(conn, "123456")["status"],
            )
            self.assertEqual(
                "654321",
                db.next_runnable(conn)["prompt_id"],
            )
            execution = conn.execute(
                "SELECT outcome,source FROM executions WHERE prompt_id='123456'"
            ).fetchone()
            self.assertEqual(("PASS", "workflowy-human"), tuple(execution))
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM audit_events "
                    "WHERE event_type='human_outcome_confirmed'"
                ).fetchone()[0],
            )
            conn.close()

    def test_fail_keeps_dependents_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="parent",
                title="Parent",
                current_path="prompts/parent.md",
            )
            db.register_prompt(
                conn,
                prompt_id="654321",
                slug="child",
                title="Child",
                current_path="prompts/child.md",
            )
            db.add_dependency(conn, "654321", "123456")
            db.set_status(conn, "123456", "running", actor="workflowy")
            db.apply_mutation(
                conn,
                {
                    "op": "human_execution",
                    "prompt_id": "123456",
                    "outcome": "FAIL",
                    "actor": "workflowy",
                    "cycle_key": "workflowy:123456:node:fail",
                },
            )
            conn.commit()
            self.assertEqual("failed", db.prompt_row(conn, "123456")["status"])
            self.assertIsNone(db.next_runnable(conn))
            conn.close()

    def test_human_result_overrides_pending_terminal_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
            )
            db.set_status(conn, "123456", "running", actor="codex")
            db.request_terminal(
                conn,
                "123456",
                "failed",
                actor="codex",
                note="automatic report",
            )
            db.apply_mutation(
                conn,
                {
                    "op": "human_execution",
                    "prompt_id": "123456",
                    "outcome": "PASS",
                    "actor": "workflowy",
                    "cycle_key": "workflowy:123456:node:pass",
                },
            )
            conn.commit()
            self.assertEqual("completed", db.prompt_row(conn, "123456")["status"])
            self.assertEqual(
                0,
                conn.execute(
                    "SELECT COUNT(*) FROM terminal_requests WHERE prompt_id='123456'"
                ).fetchone()[0],
            )
            conn.close()


if __name__ == "__main__":
    unittest.main()
