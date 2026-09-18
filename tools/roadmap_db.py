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
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    if writable:
        ensure_schema(conn)
    return conn

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute(
        "INSERT INTO meta(key,value) VALUES('schema_version','1') "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
    )
    conn.commit()

def materialization_hash(text: str) -> str:
    # Normalize the same superficial escaping used by usage exports; raw text is never stored.
    text = html.unescape(text or "")
    text = text.replace("\\_", "_")
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def refresh_materialization_hashes(conn: sqlite3.Connection, repo: Path) -> int:
    updated = 0
    for row in conn.execute(
        "SELECT prompt_id,current_path FROM prompts "
        "WHERE materialization_sha256 IS NULL AND current_path<>''"
    ).fetchall():
        path = Path(repo) / row["current_path"]
        if not path.is_file():
            continue
        sha = materialization_hash(path.read_text(encoding="utf-8"))
        conn.execute(
            "UPDATE prompts SET materialization_sha256=?,updated_at=? WHERE prompt_id=?",
            (sha, now_utc(), row["prompt_id"]),
        )
        updated += 1
    return updated

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
    conn.execute(
        "INSERT INTO status_history(prompt_id,old_status,new_status,changed_at,actor,note) "
        "VALUES(?,?,?,?,?,?)",
        (prompt_id, None, status, ts, actor, "registered"),
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (prompt_id, "prompt_registered", ts, actor, None),
    )

def set_status(
    conn: sqlite3.Connection,
    prompt_id: str,
    new_status: str,
    *,
    actor: str,
    note: str | None = None,
) -> None:
    if new_status not in ACTIVE_STATUS | TERMINAL_STATUS:
        raise RoadmapDBError(f"invalid_status:{new_status}")
    row = prompt_row(conn, prompt_id)
    old = row["status"]
    if old == new_status:
        return
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

def add_dependency(conn: sqlite3.Connection, prompt_id: str, depends_on: str, *, note: str | None = None) -> None:
    prompt_row(conn, prompt_id)
    prompt_row(conn, depends_on)
    conn.execute(
        "INSERT OR IGNORE INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
        (prompt_id, depends_on, note),
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
    prompt_row(conn, from_prompt_id)
    prompt_row(conn, to_prompt_id)
    ts = now_utc()
    conn.execute(
        """INSERT OR IGNORE INTO prompt_relations(
             from_prompt_id,to_prompt_id,relation_type,created_at,actor,note
           ) VALUES(?,?,?,?,?,?)""",
        (from_prompt_id, to_prompt_id, relation_type, ts, actor, note),
    )

def add_tag(conn: sqlite3.Connection, prompt_id: str, tag: str) -> None:
    prompt_row(conn, prompt_id)
    conn.execute("INSERT OR IGNORE INTO prompt_tags(prompt_id,tag) VALUES(?,?)", (prompt_id, tag))

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
) -> int:
    prompt_row(conn, prompt_id)
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
            set_status(conn, prompt_id, FINAL_STATUS[outcome], actor=actor, note=f"execution:{source}")
        else:
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
    ts = now_utc()
    set_status(
        conn,
        prompt_id,
        FINAL_STATUS[result],
        actor=actor,
        note=f"terminal:{source}",
    )
    conn.execute(
        "INSERT INTO audit_events(prompt_id,event_type,event_at,actor,payload_json) VALUES(?,?,?,?,?)",
        (
            prompt_id,
            "terminal_result",
            ts,
            actor,
            json.dumps({"result": result, "source": source, "note": note}, ensure_ascii=False, sort_keys=True),
        ),
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
    prompt_row(conn, prompt_id)
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

def next_runnable(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM v_runnable_prompts LIMIT 1").fetchone()

def summary_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT * FROM v_prompt_summary ORDER BY "
        "CASE WHEN status='pending' THEN 0 WHEN status='running' THEN 1 ELSE 2 END,"
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
        "WHERE p.current_path LIKE 'prompts/%' AND p.materialization_sha256 IS NULL"
    ).fetchall()
    if unhashed:
        problems.append("active_prompt_fingerprint_missing:" + ",".join(r[0] for r in unhashed))
    result={
        "ok": not problems,
        "problems": problems,
        "prompts": conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0],
        "executions": conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0],
        "analyses": conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0],
        "attention": conn.execute("SELECT COUNT(*) FROM v_attention").fetchone()[0],
    }
    conn.close()
    return result

def apply_mutation(conn: sqlite3.Connection, mutation: dict[str, Any], *, default_actor: str = "chatgpt") -> None:
    op=mutation.get("op")
    actor=mutation.get("actor") or default_actor
    if op=="analysis":
        record_analysis(
            conn, str(mutation["prompt_id"]), actor=actor,
            bottlenecks_found=mutation.get("bottlenecks_found"),
            summary=mutation.get("summary"), fix_prompt_id=mutation.get("fix_prompt_id"),
            source_ref=mutation.get("source_ref"),
        )
    elif op=="status":
        set_status(conn,str(mutation["prompt_id"]),str(mutation["status"]),actor=actor,note=mutation.get("note"))
    elif op=="relation":
        add_relation(conn,str(mutation["from_prompt_id"]),str(mutation["to_prompt_id"]),str(mutation["relation_type"]),actor=actor,note=mutation.get("note"))
    elif op=="dependency":
        add_dependency(conn,str(mutation["prompt_id"]),str(mutation["depends_on_prompt_id"]),note=mutation.get("note"))
    elif op=="tag":
        add_tag(conn,str(mutation["prompt_id"]),str(mutation["tag"]))
    elif op=="execution":
        kwargs={k:mutation.get(k) for k in (
            "cycle_key","materialization_sha256","started_at","ended_at","outcome","duration_seconds",
            "model","reasoning","codex_project","chat_title","branch","commit_before","commit_after",
            "tool_call_count","input_tokens","cached_input_tokens","uncached_input_tokens","output_tokens",
            "reasoning_output_tokens","total_tokens","source"
        ) if k in mutation}
        record_execution(conn,str(mutation["prompt_id"]),actor=actor,**kwargs)
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
    if args.cmd=="render":
        print(json.dumps({"rendered":render(repo)},sort_keys=True)); return 0
    conn=connect(repo)
    try:
        if args.cmd=="select":
            row=next_runnable(conn)
            print(json.dumps(dict(row) if row else {"status":"empty"},sort_keys=True)); return 0
        if args.cmd=="status":
            set_status(conn,args.prompt_id,args.status,actor=args.actor,note=args.note)
        elif args.cmd=="analyze":
            bf=None if args.bottlenecks_found=="unknown" else args.bottlenecks_found=="yes"
            record_analysis(conn,args.prompt_id,actor=args.actor,bottlenecks_found=bf,summary=args.summary,fix_prompt_id=args.fix_prompt_id,source_ref=args.source_ref)
        elif args.cmd=="relate":
            add_relation(conn,args.from_prompt_id,args.to_prompt_id,args.relation_type,actor=args.actor,note=args.note)
        elif args.cmd=="terminal":
            record_terminal(conn,args.prompt_id,args.result,actor=args.actor,note=args.note)
        conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()
    render(repo)
    print(json.dumps({"status":"ok","command":args.cmd},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
