#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from submit_mutation import MutationSubmitError, SCHEMA, submit_document

RESULT_STATUS = {
    "PASS": "completed",
    "FAIL": "failed",
    "BLOCKED": "blocked",
    "CANCELLED": "cancelled",
    "UNKNOWN": "unknown",
}


class RoadmapResultError(RuntimeError):
    pass


def finish_result(
    repo: Path,
    prompt_id: str,
    result: str,
    *,
    confirm_executed: bool = False,
    dry_run: bool = False,
) -> dict[str, str]:
    # repo stays in the public API for compatibility with existing prompts.
    # Deliberately do not read, modify, fetch, merge or push its git checkout.
    _ = repo
    if result not in RESULT_STATUS:
        raise RoadmapResultError(f"invalid_result:{result}")
    if not re.fullmatch(r"\d{6}", prompt_id):
        raise RoadmapResultError(f"invalid_prompt_id:{prompt_id}")
    if not dry_run and not confirm_executed:
        raise RoadmapResultError("mutation_requires_confirm_executed")

    document = {
        "schema": SCHEMA,
        "actor": "codex",
        "operations": [
            {
                "op": "status",
                "prompt_id": prompt_id,
                "status": RESULT_STATUS[result],
                "actor": "codex",
                "note": f"terminal:roadmap_result:{result}",
            }
        ],
    }
    request_key = f"terminal-{prompt_id}"

    if dry_run:
        return {
            "status": "ready",
            "prompt_id": prompt_id,
            "result": result,
            "target_status": RESULT_STATUS[result],
            "request_key": request_key,
        }

    try:
        submitted = submit_document(document, request_key=request_key)
    except MutationSubmitError as exc:
        raise RoadmapResultError(str(exc)) from exc

    return {
        "status": "queued",
        "prompt_id": prompt_id,
        "result": result,
        "target_status": RESULT_STATUS[result],
        **submitted,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Queue a terminal Codex result in the remote roadmap mutation inbox."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--result", required=True, choices=tuple(RESULT_STATUS))
    parser.add_argument("--confirm-executed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = finish_result(
            Path(args.repo).expanduser(),
            args.prompt_id,
            args.result,
            confirm_executed=args.confirm_executed,
            dry_run=args.dry_run,
        )
    except RoadmapResultError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
