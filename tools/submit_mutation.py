#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "codex-roadmap.mutation.v1"
ISSUE_PREFIX = "[roadmap-mutation] "
DEFAULT_REMOTE_REPO = os.environ.get("CODEX_ROADMAP_REMOTE_REPO", "gernalix/codex-roadmap")
# Kept for CLI compatibility; Issues are repository-scoped and do not write a branch.
DEFAULT_REMOTE_BRANCH = os.environ.get("CODEX_ROADMAP_REMOTE_BRANCH", "main")


class MutationSubmitError(RuntimeError):
    pass


def _canonical_bytes(document: dict[str, Any]) -> bytes:
    return (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _validate_request_key(request_key: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", request_key):
        raise MutationSubmitError(f"invalid_request_key:{request_key}")
    return request_key


def _gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(
            ["gh", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise MutationSubmitError("gh_cli_missing") from exc
    if check and proc.returncode:
        raise MutationSubmitError(f"gh_failed:{proc.stderr.strip()}")
    return proc


def _matching_issues(repository: str, title: str) -> list[dict[str, Any]]:
    proc = _gh(
        "issue",
        "list",
        "--repo",
        repository,
        "--state",
        "all",
        "--limit",
        "100",
        "--search",
        title,
        "--json",
        "number,title,state,body,url",
    )
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise MutationSubmitError("invalid_issue_list_response") from exc
    if not isinstance(rows, list):
        raise MutationSubmitError("invalid_issue_list_response")
    return [row for row in rows if isinstance(row, dict) and row.get("title") == title]


def submit_document(
    document: dict[str, Any],
    *,
    request_key: str,
    repository: str = DEFAULT_REMOTE_REPO,
    branch: str = DEFAULT_REMOTE_BRANCH,
) -> dict[str, str]:
    # branch is intentionally ignored: the queue is GitHub Issues, not Git refs.
    _ = branch
    if document.get("schema") != SCHEMA:
        raise MutationSubmitError("invalid_mutation_schema")
    operations = document.get("operations")
    if not isinstance(operations, list) or not operations:
        raise MutationSubmitError("empty_mutation")

    request_key = _validate_request_key(request_key)
    title = ISSUE_PREFIX + request_key
    body = _canonical_bytes(document).decode("utf-8")

    existing = _matching_issues(repository, title)
    if existing:
        for issue in existing:
            try:
                existing_doc = json.loads(str(issue.get("body") or ""))
            except json.JSONDecodeError as exc:
                raise MutationSubmitError(f"request_key_conflict:{request_key}:invalid_body") from exc
            if _canonical_bytes(existing_doc) != _canonical_bytes(document):
                raise MutationSubmitError(f"request_key_conflict:{request_key}")
        # Duplicate identical Issues are harmless: the DB receipt makes application
        # idempotent. Return the oldest canonical issue for stable reporting.
        issue = sorted(existing, key=lambda row: int(row["number"]))[0]
        state = "applied" if str(issue.get("state")).upper() == "CLOSED" else "pending"
        return {
            "submission": state,
            "request_key": request_key,
            "issue_number": str(issue["number"]),
            "issue_url": str(issue.get("url") or ""),
        }

    proc = _gh(
        "api",
        "--method",
        "POST",
        f"repos/{repository}/issues",
        "-f",
        f"title={title}",
        "-f",
        f"body={body}",
        check=False,
    )
    if proc.returncode:
        # A concurrent client may have created the same deterministic request.
        raced = _matching_issues(repository, title)
        for issue in raced:
            try:
                existing_doc = json.loads(str(issue.get("body") or ""))
            except json.JSONDecodeError:
                continue
            if _canonical_bytes(existing_doc) == _canonical_bytes(document):
                return {
                    "submission": "pending",
                    "request_key": request_key,
                    "issue_number": str(issue["number"]),
                    "issue_url": str(issue.get("url") or ""),
                }
        raise MutationSubmitError(f"gh_issue_create_failed:{proc.stderr.strip()}")

    try:
        issue = json.loads(proc.stdout)
        number = str(issue["number"])
        url = str(issue.get("html_url") or "")
    except (json.JSONDecodeError, KeyError) as exc:
        raise MutationSubmitError("invalid_issue_create_response") from exc

    return {
        "submission": "queued",
        "request_key": request_key,
        "issue_number": number,
        "issue_url": url,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Submit one immutable roadmap mutation as a GitHub Issue; never write the roadmap Git branch."
    )
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--request-key", required=True)
    parser.add_argument("--repository", default=DEFAULT_REMOTE_REPO)
    parser.add_argument("--branch", default=DEFAULT_REMOTE_BRANCH, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.file.read_text(encoding="utf-8"))
        result = submit_document(
            document,
            request_key=args.request_key,
            repository=args.repository,
            branch=args.branch,
        )
    except (OSError, ValueError, MutationSubmitError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps({"status": "ok", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
