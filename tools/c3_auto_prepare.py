#!/usr/bin/env python3
"""Bounded C3 preparation of ready auto items from canonical evidence."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import tempfile
from typing import Any

import c2_prepare_codex
from c3_storage import CANONICAL_DB
from c3_projects import project_catalog

BATCH_LIMIT = 25


def repo_slug(value: object) -> str | None:
    text = str(value or "").strip()
    if text.startswith("git@github.com:"):
        text = text.removeprefix("git@github.com:")
    elif "github.com/" in text:
        text = text.split("github.com/", 1)[1]
    text = text.removesuffix(".git").strip("/")
    return text if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text) else None


def repo_key(value: object) -> str | None:
    slug = repo_slug(value)
    return slug.lower() if slug else None


def _catalog_repositories(conn: sqlite3.Connection) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    with project_catalog(conn) as catalog:
        rows = catalog.execute("""SELECT r.project_id,p.name,r.repository_id,
                 r.remote_url,r.location,r.worktree_path,r.runtime_path
              FROM repositories r JOIN projects p USING(project_id)
              WHERE r.canonical=1""").fetchall()
    for row in rows:
        canonical_repo = repo_slug(row[3])
        if not canonical_repo:
            canonical_repo = next((slug for value in row[3:]
                                   if (slug := repo_slug(value))), None)
        if not canonical_repo:
            continue
        for value in row[3:]:
            key = repo_key(value)
            if key:
                result.setdefault(key, []).append({
                    "project_id": str(row[0]), "project_name": str(row[1]),
                    "repository_id": str(row[2]), "repo": canonical_repo,
                })
    return result


def _profile(conn: sqlite3.Connection, project_id: str, repo: str) -> dict[str, str] | None:
    rows = conn.execute("""SELECT s.activity,e.model,e.reasoning,
                 SUM(CASE WHEN e.outcome='PASS' THEN 1 ELSE 0 END) AS passed,
                 SUM(CASE WHEN e.outcome IN ('FAIL','BLOCKED') THEN 1 ELSE 0 END) AS failed
              FROM executions e
              JOIN work_items w ON w.prompt_id=e.prompt_id
              JOIN work_item_execution_specs s ON s.work_item_id=w.work_item_id
              WHERE w.project_id=? AND e.model IS NOT NULL AND e.reasoning IS NOT NULL
              GROUP BY s.activity,e.model,e.reasoning,w.repo""", (project_id,)).fetchall()
    qualified = []
    for row in rows:
        activity, model, reasoning, passed, failed = row
        if activity not in ("coding", "diagnostic") or not passed or failed:
            continue
        # The repository spelling may have changed between HTTPS and slug form,
        # but its canonical GitHub identity must still match exactly.
        source = conn.execute("""SELECT w.repo FROM executions e JOIN work_items w
             ON w.prompt_id=e.prompt_id JOIN work_item_execution_specs s
             ON s.work_item_id=w.work_item_id WHERE w.project_id=? AND s.activity=?
             AND e.model=? AND e.reasoning=? AND e.outcome='PASS'""",
             (project_id, activity, model, reasoning)).fetchall()
        if any(repo_key(item[0]) == repo_key(repo) for item in source):
            qualified.append((activity, model, reasoning))
    qualified = sorted(set(qualified))
    if len(qualified) != 1:
        return None
    activity, model, reasoning = qualified[0]
    return {"activity": activity, "model": model, "reasoning": reasoning}


def plan(conn: sqlite3.Connection, limit: int = BATCH_LIMIT) -> dict[str, Any]:
    if not 1 <= limit <= BATCH_LIMIT:
        raise ValueError("bounded_limit_required")
    catalog = _catalog_repositories(conn)
    rows = conn.execute("""SELECT w.* FROM v_work_item_runnable w
        LEFT JOIN work_item_execution_specs s USING(work_item_id)
        WHERE s.work_item_id IS NULL AND w.executor_policy='auto'
        ORDER BY w.sort_order,w.created_at,w.work_item_id""").fetchall()
    candidates, waiting = [], []
    for item in rows:
        repo = repo_key(item["repo"])
        identities = catalog.get(repo or "", [])
        distinct = {(x["project_id"], x["project_name"], x["repo"]) for x in identities}
        if not str(item["title"] or "").strip():
            waiting.append({"work_item_id": item["work_item_id"], "reason": "title_missing"})
        elif not str(item["objective"] or "").strip():
            waiting.append({"work_item_id": item["work_item_id"], "reason": "objective_missing"})
        elif not json.loads(item["acceptance_json"] or "[]"):
            waiting.append({"work_item_id": item["work_item_id"], "reason": "acceptance_missing"})
        elif len(distinct) != 1:
            waiting.append({"work_item_id": item["work_item_id"], "reason": "canonical_repository_identity_missing"})
        else:
            project_id, project_name, canonical_repo = next(iter(distinct))
            identity = {"project_id": project_id, "project_name": project_name,
                        "repo": canonical_repo}
            profile = _profile(conn, identity["project_id"], identity["repo"])
            if not profile:
                waiting.append({"work_item_id": item["work_item_id"], "reason": "unique_proven_execution_profile_missing"})
            else:
                candidates.append({"item": dict(item), "identity": identity, "profile": profile,
                    "evidence": [
                        "MegaVault canonical repository " + identities[0]["repository_id"],
                        "canonical successful execution profile for " + identity["repo"],
                    ]})
    return {"dependency_ready": len(rows), "prepared_candidates": candidates[:limit],
            "preparation_required": len(candidates), "waiting": waiting}


def prompt_body(item: dict[str, Any]) -> str:
    acceptance = json.loads(item.get("acceptance_json") or "[]")
    parts = ["# " + str(item["title"]).strip(), "", "## Objective", str(item["objective"]).strip()]
    if acceptance:
        parts += ["", "## Acceptance criteria", *["- " + str(value) for value in acceptance]]
    if str(item.get("current_action") or "").strip():
        parts += ["", "## Current action", str(item["current_action"]).strip()]
    if str(item.get("next_action") or "").strip():
        parts += ["", "## Next action", str(item["next_action"]).strip()]
    return "\n".join(parts) + "\n"


def apply(snapshot: Path, limit: int) -> dict[str, Any]:
    with closing(sqlite3.connect(f"{snapshot.resolve().as_uri()}?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        outcome = plan(conn, limit)
    results = []
    for candidate in outcome["prepared_candidates"]:
        with tempfile.TemporaryDirectory(prefix="c3-auto-prepare-") as tmp:
            base = Path(tmp)
            prompt = base / "prompt.md"
            spec_path = base / "spec.json"
            prompt.write_text(prompt_body(candidate["item"]), encoding="utf-8")
            spec = {"work_item_id": candidate["item"]["work_item_id"], "prompt_file": str(prompt),
                "source": "c3-auto-preparation", **candidate["profile"], **candidate["identity"],
                "readiness_evidence": candidate["evidence"]}
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            results.append(c2_prepare_codex.prepare(c2_prepare_codex.load_spec(spec_path)))
    return {**outcome, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=BATCH_LIMIT)
    parser.add_argument("--snapshot", type=Path, default=CANONICAL_DB)
    args = parser.parse_args()
    with closing(sqlite3.connect(f"{args.snapshot.resolve().as_uri()}?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        result = plan(conn, args.limit)
    if args.apply:
        result = apply(args.snapshot, args.limit)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
