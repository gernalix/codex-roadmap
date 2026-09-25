from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db
import work_items_migration as migration
import work_items_state_import as state_import


class WorkItemsStateImportTests(unittest.TestCase):
    def make_migrated_repo(self, root: Path) -> tuple[Path, Path]:
        repo = root / "repo"
        repo.mkdir()
        conn = db.connect(repo)
        db.register_prompt(
            conn,
            prompt_id="175908",
            slug="c2",
            title="Checklist 2.0",
            current_path="prompts/c2.md",
            prompt_type="Goal",
            project_id="51",
            project_name="codex-roadmap",
            repo="gernalix/codex-roadmap",
            queue_position=1,
        )
        db.set_status(conn, "175908", "running", actor="codex", note="launch")
        conn.commit()
        conn.close()
        migration.migrate_database(repo / "roadmap.sqlite")
        state_root = repo / "operations/task-state"
        state_root.mkdir(parents=True)
        return repo / "roadmap.sqlite", state_root

    def write_prompt_state(self, state_root: Path, *, all_done: bool = False) -> Path:
        second = "x" if all_done else " "
        remaining = "" if all_done else "- Next thing"
        current = "Everything verified." if all_done else "Doing next thing."
        path = state_root / "175908.md"
        path.write_text(
            f"""# Operational task state — 175908

PROMPT_ID: 175908

## Objective
Build one tree.

## Plan / checklist
### Phase A
- [x] Done thing
- [{second}] Next thing

## Current step
{current}

## Completed
- Done thing

## Remaining
{remaining}

## Blockers
None.

## Evidence
- commit abc

## Next action
Run next.
""",
            encoding="utf-8",
        )
        return path

    def test_prompt_checkpoint_import_preserves_running_status_and_builds_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path, state_root = self.make_migrated_repo(Path(tmp))
            self.write_prompt_state(state_root)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            result = state_import.import_state_tree(
                conn, state_root, source_commit="abc123"
            )
            conn.commit()

            self.assertEqual(1, result["imported"])
            root = conn.execute(
                "SELECT * FROM work_items WHERE prompt_id='175908'"
            ).fetchone()
            self.assertEqual("running", root["status"])
            self.assertEqual("Doing next thing.", root["current_action"])
            self.assertEqual("Run next.", root["next_action"])
            self.assertIsNone(root["blocker"])

            phase = conn.execute(
                "SELECT * FROM work_items WHERE parent_id=? AND kind='phase'",
                (root["work_item_id"],),
            ).fetchone()
            self.assertEqual("running", phase["status"])
            steps = conn.execute(
                "SELECT status,title FROM work_items WHERE parent_id=? ORDER BY sort_order",
                (phase["work_item_id"],),
            ).fetchall()
            self.assertEqual(
                [("completed", "Done thing"), ("pending", "Next thing")],
                [(row["status"], row["title"]) for row in steps],
            )
            progress = conn.execute(
                "SELECT * FROM v_work_item_progress WHERE work_item_id=?",
                (root["work_item_id"],),
            ).fetchone()
            self.assertEqual(2, progress["total_actionable"])
            self.assertEqual(1, progress["completed_actionable"])
            self.assertEqual(50.0, progress["progress_percent"])
            self.assertEqual(
                1,
                conn.execute("SELECT COUNT(*) FROM work_item_checkpoints").fetchone()[0],
            )
            self.assertEqual(
                2,
                conn.execute("SELECT COUNT(*) FROM work_item_evidence").fetchone()[0],
            )
            conn.close()

    def test_same_checkpoint_hash_is_idempotent_and_changed_checkbox_updates_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path, state_root = self.make_migrated_repo(Path(tmp))
            self.write_prompt_state(state_root)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")

            first = state_import.import_state_tree(conn, state_root, source_commit="a")
            conn.commit()
            work_item_count = conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]
            second = state_import.import_state_tree(conn, state_root, source_commit="a")
            conn.commit()
            self.assertEqual(1, first["imported"])
            self.assertEqual(1, second["idempotent"])
            self.assertEqual(
                work_item_count,
                conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0],
            )
            self.assertEqual(
                1,
                conn.execute("SELECT COUNT(*) FROM work_item_checkpoints").fetchone()[0],
            )

            self.write_prompt_state(state_root, all_done=True)
            third = state_import.import_state_tree(conn, state_root, source_commit="b")
            conn.commit()
            self.assertEqual(1, third["imported"])
            root_id = conn.execute(
                "SELECT work_item_id FROM work_items WHERE prompt_id='175908'"
            ).fetchone()[0]
            statuses = [
                row[0]
                for row in conn.execute(
                    """SELECT status FROM work_items
                       WHERE source_kind='task_state' AND kind='step'
                         AND work_item_id IN (
                           SELECT child.work_item_id
                           FROM work_items phase
                           JOIN work_items child ON child.parent_id=phase.work_item_id
                           WHERE phase.parent_id=?
                         )
                       ORDER BY title""",
                    (root_id,),
                )
            ]
            self.assertEqual(["completed", "completed"], statuses)
            self.assertEqual(
                2,
                conn.execute("SELECT COUNT(*) FROM work_item_checkpoints").fetchone()[0],
            )
            progress = conn.execute(
                "SELECT progress_percent FROM v_work_item_progress WHERE work_item_id=?",
                (root_id,),
            ).fetchone()[0]
            self.assertEqual(100.0, progress)
            conn.close()

    def test_task_id_state_creates_standalone_blocked_work_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path, state_root = self.make_migrated_repo(root)
            path = state_root / "CHATGPT-TEST.md"
            path.write_text(
                """# Standalone task

TASK_ID: CHATGPT-TEST

## Objective
Do one thing.

## Plan / checklist
- [ ] Finish it

## Current step
Investigating.

## Remaining
- Finish it

## Blockers
Need human login.

## Evidence
- observed failure

## Next action
Wait for login.
""",
                encoding="utf-8",
            )
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            result = state_import.import_state_tree(conn, state_root, source_commit="x")
            conn.commit()
            self.assertEqual(1, result["imported"])
            item = conn.execute(
                "SELECT * FROM work_items WHERE task_id='CHATGPT-TEST'"
            ).fetchone()
            self.assertEqual("blocked", item["status"])
            self.assertEqual("Investigating.", item["current_action"])
            self.assertEqual("Wait for login.", item["next_action"])
            self.assertIn("Need human login.", item["blocker"])
            self.assertGreaterEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM work_items WHERE parent_id=?",
                    (item["work_item_id"],),
                ).fetchone()[0],
                2,
            )
            conn.close()


if __name__ == "__main__":
    unittest.main()
