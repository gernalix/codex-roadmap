"""Evidence-gated BLOCKED dispositions and a read-only periodic safety net."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

import roadmap_db


TERMINAL = {"cancelled", "superseded"}


def reconcile(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    expected_updated_at: str,
    disposition: str,
    evidence: list[str],
    next_action: str,
    blocker: str | None = None,
    recovery_condition: str | None = None,
    terminal_status: str | None = None,
    superseded_by: str | None = None,
) -> dict:
    """Resolve one blocked item without changing a running executor or its receipt."""
    if disposition not in {"WAITING", "TERMINAL", "BLOCKED"}:
        raise ValueError("invalid_blocked_disposition")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(fact, str) or not fact.strip() for fact in evidence
    ):
        raise ValueError("blocker_evidence_required")
    if not isinstance(next_action, str) or not next_action.strip():
        raise ValueError("next_action_required")
    if disposition == "BLOCKED" and not all(
        isinstance(value, str) and value.strip() for value in (blocker, recovery_condition)
    ):
        raise ValueError("blocker_and_recovery_condition_required")
    if disposition != "BLOCKED" and (blocker or recovery_condition):
        raise ValueError("resolved_disposition_has_blocker")
    if disposition == "TERMINAL":
        if terminal_status not in TERMINAL:
            raise ValueError("invalid_blocked_terminal_status")
    elif terminal_status or superseded_by:
        raise ValueError("terminal_fields_require_terminal_disposition")
    if superseded_by and terminal_status != "superseded":
        raise ValueError("superseded_relation_requires_superseded_status")

    row = conn.execute(
        "SELECT * FROM work_items WHERE work_item_id=?", (work_item_id,)
    ).fetchone()
    if not row or row["status"] != "blocked":
        raise ValueError("blocked_item_required")
    if row["updated_at"] != expected_updated_at:
        raise ValueError("blocked_item_changed")
    if conn.execute("""SELECT 1 FROM work_item_runs WHERE work_item_id=?
        AND state IN ('claimed','running','recovering') LIMIT 1""", (work_item_id,)).fetchone():
        raise ValueError("active_run_requires_normal_lifecycle")
    if row["prompt_id"]:
        prior_request = conn.execute(
            "SELECT requested_status FROM terminal_requests WHERE prompt_id=?",
            (row["prompt_id"],)
        ).fetchone()
        if prior_request and prior_request[0] != "blocked":
            raise ValueError("terminal_request_requires_normal_lifecycle")
    if superseded_by:
        successor = conn.execute(
            "SELECT status FROM work_items WHERE work_item_id=?", (superseded_by,)
        ).fetchone()
        if superseded_by == work_item_id or not successor:
            raise ValueError("invalid_superseding_work_item")

    target = {"WAITING": "waiting", "BLOCKED": "blocked"}.get(disposition, terminal_status)
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if row["prompt_id"] and target in TERMINAL:
        roadmap_db.set_status(conn, row["prompt_id"], target,
                              actor="c2-blocked-reconcile", note=next_action)
    else:
        conn.execute("UPDATE work_items SET status=?,updated_at=? WHERE work_item_id=?",
                     (target, now, work_item_id))
        if row["prompt_id"] and target != "blocked":
            # Legacy prompt lifecycle treats BLOCKED as terminal and does not
            # know WAITING. This explicit reconciliation is the sole exception;
            # preserve both historical terminal requests and status history.
            conn.execute("""INSERT INTO status_history
                (prompt_id,old_status,new_status,changed_at,actor,note)
                VALUES(?,'blocked',?,?,'c2-blocked-reconcile',?)""",
                (row["prompt_id"], target, now, next_action))
    displayed_next_action = next_action
    if recovery_condition and recovery_condition not in displayed_next_action:
        displayed_next_action += " Recovery condition: " + recovery_condition
    conn.execute("""UPDATE work_items SET blocker=?,next_action=?,updated_at=?
        WHERE work_item_id=?""", (blocker if disposition == "BLOCKED" else None,
                                   displayed_next_action, now, work_item_id))
    if superseded_by:
        conn.execute("""INSERT OR IGNORE INTO work_item_relations
            (from_work_item_id,to_work_item_id,relation_type,created_at,actor,note)
            VALUES(?,?,'superseded_by',?,'c2-blocked-reconcile',?)""",
            (work_item_id, superseded_by, now, next_action))
    event = {"work_item_id": work_item_id, "old_status": "blocked", "new_status": target,
             "disposition": disposition, "evidence": evidence,
             "recovery_condition": recovery_condition, "next_action": next_action}
    conn.execute("""INSERT INTO work_item_scheduler_events(event_key,observed_at,result_json)
        VALUES(?,strftime('%s','now'),?)""",
        ("blocked-reconcile:" + work_item_id + ":" + now, json.dumps(event, ensure_ascii=False)))
    for fact in evidence:
        conn.execute("""INSERT OR IGNORE INTO work_item_evidence
            (work_item_id,evidence_kind,label,uri,value_json,created_at)
            VALUES(?,'blocked_reconcile',?,NULL,?,?)""",
            (work_item_id, fact[:120], json.dumps(fact, ensure_ascii=False), now))
    return event


def pending_review(conn: sqlite3.Connection) -> list[dict]:
    """Surface every BLOCKED item periodically; never infer from free-text blockers."""
    return [dict(row) for row in conn.execute("""SELECT w.work_item_id,w.updated_at,w.blocker,
        w.next_action,w.parent_id,w.prompt_id,
        (SELECT count(*) FROM work_item_dependencies d JOIN work_items dep
          ON dep.work_item_id=d.depends_on_work_item_id
          WHERE d.work_item_id=w.work_item_id AND d.required=1
            AND dep.status NOT IN ('completed','waived')) AS unmet_dependencies
        FROM work_items w WHERE w.status='blocked' ORDER BY w.updated_at,w.work_item_id""")]


def automatic_candidates(conn: sqlite3.Connection) -> list[dict]:
    """Return only transitions implied by structured canonical facts."""
    candidates = []
    for row in conn.execute("""SELECT w.work_item_id,w.updated_at,w.blocker
        FROM work_items w WHERE w.status='blocked' ORDER BY w.work_item_id"""):
        work_item_id = row["work_item_id"]
        blocker = str(row["blocker"] or "")
        if blocker.startswith("dependency:"):
            dependency = blocker.partition(":")[2].strip()
            matches = conn.execute("""SELECT dep.status FROM work_item_dependencies d
                JOIN work_items dep ON dep.work_item_id=d.depends_on_work_item_id
                WHERE d.work_item_id=? AND d.depends_on_work_item_id=? AND d.required=1""",
                (work_item_id, dependency)).fetchone()
            if matches and matches[0] in {"completed", "waived"}:
                unmet = conn.execute("""SELECT 1 FROM work_item_dependencies d
                    JOIN work_items dep ON dep.work_item_id=d.depends_on_work_item_id
                    WHERE d.work_item_id=? AND d.required=1
                      AND dep.status NOT IN ('completed','waived') LIMIT 1""",
                    (work_item_id,)).fetchone()
                if not unmet:
                    candidates.append({"work_item_id": work_item_id,
                                       "expected_updated_at": row["updated_at"],
                                       "kind": "dependency", "source": dependency})
    return candidates


def safety_net(conn: sqlite3.Connection, *, expected: list[dict]) -> list[dict]:
    """Apply still-current deterministic candidates from a prior read-only snapshot."""
    if not isinstance(expected, list) or len(expected) > 100:
        raise ValueError("invalid_blocked_safety_net_batch")
    current = {item["work_item_id"]: item for item in automatic_candidates(conn)}
    results = []
    for item in expected:
        if not isinstance(item, dict) or set(item) != {
            "work_item_id", "expected_updated_at", "kind", "source"
        }:
            raise ValueError("invalid_blocked_safety_net_candidate")
        candidate = current.get(item["work_item_id"])
        if candidate != item:
            continue
        results.append(reconcile(conn, item["work_item_id"],
            expected_updated_at=item["expected_updated_at"],
            disposition="WAITING",
            evidence=["Canonical required dependency completed or waived: " + item["source"]],
            next_action="Reassess runnable work after dependency completion."))
    return results
