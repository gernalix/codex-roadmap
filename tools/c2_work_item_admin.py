"""Evidence-gated reconciliation of non-prompt C2 roots by the single writer."""

from __future__ import annotations

import json
import sqlite3

import c2_identity


CLASS_STATUSES = {
    "CURRENT_READY": {"pending"},
    "CURRENT_WAITING": {"waiting", "blocked"},
    "ALREADY_IMPLEMENTED": {"completed"},
    "OBSOLETE": {"cancelled"},
    "SUPERSEDED": {"superseded"},
    "DUPLICATE_MERGE": {"superseded"},
    "NEEDS_REWRITE": {"pending", "waiting"},
}
EDITABLE_FIELDS = {
    "title", "objective", "current_action", "next_action", "blocker",
    "sort_order", "executor_policy", "repo", "actionable",
}
TERMINAL = {"completed", "cancelled", "superseded"}


def reconcile(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    classification: str,
    status: str,
    evidence: list[str],
    fields: dict | None = None,
    superseded_by: str | None = None,
    remove_dependencies: list[str] | None = None,
    include_descendants: bool = False,
) -> None:
    """Update one root and, for terminal dispositions, its imported descendants."""
    fields = dict(fields or {})
    if status not in CLASS_STATUSES.get(classification, set()):
        raise ValueError("invalid_work_item_classification")
    if set(fields) - EDITABLE_FIELDS or "status" in fields:
        raise ValueError("invalid_work_item_fields")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(fact, str) or not fact.strip() for fact in evidence
    ):
        raise ValueError("repository_evidence_required")
    if include_descendants and status not in TERMINAL:
        raise ValueError("terminal_descendant_status_required")
    if superseded_by and status != "superseded":
        raise ValueError("superseded_relation_requires_terminal_status")

    root = conn.execute("SELECT * FROM work_items WHERE work_item_id=?", (work_item_id,)).fetchone()
    if not root or root["parent_id"] or root["prompt_id"]:
        raise ValueError("nonprompt_root_required")
    if root["status"] not in ("pending", "waiting", "blocked", "unknown", status):
        raise ValueError("work_item_state_changed")
    if status in ("waiting", "blocked") and not str(fields.get("blocker") or root["blocker"] or "").strip():
        raise ValueError("waiting_blocker_required")

    descendants = [row[0] for row in conn.execute("""WITH RECURSIVE subtree(id) AS (
        SELECT work_item_id FROM work_items WHERE parent_id=?
        UNION ALL SELECT w.work_item_id FROM work_items w JOIN subtree s ON w.parent_id=s.id
    ) SELECT id FROM subtree""", (work_item_id,))] if include_descendants else []
    targets = [work_item_id, *descendants]
    for target in targets:
        row = conn.execute("SELECT prompt_id FROM work_items WHERE work_item_id=?", (target,)).fetchone()
        if row["prompt_id"]:
            raise ValueError("prompt_descendant_requires_separate_lifecycle")
        if conn.execute("""SELECT 1 FROM work_item_runs WHERE work_item_id=?
            AND state IN ('claimed','running','recovering') LIMIT 1""", (target,)).fetchone():
            raise ValueError("active_run_requires_normal_lifecycle")
    if superseded_by:
        if superseded_by == work_item_id or not conn.execute(
            "SELECT 1 FROM work_items WHERE work_item_id=?", (superseded_by,)
        ).fetchone():
            raise ValueError("invalid_superseding_work_item")
    for dependency in remove_dependencies or []:
        if not conn.execute("""SELECT 1 FROM work_item_dependencies
            WHERE work_item_id=? AND depends_on_work_item_id=?""",
            (work_item_id, dependency)).fetchone():
            raise ValueError("dependency_not_found")

    now = c2_identity.utc_now()
    assignments = ["status=?", "updated_at=?", *(f"{key}=?" for key in fields)]
    conn.execute(f"UPDATE work_items SET {','.join(assignments)} WHERE work_item_id=?",
                 [status, now, *fields.values(), work_item_id])
    if descendants:
        conn.executemany("""UPDATE work_items SET status=?,updated_at=?
            WHERE work_item_id=? AND status NOT IN ('completed','cancelled','superseded','waived','failed')""",
            [(status, now, target) for target in descendants])
    for dependency in remove_dependencies or []:
        conn.execute("""DELETE FROM work_item_dependencies
            WHERE work_item_id=? AND depends_on_work_item_id=?""", (work_item_id, dependency))
    if superseded_by:
        conn.execute("""INSERT OR IGNORE INTO work_item_relations
            (from_work_item_id,to_work_item_id,relation_type,created_at,actor,note)
            VALUES(?,?,'superseded_by',?,'c2-root-audit',?)""",
            (work_item_id, superseded_by, now, classification))
    for fact in evidence:
        conn.execute("""INSERT OR IGNORE INTO work_item_evidence
            (work_item_id,evidence_kind,label,uri,value_json,created_at)
            VALUES(?,'classification',?,NULL,?,?)""",
            (work_item_id, fact[:120], json.dumps(fact, ensure_ascii=False), now))
