"""Bounded repair of terminal task-state projections in the canonical writer."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3

import work_items_state_import as state_import


STATE_ROOT = Path(__file__).resolve().parents[1] / "operations/task-state"
TERMINAL_FILES = frozenset({
    "CHATGPT-20260924-CSS-PROMPT-INDEX.md",
    "CHATGPT-20260924-WHATSAPP-EXPORTER.md",
    "CHATGPT-20260924-RDC-SUPERVISOR.md",
})


def _reconcile(
    conn: sqlite3.Connection,
    expected_sha256: dict[str, str],
    state_root: Path,
) -> dict:
    if not isinstance(expected_sha256, dict) or set(expected_sha256) != TERMINAL_FILES:
        raise ValueError("terminal_state_file_set_mismatch")
    checked = []
    for name in sorted(TERMINAL_FILES):
        path = state_root / name
        expected = expected_sha256[name]
        if not isinstance(expected, str) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("terminal_state_source_changed:" + name)
        parsed = state_import.parse_state_file(path)
        if (
            parsed.prompt_id or not parsed.task_id
            or "PERSONALHUB" in parsed.task_id.upper()
            or not parsed.plan_phases
            or not any(items for _, items in parsed.plan_phases)
            or not all(done for _, items in parsed.plan_phases for done, _ in items)
            or not state_import._section_items(parsed.sections.get("Completed", ""))
            or state_import._remaining_items(parsed.sections.get("Remaining", ""))
            or state_import._derive_task_status(parsed) != "completed"
        ):
            raise ValueError("terminal_state_not_proven:" + name)
        owner_id = "task:" + parsed.task_id
        owner = conn.execute(
            "SELECT source_kind,status FROM work_items WHERE work_item_id=?",
            (owner_id,),
        ).fetchone()
        if not owner or owner[0] != "task_state" or owner[1] not in ("running", "completed"):
            raise ValueError("terminal_state_owner_changed:" + name)
        active = conn.execute(
            """SELECT 1 FROM work_item_runs
               WHERE work_item_id=? AND state IN ('claimed','running','recovering')""",
            (owner_id,),
        ).fetchone()
        if active:
            raise ValueError("terminal_state_run_active:" + name)
        checked.append((name, path, owner_id))

    results = []
    for name, path, owner_id in checked:
        imported = state_import.import_state_file(conn, path, state_root=state_root)
        status = conn.execute(
            "SELECT status FROM work_items WHERE work_item_id=?", (owner_id,)
        ).fetchone()[0]
        pending = conn.execute(
            """SELECT COUNT(*) FROM work_items WHERE parent_id=?
               AND source_ref=? AND status='pending'""",
            (owner_id, name + "#remaining"),
        ).fetchone()[0]
        if status != "completed" or pending:
            raise ValueError("terminal_state_reimport_incomplete:" + name)
        results.append({"source_file": name, "status": status, "idempotent": imported["idempotent"]})
    return {"reconciled": results}


def apply(conn: sqlite3.Connection, *, expected_sha256: dict[str, str]) -> dict:
    return _reconcile(conn, expected_sha256, STATE_ROOT)
