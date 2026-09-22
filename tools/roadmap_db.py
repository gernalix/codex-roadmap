#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_NAME = "roadmap.sqlite"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "roadmap.sql"
FINAL_STATUS = {
    "PASS": "completed",
    "FAIL": "failed",
    "BLOCKED": "blocked",
    "CANCELLED": "cancelled",
    "UNKNOWN": "unknown",
}
ACTIVE_STATUS = {"pending", "running"}
TERMINAL_STATUS = set(FINAL_STATUS.values()) | {"superseded"}

class RoadmapDBError(RuntimeError):
    pass

def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def db_path(repo: Path) -> Path:
    return Path(repo) / DB_NAME

def connect(repo: Path, *, writable: bool = True) -> sqlite3.Connection:
    path = db_path(repo)
    if not path.exists() and not writable:
        raise RoadmapDBError(f"database_missing:{path}")
    conn = (
        sqlite3.connect(path)
        if writable else sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    if writable:
        ensure_schema(conn)
    else:
        conn.execute("PRAGMA query_only=ON")
    return conn

def ensure_schema(conn: sqlite3.Connection) -> None:
    try:
        version = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    except sqlite3.OperationalError:
        version = None
    if not version or version[0] != "1":
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO meta(key,value) VALUES('schema_version','1') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    # Additive runtime table for the GitHub-Issue mutation inbox. Keep schema_version=1:
    # this is backward-compatible and CREATE IF NOT EXISTS is idempotent.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS mutation_receipts (
             request_key TEXT PRIMARY KEY,
             issue_number INTEGER NOT NULL UNIQUE,
             payload_sha256 TEXT NOT NULL,
             actor TEXT NOT NULL,
             applied_at TEXT NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS prompt_materializations (
             prompt_id TEXT PRIMARY KEY
                 REFERENCES prompts(prompt_id)
                 ON UPDATE CASCADE
                 ON DELETE CASCADE,
             body TEXT NOT NULL,
             sha256 TEXT NOT NULL,
             created_at TEXT NOT NULL,
             actor TEXT NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS terminal_requests (
             prompt_id TEXT PRIMARY KEY
                 REFERENCES prompts(prompt_id)
                 ON UPDATE CASCADE
                 ON DELETE RESTRICT,
             requested_status TEXT NOT NULL
                 CHECK (requested_status IN ('completed','failed','blocked','cancelled','unknown')),
             actor TEXT NOT NULL,
             note TEXT,
             requested_at TEXT NOT NULL
           )"""
    )
    # Views are runtime contracts too. Refresh this one additively so existing
    # schema_version=1 databases pick up readiness semantics without a rebuild.
    conn.execute("DROP VIEW IF EXISTS v_runnable_prompts")
    conn.execute(
        """CREATE VIEW v_runnable_prompts AS
           SELECT p.*
           FROM prompts p
           WHERE p.status='pending'
             AND NOT EXISTS (
               SELECT 1
               FROM dependencies d
               JOIN prompts dep ON dep.prompt_id=d.depends_on_prompt_id
               WHERE d.prompt_id=p.prompt_id AND dep.status<>'completed'
             )
             AND NOT EXISTS (
               SELECT 1
               FROM prompt_tags t
               WHERE t.prompt_id=p.prompt_id
                 AND t.tag LIKE 'manual-prerequisite:%'
             )
           ORDER BY COALESCE(p.queue_position, 2147483647), p.created_at, p.prompt_id"""
    )
    conn.commit()

def materialization_hash(text: str) -> str:
    # Normalize the same superficial escaping used by usage exports; raw text is never stored.
    text = html.unescape(text or "")
    text = text.replace("\\_", "_")
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def refresh_materialization_hashes(conn: sqlite3.Connection, repo: Path) -> int:
    """Backfill canonical prompt bodies from legacy prompt files when necessary."""
    updated = 0
    for row in conn.execute(
        "SELECT prompt_id,current_path,materialization_sha256 FROM prompts "
        "WHERE current_path<>''"
    ).fetchall():
        existing = conn.execute(
            "SELECT sha256 FROM prompt_materializations WHERE prompt_id=?",
            (row["prompt_id"],),
        ).fetchone()
        if existing:
            if row["materialization_sha256"] != existing["sha256"]:
                conn.execute(
                    "UPDATE prompts SET materialization_sha256=?,updated_at=? WHERE prompt_id=?",
                    (existing["sha256"], now_utc(), row["prompt_id"]),
                )
                updated += 1
            continue
        path = Path(repo) / row["current_path"]
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8")
        sha = materialization_hash(body)
        conn.execute(
            """INSERT INTO prompt_materializations(prompt_id,body,sha256,created_at,actor)
               VALUES(?,?,?,?,?)""",
            (row["prompt_id"], body, sha, now_utc(), "legacy-backfill"),
        )
        conn.execute(
            "UPDATE prompts SET materialization_sha256=?,updated_at=? WHERE prompt_id=?",
            (sha, now_utc(), row["prompt_id"]),
        )
        updated += 1
    return updated


def canonical_prompt_text(conn: sqlite3.Connection, prompt_id: str) -> str | None:
    row = conn.execute(
        "SELECT body FROM prompt_materializations WHERE prompt_id=?",
        (prompt_id,),
    ).fetchone()
    return str(row["body"]) if row else None

def prompt_row(conn: sqlite3.Connection, prompt_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone()
    if not row:
        raise RoadmapDBError(f"prompt_not_found:{prompt_id}")
    return row

def ensure_historical_stub(
    conn: sqlite3.Connection,
    prompt_id: str,
    *,
    title: str | None = None,
    status: str = "unknown",
    actor: str = "system",
) -> None:
    if conn.execute("SELECT 1 FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone():
        return
    ts = now_utc()
    slug = f"prompt-{prompt_id}"
    conn.execute(
        """INSERT INTO prompts(
             prompt_id,slug,title,prompt_type,status,current_path,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (prompt_id, slug, title or f"Prompt {prompt_id}", "Prompt", status, "", ts, ts),
    )
    conn.execute(
        "INSERT INTO status_history(prompt_id,old_status,new_status,changed_at,actor,note) "
        "VALUES(?,?,?,?,?,?)",
        (prompt_id, None, status, ts, actor, "historical stub"),
    )

def register_prompt(
    conn: sqlite3.Connection,
    *,
    prompt_id: str,
    slug: str,
    title: str,
    current_path: str,
    project_id: str | None = None,
    project_name: str | None = None,
    repo: str | None = None,
    chat_guidance: str | None = None,
    prompt_type: str = "Prompt",
    model: str | None = None,
    reasoning: str | None = None,
    megavault_mode: str | None = None,
    campaign_id: str | None = None,
    explanation: str = "",
    status: str = "pending",
    queue_position: int | None = None,
    prompt_text: str | None = None,
    actor: str = "chatgpt",
) -> None:
    if not re.fullmatch(r"\d{6}", prompt_id):
        raise RoadmapDBError(f"invalid_prompt_id:{prompt_id}")
    if status not in ACTIVE_STATUS | TERMINAL_STATUS:
        raise RoadmapDBError(f"invalid_status:{status}")
    ts = now_utc()
    sha = materialization_hash(prompt_text) if prompt_text is not None else None
    existing = conn.execute("SELECT status FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone()
    if existing:
        raise RoadmapDBError(f"prompt_id_exists:{prompt_id}")
    conn.execute(
        """INSERT INTO prompts(
          prompt_id,slug,title,project_id,project_name,repo,chat_guidance,prompt_type,
          model,reasoning,megavault_mode,campaign_id,explanation,status,queue_position,
          current_path,materialization_sha256,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            prompt_id, slug, title, project_id, project_name, repo, chat_guidance,
            prompt_type, model, reasoning, megavault_mode, campaign_id, explanation,
            status, queue_position, current_path, sha, ts, ts,
        ),
    )
    if prompt_text is not None:
        conn.execute(
            """INSERT INTO prompt_materializations(prompt_id,body,sha256,created_at,actor)
               VALUES(?,?,?,?,?)""",
            (prompt_id, prompt_text, sha, ts, actor),
        )
    conn.execute(
        "INSERT INTO status_history(prompt_id,old_status,new_status,changed_at,actor,note) "
        "VALUES(?,?,?,?,?,?)",
        (prompt_id, None, status, ts, actor, "registered"),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (prompt_id, "prompt_registered", ts, actor, None),
    )

def assert_prompt_not_running(
    conn: sqlite3.Connection,
    prompt_id: str,
    action: str,
) -> sqlite3.Row:
    row = prompt_row(conn, prompt_id)
    if row["status"] == "running":
        raise RoadmapDBError(f"running_prompt_locked:{prompt_id}:{action}")
    return row

def set_status(
    conn: sqlite3.Connection,
    prompt_id: str,
    new_status: str,
    *,
    actor: str,
    note: str | None = None,
    allow_running_terminal: bool = False,
) -> None:
    if new_status not in ACTIVE_STATUS | TERMINAL_STATUS:
        raise RoadmapDBError(f"invalid_status:{new_status}")
    row = prompt_row(conn, prompt_id)
    old = row["status"]
    if old == new_status:
        return
    if old in TERMINAL_STATUS and new_status in ACTIVE_STATUS:
        raise RoadmapDBError(f"terminal_prompt_cannot_reactivate:{prompt_id}:{old}->{new_status}")
    if old == "pending" and new_status == "running":
        blockers = [
            dep["depends_on_prompt_id"]
            for dep in conn.execute(
                """SELECT d.depends_on_prompt_id
                   FROM dependencies d
                   JOIN prompts dep ON dep.prompt_id=d.depends_on_prompt_id
                   WHERE d.prompt_id=? AND dep.status<>'completed'
                   ORDER BY d.depends_on_prompt_id""",
                (prompt_id,),
            ).fetchall()
        ]
        if blockers:
            raise RoadmapDBError(
                f"prompt_dependencies_incomplete:{prompt_id}:{','.join(blockers)}"
            )
    if old == "running" and new_status != "running":
        if not (allow_running_terminal and new_status in (TERMINAL_STATUS - {"superseded"})):
            raise RoadmapDBError(f"running_prompt_locked:{prompt_id}:status:{new_status}")
    ts = now_utc()
    conn.execute(
        "UPDATE prompts SET status=?, updated_at=? WHERE prompt_id=?",
        (new_status, ts, prompt_id),
    )
    conn.execute(
        "INSERT INTO status_history(prompt_id,old_status,new_status,changed_at,actor,note) "
        "VALUES(?,?,?,?,?,?)",
        (prompt_id, old, new_status, ts, actor, note),
    )

def reconcile_terminal_requests(
    conn: sqlite3.Connection,
    *,
    actor: str = "single-writer",
) -> int:
    reconciled = 0
    rows = conn.execute(
        """SELECT tr.prompt_id,tr.requested_status,tr.note,p.status
           FROM terminal_requests tr
           JOIN prompts p ON p.prompt_id=tr.prompt_id
           ORDER BY tr.requested_at,tr.prompt_id"""
    ).fetchall()
    for row in rows:
        current = str(row["status"])
        requested = str(row["requested_status"])
        if current == requested:
            continue
        if current != "running":
            conn.execute(
                "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
                (
                    row["prompt_id"],
                    "terminal_reconcile_skipped",
                    now_utc(),
                    actor,
                    json.dumps(
                        {"current_status": current, "requested_status": requested},
                        sort_keys=True,
                    ),
                ),
            )
            continue
        set_status(
            conn,
            str(row["prompt_id"]),
            requested,
            actor=actor,
            note=row["note"] or f"terminal_reconcile:{requested}",
            allow_running_terminal=True,
        )
        reconciled += 1
    return reconciled


def set_model(
    conn: sqlite3.Connection,
    prompt_id: str,
    model: str,
    *,
    actor: str = "chatgpt",
    note: str | None = None,
) -> None:
    row = assert_prompt_not_running(conn, prompt_id, "model")
    old_model = row["model"]
    if old_model == model:
        return
    ts = now_utc()
    conn.execute(
        "UPDATE prompts SET model=?, updated_at=? WHERE prompt_id=?",
        (model, ts, prompt_id),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "prompt_model_updated",
            ts,
            actor,
            json.dumps(
                {"old_model": old_model, "new_model": model, "note": note},
                ensure_ascii=False,
                sort_keys=True,
            ),
        ),
    )

def set_explanation(
    conn: sqlite3.Connection,
    prompt_id: str,
    explanation: str,
    *,
    actor: str = "chatgpt",
    note: str | None = None,
) -> None:
    # `explanation` is presentation-only metadata used by human-facing
    # views. Updating it while a prompt is running does not alter the canonical
    # prompt body, execution parameters, dependencies, or workflow state.
    row = prompt_row(conn, prompt_id)
    old_explanation = row["explanation"] or ""
    if old_explanation == explanation:
        return
    ts = now_utc()
    conn.execute(
        "UPDATE prompts SET explanation=?, updated_at=? WHERE prompt_id=?",
        (explanation, ts, prompt_id),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "prompt_explanation_updated",
            ts,
            actor,
            json.dumps(
                {"old_explanation": old_explanation, "new_explanation": explanation, "note": note},
                ensure_ascii=False,
                sort_keys=True,
            ),
        ),
    )

def reorder_prompt(
    conn: sqlite3.Connection,
    prompt_id: str,
    queue_position: int,
    *,
    actor: str = "chatgpt",
    note: str | None = None,
) -> None:
    if queue_position < 1:
        raise RoadmapDBError(f"invalid_queue_position:{queue_position}")
    row = assert_prompt_not_running(conn, prompt_id, "reorder")
    if row["status"] not in ACTIVE_STATUS:
        raise RoadmapDBError(f"reorder_terminal_prompt:{prompt_id}:{row['status']}")
    old_position = row["queue_position"]
    if old_position == queue_position:
        return
    ts = now_utc()
    conn.execute(
        "UPDATE prompts SET queue_position=?, updated_at=? WHERE prompt_id=?",
        (queue_position, ts, prompt_id),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "prompt_reordered",
            ts,
            actor,
            json.dumps({"old_queue_position": old_position, "new_queue_position": queue_position, "note": note}, ensure_ascii=False, sort_keys=True),
        ),
    )

def add_dependency(conn: sqlite3.Connection, prompt_id: str, depends_on: str, *, note: str | None = None) -> None:
    assert_prompt_not_running(conn, prompt_id, "dependency")
    prompt_row(conn, depends_on)
    conn.execute(
        "INSERT OR IGNORE INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
        (prompt_id, depends_on, note),
    )

def replace_dependency(
    conn: sqlite3.Connection,
    prompt_id: str,
    old_depends_on: str,
    new_depends_on: str,
    *,
    actor: str = "chatgpt",
    note: str | None = None,
) -> None:
    assert_prompt_not_running(conn, prompt_id, "dependency_replace")
    prompt_row(conn, old_depends_on)
    prompt_row(conn, new_depends_on)
    if old_depends_on == new_depends_on:
        return
    existing = conn.execute(
        "SELECT 1 FROM dependencies WHERE prompt_id=? AND depends_on_prompt_id=?",
        (prompt_id, old_depends_on),
    ).fetchone()
    if not existing:
        already_forwarded = conn.execute(
            "SELECT 1 FROM dependencies WHERE prompt_id=? AND depends_on_prompt_id=?",
            (prompt_id, new_depends_on),
        ).fetchone()
        if already_forwarded:
            return
        raise RoadmapDBError(f"dependency_not_found:{prompt_id}:{old_depends_on}")
    conn.execute(
        "INSERT OR IGNORE INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
        (prompt_id, new_depends_on, note),
    )
    conn.execute(
        "DELETE FROM dependencies WHERE prompt_id=? AND depends_on_prompt_id=?",
        (prompt_id, old_depends_on),
    )
    ts = now_utc()
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "dependency_replaced",
            ts,
            actor,
            json.dumps(
                {"old_depends_on": old_depends_on, "new_depends_on": new_depends_on, "note": note},
                ensure_ascii=False,
                sort_keys=True,
            ),
        ),
    )

def add_relation(
    conn: sqlite3.Connection,
    from_prompt_id: str,
    to_prompt_id: str,
    relation_type: str,
    *,
    actor: str,
    note: str | None = None,
) -> None:
    source = assert_prompt_not_running(conn, from_prompt_id, f"relation:{relation_type}")
    target = prompt_row(conn, to_prompt_id)
    if target["status"] == "running":
        raise RoadmapDBError(f"running_prompt_locked:{to_prompt_id}:relation_target:{relation_type}")
    ts = now_utc()
    conn.execute(
        """INSERT OR IGNORE INTO prompt_relations(
             from_prompt_id,to_prompt_id,relation_type,created_at,actor,note
           ) VALUES(?,?,?,?,?,?)""",
        (from_prompt_id, to_prompt_id, relation_type, ts, actor, note),
    )

    # Fix/replacement/merge relations are dependency successors. Pending children
    # should follow the new prompt automatically so a terminal parent never
    # strands the rest of the queue. Running children remain immutable.
    if relation_type in {"fix", "replacement", "merge"}:
        children = conn.execute(
            """SELECT d.prompt_id,d.note
               FROM dependencies d
               JOIN prompts p ON p.prompt_id=d.prompt_id
               WHERE d.depends_on_prompt_id=? AND p.status='pending'
               ORDER BY d.prompt_id""",
            (from_prompt_id,),
        ).fetchall()
        for child in children:
            child_id = str(child["prompt_id"])
            if child_id == to_prompt_id:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
                (
                    child_id,
                    to_prompt_id,
                    child["note"] or f"auto-forwarded from {from_prompt_id}",
                ),
            )
            conn.execute(
                "DELETE FROM dependencies WHERE prompt_id=? AND depends_on_prompt_id=?",
                (child_id, from_prompt_id),
            )
            conn.execute(
                "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
                (
                    child_id,
                    "dependency_auto_forwarded",
                    ts,
                    actor,
                    json.dumps(
                        {
                            "from_prompt_id": from_prompt_id,
                            "to_prompt_id": to_prompt_id,
                            "relation_type": relation_type,
                        },
                        sort_keys=True,
                    ),
                ),
            )

    if relation_type in {"replacement", "merge"} and source["status"] == "pending":
        set_status(
            conn,
            from_prompt_id,
            "superseded",
            actor=actor,
            note=note or f"auto-superseded by {relation_type}:{to_prompt_id}",
        )

def add_tag(conn: sqlite3.Connection, prompt_id: str, tag: str) -> None:
    assert_prompt_not_running(conn, prompt_id, "tag")
    conn.execute("INSERT OR IGNORE INTO prompt_tags(prompt_id,tag) VALUES(?,?)", (prompt_id, tag))

def request_terminal(
    conn: sqlite3.Connection,
    prompt_id: str,
    requested_status: str,
    *,
    actor: str = "codex",
    note: str | None = None,
) -> None:
    if requested_status not in (TERMINAL_STATUS - {"superseded"}):
        raise RoadmapDBError(f"invalid_terminal_request:{requested_status}")
    row = prompt_row(conn, prompt_id)
    existing = conn.execute(
        "SELECT requested_status FROM terminal_requests WHERE prompt_id=?",
        (prompt_id,),
    ).fetchone()
    if existing:
        if existing["requested_status"] != requested_status:
            raise RoadmapDBError(
                f"terminal_request_conflict:{prompt_id}:{existing['requested_status']}->{requested_status}"
            )
        if row["status"] == requested_status:
            return
        if row["status"] != "running":
            raise RoadmapDBError(
                f"terminal_request_state_conflict:{prompt_id}:{row['status']}->{requested_status}"
            )
    else:
        if row["status"] == requested_status:
            return
        if row["status"] != "running":
            raise RoadmapDBError(f"terminal_request_requires_running:{prompt_id}:{row['status']}")
        ts = now_utc()
        conn.execute(
            """INSERT INTO terminal_requests(prompt_id,requested_status,actor,note,requested_at)
               VALUES(?,?,?,?,?)""",
            (prompt_id, requested_status, actor, note, ts),
        )
        conn.execute(
            "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
            (
                prompt_id,
                "terminal_requested",
                ts,
                actor,
                json.dumps(
                    {"requested_status": requested_status, "note": note},
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            ),
        )

    # The explicit terminal request is authoritative for scheduling. Finalize now
    # so children of PASS prompts become runnable immediately and stale locks can
    # be reclaimed without waiting for telemetry. codex-usage remains an
    # independent audit/metrics source and can later record identity conflicts or
    # an outcome mismatch without keeping the roadmap stuck in running.
    set_status(
        conn,
        prompt_id,
        requested_status,
        actor=actor,
        note=note or f"terminal_request:{requested_status}",
        allow_running_terminal=True,
    )

def record_execution(
    conn: sqlite3.Connection,
    prompt_id: str,
    *,
    cycle_key: str | None = None,
    materialization_sha256: str | None = None,
    started_at: str | None = None,
    ended_at: str | None = None,
    outcome: str | None = None,
    duration_seconds: float | None = None,
    model: str | None = None,
    reasoning: str | None = None,
    codex_project: str | None = None,
    chat_title: str | None = None,
    branch: str | None = None,
    commit_before: str | None = None,
    commit_after: str | None = None,
    tool_call_count: int | None = None,
    input_tokens: int | None = None,
    cached_input_tokens: int | None = None,
    uncached_input_tokens: int | None = None,
    output_tokens: int | None = None,
    reasoning_output_tokens: int | None = None,
    total_tokens: int | None = None,
    source: str = "manual",
    actor: str = "codex",
    update_status: bool = True,
    allow_running_terminal: bool = False,
) -> int:
    row = prompt_row(conn, prompt_id)
    if outcome is not None and outcome not in FINAL_STATUS:
        raise RoadmapDBError(f"invalid_outcome:{outcome}")
    ts = now_utc()
    values = (
        prompt_id, cycle_key, materialization_sha256, started_at, ended_at, outcome,
        duration_seconds, model, reasoning, codex_project, chat_title, branch,
        commit_before, commit_after, tool_call_count, input_tokens, cached_input_tokens,
        uncached_input_tokens, output_tokens, reasoning_output_tokens, total_tokens,
        source, ts,
    )
    if cycle_key:
        existing = conn.execute("SELECT execution_id FROM executions WHERE cycle_key=?", (cycle_key,)).fetchone()
        if existing:
            return int(existing["execution_id"])
    cur = conn.execute(
        """INSERT INTO executions(
          prompt_id,cycle_key,materialization_sha256,started_at,ended_at,outcome,duration_seconds,
          model,reasoning,codex_project,chat_title,branch,commit_before,commit_after,tool_call_count,
          input_tokens,cached_input_tokens,uncached_input_tokens,output_tokens,
          reasoning_output_tokens,total_tokens,source,recorded_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        values,
    )
    if update_status:
        if outcome:
            target_status = FINAL_STATUS[outcome]
            terminal_request = conn.execute(
                "SELECT requested_status FROM terminal_requests WHERE prompt_id=?",
                (prompt_id,),
            ).fetchone()
            if terminal_request and terminal_request["requested_status"] != target_status:
                conn.execute(
                    "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
                    (
                        prompt_id,
                        "terminal_outcome_mismatch",
                        ts,
                        actor,
                        json.dumps(
                            {
                                "requested_status": terminal_request["requested_status"],
                                "observed_status": target_status,
                                "source": source,
                            },
                            sort_keys=True,
                        ),
                    ),
                )
            else:
                set_status(
                    conn,
                    prompt_id,
                    target_status,
                    actor=actor,
                    note=f"execution:{source}",
                    allow_running_terminal=allow_running_terminal,
                )
                conn.execute("DELETE FROM terminal_requests WHERE prompt_id=?", (prompt_id,))
        elif row["status"] == "pending":
            set_status(conn, prompt_id, "running", actor=actor, note=f"execution_started:{source}")
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (prompt_id, "execution_recorded", ts, actor, json.dumps({"source":source,"outcome":outcome}, sort_keys=True)),
    )
    return int(cur.lastrowid)

def record_terminal(
    conn: sqlite3.Connection,
    prompt_id: str,
    result: str,
    *,
    actor: str = "codex",
    source: str = "roadmap_result",
    note: str | None = None,
) -> None:
    if result not in FINAL_STATUS:
        raise RoadmapDBError(f"invalid_outcome:{result}")
    request_terminal(
        conn,
        prompt_id,
        FINAL_STATUS[result],
        actor=actor,
        note=f"terminal:{source}:{result}" if note is None else note,
    )

def record_analysis(
    conn: sqlite3.Connection,
    prompt_id: str,
    *,
    actor: str = "chatgpt",
    bottlenecks_found: bool | None = None,
    summary: str | None = None,
    fix_prompt_id: str | None = None,
    source_ref: str | None = None,
) -> None:
    assert_prompt_not_running(conn, prompt_id, "analysis")
    if fix_prompt_id is not None:
        prompt_row(conn, fix_prompt_id)
    ts = now_utc()
    conn.execute(
        """INSERT INTO analyses(prompt_id,analyzed_at,actor,bottlenecks_found,summary,fix_prompt_id,source_ref)
           VALUES(?,?,?,?,?,?,?)""",
        (prompt_id, ts, actor, None if bottlenecks_found is None else int(bottlenecks_found), summary, fix_prompt_id, source_ref),
    )
    if fix_prompt_id:
        add_relation(conn, prompt_id, fix_prompt_id, "fix", actor=actor, note="analysis-generated fix")
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (prompt_id, "analysis_recorded", ts, actor, json.dumps({"fix_prompt_id":fix_prompt_id}, sort_keys=True)),
    )

def record_code_change(
    conn: sqlite3.Connection,
    prompt_id: str,
    *,
    repository: str,
    change_type: str,
    commit_sha: str | None = None,
    summary: str | None = None,
    analysis_id: int | None = None,
    actor: str = "chatgpt",
) -> int:
    assert_prompt_not_running(conn, prompt_id, "code_change")
    if analysis_id is None:
        row = conn.execute(
            "SELECT analysis_id FROM analyses WHERE prompt_id=? "
            "ORDER BY analyzed_at DESC, analysis_id DESC LIMIT 1",
            (prompt_id,),
        ).fetchone()
        if not row:
            raise RoadmapDBError(f"analysis_required_before_code_change:{prompt_id}")
        analysis_id = int(row["analysis_id"])
    else:
        row = conn.execute(
            "SELECT prompt_id FROM analyses WHERE analysis_id=?",
            (analysis_id,),
        ).fetchone()
        if not row or row["prompt_id"] != prompt_id:
            raise RoadmapDBError(f"analysis_prompt_mismatch:{analysis_id}:{prompt_id}")
    ts = now_utc()
    cur = conn.execute(
        """INSERT INTO analysis_code_changes(
             analysis_id,prompt_id,repository,change_type,commit_sha,summary,created_at,actor
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (analysis_id,prompt_id,repository,change_type,commit_sha,summary,ts,actor),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "analysis_code_change_recorded",
            ts,
            actor,
            json.dumps(
                {
                    "analysis_id": analysis_id,
                    "repository": repository,
                    "change_type": change_type,
                    "commit_sha": commit_sha,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        ),
    )
    return int(cur.lastrowid)

def next_runnable(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM v_runnable_prompts LIMIT 1").fetchone()

def summary_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT * FROM v_prompt_summary ORDER BY "
        "CASE WHEN status='running' THEN 0 WHEN status='pending' THEN 1 ELSE 2 END,"
        "COALESCE(queue_position,2147483647), created_at, prompt_id"
    ))

def reconcile_prompt_file_locations(repo: Path) -> int:
    from roadmap_render import reconcile_prompt_file_locations as _impl
    return _impl(repo)

def render(repo: Path) -> list[str]:
    from roadmap_render import render as _impl
    return _impl(repo)

def verify(repo: Path) -> dict[str, Any]:
    repo=Path(repo)
    conn=connect(repo, writable=False)
    problems=[]
    fk=conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk:
        problems.append(f"foreign_key_errors:{len(fk)}")
    dup=conn.execute("SELECT prompt_id,COUNT(*) c FROM prompts GROUP BY prompt_id HAVING c>1").fetchall()
    if dup:
        problems.append("duplicate_prompt_ids")
    bad=conn.execute(
        "SELECT p.prompt_id FROM prompts p WHERE p.status='pending' AND p.current_path NOT LIKE 'prompts/%'"
    ).fetchall()
    if bad:
        problems.append("pending_path_invalid:" + ",".join(r[0] for r in bad))
    unhashed=conn.execute(
        "SELECT p.prompt_id FROM prompts p "
        "WHERE p.status IN ('pending','running') AND p.materialization_sha256 IS NULL"
    ).fetchall()
    if unhashed:
        problems.append("active_prompt_fingerprint_missing:" + ",".join(r[0] for r in unhashed))
    has_materializations = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='prompt_materializations'"
    ).fetchone()
    if has_materializations:
        missing_body=conn.execute(
            """SELECT p.prompt_id FROM prompts p
               LEFT JOIN prompt_materializations m ON m.prompt_id=p.prompt_id
               WHERE p.status IN ('pending','running') AND m.prompt_id IS NULL"""
        ).fetchall()
        if missing_body:
            problems.append("active_prompt_body_missing:" + ",".join(r[0] for r in missing_body))
    result={
        "ok": not problems,
        "problems": problems,
        "prompts": conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0],
        "executions": conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0],
        "analyses": conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0],
        "chatgpt_code_changes": conn.execute("SELECT COUNT(*) FROM analysis_code_changes").fetchone()[0],
        "attention": conn.execute("SELECT COUNT(*) FROM v_attention").fetchone()[0],
    }
    conn.close()
    return result

def apply_mutation(conn: sqlite3.Connection, mutation: dict[str, Any], *, default_actor: str = "chatgpt") -> None:
    op=mutation.get("op")
    actor=mutation.get("actor") or default_actor
    if op=="reconcile_terminals":
        reconcile_terminal_requests(conn, actor=actor)
    elif op=="analysis":
        record_analysis(
            conn, str(mutation["prompt_id"]), actor=actor,
            bottlenecks_found=mutation.get("bottlenecks_found"),
            summary=mutation.get("summary"), fix_prompt_id=mutation.get("fix_prompt_id"),
            source_ref=mutation.get("source_ref"),
        )
    elif op=="model":
        set_model(
            conn,
            str(mutation["prompt_id"]),
            str(mutation["model"]),
            actor=actor,
            note=mutation.get("note"),
        )
    elif op=="explanation":
        set_explanation(
            conn,
            str(mutation["prompt_id"]),
            str(mutation["explanation"]),
            actor=actor,
            note=mutation.get("note"),
        )
    elif op=="terminal_request":
        request_terminal(
            conn,
            str(mutation["prompt_id"]),
            str(mutation["status"]),
            actor=actor,
            note=mutation.get("note"),
        )
    elif op=="status":
        set_status(conn,str(mutation["prompt_id"]),str(mutation["status"]),actor=actor,note=mutation.get("note"))
    elif op=="relation":
        add_relation(conn,str(mutation["from_prompt_id"]),str(mutation["to_prompt_id"]),str(mutation["relation_type"]),actor=actor,note=mutation.get("note"))
    elif op=="dependency":
        add_dependency(conn,str(mutation["prompt_id"]),str(mutation["depends_on_prompt_id"]),note=mutation.get("note"))
    elif op=="dependency_replace":
        replace_dependency(
            conn,
            str(mutation["prompt_id"]),
            str(mutation["old_depends_on_prompt_id"]),
            str(mutation["new_depends_on_prompt_id"]),
            actor=actor,
            note=mutation.get("note"),
        )
    elif op=="reorder":
        reorder_prompt(
            conn,
            str(mutation["prompt_id"]),
            int(mutation["queue_position"]),
            actor=actor,
            note=mutation.get("note"),
        )
    elif op=="tag":
        add_tag(conn,str(mutation["prompt_id"]),str(mutation["tag"]))
    elif op=="code_change":
        record_code_change(
            conn,
            str(mutation["prompt_id"]),
            repository=str(mutation["repository"]),
            change_type=str(mutation["change_type"]),
            commit_sha=mutation.get("commit_sha"),
            summary=mutation.get("summary"),
            analysis_id=mutation.get("analysis_id"),
            actor=actor,
        )
    elif op in {"execution","usage_execution"}:
        prompt_id=str(mutation["prompt_id"])
        kwargs={k:mutation.get(k) for k in (
            "cycle_key","materialization_sha256","started_at","ended_at","outcome","duration_seconds",
            "model","reasoning","codex_project","chat_title","branch","commit_before","commit_after",
            "tool_call_count","input_tokens","cached_input_tokens","uncached_input_tokens","output_tokens",
            "reasoning_output_tokens","total_tokens","source"
        ) if k in mutation}
        update_status=True
        if op=="usage_execution":
            row=prompt_row(conn,prompt_id)
            observed=mutation.get("materialization_sha256")
            expected=row["materialization_sha256"]
            cycle_key=mutation.get("cycle_key")
            conflict=bool(expected and observed and expected != observed)
            if conflict:
                existing=conn.execute(
                    """SELECT 1 FROM identity_conflicts
                       WHERE prompt_id=? AND observed_cycle_key IS ? AND observed_sha256=?""",
                    (prompt_id,cycle_key,observed),
                ).fetchone()
                if not existing:
                    conn.execute(
                        """INSERT INTO identity_conflicts(
                             prompt_id,observed_cycle_key,expected_sha256,observed_sha256,detected_at,source
                           ) VALUES(?,?,?,?,?,?)""",
                        (prompt_id,cycle_key,expected,observed,now_utc(),"codex-usage"),
                    )
                update_status=False
        record_execution(
            conn,
            prompt_id,
            actor=actor,
            update_status=update_status,
            allow_running_terminal=(op=="usage_execution"),
            **kwargs,
        )
    elif op=="register":
        data={k:v for k,v in mutation.items() if k not in {"op","actor"}}
        register_prompt(conn,actor=actor,**data)
    else:
        raise RoadmapDBError(f"unknown_mutation_op:{op}")

def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Manage codex-roadmap SQLite source of truth.")
    p.add_argument("--repo",default=".")
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("verify")
    sub.add_parser("render")
    sub.add_parser("select")
    st=sub.add_parser("status")
    st.add_argument("--prompt-id",required=True); st.add_argument("--status",required=True); st.add_argument("--actor",default="chatgpt"); st.add_argument("--note")
    an=sub.add_parser("analyze")
    an.add_argument("--prompt-id",required=True); an.add_argument("--actor",default="chatgpt")
    an.add_argument("--bottlenecks-found",choices=("yes","no","unknown"),default="unknown")
    an.add_argument("--summary"); an.add_argument("--fix-prompt-id"); an.add_argument("--source-ref")
    rel=sub.add_parser("relate")
    rel.add_argument("--from-prompt-id",required=True); rel.add_argument("--to-prompt-id",required=True)
    rel.add_argument("--relation-type",required=True); rel.add_argument("--actor",default="chatgpt"); rel.add_argument("--note")
    term=sub.add_parser("terminal")
    term.add_argument("--prompt-id",required=True); term.add_argument("--result",required=True,choices=tuple(FINAL_STATUS))
    term.add_argument("--actor",default="codex"); term.add_argument("--note")
    return p

def main(argv: list[str] | None=None) -> int:
    args=build_parser().parse_args(argv)
    repo=Path(args.repo).expanduser().resolve()
    if args.cmd=="verify":
        print(json.dumps(verify(repo),sort_keys=True)); return 0
    if args.cmd=="select":
        conn=connect(repo,writable=False)
        try:
            row=next_runnable(conn)
            print(json.dumps(dict(row) if row else {"status":"empty"},sort_keys=True))
        finally:
            conn.close()
        return 0

    # Canonical roadmap writes and generated-view refreshes are single-writer only.
    # Operational clients must submit a codex-roadmap.mutation.v1 GitHub Issue via
    # tools/submit_mutation.py (terminal results use roadmap_result/roadmap_finish).
    print(json.dumps({
        "status":"blocked",
        "error":"direct_roadmap_write_forbidden",
        "command":args.cmd,
        "use":"tools/submit_mutation.py -> [roadmap-mutation] Issue -> GitHub Actions single writer",
    },sort_keys=True))
    return 2

if __name__=="__main__":
    raise SystemExit(main())
