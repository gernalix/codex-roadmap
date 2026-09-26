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
COMPLETED_PROMPT_FILES = frozenset({"175908.md"})


def _reconcile_completed_prompts(
    conn: sqlite3.Connection,
    expected_sha256: dict[str, str] | None,
    state_root: Path,
) -> list[dict]:
    if expected_sha256 is None:
        return []
    if not isinstance(expected_sha256, dict) or set(expected_sha256) != COMPLETED_PROMPT_FILES:
        raise ValueError("terminal_prompt_file_set_mismatch")
    results = []
    for name in sorted(COMPLETED_PROMPT_FILES):
        path = state_root / name
        expected = expected_sha256[name]
        if not isinstance(expected, str) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("terminal_prompt_source_changed:" + name)
        parsed = state_import.parse_state_file(path)
        if not parsed.prompt_id or parsed.task_id or not parsed.plan_phases:
            raise ValueError("terminal_prompt_state_invalid:" + name)
        owner = conn.execute(
            """SELECT work_item_id,status,project_name,repo FROM work_items
               WHERE prompt_id=?""",
            (parsed.prompt_id,),
        ).fetchone()
        if not owner or owner["status"] != "completed":
            raise ValueError("terminal_prompt_owner_not_completed:" + name)
        compact = lambda value: "".join(c for c in str(value or "").lower() if c.isalnum())
        repo_tail = str(owner["repo"] or "").rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        if (
            compact(owner["project_name"]) == "personalhub"
            or compact(repo_tail) == "personalhub"
            or conn.execute(
                """SELECT 1 FROM work_item_tags
                   WHERE work_item_id=? AND lower(tag)='personalhub'""",
                (owner["work_item_id"],),
            ).fetchone()
        ):
            raise ValueError("terminal_prompt_personalhub_forbidden:" + name)
        active = conn.execute(
            """SELECT 1 FROM work_item_runs
               WHERE work_item_id=? AND state IN ('claimed','running','recovering')""",
            (owner["work_item_id"],),
        ).fetchone()
        if active:
            raise ValueError("terminal_prompt_run_active:" + name)
        imported = state_import.import_state_file(conn, path, state_root=state_root)
        rows = conn.execute(
            """WITH RECURSIVE descendants(work_item_id) AS (
                 SELECT work_item_id FROM work_items WHERE parent_id=?
                 UNION ALL
                 SELECT w.work_item_id FROM work_items w
                 JOIN descendants d ON w.parent_id=d.work_item_id
               )
               SELECT w.work_item_id FROM descendants d
               JOIN work_items w ON w.work_item_id=d.work_item_id
               WHERE w.source_kind='task_state'
                 AND w.source_ref LIKE ?
                 AND w.status='running'""",
            (owner["work_item_id"], name + "#%"),
        ).fetchall()
        now = state_import._utc_now()
        for row in rows:
            conn.execute(
                """UPDATE work_items SET status='superseded',updated_at=?
                   WHERE work_item_id=? AND status='running'""",
                (now, row["work_item_id"]),
            )
        remaining = conn.execute(
            """WITH RECURSIVE descendants(work_item_id) AS (
                 SELECT work_item_id FROM work_items WHERE parent_id=?
                 UNION ALL
                 SELECT w.work_item_id FROM work_items w
                 JOIN descendants d ON w.parent_id=d.work_item_id
               )
               SELECT 1 FROM descendants d JOIN work_items w
                 ON w.work_item_id=d.work_item_id
               WHERE w.source_kind='task_state'
                 AND w.source_ref LIKE ?
                 AND w.status='running' LIMIT 1""",
            (owner["work_item_id"], name + "#%"),
        ).fetchone()
        if remaining:
            raise ValueError("terminal_prompt_reimport_incomplete:" + name)
        results.append({
            "source_file": name,
            "status": owner["status"],
            "superseded_running_descendants": len(rows),
            "idempotent": imported["idempotent"],
        })
    return results


def _reconcile(
    conn: sqlite3.Connection,
    expected_sha256: dict[str, str] | None,
    state_root: Path,
    completed_prompt_sha256: dict[str, str] | None = None,
) -> dict:
    if expected_sha256 is None and completed_prompt_sha256 is None:
        raise ValueError("terminal_state_file_set_mismatch")
    checked = []
    if expected_sha256 is not None and (
        not isinstance(expected_sha256, dict) or set(expected_sha256) != TERMINAL_FILES
    ):
        raise ValueError("terminal_state_file_set_mismatch")
    for name in sorted(TERMINAL_FILES if expected_sha256 is not None else ()):
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
    results.extend(_reconcile_completed_prompts(conn, completed_prompt_sha256, state_root))
    return {"reconciled": results}


def apply(
    conn: sqlite3.Connection,
    *,
    expected_sha256: dict[str, str] | None = None,
    completed_prompt_sha256: dict[str, str] | None = None,
) -> dict:
    return _reconcile(
        conn,
        expected_sha256,
        STATE_ROOT,
        completed_prompt_sha256=completed_prompt_sha256,
    )
