#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid
from typing import Any

import c2_identity
import c2_scheduler
import roadmap_db


class C2IntakeError(RuntimeError):
    pass


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(Path(path).expanduser().resolve())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _require_c2_schema(conn: sqlite3.Connection) -> None:
    required = {"work_items", "prompt_id_registry", "projects"}
    tables = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    missing = sorted(required - tables)
    if missing:
        raise C2IntakeError("c2_schema_missing:" + ",".join(missing))


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value[:48] or "work-item"


def _new_work_item_id() -> str:
    return "wi:" + uuid.uuid4().hex


def _proven_codex_pair(conn: sqlite3.Connection, item: sqlite3.Row,
                       model: str | None, reasoning: str | None) -> tuple[str,str] | None:
    """Reuse one exact successful pair only within the same project and repo."""
    if not item['project_id'] or not item['repo']:
        return None
    rows=conn.execute('''SELECT e.model,e.reasoning,
          SUM(CASE WHEN e.outcome='PASS' THEN 1 ELSE 0 END) AS passed,
          SUM(CASE WHEN e.outcome IN ('FAIL','BLOCKED') THEN 1 ELSE 0 END) AS failed
        FROM executions e JOIN work_items w ON w.prompt_id=e.prompt_id
        WHERE w.project_id=? AND w.repo=? AND e.model IS NOT NULL AND e.reasoning IS NOT NULL
          AND (? IS NULL OR e.model=?) AND (? IS NULL OR e.reasoning=?)
        GROUP BY e.model,e.reasoning''',
        (item['project_id'],item['repo'],model,model,reasoning,reasoning)).fetchall()
    qualified=[(str(row['model']),str(row['reasoning'])) for row in rows
               if row['passed']>=2 and row['failed']==0]
    return qualified[0] if len(qualified)==1 else None


def _project_and_repo(
    conn: sqlite3.Connection,
    project: str | None,
    repo: str | None,
) -> tuple[int | None, str | None, str | None]:
    if project is None:
        return None, None, repo
    project_id = c2_identity.resolve_project_id(conn, project)
    row = conn.execute(
        "SELECT name FROM projects WHERE project_id=?",
        (project_id,),
    ).fetchone()
    project_name = str(row[0]) if row else None
    if repo:
        return project_id, project_name, repo
    canonical = conn.execute(
        """SELECT COALESCE(remote_url,worktree_path,location)
           FROM repositories
           WHERE project_id=? AND canonical=1
           ORDER BY
             CASE repository_kind
               WHEN 'remote_repo' THEN 0
               WHEN 'local_worktree' THEN 1
               ELSE 2
             END,
             repository_id
           LIMIT 1""",
        (project_id,),
    ).fetchone()
    return project_id, project_name, (str(canonical[0]) if canonical and canonical[0] else None)

def add_work_item(
    conn: sqlite3.Connection,
    *,
    title: str,
    objective: str | None = None,
    acceptance: list[str] | None = None,
    kind: str = "task",
    executor_policy: str = "auto",
    project: str | None = None,
    repo: str | None = None,
    parent_id: str | None = None,
    depends_on: list[str] | None = None,
    tags: list[str] | None = None,
    next_action: str | None = None,
    current_action: str | None = None,
    sort_order: int | None = None,
    execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_c2_schema(conn)
    kind = str(kind)
    if kind not in {"goal", "task", "phase", "step", "gate"}:
        raise C2IntakeError(f"invalid_kind:{kind}")
    if executor_policy not in {"auto", "codex", "rdc", "chatgpt", "human"}:
        raise C2IntakeError(f"invalid_executor_policy:{executor_policy}")
    if execution is not None and executor_policy != "auto":
        raise C2IntakeError("execution_context_requires_auto_policy")
    if not str(title).strip():
        raise C2IntakeError("title_required")
    project_id, project_name, resolved_repo = _project_and_repo(conn, project, repo)
    if parent_id is not None:
        parent = conn.execute(
            "SELECT 1 FROM work_items WHERE work_item_id=?",
            (parent_id,),
        ).fetchone()
        if not parent:
            raise C2IntakeError(f"parent_not_found:{parent_id}")
    dependencies = list(depends_on or [])
    for dependency in dependencies:
        if dependency == parent_id:
            # Parent/child hierarchy alone is not automatically a dependency.
            # If explicitly requested it is still valid, so only existence is checked.
            pass
        row = conn.execute(
            "SELECT 1 FROM work_items WHERE work_item_id=?",
            (dependency,),
        ).fetchone()
        if not row:
            raise C2IntakeError(f"dependency_not_found:{dependency}")
    work_item_id = _new_work_item_id()
    now = c2_identity.utc_now()
    conn.execute(
        """INSERT INTO work_items(
             work_item_id,parent_id,kind,title,objective,acceptance_json,status,executor_policy,sort_order,
             current_action,next_action,blocker,project_id,project_name,repo,
             prompt_id,task_id,required,actionable,source_kind,source_ref,
             created_at,updated_at
           ) VALUES(?,?,?,?,?,?,'pending', ?, ?, ?, ?, NULL, ?, ?, ?,
                    NULL,NULL,1,1,'c2-intake','c2-intake',?,?)""",
        (
            work_item_id,
            parent_id,
            kind,
            str(title).strip(),
            objective,
            json.dumps(acceptance or [],ensure_ascii=False),
            executor_policy,
            sort_order,
            current_action,
            next_action,
            str(project_id) if project_id is not None else None,
            project_name,
            resolved_repo,
            now,
            now,
        ),
    )
    for dependency in dependencies:
        conn.execute(
            """INSERT INTO work_item_dependencies(
                 work_item_id,depends_on_work_item_id,required,note
               ) VALUES(?,?,1,'c2-intake')""",
            (work_item_id, dependency),
        )
    for tag in tags or []:
        value = str(tag).strip()
        if value:
            conn.execute(
                "INSERT OR IGNORE INTO work_item_tags(work_item_id,tag) VALUES(?,?)",
                (work_item_id, value),
            )
    readiness = None
    if executor_policy == "auto":
        c2_scheduler.install_schema(conn)
        readiness = c2_scheduler.configure_auto(conn,work_item_id,execution=execution)
    return dict(
        conn.execute(
            "SELECT * FROM work_items WHERE work_item_id=?",
            (work_item_id,),
        ).fetchone()
    ) | ({"execution_readiness": readiness} if readiness else {})

def prepare_codex(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    prompt_text: str,
    source: str,
    model: str | None = None,
    reasoning: str | None = None,
    megavault_mode: str | None = None,
    parent_prompt_id: int | None = None,
    execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_c2_schema(conn)
    item = conn.execute(
        "SELECT * FROM work_items WHERE work_item_id=?",
        (work_item_id,),
    ).fetchone()
    if not item:
        raise C2IntakeError(f"work_item_not_found:{work_item_id}")
    if item["status"] != "pending":
        raise C2IntakeError(
            f"work_item_not_pending:{work_item_id}:{item['status']}"
        )
    if item["prompt_id"] is not None:
        raise C2IntakeError(f"work_item_already_prompt_backed:{work_item_id}")
    header = "\n".join(str(prompt_text).splitlines()[:16])
    if re.search(r"(?i)(?:^|[|\s])(?:model|reasoning)\s*=", header):
        raise C2IntakeError("prompt_text_contains_execution_metadata")
    if model is None or reasoning is None:
        proven=_proven_codex_pair(conn,item,model,reasoning)
        if proven:
            model=model or proven[0]
            reasoning=reasoning or proven[1]
    project_id = int(item["project_id"]) if item["project_id"] is not None else None
    prompt_id = c2_identity.allocate_prompt_id(
        conn,
        source=source,
        request_id="c2-prepare-" + work_item_id.replace(":", "-"),
        project_id=project_id,
        parent_prompt_id=parent_prompt_id,
    )
    prompt_id_match = re.search(
        r"(?m)^PROMPT_ID\s*[:=]\s*(\d{6})\s*$",
        prompt_text,
    )
    if prompt_id_match and prompt_id_match.group(1) != str(prompt_id):
        raise C2IntakeError("prompt_text_prompt_id_mismatch")
    if not prompt_id_match:
        prompt_text = f"PROMPT_ID={prompt_id}\n\n{prompt_text.lstrip()}"
    digest = roadmap_db.materialization_hash(prompt_text)
    prompt_type = "Goal" if item["kind"] == "goal" else "Prompt"
    slug = f"{_slug(str(item['title']))}-{prompt_id}"
    current_path = f"prompts/{slug}.md"
    now = c2_identity.utc_now()
    prompt_surface = conn.execute(
        "SELECT type FROM sqlite_master WHERE name='prompts'"
    ).fetchone()
    cutover = bool(prompt_surface and str(prompt_surface[0]) == "view")
    if not cutover:
        raise C2IntakeError("work_items_cutover_required_before_codex_materialization")

    conn.execute(
        """INSERT INTO prompt_metadata(
             prompt_id,slug,chat_guidance,prompt_type,model,reasoning,
             megavault_mode,campaign_id,explanation,current_path,
             materialization_sha256,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            str(prompt_id),
            slug,
            None,
            prompt_type,
            model,
            reasoning,
            megavault_mode,
            None,
            "",
            current_path,
            digest,
            now,
            now,
        ),
    )
    conn.execute(
        """UPDATE work_items
           SET prompt_id=?,executor_policy='codex',updated_at=?
           WHERE work_item_id=?""",
        (str(prompt_id), now, work_item_id),
    )
    conn.execute(
        """INSERT INTO prompt_materializations(
             prompt_id,body,sha256,created_at,actor
           ) VALUES(?,?,?,?,?)""",
        (str(prompt_id), prompt_text, digest, now, "c2-intake"),
    )
    conn.execute(
        """INSERT INTO status_history(
             prompt_id,old_status,new_status,changed_at,actor,note
           ) VALUES(?,NULL,'pending',?,'c2-intake','work item materialized for Codex')""",
        (str(prompt_id), now),
    )
    conn.execute(
        """INSERT INTO audit_events(
             prompt_id,event_type,event_at,actor,payload_json
           ) VALUES(?, 'prompt_registered', ?, 'c2-intake', ?)""",
        (
            str(prompt_id),
            now,
            json.dumps(
                {"work_item_id": work_item_id, "source": source},
                sort_keys=True,
            ),
        ),
    )
    raw_digest = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    c2_identity.materialize_prompt_id(
        conn,
        prompt_id,
        content_sha256=raw_digest,
    )
    execution_readiness = None
    if execution is not None:
        c2_scheduler.install_schema(conn)
        execution_readiness = c2_scheduler.configure_auto(conn,work_item_id,execution=execution)
    return {
        "work_item_id": work_item_id,
        "prompt_id": str(prompt_id),
        "current_path": current_path,
        "materialization_sha256": digest,
        "registry_content_sha256": raw_digest,
        "model": model,
        "reasoning": reasoning,
        "prompt_type": prompt_type,
        **({"execution_readiness": execution_readiness} if execution_readiness else {}),
    }


def repair_prompt_materialization(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    expected_sha256: str,
    prompt_text: str,
) -> dict[str, str]:
    """Fenced repair for a pending C2 prompt whose canonical body is malformed."""
    _require_c2_schema(conn)
    item = conn.execute(
        "SELECT * FROM work_items WHERE work_item_id=?", (work_item_id,)
    ).fetchone()
    if not item or item["status"] != "pending" or not item["prompt_id"]:
        raise C2IntakeError("pending_prompt_backed_work_item_required")
    if c2_scheduler.external_personalhub(conn, item):
        raise C2IntakeError("external_personalhub_workload")
    prompt_id = str(item["prompt_id"])
    if not re.search(
        rf"(?m)^PROMPT_ID\s*[:=]\s*{re.escape(prompt_id)}\s*$",
        prompt_text,
    ):
        raise C2IntakeError("canonical_prompt_id_header_required")
    c2_scheduler.install_schema(conn)
    if conn.execute(
        """SELECT 1 FROM work_item_runs
           WHERE work_item_id=? AND state IN ('claimed','running','recovering')""",
        (work_item_id,),
    ).fetchone():
        raise C2IntakeError("active_run_blocks_materialization_repair")
    row = conn.execute(
        "SELECT materialization_sha256 FROM prompts WHERE prompt_id=?", (prompt_id,)
    ).fetchone()
    if not row or str(row["materialization_sha256"] or "") != str(expected_sha256):
        raise C2IntakeError("materialization_sha256_mismatch")
    roadmap_db.set_prompt_text(
        conn,
        prompt_id,
        prompt_text,
        actor="c2-control",
        note="fenced C2 materialization repair",
    )
    updated = conn.execute(
        "SELECT materialization_sha256 FROM prompts WHERE prompt_id=?", (prompt_id,)
    ).fetchone()
    return {
        "work_item_id": work_item_id,
        "prompt_id": prompt_id,
        "materialization_sha256": str(updated["materialization_sha256"]),
    }


def show_work_item(conn: sqlite3.Connection, work_item_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM v_work_item_summary WHERE work_item_id=?",
        (work_item_id,),
    ).fetchone()
    if not row:
        raise C2IntakeError(f"work_item_not_found:{work_item_id}")
    result = dict(row)
    result["dependencies"] = [
        str(r[0])
        for r in conn.execute(
            """SELECT depends_on_work_item_id
               FROM work_item_dependencies
               WHERE work_item_id=?
               ORDER BY depends_on_work_item_id""",
            (work_item_id,),
        )
    ]
    result["tags"] = [
        str(r[0])
        for r in conn.execute(
            "SELECT tag FROM work_item_tags WHERE work_item_id=? ORDER BY tag",
            (work_item_id,),
        )
    ]
    return result


def runnable_work_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM v_work_item_runnable"
        ).fetchall()
    ]

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="C2 canonical work-item intake")
    parser.add_argument("--db", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("--title", required=True)
    add.add_argument("--objective")
    add.add_argument("--acceptance", action="append", default=[])
    add.add_argument("--kind", default="task")
    add.add_argument("--executor-policy", default="auto")
    add.add_argument("--project")
    add.add_argument("--repo")
    add.add_argument("--parent-id")
    add.add_argument("--depends-on", action="append", default=[])
    add.add_argument("--tag", action="append", default=[])
    add.add_argument("--next-action")
    add.add_argument("--current-action")
    add.add_argument("--sort-order", type=int)
    add.add_argument("--execution-json", type=Path,
                     help="Structured execution context; auto policy creates a spec only when complete")

    prepare = sub.add_parser("prepare-codex")
    prepare.add_argument("work_item_id")
    prepare.add_argument("--prompt-file", type=Path, required=True)
    prepare.add_argument("--source", required=True)
    prepare.add_argument("--model")
    prepare.add_argument("--reasoning")
    prepare.add_argument("--megavault-mode")
    prepare.add_argument("--parent-prompt-id", type=int)
    prepare.add_argument("--execution-json", type=Path,
                         help="Structured worktree and other exact execution context")

    show = sub.add_parser("show")
    show.add_argument("work_item_id")
    sub.add_parser("runnable")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with closing(_connect(args.db)) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                if args.command == "add":
                    payload = add_work_item(
                        conn,
                        title=args.title,
                        objective=args.objective,
                        acceptance=args.acceptance,
                        kind=args.kind,
                        executor_policy=args.executor_policy,
                        project=args.project,
                        repo=args.repo,
                        parent_id=args.parent_id,
                        depends_on=args.depends_on,
                        tags=args.tag,
                        next_action=args.next_action,
                        current_action=args.current_action,
                        sort_order=args.sort_order,
                        execution=json.loads(args.execution_json.read_text(encoding="utf-8"))
                        if args.execution_json else None,
                    )
                elif args.command == "prepare-codex":
                    prompt_text = args.prompt_file.read_text(encoding="utf-8")
                    payload = prepare_codex(
                        conn,
                        args.work_item_id,
                        prompt_text=prompt_text,
                        source=args.source,
                        model=args.model,
                        reasoning=args.reasoning,
                        megavault_mode=args.megavault_mode,
                        parent_prompt_id=args.parent_prompt_id,
                        execution=json.loads(args.execution_json.read_text(encoding="utf-8"))
                        if args.execution_json else None,
                    )
                elif args.command == "show":
                    payload = show_work_item(conn, args.work_item_id)
                elif args.command == "runnable":
                    payload = runnable_work_items(conn)
                else:
                    raise AssertionError(args.command)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    except (OSError, sqlite3.Error, C2IntakeError, c2_identity.C2IdentityError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", "result": payload}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
