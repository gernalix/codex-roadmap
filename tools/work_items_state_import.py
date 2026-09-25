#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from work_items_migration import (
    FEATURE_META_KEY,
    FEATURE_VERSION,
    prompt_work_item_id,
)

PROMPT_ID_RE = re.compile(r"(?m)^PROMPT_ID\s*[:=]\s*(\d{6})\s*$")
TASK_ID_RE = re.compile(r"(?m)^TASK_ID\s*[:=]\s*([^\s]+)\s*$")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
CHECK_RE = re.compile(r"^\s*[-*]\s*\[([ xX])\]\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")


@dataclass
class ParsedState:
    path: Path
    title: str
    prompt_id: str | None
    task_id: str | None
    sections: dict[str, str] = field(default_factory=dict)
    plan_phases: list[tuple[str, list[tuple[bool, str]]]] = field(default_factory=list)


class StateImportError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).strip()


def _stable_id(owner_id: str, kind: str, *parts: str) -> str:
    basis = "\x1f".join([owner_id, kind, *(_norm(part).lower() for part in parts)])
    return f"state:{kind}:{hashlib.sha256(basis.encode('utf-8')).hexdigest()[:20]}"

def parse_state_file(path: Path) -> ParsedState:
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), Path(path).stem)
    prompt_match = PROMPT_ID_RE.search(raw)
    task_match = TASK_ID_RE.search(raw)
    prompt_id = prompt_match.group(1) if prompt_match else None
    task_id = task_match.group(1) if task_match else None

    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    current_phase: str | None = None
    phase_items: dict[str, list[tuple[bool, str]]] = {}
    phase_order: list[str] = []

    for line in lines:
        heading = HEADING_RE.match(line)
        if heading:
            level, name = heading.groups()
            if level == "##":
                current_section = name.strip()
                sections.setdefault(current_section, [])
                current_phase = None
            elif level == "###" and current_section == "Plan / checklist":
                current_phase = name.strip()
                if current_phase not in phase_items:
                    phase_items[current_phase] = []
                    phase_order.append(current_phase)
            continue
        if current_section is not None:
            sections.setdefault(current_section, []).append(line)
        if current_section == "Plan / checklist":
            checked = CHECK_RE.match(line)
            if checked:
                phase = current_phase or "Plan"
                if phase not in phase_items:
                    phase_items[phase] = []
                    phase_order.append(phase)
                phase_items[phase].append((checked.group(1).lower() == "x", _norm(checked.group(2))))

    return ParsedState(
        path=Path(path),
        title=title,
        prompt_id=prompt_id,
        task_id=task_id,
        sections={key: "\n".join(value).strip() for key, value in sections.items()},
        plan_phases=[(phase, phase_items[phase]) for phase in phase_order],
    )


def _section_items(text: str) -> list[str]:
    if not text.strip():
        return []
    items: list[str] = []
    paragraph: list[str] = []
    for line in text.splitlines():
        bullet = BULLET_RE.match(line)
        check = CHECK_RE.match(line)
        if check or bullet:
            if paragraph:
                items.append(_norm(" ".join(paragraph)))
                paragraph.clear()
            items.append(_norm((check or bullet).group(2 if check else 1)))
        elif line.strip():
            paragraph.append(line.strip())
        elif paragraph:
            items.append(_norm(" ".join(paragraph)))
            paragraph.clear()
    if paragraph:
        items.append(_norm(" ".join(paragraph)))
    return [item for item in items if item]

def _none_blocker(text: str) -> bool:
    value = _norm(text).lower().strip(" .—-")
    return (
        not value
        or value in {"none", "nessuno", "nessun blocker", "no blockers"}
        or value.startswith("no active blocker")
        or value.startswith("none for ")
    )


def _derive_task_status(parsed: ParsedState) -> str:
    blockers = parsed.sections.get("Blockers", "")
    if blockers and not _none_blocker(blockers):
        return "blocked"
    remaining = _section_items(parsed.sections.get("Remaining", ""))
    if remaining:
        return "running"
    completed = _section_items(parsed.sections.get("Completed", ""))
    if completed:
        return "completed"
    return "unknown"

def _ensure_feature(conn: sqlite3.Connection) -> None:
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='work_items'"
    ).fetchone()
    version = conn.execute(
        "SELECT value FROM meta WHERE key=?",
        (FEATURE_META_KEY,),
    ).fetchone()
    if not table or not version or str(version[0]) != FEATURE_VERSION:
        raise StateImportError("work_items_migration_required")


def _owner_id(conn: sqlite3.Connection, parsed: ParsedState, source_ref: str) -> str:
    if parsed.prompt_id:
        row = conn.execute(
            "SELECT work_item_id FROM work_items WHERE prompt_id=?",
            (parsed.prompt_id,),
        ).fetchone()
        if row:
            return str(row[0])
        work_item_id = prompt_work_item_id(parsed.prompt_id)
        now = _utc_now()
        conn.execute(
            """INSERT INTO work_items(
                 work_item_id,parent_id,kind,title,status,executor_policy,sort_order,
                 current_action,next_action,blocker,project_id,project_name,repo,
                 prompt_id,task_id,required,actionable,source_kind,source_ref,
                 created_at,updated_at
               ) VALUES(?,NULL,'task',?,?,'codex',NULL,NULL,NULL,NULL,NULL,NULL,NULL,
                        ?,NULL,1,1,'task_state',?,?,?)""",
            (
                work_item_id,
                parsed.title,
                _derive_task_status(parsed),
                parsed.prompt_id,
                source_ref,
                now,
                now,
            ),
        )
        return work_item_id
    if not parsed.task_id:
        raise StateImportError(f"state_identity_missing:{source_ref}")
    work_item_id = f"task:{parsed.task_id}"
    now = _utc_now()
    conn.execute(
        """INSERT OR IGNORE INTO work_items(
             work_item_id,parent_id,kind,title,status,executor_policy,sort_order,
             current_action,next_action,blocker,project_id,project_name,repo,
             prompt_id,task_id,required,actionable,source_kind,source_ref,
             created_at,updated_at
           ) VALUES(?,NULL,'task',?,?,'auto',NULL,NULL,NULL,NULL,NULL,NULL,NULL,
                    NULL,?,1,1,'task_state',?,?,?)""",
        (
            work_item_id,
            parsed.title,
            _derive_task_status(parsed),
            parsed.task_id,
            source_ref,
            now,
            now,
        ),
    )
    return work_item_id

def _upsert_child(
    conn: sqlite3.Connection,
    *,
    work_item_id: str,
    parent_id: str,
    kind: str,
    title: str,
    status: str,
    sort_order: int,
    source_ref: str,
    inherited: sqlite3.Row,
    actionable: bool,
) -> None:
    now = _utc_now()
    conn.execute(
        """INSERT INTO work_items(
             work_item_id,parent_id,kind,title,status,executor_policy,sort_order,
             current_action,next_action,blocker,project_id,project_name,repo,
             prompt_id,task_id,required,actionable,source_kind,source_ref,
             created_at,updated_at
           ) VALUES(?,?,?,?,?,'auto',?,NULL,NULL,NULL,?,?,?,NULL,NULL,1,?,'task_state',?,?,?)
           ON CONFLICT(work_item_id) DO UPDATE SET
             parent_id=excluded.parent_id,
             kind=excluded.kind,
             title=excluded.title,
             status=excluded.status,
             sort_order=excluded.sort_order,
             project_id=excluded.project_id,
             project_name=excluded.project_name,
             repo=excluded.repo,
             actionable=excluded.actionable,
             source_ref=excluded.source_ref,
             updated_at=excluded.updated_at
           WHERE work_items.source_kind='task_state'""",
        (
            work_item_id,
            parent_id,
            kind,
            title,
            status,
            sort_order,
            inherited["project_id"],
            inherited["project_name"],
            inherited["repo"],
            int(actionable),
            source_ref,
            now,
            now,
        ),
    )

def _insert_evidence(
    conn: sqlite3.Connection,
    *,
    owner_id: str,
    source_file: str,
    section: str,
    text: str,
) -> None:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    conn.execute(
        """INSERT OR IGNORE INTO work_item_evidence(
             work_item_id,evidence_kind,label,uri,value_json,created_at
           ) VALUES(?,?,?,?,?,?)""",
        (
            owner_id,
            section.lower().replace(" ", "_"),
            text,
            f"state://{source_file}#{section.lower().replace(' ', '-')}-{digest}",
            json.dumps({"text": text}, ensure_ascii=False, sort_keys=True),
            _utc_now(),
        ),
    )


def import_state_file(
    conn: sqlite3.Connection,
    path: Path,
    *,
    state_root: Path,
    source_commit: str | None = None,
) -> dict[str, Any]:
    _ensure_feature(conn)
    parsed = parse_state_file(path)
    if not parsed.prompt_id and not parsed.task_id:
        return {"status": "skipped", "reason": "identity_missing", "path": str(path)}
    raw = Path(path).read_bytes()
    source_sha = _sha256_bytes(raw)
    source_file = Path(path).resolve().relative_to(Path(state_root).resolve()).as_posix()
    owner_id = _owner_id(conn, parsed, source_file)
    existing = conn.execute(
        """SELECT checkpoint_id FROM work_item_checkpoints
           WHERE work_item_id=? AND source_file=? AND source_sha256=?""",
        (owner_id, source_file, source_sha),
    ).fetchone()
    if existing:
        return {
            "status": "ok",
            "idempotent": True,
            "work_item_id": owner_id,
            "source_file": source_file,
            "children": 0,
            "evidence": 0,
        }

    current_step = parsed.sections.get("Current step", "").strip() or None
    next_action = parsed.sections.get("Next action", "").strip() or None
    blockers_text = parsed.sections.get("Blockers", "").strip()
    blocker = None if _none_blocker(blockers_text) else blockers_text or None
    now = _utc_now()

    owner = conn.execute(
        "SELECT * FROM work_items WHERE work_item_id=?",
        (owner_id,),
    ).fetchone()
    if owner is None:
        raise StateImportError(f"work_item_missing:{owner_id}")
    if parsed.prompt_id:
        # Preserve lifecycle semantics of prompt-backed roots, especially already
        # running prompts. Operational fields are new C2 state, not lifecycle edits.
        conn.execute(
            """UPDATE work_items
               SET current_action=?,next_action=?,blocker=?
               WHERE work_item_id=?""",
            (current_step, next_action, blocker, owner_id),
        )
    else:
        conn.execute(
            """UPDATE work_items
               SET title=?,status=?,current_action=?,next_action=?,blocker=?,updated_at=?
               WHERE work_item_id=? AND source_kind='task_state'""",
            (
                parsed.title,
                _derive_task_status(parsed),
                current_step,
                next_action,
                blocker,
                now,
                owner_id,
            ),
        )
    owner = conn.execute(
        "SELECT * FROM work_items WHERE work_item_id=?",
        (owner_id,),
    ).fetchone()
    assert owner is not None

    completed_items = _section_items(parsed.sections.get("Completed", ""))
    remaining_items = _section_items(parsed.sections.get("Remaining", ""))
    evidence_items = _section_items(parsed.sections.get("Evidence", ""))
    conn.execute(
        """INSERT INTO work_item_checkpoints(
             work_item_id,source_file,source_commit,source_sha256,objective,
             current_step,next_action,blocker,completed_json,remaining_json,
             evidence_json,captured_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            owner_id,
            source_file,
            source_commit,
            source_sha,
            parsed.sections.get("Objective", "").strip() or None,
            current_step,
            next_action,
            blocker,
            json.dumps(completed_items, ensure_ascii=False),
            json.dumps(remaining_items, ensure_ascii=False),
            json.dumps(evidence_items, ensure_ascii=False),
            now,
        ),
    )

    seen_children: set[str] = set()
    normalized_plan_items: set[str] = set()
    order = 1000
    for phase_title, items in parsed.plan_phases:
        if not items:
            continue
        phase_id = _stable_id(owner_id, "phase", phase_title)
        phase_status = "completed" if all(done for done, _ in items) else (
            "running" if owner["status"] == "running" else "pending"
        )
        _upsert_child(
            conn,
            work_item_id=phase_id,
            parent_id=owner_id,
            kind="phase",
            title=phase_title,
            status=phase_status,
            sort_order=order,
            source_ref=f"{source_file}#phase",
            inherited=owner,
            actionable=False,
        )
        seen_children.add(phase_id)
        order += 100
        step_order = order
        for done, text in items:
            normalized_plan_items.add(_norm(text).lower())
            step_id = _stable_id(owner_id, "step", phase_title, text)
            _upsert_child(
                conn,
                work_item_id=step_id,
                parent_id=phase_id,
                kind="step",
                title=text,
                status="completed" if done else "pending",
                sort_order=step_order,
                source_ref=f"{source_file}#plan-step",
                inherited=owner,
                actionable=True,
            )
            seen_children.add(step_id)
            step_order += 1
        order += 100

    def add_section_steps(section: str, items: list[str], status: str) -> None:
        nonlocal order
        for text in items:
            if _norm(text).lower() in normalized_plan_items:
                continue
            step_id = _stable_id(owner_id, "step", section, text)
            _upsert_child(
                conn,
                work_item_id=step_id,
                parent_id=owner_id,
                kind="step",
                title=text,
                status=status,
                sort_order=order,
                source_ref=f"{source_file}#{section.lower()}",
                inherited=owner,
                actionable=True,
            )
            seen_children.add(step_id)
            order += 1

    add_section_steps("Completed", completed_items, "completed")
    add_section_steps("Remaining", remaining_items, "pending")

    if blocker:
        blocker_items = _section_items(blockers_text) or [blocker]
        for text in blocker_items:
            gate_id = _stable_id(owner_id, "gate", "Blockers", text)
            _upsert_child(
                conn,
                work_item_id=gate_id,
                parent_id=owner_id,
                kind="gate",
                title=f"Resolve blocker: {text}",
                status="blocked",
                sort_order=order,
                source_ref=f"{source_file}#blocker",
                inherited=owner,
                actionable=True,
            )
            seen_children.add(gate_id)
            order += 1

    for text in completed_items:
        _insert_evidence(
            conn,
            owner_id=owner_id,
            source_file=source_file,
            section="Completed",
            text=text,
        )
    for text in evidence_items:
        _insert_evidence(
            conn,
            owner_id=owner_id,
            source_file=source_file,
            section="Evidence",
            text=text,
        )

    # Converge task-state-derived children for this file without deleting history.
    prefix = source_file + "#"
    stale = [
        str(row[0])
        for row in conn.execute(
            """SELECT work_item_id FROM work_items
               WHERE source_kind='task_state'
                 AND source_ref LIKE ?
                 AND work_item_id<>?""",
            (prefix + "%", owner_id),
        )
        if str(row[0]) not in seen_children
    ]
    for work_item_id in stale:
        conn.execute(
            """UPDATE work_items
               SET status='superseded',updated_at=?
               WHERE work_item_id=? AND source_kind='task_state'""",
            (now, work_item_id),
        )

    return {
        "status": "ok",
        "idempotent": False,
        "work_item_id": owner_id,
        "source_file": source_file,
        "children": len(seen_children),
        "superseded_children": len(stale),
        "evidence": len(completed_items) + len(evidence_items),
    }


def import_state_tree(
    conn: sqlite3.Connection,
    state_root: Path,
    *,
    source_commit: str | None = None,
) -> dict[str, Any]:
    root = Path(state_root).resolve()
    if not root.is_dir():
        raise StateImportError(f"state_root_missing:{root}")
    imported = 0
    idempotent = 0
    skipped = 0
    children = 0
    evidence = 0
    results: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        result = import_state_file(
            conn,
            path,
            state_root=root,
            source_commit=source_commit,
        )
        results.append(result)
        if result["status"] == "skipped":
            skipped += 1
        elif result.get("idempotent"):
            idempotent += 1
        else:
            imported += 1
            children += int(result.get("children", 0))
            evidence += int(result.get("evidence", 0))
    return {
        "imported": imported,
        "idempotent": idempotent,
        "skipped": skipped,
        "children": children,
        "evidence": evidence,
        "files": len(results),
        "results": results,
    }

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import operational task-state Markdown into migrated work_items"
    )
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--source-commit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        conn = sqlite3.connect(Path(args.db).expanduser().resolve())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            conn.execute("BEGIN IMMEDIATE")
            result = import_state_tree(
                conn,
                args.state_root,
                source_commit=args.source_commit,
            )
            fk = conn.execute("PRAGMA foreign_key_check").fetchall()
            quick = str(conn.execute("PRAGMA quick_check").fetchone()[0])
            if fk or quick != "ok":
                raise StateImportError(
                    f"state_import_validation_failed:quick={quick}:fk={len(fk)}"
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except (OSError, sqlite3.Error, StateImportError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
