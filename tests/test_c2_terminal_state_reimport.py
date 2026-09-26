from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import c2_scheduler
import c2_terminal_state_reimport as repair
import work_items_state_import as state_import
from tests.test_c2_intake import C2IntakeTests


class TerminalStateReimportTests(unittest.TestCase):
    def make_source(self, root: Path) -> tuple[sqlite3.Connection, Path, dict[str, str]]:
        db_path = C2IntakeTests().make_cutover_db(root)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        c2_scheduler.install_schema(conn)
        state_root = root / "operations/task-state"
        state_root.mkdir(parents=True)
        expected = {}
        for name in repair.TERMINAL_FILES:
            raw = (repair.STATE_ROOT / name).read_bytes()
            (state_root / name).write_bytes(raw)
            expected[name] = hashlib.sha256(raw).hexdigest()
            state_import.import_state_file(conn, state_root / name, state_root=state_root)
        conn.commit()
        return conn, state_root, expected

    def test_repairs_only_terminal_roots_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            conn, state_root, expected = self.make_source(Path(tmp))
            try:
                for name in repair.TERMINAL_FILES:
                    parsed = state_import.parse_state_file(state_root / name)
                    owner_id = "task:" + parsed.task_id
                    old_text = state_import._section_items(parsed.sections["Remaining"])[0]
                    old_id = state_import._stable_id(owner_id, "step", "Remaining", old_text)
                    conn.execute(
                        """INSERT INTO work_items(
                             work_item_id,parent_id,kind,title,status,executor_policy,
                             required,actionable,source_kind,source_ref,created_at,updated_at
                           ) VALUES(?,?,'step',?,'pending','auto',
                                    1,1,'task_state',?,'x','x')""",
                        (old_id, owner_id, old_text, name + "#remaining"),
                    )
                    conn.execute(
                        "UPDATE work_items SET status='running' WHERE work_item_id=?",
                        (owner_id,),
                    )
                    conn.execute(
                        "UPDATE work_item_checkpoints SET remaining_json=? WHERE work_item_id=?",
                        (json.dumps([old_text]), owner_id),
                    )
                count_before = conn.execute("SELECT COUNT(*) FROM work_item_checkpoints").fetchone()[0]
                first = repair._reconcile(conn, expected, state_root)
                second = repair._reconcile(conn, expected, state_root)
                self.assertEqual(3, len(first["reconciled"]))
                self.assertEqual(first, second)
                self.assertEqual(count_before, conn.execute(
                    "SELECT COUNT(*) FROM work_item_checkpoints"
                ).fetchone()[0])
                self.assertEqual(3, conn.execute(
                    """SELECT COUNT(*) FROM work_items WHERE task_id IN (
                         'CHATGPT-20260924-CSS-PROMPT-INDEX',
                         'CHATGPT-20260924-WHATSAPP-EXPORTER',
                         'CHATGPT-20260924-RDC-SUPERVISOR') AND status='completed'"""
                ).fetchone()[0])
                self.assertEqual(3, conn.execute(
                    """SELECT COUNT(*) FROM work_items
                       WHERE source_ref LIKE 'CHATGPT-20260924-%#remaining'
                         AND status='superseded'"""
                ).fetchone()[0])
                self.assertEqual("ok", conn.execute("PRAGMA quick_check").fetchone()[0])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            finally:
                conn.close()

    def test_completed_prompt_repair_supersedes_stale_running_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = C2IntakeTests().make_cutover_db(root)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            c2_scheduler.install_schema(conn)
            state_root = root / "state"
            state_root.mkdir()
            name = "123456.md"
            path = state_root / name
            path.write_text(
                """# Operational task state — 123456

PROMPT_ID: 123456

## Plan / checklist
### Phase 1
- [ ] Historical unfinished step

## Completed
- Parent acceptance passed.

## Remaining
- Follow-up lives in a separate work item.
""",
                encoding="utf-8",
            )
            conn.execute(
                """UPDATE work_items
                   SET status='completed',project_name='codex-roadmap',
                       repo='gernalix/codex-roadmap'
                   WHERE prompt_id='123456'"""
            )
            state_import.import_state_file(conn, path, state_root=state_root)
            phase_id = state_import._stable_id("prompt:123456", "phase", "Phase 1")
            conn.execute(
                "UPDATE work_items SET status='running' WHERE work_item_id=?",
                (phase_id,),
            )
            conn.commit()
            expected = {name: hashlib.sha256(path.read_bytes()).hexdigest()}
            try:
                with mock.patch.object(
                    repair, "COMPLETED_PROMPT_FILES", frozenset({name})
                ):
                    first = repair._reconcile_completed_prompts(conn, expected, state_root)
                    second = repair._reconcile_completed_prompts(conn, expected, state_root)
                self.assertEqual(1, first[0]["superseded_running_descendants"])
                self.assertEqual(0, second[0]["superseded_running_descendants"])
                self.assertEqual(
                    "superseded",
                    conn.execute(
                        "SELECT status FROM work_items WHERE work_item_id=?",
                        (phase_id,),
                    ).fetchone()[0],
                )
                self.assertEqual("ok", conn.execute("PRAGMA quick_check").fetchone()[0])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            finally:
                conn.close()

    def test_changed_source_or_file_set_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            conn, state_root, expected = self.make_source(Path(tmp))
            try:
                with self.assertRaisesRegex(ValueError, "terminal_state_file_set_mismatch"):
                    repair._reconcile(conn, {}, state_root)
                altered = dict(expected)
                altered["CHATGPT-20260924-RDC-SUPERVISOR.md"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "terminal_state_source_changed"):
                    repair._reconcile(conn, altered, state_root)
                self.assertEqual(0, conn.execute(
                    "SELECT COUNT(*) FROM work_items WHERE status='superseded'"
                ).fetchone()[0])
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
