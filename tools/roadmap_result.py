#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sqlite3
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


ROADMAP_ROOT = Path.home() / "projects" / "codex-roadmap"
ROADMAP_DB = ROADMAP_ROOT / "roadmap.sqlite"


def _current_running_generation(prompt_id: str) -> int:
    """Read a candidate run generation; the writer validates it again atomically."""
    try:
        from roadmap_pull import guarded_pull

        guarded_pull(ROADMAP_ROOT)
    except Exception as exc:
        raise RoadmapResultError("current_run_refresh_failed") from exc
    try:
        conn = sqlite3.connect(f"file:{ROADMAP_DB.resolve()}?mode=ro", uri=True)
        row = conn.execute(
            "SELECT p.status,(SELECT MAX(history_id) FROM status_history "
            "WHERE prompt_id=p.prompt_id AND new_status='running') "
            "FROM prompts p WHERE p.prompt_id=?",
            (prompt_id,),
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        raise RoadmapResultError("current_run_read_failed") from exc
    finally:
        try:
            conn.close()
        except UnboundLocalError:
            pass
    if not row or row[0] != "running" or row[1] is None:
        raise RoadmapResultError("current_run_not_running")
    return int(row[1])


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

    running_history_id = _current_running_generation(prompt_id)

    document = {
        "schema": SCHEMA,
        "actor": "codex",
        "operations": [
            {
                "op": "terminal_request",
                "prompt_id": prompt_id,
                "status": RESULT_STATUS[result],
                "actor": "codex",
                "note": f"terminal:roadmap_result:{result}",
                "expected_running_history_id": running_history_id,
            }
        ],
    }
    request_key = f"terminal-{prompt_id}-{running_history_id}-{RESULT_STATUS[result]}"

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
