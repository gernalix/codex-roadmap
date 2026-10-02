#!/usr/bin/env python3
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from roadmap_db import RoadmapDBError, canonical_prompt_text, connect, now_utc, prompt_row, summary_rows

_PROMPT_ID_HEADER_RE = re.compile(r"(?m)^PROMPT_ID\s*[:=]\s*\d{6}\s*$")


def _project_prompt_body(prompt_id: str, body: str) -> str:
    if _PROMPT_ID_HEADER_RE.search(body):
        return body
    return f"PROMPT_ID={prompt_id}\n\n{body}"


_FINAL_STATUS_OUTCOME = {
    "completed": "PASS",
    "failed": "FAIL",
    "blocked": "BLOCKED",
    "cancelled": "CANCELLED",
    "unknown": "UNKNOWN",
}

def _effective_outcome(row: sqlite3.Row | dict[str, Any]) -> Any:
    """Prefer the authoritative terminal roadmap state over stale telemetry."""
    return _FINAL_STATUS_OUTCOME.get(row["status"], row["last_outcome"])


def reconcile_prompt_file_locations(repo: Path) -> int:
    """Keep prompt file directory consistent with terminal status without inventing files."""
    repo=Path(repo)
    from c3_storage import REPO, CANONICAL_DB
    if repo.resolve() == REPO.resolve() and CANONICAL_DB.exists():
        raise RoadmapDBError('legacy_file_lifecycle_retired_use_c3_writer')
    conn=connect(repo)
    moved=0
    try:
        rows=conn.execute(
            "SELECT prompt_id,slug,status,current_path FROM prompts WHERE current_path<>''"
        ).fetchall()
        for row in rows:
            current=row["current_path"]
            src=repo/current
            if row["status"]=="completed":
                target_dir="completed"
                target_name=src.name
            elif row["status"] in ("failed","blocked","cancelled","superseded","unknown"):
                target_dir="falliti"
                target_name=src.name
            else:
                target_dir="prompts"
                target_name=f"{row['slug']}.md"
            dest_rel=f"{target_dir}/{target_name}"
            if current==dest_rel:
                continue
            dest=repo/dest_rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            if src.is_file():
                if dest.exists():
                    if src.read_bytes()!=dest.read_bytes():
                        raise RoadmapDBError(f"archive_destination_exists:{dest_rel}")
                    src.unlink()
                else:
                    src.rename(dest)
            elif dest.is_file():
                body=canonical_prompt_text(conn,str(row["prompt_id"]))
                if body is None or dest.read_text(encoding="utf-8")!=body:
                    raise RoadmapDBError(f"prompt_materialization_conflict:{dest_rel}")
            else:
                continue
            if conn.execute(
                "SELECT type FROM sqlite_master WHERE name='prompts'"
            ).fetchone()[0] == "view":
                conn.execute(
                    "UPDATE prompt_metadata SET current_path=?,updated_at=? WHERE prompt_id=?",
                    (dest_rel,now_utc(),row["prompt_id"]),
                )
            else:
                conn.execute(
                    "UPDATE prompts SET current_path=?,updated_at=? WHERE prompt_id=?",
                    (dest_rel,now_utc(),row["prompt_id"]),
                )
            moved += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return moved

def render(repo: Path) -> list[str]:
    repo = Path(repo)
    conn = connect(repo, writable=False)
    rows = summary_rows(conn)

    # Optional prompt-file export only. Operational clients use SQLite/API;
    # historical current_path links remain reconstructible, never authoritative.
    for row in rows:
        current_path = str(row["current_path"] or "")
        if not current_path.endswith(".md"):
            continue
        body = canonical_prompt_text(conn, str(row["prompt_id"]))
        if body is None:
            continue
        path = repo / current_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_project_prompt_body(str(row["prompt_id"]), body), encoding="utf-8")

    conn.close()
    return []
