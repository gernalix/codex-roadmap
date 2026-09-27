#!/usr/bin/env python3
"""Capture one incidental C2 issue with no roadmap scan or classification."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import uuid

from submit_mutation import submit_document


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def _context(args) -> dict[str, str]:
    task_id = args.task_id or _env("C2_TASK_ID") or _env("C2_WORK_ITEM_ID")
    run_id = args.run_id or _env("C2_RUN_ID")
    chat_url = args.chat_url or _env("CHATGPT_CONVERSATION_URL")
    executor_ref = args.executor_ref or _env("C2_EXECUTOR_REF")
    thread_id = _env("CODEX_THREAD_ID")
    if not chat_url and thread_id:
        chat_url = "codex://threads/" + thread_id
    if not executor_ref and thread_id:
        executor_ref = thread_id

    result: dict[str, str] = {}
    for key, value in (
        ("task_id", task_id),
        ("run_id", run_id),
        ("chat_url", chat_url),
        ("executor_ref", executor_ref),
    ):
        if value:
            result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--stdin", action="store_true", help="Read the exact description from stdin")
    source.add_argument("--file", type=Path, help="Read the exact description from a UTF-8 file")
    source.add_argument("--json", help="JSON object with description and optional capture metadata")
    parser.add_argument("description", nargs="?")
    parser.add_argument("--issue-id", help="Stable issue:<32 hex> identity for an idempotent retry")
    parser.add_argument("--task-id")
    parser.add_argument("--run-id")
    parser.add_argument("--repo")
    parser.add_argument("--code-location")
    parser.add_argument("--executor-ref")
    parser.add_argument("--chat-url")
    args = parser.parse_args()

    if args.description is not None and (args.stdin or args.file or args.json):
        parser.error("choose one description source")
    payload = {}
    if args.json:
        try:
            payload = json.loads(args.json)
        except json.JSONDecodeError:
            parser.error("invalid JSON payload")
        allowed = {"description", "issue_id", "task_id", "run_id", "repo",
                   "code_location", "executor_ref", "chat_url"}
        if not isinstance(payload, dict) or set(payload) - allowed:
            parser.error("invalid JSON capture fields")
        description = payload.get("description")
    elif args.stdin:
        description = sys.stdin.read()
    elif args.file:
        description = args.file.read_text(encoding="utf-8")
    else:
        description = args.description
    if not isinstance(description, str) or not description.strip():
        parser.error("description required")

    supplied_id = args.issue_id or payload.get("issue_id")
    if supplied_id and not re.fullmatch(r"issue:[0-9a-f]{32}", supplied_id):
        parser.error("invalid issue ID")

    issue_id = supplied_id or "issue:" + uuid.uuid4().hex
    arguments = {
        "issue_id": issue_id,
        "description": description,
        **_context(args),
    }
    for key in ("task_id", "run_id", "repo", "code_location", "executor_ref", "chat_url"):
        value = getattr(args, key) or payload.get(key)
        if value:
            arguments[key] = value

    request_key = "c2-issue-capture-" + issue_id.removeprefix("issue:")
    result = submit_document(
        {
            "schema": "codex-roadmap.mutation.v1",
            "actor": "c2-issue-capture",
            "operations": [{"op": "c2_capture_issue", "arguments": arguments}],
        },
        request_key=request_key,
        lookup_existing=bool(supplied_id),
    )
    print(json.dumps({"issue_id": issue_id, **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
