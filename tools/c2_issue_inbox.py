"""Incidental issue inbox with fenced, audited corrections and triage."""
from __future__ import annotations

import json
import hashlib
import re
import sqlite3
import time
import uuid

import c2_identity
import c2_intake
import c2_human_copy


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
  state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','promoted','discarded','voided')),
  matched_work_item_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  promoted_work_item_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  disposition_reason TEXT,
  triaged_by TEXT,
  triaged_at_ms INTEGER,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS issue_inbox_revisions (
  mutation_id TEXT PRIMARY KEY,
  issue_id TEXT NOT NULL REFERENCES issue_inbox(issue_id) ON DELETE RESTRICT,
  operation TEXT NOT NULL CHECK(operation IN ('edit','void')),
  actor TEXT NOT NULL,
  reason TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  before_json TEXT NOT NULL,
  after_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_issue_inbox_revisions_issue
  ON issue_inbox_revisions(issue_id, created_at, mutation_id);
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
    # SQLite cannot widen a CHECK in place. No table references issue_inbox, so
    # preserve every row while replacing only the old state constraint.
    table_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='issue_inbox'").fetchone()[0]
    if "'voided'" not in table_sql:
        conn.execute("DROP VIEW IF EXISTS v_issue_inbox_pending_ordered")
        revisions = [tuple(row) for row in conn.execute(
            "SELECT mutation_id,issue_id,operation,actor,reason,payload_json,before_json,after_json,created_at FROM issue_inbox_revisions")]
        conn.execute("DROP TABLE IF EXISTS issue_inbox_revisions")
        conn.execute("CREATE TABLE issue_inbox_migrated " + table_sql[table_sql.index('('):].replace(
            "CHECK(state IN ('pending','promoted','discarded'))",
            "CHECK(state IN ('pending','promoted','discarded','voided'))"))
        conn.execute("INSERT INTO issue_inbox_migrated SELECT * FROM issue_inbox")
        conn.execute("DROP TABLE issue_inbox")
        conn.execute("ALTER TABLE issue_inbox_migrated RENAME TO issue_inbox")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_issue_inbox_state_observed ON issue_inbox(state,observed_at_ms,issue_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_issue_inbox_repo_state ON issue_inbox(repo,state,observed_at_ms)")
        conn.execute("""CREATE TABLE issue_inbox_revisions (
          mutation_id TEXT PRIMARY KEY,
          issue_id TEXT NOT NULL REFERENCES issue_inbox(issue_id) ON DELETE RESTRICT,
          operation TEXT NOT NULL CHECK(operation IN ('edit','void')),
          actor TEXT NOT NULL, reason TEXT NOT NULL, payload_json TEXT NOT NULL,
          before_json TEXT NOT NULL, after_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("CREATE INDEX idx_issue_inbox_revisions_issue ON issue_inbox_revisions(issue_id,created_at,mutation_id)")
        conn.executemany("""INSERT INTO issue_inbox_revisions
            (mutation_id,issue_id,operation,actor,reason,payload_json,before_json,after_json,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)""", revisions)
    links_exist = bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='issue_work_item_links'").fetchone())
    conn.execute("""CREATE TABLE IF NOT EXISTS issue_work_item_links (
        issue_id TEXT NOT NULL REFERENCES issue_inbox(issue_id) ON DELETE RESTRICT,
        work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
        role TEXT NOT NULL CHECK(role IN ('decision','matched')),
        created_at TEXT NOT NULL,
        PRIMARY KEY(issue_id,work_item_id,role))""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_issue_work_item_links_item ON issue_work_item_links(work_item_id,issue_id)")
    conn.execute("""CREATE TABLE IF NOT EXISTS issue_reconciliation_batches (
        batch_id TEXT PRIMARY KEY, payload_sha256 TEXT NOT NULL,
        result_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
    # Scalar columns remain for old readers; backfill is repeatable.
    if not links_exist:
        for column, role in (("matched_work_item_id", "matched"),
                             ("promoted_work_item_id", "decision")):
            conn.execute(f"""INSERT OR IGNORE INTO issue_work_item_links
                (issue_id,work_item_id,role,created_at)
                SELECT issue_id,{column},?,created_at FROM issue_inbox
                WHERE {column} IS NOT NULL""", (role,))
    conn.execute(
        """CREATE VIEW IF NOT EXISTS v_issue_inbox_pending_ordered AS
           SELECT i.* FROM issue_inbox i WHERE i.state='pending'
           ORDER BY i.observed_at_ms,i.issue_id"""
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


EDIT_FIELDS = frozenset({"description", "repo", "code_location", "executor_ref", "chat_url"})


def _change(conn: sqlite3.Connection, *, issue_id: str, mutation_id: str,
            operation: str, actor: str, reason: str, changes: dict | None = None) -> dict:
    _transaction(conn)
    install_schema(conn)
    _issue_id(issue_id)
    if not re.fullmatch(r"[0-9a-f]{32}", str(mutation_id)):
        raise IssueInboxError("invalid_mutation_id")
    actor = _required_text(actor, "actor")
    reason = _required_text(reason, "reason")
    if operation == "edit":
        if not isinstance(changes, dict) or not changes or set(changes) - EDIT_FIELDS:
            raise IssueInboxError("invalid_edit_fields")
        normalized = {key: (_required_description(value) if key == "description"
                            else _optional_text(value)) for key, value in changes.items()}
    else:
        if changes is not None:
            raise IssueInboxError("void_disallows_changes")
        normalized = {}
    payload = json.dumps({"issue_id": issue_id, "operation": operation,
                          "actor": actor, "reason": reason, "changes": normalized},
                         ensure_ascii=False, sort_keys=True)
    prior = conn.execute("SELECT * FROM issue_inbox_revisions WHERE mutation_id=?", (mutation_id,)).fetchone()
    if prior:
        if prior["payload_json"] != payload:
            raise IssueInboxError("mutation_id_conflict")
        return json.loads(prior["after_json"])
    before = dict(_row(conn, issue_id))
    if operation == "edit":
        after = {**before, **normalized}
        if after == before:
            raise IssueInboxError("edit_no_change")
        assignments = ",".join(f"{key}=?" for key in normalized)
        conn.execute(f"UPDATE issue_inbox SET {assignments} WHERE issue_id=?",
                     (*normalized.values(), issue_id))
    else:
        conn.execute("UPDATE issue_inbox SET state='voided',disposition_reason=?,triaged_by=?,triaged_at_ms=? WHERE issue_id=?",
                     (reason, actor, int(time.time() * 1000), issue_id))
    after = dict(conn.execute("SELECT * FROM issue_inbox WHERE issue_id=?", (issue_id,)).fetchone())
    conn.execute("""INSERT INTO issue_inbox_revisions
        (mutation_id,issue_id,operation,actor,reason,payload_json,before_json,after_json,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)""", (mutation_id, issue_id, operation, actor, reason,
        payload, json.dumps(before, ensure_ascii=False, sort_keys=True),
        json.dumps(after, ensure_ascii=False, sort_keys=True), c2_identity.utc_now()))
    return after


def edit(conn: sqlite3.Connection, *, issue_id: str, mutation_id: str,
         actor: str, reason: str, changes: dict) -> dict:
    return _change(conn, issue_id=issue_id, mutation_id=mutation_id,
                   operation="edit", actor=actor, reason=reason, changes=changes)


def void(conn: sqlite3.Connection, *, issue_id: str, mutation_id: str,
         actor: str, reason: str) -> dict:
    return _change(conn, issue_id=issue_id, mutation_id=mutation_id,
                   operation="void", actor=actor, reason=reason)


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


def _link(conn: sqlite3.Connection, issue_id: str, work_item_id: str, role: str) -> None:
    conn.execute("""INSERT OR IGNORE INTO issue_work_item_links
        (issue_id,work_item_id,role,created_at) VALUES(?,?,?,?)""",
        (issue_id,work_item_id,role,c2_identity.utc_now()))


def reconcile_batch(conn: sqlite3.Connection, *, batch_id: str,
                    decisions: list[dict], new_items: list[dict] | None = None,
                    triaged_by: str) -> dict:
    """Apply one bounded semantic cluster/merge/split decision in the writer transaction.

    References to new items use ``@alias``. Unmentioned pending observations remain pending.
    """
    _transaction(conn)
    install_schema(conn)
    batch_id = _required_text(batch_id, "batch_id")
    triaged_by = _required_text(triaged_by, "triaged_by")
    new_items = new_items or []
    if not isinstance(decisions, list) or not 1 <= len(decisions) <= 25:
        raise IssueInboxError("decisions_must_be_bounded_list")
    if not isinstance(new_items, list) or len(new_items) > 25:
        raise IssueInboxError("new_items_must_be_bounded_list")
    payload = json.dumps({"decisions": decisions, "new_items": new_items,
                          "triaged_by": triaged_by}, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    previous = conn.execute("SELECT payload_sha256,result_json FROM issue_reconciliation_batches WHERE batch_id=?",
                            (batch_id,)).fetchone()
    if previous:
        if previous[0] != digest:
            raise IssueInboxError("batch_id_conflict")
        return json.loads(previous[1])
    aliases = {}
    for spec in new_items:
        if not isinstance(spec, dict):
            raise IssueInboxError("new_item_must_be_object")
        alias = str(spec.get("alias", ""))
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", alias) or alias in aliases:
            raise IssueInboxError("invalid_or_duplicate_alias")
        aliases[alias] = None
    issue_ids = [str(d.get("issue_id", "")) for d in decisions if isinstance(d, dict)]
    if len(issue_ids) != len(decisions) or len(set(issue_ids)) != len(issue_ids):
        raise IssueInboxError("duplicate_or_invalid_decision")
    rows = {issue_id: _row(conn, issue_id) for issue_id in issue_ids}
    used_aliases = set()
    for decision in decisions:
        _required_text(decision.get("reason"), "reason")
        refs = decision.get("work_item_ids")
        if not isinstance(refs, list) or len(refs) > 25 or any(not isinstance(r, str) for r in refs) or len(set(refs)) != len(refs):
            raise IssueInboxError("invalid_work_item_ids")
        for ref in refs:
            if ref.startswith("@"):
                if ref[1:] not in aliases:
                    raise IssueInboxError("unknown_alias")
                used_aliases.add(ref[1:])
            else:
                _matched(conn, ref)
    if used_aliases != set(aliases):
        raise IssueInboxError("unused_new_item")
    for spec in new_items:
        alias = spec["alias"]
        item = c2_intake.add_work_item(conn, **{k: v for k, v in spec.items() if k != "alias"})
        aliases[alias] = item["work_item_id"]
    outcomes = []
    for decision in decisions:
        issue = rows[decision["issue_id"]]
        targets = [aliases[ref[1:]] if ref.startswith("@") else ref
                   for ref in decision["work_item_ids"]]
        for target in targets:
            _link(conn, issue["issue_id"], target, "decision")
            _record_evidence(conn, target, issue)
        state = "promoted" if targets else "discarded"
        conn.execute("""UPDATE issue_inbox SET state=?,promoted_work_item_id=?,
            disposition_reason=?,triaged_by=?,triaged_at_ms=? WHERE issue_id=?""",
            (state, targets[0] if targets else None, decision["reason"],
             triaged_by, int(time.time() * 1000), issue["issue_id"]))
        outcomes.append({"issue_id": issue["issue_id"], "state": state,
                         "work_item_ids": targets})
    result = {"batch_id": batch_id, "aliases": aliases, "decisions": outcomes}
    conn.execute("""INSERT INTO issue_reconciliation_batches
        (batch_id,payload_sha256,result_json,created_at) VALUES(?,?,?,?)""",
        (batch_id,digest,json.dumps(result,sort_keys=True),c2_identity.utc_now()))
    return result


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
    human_title: str | None = None,
    ai_title: str | None = None,
    human_summary: str | None = None,
    copy_status: str = "complete",
) -> dict:
    """Absorb an observation into active work or create a successor/regression."""
    _transaction(conn)
    issue = _row(conn, issue_id)
    matched = _matched(conn, matched_work_item_id)
    reason = _required_text(reason, "reason")
    triaged_by = _required_text(triaged_by, "triaged_by")

    copy_values = (human_title, ai_title, human_summary)
    if any(value is not None for value in copy_values) and not all(
        value is not None for value in copy_values
    ):
        raise IssueInboxError("complete_human_copy_required")

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

    if all(value is not None for value in copy_values):
        c2_human_copy.set_copy(
            conn,
            entity_kind="issue",
            entity_id=str(issue["issue_id"]),
            human_title=str(human_title),
            ai_title=str(ai_title),
            human_summary=str(human_summary),
            copy_status=copy_status,
            source="issue-triage",
        )
        c2_human_copy.set_copy(
            conn,
            entity_kind="work_item",
            entity_id=promoted_id,
            human_title=str(human_title),
            ai_title=str(ai_title),
            human_summary=str(human_summary),
            copy_status=copy_status,
            source="issue-triage",
        )

    _record_evidence(conn, promoted_id, issue)
    _link(conn, issue_id, promoted_id, "decision")
    if matched_work_item_id:
        _link(conn, issue_id, matched_work_item_id, "matched")
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
    if matched_work_item_id:
        _link(conn, issue_id, matched_work_item_id, "matched")
    return {"issue_id": issue_id, "state": "discarded", "matched_work_item_id": matched_work_item_id}


def ensure_triage(*args, **kwargs):
    raise IssueInboxError("retired_recursive_inbox_executor: use maintain_issue_inbox")
