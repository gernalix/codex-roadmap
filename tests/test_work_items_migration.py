from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db
import work_items_migration as migration


class WorkItemsMigrationTests(unittest.TestCase):
    def make_v1_repo(self, root: Path) -> Path:
        conn = db.connect(root)
        db.register_prompt(
            conn,
            prompt_id="111111",
            slug="goal",
            title="Goal",
            current_path="prompts/goal.md",
            prompt_type="Goal",
            project_id="51",
            project_name="codex-roadmap",
            repo="gernalix/codex-roadmap",
            queue_position=1,
        )
        db.register_prompt(
            conn,
            prompt_id="222222",
            slug="child",
            title="Child",
            current_path="prompts/child.md",
            project_id="51",
            project_name="codex-roadmap",
            repo="gernalix/codex-roadmap",
            queue_position=2,
        )
        db.register_prompt(
            conn,
            prompt_id="333333",
            slug="running",
            title="Running",
            current_path="prompts/running.md",
            prompt_type="Goal",
            project_id="51",
            project_name="codex-roadmap",
            repo="gernalix/codex-roadmap",
            queue_position=3,
        )
        db.add_relation(conn, "111111", "222222", "parent", actor="test")
        db.add_dependency(conn, "222222", "111111", note="parent gate")
        db.add_tag(conn, "222222", "example")
        db.set_status(conn, "111111", "completed", actor="test")
        db.set_status(conn, "333333", "running", actor="codex", note="launch")
        conn.commit()
        conn.close()
        return root / "roadmap.sqlite"

    def test_backfill_preserves_prompt_state_hierarchy_and_scheduler_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = self.make_v1_repo(Path(tmp))
            result = migration.migrate_database(db_path)
            self.assertTrue(result["ok"])
            self.assertEqual(3, result["prompts"])
            self.assertEqual(3, result["mapped_prompts"])
            self.assertEqual("1", result["feature_version"])

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            goal = conn.execute(
                "SELECT * FROM work_items WHERE prompt_id='111111'"
            ).fetchone()
            child = conn.execute(
                "SELECT * FROM work_items WHERE prompt_id='222222'"
            ).fetchone()
            running = conn.execute(
                "SELECT * FROM work_items WHERE prompt_id='333333'"
            ).fetchone()
            self.assertEqual("goal", goal["kind"])
            self.assertEqual("prompt:111111", child["parent_id"])
            self.assertEqual("running", running["status"])
            self.assertEqual("codex", running["executor_policy"])
            self.assertEqual(
                1,
                conn.execute(
                    """SELECT COUNT(*) FROM work_item_dependencies
                       WHERE work_item_id='prompt:222222'
                         AND depends_on_work_item_id='prompt:111111'"""
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                conn.execute(
                    """SELECT COUNT(*) FROM work_item_tags
                       WHERE work_item_id='prompt:222222' AND tag='example'"""
                ).fetchone()[0],
            )
            progress = conn.execute(
                "SELECT * FROM v_work_item_progress WHERE work_item_id='prompt:111111'"
            ).fetchone()
            self.assertEqual(1, progress["total_actionable"])
            self.assertEqual(0, progress["completed_actionable"])
            self.assertEqual(0.0, progress["progress_percent"])
            runnable = [
                row[0]
                for row in conn.execute(
                    "SELECT prompt_id FROM v_work_item_runnable ORDER BY prompt_id"
                )
            ]
            self.assertEqual(["222222"], runnable)
            conn.close()

    def test_migration_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = self.make_v1_repo(Path(tmp))
            first = migration.migrate_database(db_path)
            second = migration.migrate_database(db_path)
            self.assertTrue(first["ok"])
            self.assertTrue(second["ok"])
            self.assertEqual(3, first["work_items"])
            self.assertEqual(3, second["work_items"])
            self.assertEqual(0, second["work_items_inserted"])

    def test_backup_and_rollback_restore_original_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = self.make_v1_repo(root)
            conn = sqlite3.connect(db_path)
            before_rows = conn.execute(
                "SELECT prompt_id,status,queue_position FROM prompts ORDER BY prompt_id"
            ).fetchall()
            conn.close()
            backup = root / "backup.sqlite"
            backup_result = migration.create_backup(db_path, backup)
            self.assertEqual("ok", backup_result["quick_check"])
            self.assertEqual(0, backup_result["foreign_key_errors"])

            migration.migrate_database(db_path)
            conn = sqlite3.connect(db_path)
            self.assertIsNotNone(
                conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='work_items'"
                ).fetchone()
            )
            conn.close()

            rollback = migration.restore_backup(backup, db_path)
            self.assertEqual(backup_result["sha256"], rollback["sha256"])
            conn = sqlite3.connect(db_path)
            self.assertIsNone(
                conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='work_items'"
                ).fetchone()
            )
            self.assertEqual(3, conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0])
            self.assertEqual(
                before_rows,
                conn.execute(
                    "SELECT prompt_id,status,queue_position FROM prompts ORDER BY prompt_id"
                ).fetchall(),
            )
            self.assertEqual("ok", conn.execute("PRAGMA quick_check").fetchone()[0])
            self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            conn.close()


if __name__ == "__main__":
    unittest.main()
