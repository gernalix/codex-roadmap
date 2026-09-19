#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from roadmap_result import RoadmapResultError, finish_result


DEFAULT_REPO_TASK = Path.home() / "projects" / "github-autosync" / "repo_single_writer.py"


def _wait_repo_single_writer(prompt_id: str, *, timeout: float = 900.0) -> str:
    if not DEFAULT_REPO_TASK.is_file():
        raise RoadmapResultError("repo_task_helper_missing")
    proc = subprocess.run(
        [
            "python3",
            str(DEFAULT_REPO_TASK),
            "wait-any",
            "--task-id",
            prompt_id,
            "--timeout",
            str(timeout),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RoadmapResultError(f"repo_single_writer_not_merged:{detail}")
    return proc.stdout.strip() or "no-task-record"


def finish(
    repo: Path,
    prompt_id: str,
    *,
    dry_run: bool = False,
    confirm_executed: bool = False,
    integration_timeout: float = 900.0,
):
    integration = "dry-run"
    if not dry_run:
        integration = _wait_repo_single_writer(prompt_id, timeout=integration_timeout)
    payload = finish_result(
        repo,
        prompt_id,
        "PASS",
        dry_run=dry_run,
        confirm_executed=confirm_executed,
    )
    return {
        **payload,
        "finish_mode": "remote_single_writer",
        "repo_integration": integration,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Compatibility wrapper: queue PASS for the roadmap single writer.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-executed", action="store_true")
    parser.add_argument("--integration-timeout", type=float, default=900.0)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        payload = finish(
            Path(args.repo).expanduser(),
            args.prompt_id,
            dry_run=args.dry_run,
            confirm_executed=args.confirm_executed,
            integration_timeout=args.integration_timeout,
        )
    except RoadmapResultError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
