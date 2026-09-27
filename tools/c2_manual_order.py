"""Fenced manual ordering primitives for Workflowy-projected C2 entities."""
from __future__ import annotations

import sqlite3

import c2_identity


SCOPES = frozenset({"inbox", "roadmap"})
SOURCE = "workflowy"


class ManualOrderError(RuntimeError):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS manual_order_overrides (
  scope TEXT NOT NULL CHECK(scope IN ('inbox','roadmap')),
  entity_id TEXT NOT NULL,
  rank INTEGER NOT NULL CHECK(rank >= 0),
  source TEXT NOT NULL CHECK(source='workflowy'),
  source_modified_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(scope, entity_id),
  UNIQUE(scope, rank)
);
CREATE VIEW IF NOT EXISTS v_roadmap_manual_order AS
SELECT
  w.*,
  CASE
    WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p0') THEN 0
    WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p1') THEN 1
    WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p2') THEN 2
    ELSE 3
  END AS ai_priority_rank,
  o.rank AS manual_rank,
  o.source AS manual_order_source,
  o.source_modified_at AS manual_order_source_modified_at,
  o.updated_at AS manual_order_updated_at
FROM work_items w
LEFT JOIN manual_order_overrides o
  ON o.scope='roadmap' AND o.entity_id=w.work_item_id;
"""


def install_schema(conn: sqlite3.Connection) -> None:
    statement = ""
    for line in SCHEMA.splitlines():
        statement += line + "\n"
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ""
    if statement.strip():
        raise ManualOrderError("incomplete_manual_order_schema")


def _transaction(conn: sqlite3.Connection) -> None:
    if not conn.in_transaction:
        raise ManualOrderError("canonical_writer_transaction_required")


def _scope(value: object) -> str:
    if not isinstance(value, str) or value not in SCOPES:
        raise ManualOrderError("invalid_manual_order_scope")
    return value


def _ids(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ManualOrderError("ordered_ids_must_be_list")
    if not all(isinstance(entity_id, str) and entity_id for entity_id in value):
        raise ManualOrderError("invalid_manual_order_entity_id")
    if len(set(value)) != len(value):
        raise ManualOrderError("duplicate_manual_order_entity_id")
    return value


def _canonical_ids(conn: sqlite3.Connection, scope: str, *, pending_only: bool) -> set[str]:
    if scope == "roadmap":
        return {str(row[0]) for row in conn.execute("SELECT work_item_id FROM work_items")}
    import c2_issue_inbox

    c2_issue_inbox.install_schema(conn)
    where = " WHERE state='pending'" if pending_only else ""
    return {
        str(row[0])
        for row in conn.execute("SELECT issue_id FROM issue_inbox" + where)
    }


def _validate_ids(
    conn: sqlite3.Connection,
    scope: str,
    entity_ids: list[str],
    *,
    pending_only: bool,
) -> None:
    invalid = sorted(set(entity_ids) - _canonical_ids(conn, scope, pending_only=pending_only))
    if invalid:
        raise ManualOrderError("invalid_manual_order_ids:" + ",".join(invalid))


def set_manual_order(
    conn: sqlite3.Connection,
    *,
    scope: str,
    ordered_ids: list[str],
    source: str,
    source_modified_at: str,
) -> dict:
    """Replace one complete displayed scope without touching semantic ordering or state."""
    _transaction(conn)
    install_schema(conn)
    scope = _scope(scope)
    ordered_ids = _ids(ordered_ids)
    if source != SOURCE:
        raise ManualOrderError("invalid_manual_order_source")
    if not isinstance(source_modified_at, str) or not source_modified_at:
        raise ManualOrderError("source_modified_at_required")
    _validate_ids(conn, scope, ordered_ids, pending_only=(scope == "inbox"))

    updated_at = c2_identity.utc_now()
    existing = [
        (str(row[0]), int(row[1]), str(row[2]), str(row[3]))
        for row in conn.execute(
            """SELECT entity_id,rank,source,source_modified_at
               FROM manual_order_overrides WHERE scope=? ORDER BY rank,entity_id""",
            (scope,),
        )
    ]
    desired = [
        (entity_id, rank, source, source_modified_at)
        for rank, entity_id in enumerate(ordered_ids)
    ]
    if existing == desired:
        return read_manual_order(conn, scope)

    keep = set(ordered_ids)
    stale = [
        str(row[0])
        for row in conn.execute(
            "SELECT entity_id FROM manual_order_overrides WHERE scope=?", (scope,)
        )
        if str(row[0]) not in keep
    ]
    if stale:
        conn.executemany(
            "DELETE FROM manual_order_overrides WHERE scope=? AND entity_id=?",
            [(scope, entity_id) for entity_id in stale],
        )

    # Avoid transient UNIQUE(scope,rank) collisions while replacing the full order.
    conn.execute(
        "UPDATE manual_order_overrides SET rank=rank+? WHERE scope=?",
        (len(ordered_ids) + len(stale) + 1, scope),
    )
    for rank, entity_id in enumerate(ordered_ids):
        conn.execute(
            """INSERT INTO manual_order_overrides(
                 scope,entity_id,rank,source,source_modified_at,updated_at
               ) VALUES(?,?,?,?,?,?)
               ON CONFLICT(scope,entity_id) DO UPDATE SET
                 rank=excluded.rank,
                 source=excluded.source,
                 source_modified_at=excluded.source_modified_at,
                 updated_at=excluded.updated_at
               WHERE manual_order_overrides.rank<>excluded.rank
                  OR manual_order_overrides.source<>excluded.source
                  OR manual_order_overrides.source_modified_at<>excluded.source_modified_at""",
            (scope, entity_id, rank, source, source_modified_at, updated_at),
        )
    return read_manual_order(conn, scope)


def clear_manual_order(
    conn: sqlite3.Connection,
    *,
    scope: str,
    ids: list[str] | None = None,
) -> dict:
    _transaction(conn)
    install_schema(conn)
    scope = _scope(scope)
    if ids is None:
        conn.execute("DELETE FROM manual_order_overrides WHERE scope=?", (scope,))
    else:
        ids = _ids(ids)
        _validate_ids(conn, scope, ids, pending_only=False)
        conn.executemany(
            "DELETE FROM manual_order_overrides WHERE scope=? AND entity_id=?",
            [(scope, entity_id) for entity_id in ids],
        )
    return read_manual_order(conn, scope)


def read_manual_order(conn: sqlite3.Connection, scope: str) -> dict:
    install_schema(conn)
    scope = _scope(scope)
    rows = [
        dict(row)
        for row in conn.execute(
            """SELECT entity_id,rank,source,source_modified_at,updated_at
               FROM manual_order_overrides WHERE scope=? ORDER BY rank,entity_id""",
            (scope,),
        )
    ]
    return {"scope": scope, "items": rows}
