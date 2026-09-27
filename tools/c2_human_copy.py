"""Human-facing presentation copy for C2 entities.

This table is presentation-only: it never changes lifecycle, dependencies, priority,
or canonical technical titles.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3

import c2_identity

ENTITY_KINDS = {"work_item", "issue"}
STATUSES = {"complete", "fallback", "needs_clarification"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS c2_human_copy (
  entity_kind TEXT NOT NULL CHECK(entity_kind IN ('work_item','issue')),
  entity_id TEXT NOT NULL,
  human_title TEXT NOT NULL,
  ai_title TEXT NOT NULL,
  human_summary TEXT NOT NULL,
  copy_status TEXT NOT NULL DEFAULT 'complete'
    CHECK(copy_status IN ('complete','fallback','needs_clarification')),
  source TEXT NOT NULL DEFAULT 'ai',
  source_sha256 TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(entity_kind, entity_id)
);
CREATE INDEX IF NOT EXISTS idx_c2_human_copy_status
  ON c2_human_copy(copy_status, entity_kind, entity_id);
"""

class HumanCopyError(RuntimeError):
    pass

def install_schema(conn: sqlite3.Connection) -> None:
    statement = ""
    for line in SCHEMA.splitlines():
        statement += line + "\n"
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ""
    if statement.strip():
        raise HumanCopyError("incomplete_human_copy_schema")

def _one_line(value: object, field: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        raise HumanCopyError(field + "_required")
    return text

def _validate(human_title: str, ai_title: str, human_summary: str, copy_status: str) -> tuple[str,str,str,str]:
    human_title = _one_line(human_title, "human_title")
    ai_title = _one_line(ai_title, "ai_title")
    human_summary = _one_line(human_summary, "human_summary")
    copy_status = str(copy_status or "complete").strip()
    if copy_status not in STATUSES:
        raise HumanCopyError("invalid_copy_status")
    if len(human_title) > 120:
        raise HumanCopyError("human_title_too_long")
    if len(ai_title) > 220:
        raise HumanCopyError("ai_title_too_long")
    if len(human_summary) > 600:
        raise HumanCopyError("human_summary_too_long")
    if human_title.endswith(("...", "…")):
        raise HumanCopyError("human_title_must_not_be_truncated")
    return human_title, ai_title, human_summary, copy_status

def source_document(conn: sqlite3.Connection, entity_kind: str, entity_id: str) -> dict:
    """Return the lifecycle-aware source used to fence asynchronous humanization."""
    if entity_kind == "work_item":
        row = conn.execute(
            """SELECT title,objective,status,current_action,next_action,blocker
               FROM work_items WHERE work_item_id=?""",
            (entity_id,),
        ).fetchone()
        if not row:
            raise HumanCopyError("work_item_not_found")
        return {
            "title": row[0], "objective": row[1], "status": row[2],
            "current_action": row[3], "next_action": row[4], "blocker": row[5],
        }
    if entity_kind == "issue":
        row = conn.execute(
            """SELECT description,state,matched_work_item_id,promoted_work_item_id,
                      disposition_reason
               FROM issue_inbox WHERE issue_id=?""",
            (entity_id,),
        ).fetchone()
        if not row:
            raise HumanCopyError("issue_not_found")
        return {
            "description": row[0], "state": row[1],
            "matched_work_item_id": row[2], "promoted_work_item_id": row[3],
            "disposition_reason": row[4],
        }
    raise HumanCopyError("invalid_entity_kind")

def source_sha256(conn: sqlite3.Connection, entity_kind: str, entity_id: str) -> str:
    raw = json.dumps(
        source_document(conn, entity_kind, entity_id),
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode()
    return hashlib.sha256(raw).hexdigest()

def set_copy(
    conn: sqlite3.Connection,
    *,
    entity_kind: str,
    entity_id: str,
    human_title: str,
    ai_title: str,
    human_summary: str,
    copy_status: str = "complete",
    source: str = "ai",
    expected_source_sha256: str | None = None,
) -> dict:
    if not conn.in_transaction:
        raise HumanCopyError("canonical_writer_transaction_required")
    install_schema(conn)
    entity_kind = str(entity_kind)
    if entity_kind not in ENTITY_KINDS:
        raise HumanCopyError("invalid_entity_kind")
    entity_id = _one_line(entity_id, "entity_id")
    human_title, ai_title, human_summary, copy_status = _validate(
        human_title, ai_title, human_summary, copy_status
    )
    source = _one_line(source, "source")
    digest = source_sha256(conn, entity_kind, entity_id)
    if expected_source_sha256 is not None:
        expected = str(expected_source_sha256).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise HumanCopyError("invalid_expected_source_sha256")
        if expected != digest:
            raise HumanCopyError("stale_human_copy_source")
    now = c2_identity.utc_now()
    conn.execute(
        """INSERT INTO c2_human_copy(
             entity_kind,entity_id,human_title,ai_title,human_summary,
             copy_status,source,source_sha256,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?)
           ON CONFLICT(entity_kind,entity_id) DO UPDATE SET
             human_title=excluded.human_title,
             ai_title=excluded.ai_title,
             human_summary=excluded.human_summary,
             copy_status=excluded.copy_status,
             source=excluded.source,
             source_sha256=excluded.source_sha256,
             updated_at=excluded.updated_at""",
        (entity_kind, entity_id, human_title, ai_title, human_summary,
         copy_status, source, digest, now),
    )
    return {
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "human_title": human_title,
        "ai_title": ai_title,
        "human_summary": human_summary,
        "copy_status": copy_status,
        "source": source,
        "source_sha256": digest,
    }

def get_copy(conn: sqlite3.Connection, entity_kind: str, entity_id: str) -> dict | None:
    install_schema(conn)
    row = conn.execute(
        "SELECT * FROM c2_human_copy WHERE entity_kind=? AND entity_id=?",
        (entity_kind, entity_id),
    ).fetchone()
    return dict(row) if row else None
