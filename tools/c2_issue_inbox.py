"""Append-only incidental issue inbox and fenced C2 triage primitives."""
from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid

import c2_identity
import c2_intake


ACTIVE_STATES = {"pending", "running", "waiting", "blocked", "needs_fix", "unknown"}
COMPLETED_STATES = {"completed"}
DISCARDABLE_MATCH_STATES = {"cancelled", "superseded", "waived"}


class IssueInboxError(RuntimeError):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS issue_inbox (
  issue_id TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  repo TEXT,
  code_location TEXT,
  executor_ref TEXT,
  chat_url TEXT,
  origin_work_item_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  origin_run_id TEXT REFERENCES work_item_runs(run_id) ON DELETE RESTRICT,
  observed_at_ms INTEGER NOT NULL CHECK(observed_at_ms > 0),
  state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','promoted','discarded')),
  matched_work_item_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  promoted_work_item_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  disposition_reason TEXT,
  triaged_by TEXT,
  triaged_at_ms INTEGER,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_issue_inbox_state_observed
  ON issue_inbox(state, observed_at_ms, issue_id);
CREATE INDEX IF NOT EXISTS idx_issue_inbox_repo_state
  ON issue_inbox(repo, state, observed_at_ms);
"""


def install_schema(conn: sqlite3.Connection) -> None:
    statement = ""
    for line in SCHEMA.splitlines():
        statement += line + "\n"
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ""
    if statement.strip():
        raise IssueInboxError("incomplete_issue_inbox_schema")
    columns = {str(row[1]) for row in conn.execute("PRAGMA table_info(issue_inbox)")}
    for column, ddl in (
        ("chat_url", "TEXT"),
        ("origin_work_item_id", "TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT"),
        ("origin_run_id", "TEXT REFERENCES work_item_runs(run_id) ON DELETE RESTRICT"),
    ):
        if column not in columns:
            conn.execute(f"ALTER TABLE issue_inbox ADD COLUMN {column} {ddl}")


def _transaction(conn: sqlite3.Connection) -> None:
    if not conn.in_transaction:
        raise IssueInboxError("canonical_writer_transaction_required")


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _required_text(value: object, field: str) -> str:
    result = _optional_text(value)
    if result is None:
        raise IssueInboxError(field + "_required")
    return result


def _issue_id(value: str | None) -> str:
    if value is None:
        return "issue:" + uuid.uuid4().hex
    value = str(value)
    if not re.fullmatch(r"issue:[0-9a-f]{32}", value):
        raise IssueInboxError("invalid_issue_id")
    return value


def _work_item_for_task_id(conn: sqlite3.Connection, task_id: str | None) -> sqlite3.Row | None:
    value = _optional_text(task_id)
    if value is None:
        return None
    for column in ("work_item_id", "task_id", "prompt_id"):
        row = conn.execute(
            f"SELECT * FROM work_items WHERE {column}=?",
            (value,),
        ).fetchone()
        if row:
            return row
    raise IssueInboxError("origin_task_not_found")


def _origin_context(
    conn: sqlite3.Connection,
    *,
    task_id: str | None,
    run_id: str | None,
) -> tuple[str | None, str | None, str | None, str | None]:
    item = _work_item_for_task_id(conn, task_id)
    run = None
    if run_id:
        run = conn.execute("SELECT * FROM work_item_runs WHERE run_id=?", (run_id,)).fetchone()
        if not run:
            raise IssueInboxError("origin_run_not_found")
        if item and str(run["work_item_id"]) != str(item["work_item_id"]):
            raise IssueInboxError("origin_task_run_mismatch")
        if item is None:
            item = conn.execute(
                "SELECT * FROM work_items WHERE work_item_id=?",
                (run["work_item_id"],),
            ).fetchone()

    binding = None
    if run is not None:
        binding = conn.execute(
            "SELECT * FROM work_item_executor_bindings WHERE run_id=?",
            (run["run_id"],),
        ).fetchone()
    elif item is not None:
        binding = conn.execute(
            """SELECT b.* FROM work_item_executor_bindings b
               JOIN work_item_runs r USING(run_id)
               WHERE b.work_item_id=?
               ORDER BY CASE WHEN r.state IN ('claimed','running','recovering') THEN 0 ELSE 1 END,
                        b.bound_at DESC
               LIMIT 1""",
            (item["work_item_id"],),
        ).fetchone()
        if binding:
            run = conn.execute(
                "SELECT * FROM work_item_runs WHERE run_id=?",
                (binding["run_id"],),
            ).fetchone()

    return (
        str(item["work_item_id"]) if item else None,
        str(run["run_id"]) if run else None,
        str(binding["executor_ref"]) if binding else None,
        str(binding["chat_url"]) if binding else None,
    )


def capture(
    conn: sqlite3.Connection,
    *,
    description: str,
    repo: str | None = None,
    code_location: str | None = None,
    executor_ref: str | None = None,
    chat_url: str | None = None,
    task_id: str | None = None,
    run_id: str | None = None,
    observed_at_ms: int | None = None,
    issue_id: str | None = None,
) -> dict:
    """Capture observed facts plus O(1) execution identity; never semantically scan or deduplicate."""
    _transaction(conn)
    install_schema(conn)
    origin_item, origin_run, bound_executor, bound_url = _origin_context(
        conn, task_id=task_id, run_id=run_id
    )
    executor_ref = _optional_text(executor_ref) or bound_executor
    chat_url = _optional_text(chat_url) or bound_url
    observed = int(time.time() * 1000) if observed_at_ms is None else int(observed_at_ms)
    if observed <= 0:
        raise IssueInboxError("invalid_observed_at_ms")
    identity = _issue_id(issue_id)
    conn.execute(
        """INSERT INTO issue_inbox(
             issue_id,description,repo,code_location,executor_ref,chat_url,
             origin_work_item_id,origin_run_id,observed_at_ms,state,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,'pending',?)""",
        (
            identity,
            _required_text(description, "description"),
            _optional_text(repo),
            _optional_text(code_location),
            _optional_text(executor_ref),
            _optional_text(chat_url),
            origin_item,
            origin_run,
            observed,
            c2_identity.utc_now(),
        ),
    )
    return dict(conn.execute("SELECT * FROM issue_inbox WHERE issue_id=?", (identity,)).fetchone())


def _row(conn: sqlite3.Connection, issue_id: str) -> sqlite3.Row:
    install_schema(conn)
    row = conn.execute("SELECT * FROM issue_inbox WHERE issue_id=?", (issue_id,)).fetchone()
    if not row:
        raise IssueInboxError("issue_not_found")
    if row["state"] != "pending":
        raise IssueInboxError("issue_already_triaged")
    return row


def _matched(conn: sqlite3.Connection, work_item_id: str | None) -> sqlite3.Row | None:
    if not work_item_id:
        return None
    row = conn.execute("SELECT * FROM work_items WHERE work_item_id=?", (work_item_id,)).fetchone()
    if not row:
        raise IssueInboxError("matched_work_item_not_found")
    return row


def _record_evidence(conn: sqlite3.Connection, work_item_id: str, issue: sqlite3.Row) -> None:
    payload = {
        "issue_id": issue["issue_id"],
        "description": issue["description"],
        "repo": issue["repo"],
        "code_location": issue["code_location"],
        "executor_ref": issue["executor_ref"],
        "chat_url": issue["chat_url"],
        "origin_work_item_id": issue["origin_work_item_id"],
        "origin_run_id": issue["origin_run_id"],
        "observed_at_ms": issue["observed_at_ms"],
    }
    conn.execute(
        """INSERT OR IGNORE INTO work_item_evidence(
             work_item_id,evidence_kind,label,uri,value_json,created_at
           ) VALUES(?,'issue_inbox',?,?,?,?)""",
        (
            work_item_id,
            issue["issue_id"],
            issue["chat_url"] or issue["executor_ref"],
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
            c2_identity.utc_now(),
        ),
    )


def _new_promoted_item(
    conn: sqlite3.Connection,
    issue: sqlite3.Row,
    *,
    matched: sqlite3.Row | None,
    title: str | None,
    objective: str | None,
    parent_id: str | None,
    depends_on: list[str] | None,
    tags: list[str] | None,
    sort_order: int | None,
    executor_policy: str,
    project: str | None,
    repo: str | None,
) -> dict:
    regression = bool(matched and matched["status"] in COMPLETED_STATES)
    default_title = (
        "Regression: " + str(matched["title"])
        if regression
        else str(issue["description"])[:120]
    )
    promoted = c2_intake.add_work_item(
        conn,
        title=title or default_title,
        objective=objective or str(issue["description"]),
        executor_policy=executor_policy,
        project=project if project is not None else (matched["project_id"] if matched else None),
        repo=repo or issue["repo"] or (matched["repo"] if matched else None),
        parent_id=parent_id if parent_id is not None else (matched["parent_id"] if matched else None),
        depends_on=depends_on,
        tags=[*(tags or []), "source:issue-inbox", *(["regression"] if regression else [])],
        sort_order=sort_order if sort_order is not None else (matched["sort_order"] if matched else None),
    )
    target_id = str(promoted["work_item_id"])
    if regression and matched is not None:
        conn.execute(
            """INSERT OR IGNORE INTO work_item_relations(
                 from_work_item_id,to_work_item_id,relation_type,created_at,actor,note
               ) VALUES(?,?,'regression_of',?,'c2-issue-triage',?)""",
            (target_id, matched["work_item_id"], c2_identity.utc_now(), issue["issue_id"]),
        )
    return promoted


def promote(
    conn: sqlite3.Connection,
    *,
    issue_id: str,
    reason: str,
    triaged_by: str,
    matched_work_item_id: str | None = None,
    title: str | None = None,
    objective: str | None = None,
    parent_id: str | None = None,
    depends_on: list[str] | None = None,
    tags: list[str] | None = None,
    sort_order: int | None = None,
    executor_policy: str = "auto",
    project: str | None = None,
    repo: str | None = None,
) -> dict:
    """Absorb an observation into active work or create a successor/regression."""
    _transaction(conn)
    issue = _row(conn, issue_id)
    matched = _matched(conn, matched_work_item_id)
    reason = _required_text(reason, "reason")
    triaged_by = _required_text(triaged_by, "triaged_by")

    if matched and matched["status"] in ACTIVE_STATES:
        target = dict(matched)
        promoted_id = str(matched["work_item_id"])
    else:
        target = _new_promoted_item(
            conn, issue, matched=matched, title=title, objective=objective,
            parent_id=parent_id, depends_on=depends_on, tags=tags,
            sort_order=sort_order, executor_policy=executor_policy,
            project=project, repo=repo,
        )
        promoted_id = str(target["work_item_id"])

    _record_evidence(conn, promoted_id, issue)
    triaged_at = int(time.time() * 1000)
    conn.execute(
        """UPDATE issue_inbox
           SET state='promoted',matched_work_item_id=?,promoted_work_item_id=?,
               disposition_reason=?,triaged_by=?,triaged_at_ms=?
           WHERE issue_id=?""",
        (matched_work_item_id, promoted_id, reason, triaged_by, triaged_at, issue_id),
    )
    return {
        "issue_id": issue_id,
        "state": "promoted",
        "matched_work_item_id": matched_work_item_id,
        "promoted_work_item_id": promoted_id,
        "regression": bool(matched and matched["status"] in COMPLETED_STATES),
    }


def discard(
    conn: sqlite3.Connection,
    *,
    issue_id: str,
    reason: str,
    triaged_by: str,
    matched_work_item_id: str | None = None,
) -> dict:
    """Discard only irrelevant/obsolete observations; never discard a reproduced fixed item."""
    _transaction(conn)
    issue = _row(conn, issue_id)
    matched = _matched(conn, matched_work_item_id)
    if matched and matched["status"] not in DISCARDABLE_MATCH_STATES:
        if matched["status"] in COMPLETED_STATES:
            raise IssueInboxError("fresh_observation_of_completed_item_requires_regression")
        raise IssueInboxError("relevant_matched_item_requires_promotion")
    reason = _required_text(reason, "reason")
    triaged_by = _required_text(triaged_by, "triaged_by")
    triaged_at = int(time.time() * 1000)
    conn.execute(
        """UPDATE issue_inbox
           SET state='discarded',matched_work_item_id=?,disposition_reason=?,
               triaged_by=?,triaged_at_ms=?
           WHERE issue_id=?""",
        (matched_work_item_id, reason, triaged_by, triaged_at, issue_id),
    )
    return {"issue_id": issue_id, "state": "discarded", "matched_work_item_id": matched_work_item_id}
