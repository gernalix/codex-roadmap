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
  executor TEXT,
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
        ("executor", "TEXT"),
        ("origin_work_item_id", "TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT"),
        ("origin_run_id", "TEXT REFERENCES work_item_runs(run_id) ON DELETE RESTRICT"),
    ):
        if column not in columns:
            conn.execute(f"ALTER TABLE issue_inbox ADD COLUMN {column} {ddl}")
    import c2_manual_order

    c2_manual_order.install_schema(conn)
    conn.execute(
        """CREATE VIEW IF NOT EXISTS v_issue_inbox_pending_ordered AS
           SELECT
             i.*,
             o.rank AS manual_rank,
             o.source AS manual_order_source,
             o.source_modified_at AS manual_order_source_modified_at,
             o.updated_at AS manual_order_updated_at
           FROM issue_inbox i
           LEFT JOIN manual_order_overrides o
             ON o.scope='inbox' AND o.entity_id=i.issue_id
           WHERE i.state='pending'
           ORDER BY CASE WHEN o.rank IS NULL THEN 1 ELSE 0 END,
                    o.rank,i.observed_at_ms,i.issue_id"""
    )


def _transaction(conn: sqlite3.Connection) -> None:
    if not conn.in_transaction:
        raise IssueInboxError("canonical_writer_transaction_required")


def pending_issues(conn: sqlite3.Connection) -> list[dict]:
    """Return pending inbox rows in the authoritative human/AI triage order."""
    install_schema(conn)
    return [dict(row) for row in conn.execute("SELECT * FROM v_issue_inbox_pending_ordered")]


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


def _required_description(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IssueInboxError("description_required")
    return value


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
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
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
    start = None
    if run is not None:
        binding = conn.execute(
            "SELECT * FROM work_item_executor_bindings WHERE run_id=?",
            (run["run_id"],),
        ).fetchone()
        start = conn.execute(
            "SELECT * FROM work_item_executor_starts WHERE run_id=?",
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
        start = conn.execute(
            """SELECT * FROM work_item_executor_starts
               WHERE work_item_id=?
               ORDER BY started_at DESC LIMIT 1""",
            (item["work_item_id"],),
        ).fetchone()
        if run is None and start and start["run_id"]:
            run = conn.execute(
                "SELECT * FROM work_item_runs WHERE run_id=?",
                (start["run_id"],),
            ).fetchone()

    executor = str(run["executor"]) if run else (str(start["executor"]) if start else None)
    executor_ref = str(binding["executor_ref"]) if binding else (
        str(start["executor_ref"]) if start and start["executor_ref"] else None
    )
    chat_url = str(binding["chat_url"]) if binding else (
        str(start["chat_url"]) if start and start["chat_url"] else None
    )
    return (
        str(item["work_item_id"]) if item else None,
        str(run["run_id"]) if run else None,
        executor,
        executor_ref,
        chat_url,
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
    origin_item, origin_run, executor, bound_executor, bound_url = _origin_context(
        conn, task_id=task_id, run_id=run_id
    )
    if bound_executor and _optional_text(executor_ref) not in (None, bound_executor):
        raise IssueInboxError("executor_ref_binding_conflict")
    if bound_url and _optional_text(chat_url) not in (None, bound_url):
        raise IssueInboxError("chat_url_binding_conflict")
    executor_ref = _optional_text(executor_ref) or bound_executor
    chat_url = _optional_text(chat_url) or bound_url
    observed = int(time.time() * 1000) if observed_at_ms is None else int(observed_at_ms)
    if observed <= 0:
        raise IssueInboxError("invalid_observed_at_ms")
    identity = _issue_id(issue_id)
    conn.execute(
        """INSERT INTO issue_inbox(
             issue_id,description,repo,code_location,executor,executor_ref,chat_url,
             origin_work_item_id,origin_run_id,observed_at_ms,state,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,'pending',?)""",
        (
            identity,
            _required_description(description),
            _optional_text(repo),
            _optional_text(code_location),
            executor,
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
        "executor": issue["executor"],
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


def ensure_triage(conn: sqlite3.Connection, *, project_url: str) -> dict:
    """Atomically create one runnable triage item for the current pending batch."""
    _transaction(conn)
    install_schema(conn)
    if not re.fullmatch(r"https://chatgpt\.com/g/g-p-[a-z0-9]+/project/?", project_url):
        raise IssueInboxError("explicit_c2_project_url_required")
    pending = conn.execute("SELECT COUNT(*) FROM issue_inbox WHERE state='pending'").fetchone()[0]
    if not pending:
        return {"state": "empty"}
    active = conn.execute("""SELECT w.work_item_id FROM work_items w
        JOIN work_item_tags t USING(work_item_id)
        WHERE t.tag='c2:issue-triage'
          AND w.status NOT IN ('completed','failed','cancelled','superseded','waived')
        ORDER BY w.created_at,w.work_item_id LIMIT 1""").fetchone()
    if active:
        return {"state": "existing", "work_item_id": active[0]}
    item = c2_intake.add_work_item(
        conn, title="Triage C2 issue inbox",
        objective=(
            "Process every row from v_issue_inbox_pending_ordered in its displayed order. "
            "Use the canonical snapshot to identify "
            "related roadmap/repository work. Submit c2_promote_issue or c2_discard_issue "
            "through tools/c2_control.py with the current supervisor ID and fencing token. "
            "For active matches, promote into the existing work item with evidence. "
            "For completed matches, promote a regression successor; never discard as fixed. "
            "Before every promotion, review relative priority and dependencies in both "
            "directions against the current queue; encode verified changes explicitly. "
            "For irrelevant or obsolete issues, discard with a concrete reason. "
            "Read pending rows again before completion and finish only when none remain."
        ),
        acceptance=["No pending issue_inbox rows remain at completion"],
        next_action=(
            "Read v_issue_inbox_pending_ordered; apply one fenced disposition per row in order."
        ),
        tags=["c2:issue-triage", "priority:p0"],
        execution={"activity": "semantic", "project_url": project_url,
                   "resources": ["c2:issue-triage"], "max_attempts": 3},
    )
    return {"state": "created", "work_item_id": item["work_item_id"], "pending": pending}
