#!/usr/bin/env python3
"""Capture one incidental C2 issue with no roadmap scan or classification."""
from __future__ import annotations

import argparse
import json
import os
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
    parser.add_argument("description")
    parser.add_argument("--task-id")
    parser.add_argument("--run-id")
    parser.add_argument("--repo")
    parser.add_argument("--code-location")
    parser.add_argument("--executor-ref")
    parser.add_argument("--chat-url")
    args = parser.parse_args()

    issue_id = "issue:" + uuid.uuid4().hex
    arguments = {
        "issue_id": issue_id,
        "description": args.description,
        **_context(args),
    }
    if args.repo:
        arguments["repo"] = args.repo
    if args.code_location:
        arguments["code_location"] = args.code_location

    request_key = "c2-issue-capture-" + issue_id.removeprefix("issue:")
    result = submit_document(
        {
            "schema": "codex-roadmap.mutation.v1",
            "actor": "c2-issue-capture",
            "operations": [{"op": "c2_capture_issue", "arguments": arguments}],
        },
        request_key=request_key,
        lookup_existing=False,
    )
    print(json.dumps({"issue_id": issue_id, **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
