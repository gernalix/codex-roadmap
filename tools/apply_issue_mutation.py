#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from roadmap_db import (
    apply_mutation,
    connect,
    now_utc,
    reconcile_prompt_file_locations,
    refresh_materialization_hashes,
    render,
)

SCHEMA = "codex-roadmap.mutation.v1"
TITLE_PREFIX = "[roadmap-mutation] "
REQUEST_KEY_RE = re.compile(r"[A-Za-z0-9._-]+\Z")


class IssueMutationError(RuntimeError):
    pass


def canonical_bytes(document: dict[str, Any]) -> bytes:
    return (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def parse_event(event_path: Path) -> tuple[int, str, str, dict[str, Any]]:
    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
        issue = event["issue"]
        issue_number = int(issue["number"])
        title = str(issue["title"])
        body = str(issue.get("body") or "")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise IssueMutationError("invalid_issue_event") from exc

    if not title.startswith(TITLE_PREFIX):
        raise IssueMutationError("not_roadmap_mutation_issue")
    request_key = title[len(TITLE_PREFIX):].strip()
    if not REQUEST_KEY_RE.fullmatch(request_key):
        raise IssueMutationError(f"invalid_request_key:{request_key}")

    try:
        document = json.loads(body)
    except json.JSONDecodeError as exc:
        raise IssueMutationError("issue_body_not_json") from exc
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise IssueMutationError("invalid_mutation_schema")
    operations = document.get("operations")
    if not isinstance(operations, list) or not operations:
        raise IssueMutationError("empty_mutation")
    return issue_number, request_key, str(document.get("actor") or "unknown"), document


def _safe_prompt_path(repo: Path, rel: str) -> Path:
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts or len(path.parts) < 2 or path.parts[0] != "prompts":
        raise IssueMutationError(f"invalid_prompt_path:{rel}")
    target = (repo / path).resolve()
    prompts_root = (repo / "prompts").resolve()
    if prompts_root not in target.parents:
        raise IssueMutationError(f"invalid_prompt_path:{rel}")
    return target


def materialize_registered_prompts(repo: Path, document: dict[str, Any]) -> int:
    written = 0
    for operation in document["operations"]:
        if not isinstance(operation, dict) or operation.get("op") != "register":
            continue
        prompt_text = operation.get("prompt_text")
        current_path = operation.get("current_path")
        if not isinstance(prompt_text, str) or not isinstance(current_path, str):
            raise IssueMutationError("register_requires_prompt_text_and_current_path")
        target = _safe_prompt_path(repo, current_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        normalized = prompt_text if prompt_text.endswith("\n") else prompt_text + "\n"
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing != normalized:
                raise IssueMutationError(f"prompt_materialization_conflict:{current_path}")
            continue
        target.write_text(normalized, encoding="utf-8")
        written += 1
    return written


def apply_issue(repo: Path, event_path: Path) -> dict[str, Any]:
    repo = Path(repo).resolve()
    issue_number, request_key, actor, document = parse_event(event_path)
    payload_sha256 = hashlib.sha256(canonical_bytes(document)).hexdigest()

    conn = connect(repo)
    operations_applied = 0
    idempotent = False
    try:
        receipt = conn.execute(
            "SELECT * FROM mutation_receipts WHERE request_key=?", (request_key,)
        ).fetchone()
        if receipt:
            if (
                int(receipt["issue_number"]) != issue_number
                or str(receipt["payload_sha256"]) != payload_sha256
            ):
                raise IssueMutationError(f"request_key_conflict:{request_key}")
            idempotent = True
        else:
            issue_collision = conn.execute(
                "SELECT request_key,payload_sha256 FROM mutation_receipts WHERE issue_number=?",
                (issue_number,),
            ).fetchone()
            if issue_collision:
                raise IssueMutationError(
                    f"issue_number_conflict:{issue_number}:{issue_collision['request_key']}"
                )
            for operation in document["operations"]:
                if not isinstance(operation, dict):
                    raise IssueMutationError("invalid_operation")
                apply_mutation(conn, operation, default_actor=actor)
                operations_applied += 1
            refresh_materialization_hashes(conn, repo)
            conn.execute(
                """INSERT INTO mutation_receipts(
                     request_key,issue_number,payload_sha256,actor,applied_at
                   ) VALUES(?,?,?,?,?)""",
                (request_key, issue_number, payload_sha256, actor, now_utc()),
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    # Prompt files are part of the writer-owned materialization, not client commits.
    # On an idempotent rerun this also repairs a missing file before re-rendering.
    materialized = materialize_registered_prompts(repo, document)
    reconcile_prompt_file_locations(repo)
    render(repo)
    return {
        "status": "ok",
        "issue_number": issue_number,
        "request_key": request_key,
        "operations": operations_applied,
        "materialized_prompts": materialized,
        "idempotent": idempotent,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply one GitHub Issue roadmap mutation through the canonical single writer."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--event", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = apply_issue(Path(args.repo), args.event)
    except (IssueMutationError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
