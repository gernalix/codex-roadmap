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
    "sort_order", "executor_policy", "repo", "project_id", "project_name",
    "actionable", "acceptance_json",
}


def reparent(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    parent_id: str | None,
    expected_parent_id: str | None,
    evidence: list[str],
    actor: str = "c2-reparent-item",
) -> dict:
    """Move one non-prompt work item in the hierarchy with race and cycle guards."""
    if not conn.in_transaction:
        raise ValueError("canonical_writer_transaction_required")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(fact, str) or not fact.strip() for fact in evidence
    ):
        raise ValueError("repository_evidence_required")
    row = conn.execute(
        "SELECT work_item_id,parent_id,prompt_id FROM work_items WHERE work_item_id=?",
        (work_item_id,),
    ).fetchone()
    if not row:
        raise ValueError("work_item_not_found")
    if row["prompt_id"]:
        raise ValueError("prompt_work_item_reparent_forbidden")
    current_parent = row["parent_id"]
    if current_parent != expected_parent_id:
        raise ValueError("parent_precondition_changed")
    if parent_id == work_item_id:
        raise ValueError("hierarchy_cycle")
    if conn.execute("""SELECT 1 FROM work_item_runs WHERE work_item_id=?
        AND state IN ('claimed','running','recovering') LIMIT 1""",
        (work_item_id,)).fetchone():
        raise ValueError("active_run_requires_normal_lifecycle")
    if parent_id is not None:
        parent = conn.execute(
            "SELECT work_item_id FROM work_items WHERE work_item_id=?", (parent_id,)
        ).fetchone()
        if not parent:
            raise ValueError("parent_not_found")
        if conn.execute("""WITH RECURSIVE descendants(id) AS (
            SELECT work_item_id FROM work_items WHERE parent_id=?
            UNION ALL SELECT w.work_item_id FROM work_items w
            JOIN descendants d ON w.parent_id=d.id
        ) SELECT 1 FROM descendants WHERE id=? LIMIT 1""",
            (work_item_id, parent_id)).fetchone():
            raise ValueError("hierarchy_cycle")
    now = c2_identity.utc_now()
    conn.execute(
        "UPDATE work_items SET parent_id=?,updated_at=? WHERE work_item_id=?",
        (parent_id, now, work_item_id),
    )
    label = f"{current_parent or '<root>'}->{parent_id or '<root>'}"
    for fact in evidence:
        conn.execute("""INSERT OR IGNORE INTO work_item_evidence
            (work_item_id,evidence_kind,label,uri,value_json,created_at)
            VALUES(?,'reparent',?,NULL,?,?)""",
            (work_item_id, label, json.dumps({
                "actor": actor,
                "from_parent_id": current_parent,
                "to_parent_id": parent_id,
                "evidence": fact,
            }, ensure_ascii=False, sort_keys=True), now))
    return {
        "work_item_id": work_item_id,
        "from_parent_id": current_parent,
        "parent_id": parent_id,
    }
TERMINAL = {"completed", "cancelled", "superseded"}
DESCENDANT_TERMINAL = {
    "ALREADY_IMPLEMENTED": "completed",
    "OBSOLETE": "cancelled",
    "SUPERSEDED": "superseded",
    "DUPLICATE_MERGE": "superseded",
}


def reconcile_descendant(
    conn: sqlite3.Connection,
    work_item_id: str,
    *,
    expected_parent_id: str,
    expected_source_ref: str,
    expected_status: str,
    classification: str,
    evidence: list[str],
    superseded_by: str | None = None,
) -> None:
    """Terminalize one named non-prompt child without changing its live root."""
    status = DESCENDANT_TERMINAL.get(classification)
    if not status:
        raise ValueError("invalid_descendant_classification")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(fact, str) or not fact.strip() for fact in evidence
    ):
        raise ValueError("repository_evidence_required")
    row = conn.execute("SELECT * FROM work_items WHERE work_item_id=?", (work_item_id,)).fetchone()
    if not row or not row["parent_id"] or row["prompt_id"]:
        raise ValueError("nonprompt_descendant_required")
    if (row["parent_id"] != expected_parent_id or
            row["source_ref"] != expected_source_ref or
            row["status"] != expected_status):
        raise ValueError("descendant_precondition_changed")
    if row["status"] not in ("pending", "waiting", "blocked", "unknown", status):
        raise ValueError("descendant_lifecycle_conflict")
    if superseded_by:
        successor = conn.execute(
            "SELECT parent_id FROM work_items WHERE work_item_id=?", (superseded_by,)
        ).fetchone()
        if (status != "superseded" or superseded_by == work_item_id or not successor or
                (row["kind"] == "gate" and successor["parent_id"] != row["parent_id"])):
            raise ValueError("invalid_descendant_successor")
    elif status == "superseded":
        raise ValueError("descendant_successor_required")
    if conn.execute("""WITH RECURSIVE ancestors(id,parent_id) AS (
        SELECT work_item_id,parent_id FROM work_items WHERE work_item_id=?
        UNION ALL SELECT p.work_item_id,p.parent_id FROM work_items p
        JOIN ancestors a ON p.work_item_id=a.parent_id
    ) SELECT 1 FROM ancestors a JOIN work_item_runs r ON r.work_item_id=a.id
      WHERE r.state IN ('claimed','running','recovering') LIMIT 1""",
                    (work_item_id,)).fetchone():
        raise ValueError("active_run_requires_normal_lifecycle")
    if conn.execute("""WITH RECURSIVE descendants(id) AS (
        SELECT work_item_id FROM work_items WHERE parent_id=?
        UNION ALL SELECT w.work_item_id FROM work_items w
        JOIN descendants d ON w.parent_id=d.id
    ) SELECT 1 FROM descendants d JOIN work_items w ON w.work_item_id=d.id
      WHERE w.required=1 AND w.status NOT IN ('completed','cancelled','superseded','waived')
      LIMIT 1""", (work_item_id,)).fetchone():
        raise ValueError("required_descendant_incomplete")
    now = c2_identity.utc_now()
    conn.execute("""UPDATE work_items SET status=?,blocker=NULL,current_action=?,
        next_action=NULL,updated_at=? WHERE work_item_id=?""",
                 (status, classification, now, work_item_id))
    if superseded_by:
        conn.execute("""INSERT OR IGNORE INTO work_item_relations
            (from_work_item_id,to_work_item_id,relation_type,created_at,actor,note)
            VALUES(?,?,'superseded_by',?,'c2-descendant-audit',?)""",
                     (work_item_id, superseded_by, now, classification))
    for fact in evidence:
        conn.execute("""INSERT OR IGNORE INTO work_item_evidence
            (work_item_id,evidence_kind,label,uri,value_json,created_at)
            VALUES(?,'classification',?,NULL,?,?)""",
                     (work_item_id, fact[:120], json.dumps(fact, ensure_ascii=False), now))


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
    add_dependencies: list[str] | None = None,
    replace_dependencies: list[str] | None = None,
    add_tags: list[str] | None = None,
    replace_tags: list[str] | None = None,
    include_descendants: bool = False,
) -> None:
    """Update one root and, for terminal dispositions, its imported descendants."""
    fields = dict(fields or {})
    if status not in CLASS_STATUSES.get(classification, set()):
        raise ValueError("invalid_work_item_classification")
    if set(fields) - EDITABLE_FIELDS or "status" in fields:
        raise ValueError("invalid_work_item_fields")
    if "acceptance_json" in fields:
        acceptance = fields["acceptance_json"]
        if not isinstance(acceptance, list) or any(
            not isinstance(item, str) or not item.strip() for item in acceptance
        ):
            raise ValueError("invalid_acceptance")
        fields["acceptance_json"] = json.dumps(acceptance, ensure_ascii=False)
    if "project_id" in fields:
        project = conn.execute(
            "SELECT project_id,name FROM projects WHERE project_id=?",
            (str(fields["project_id"]),),
        ).fetchone()
        if not project:
            raise ValueError("noncanonical_project_reference")
        fields["project_id"] = str(project["project_id"])
        if "project_name" in fields and fields["project_name"] != project["name"]:
            raise ValueError("noncanonical_project_name")
        fields.setdefault("project_name", project["name"])
    elif "project_name" in fields:
        raise ValueError("project_id_required_for_project_name")
    if replace_dependencies is not None and add_dependencies:
        raise ValueError("dependency_add_replace_conflict")
    if replace_tags is not None and add_tags:
        raise ValueError("tag_add_replace_conflict")
    for values, error in (
        (remove_dependencies, "invalid_dependencies"),
        (add_dependencies, "invalid_dependencies"),
        (replace_dependencies, "invalid_dependencies"),
        (add_tags, "invalid_tags"),
        (replace_tags, "invalid_tags"),
    ):
        if values is not None:
            if (not isinstance(values, list)
                    or any(not isinstance(value, str) or not value.strip() for value in values)):
                raise ValueError(error)
            normalized = [value.strip() for value in values]
            if len(normalized) != len(set(normalized)):
                raise ValueError(error)
            if error == "invalid_dependencies":
                if values is remove_dependencies:
                    remove_dependencies = normalized
                elif values is add_dependencies:
                    add_dependencies = normalized
                else:
                    replace_dependencies = normalized
            elif values is add_tags:
                add_tags = normalized
            else:
                replace_tags = normalized
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
    for target in descendants:
        descendant = conn.execute(
            "SELECT kind,required,status FROM work_items WHERE work_item_id=?", (target,)
        ).fetchone()
        if (descendant["kind"] == "gate" and descendant["required"]
                and descendant["status"] not in
                ("completed", "cancelled", "superseded", "waived", "failed")):
            raise ValueError("required_descendant_gate_requires_separate_resolution")
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
    desired_dependencies = replace_dependencies
    for dependency in (add_dependencies or []) + (replace_dependencies or []):
        if dependency == work_item_id or not conn.execute(
            "SELECT 1 FROM work_items WHERE work_item_id=?", (dependency,)
        ).fetchone():
            raise ValueError("dependency_not_found")
        if conn.execute("""WITH RECURSIVE ancestors(id) AS (
            SELECT depends_on_work_item_id FROM work_item_dependencies WHERE work_item_id=?
            UNION SELECT d.depends_on_work_item_id FROM work_item_dependencies d
            JOIN ancestors a ON d.work_item_id=a.id
        ) SELECT 1 FROM ancestors WHERE id=? LIMIT 1""",
            (dependency, work_item_id)).fetchone():
            raise ValueError("dependency_cycle")
    for dependency in remove_dependencies or []:
        if not conn.execute("SELECT 1 FROM work_item_dependencies WHERE work_item_id=? AND depends_on_work_item_id=?",
                            (work_item_id, dependency)).fetchone():
            raise ValueError("dependency_not_found")

    now = c2_identity.utc_now()
    assignments = ["status=?", "updated_at=?", *(f"{key}=?" for key in fields)]
    conn.execute(f"UPDATE work_items SET {','.join(assignments)} WHERE work_item_id=?",
                 [status, now, *fields.values(), work_item_id])
    if desired_dependencies is not None:
        conn.execute("DELETE FROM work_item_dependencies WHERE work_item_id=?", (work_item_id,))
    for dependency in (add_dependencies or []) if desired_dependencies is None else desired_dependencies:
        conn.execute("""INSERT OR IGNORE INTO work_item_dependencies
            (work_item_id,depends_on_work_item_id,required,note) VALUES(?,?,1,'c2_reconcile_item')""",
            (work_item_id, dependency))
    if replace_tags is not None:
        conn.execute("DELETE FROM work_item_tags WHERE work_item_id=?", (work_item_id,))
    for tag in (add_tags or []) if replace_tags is None else replace_tags:
        conn.execute("INSERT OR IGNORE INTO work_item_tags(work_item_id,tag) VALUES(?,?)",
                     (work_item_id, tag.strip()))
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
