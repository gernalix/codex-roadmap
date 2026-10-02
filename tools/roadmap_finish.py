#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from roadmap_result import RoadmapResultError, finish_result
from c2_repository_integration import (RepositoryIntegrationError, prompt_repository,
                                       queue_integration)

from c3_storage import CANONICAL_DB

ROADMAP_DB = CANONICAL_DB


def _queue_repo_integration(prompt_id: str, repo: Path | None = None) -> tuple[str, bool]:
    """Queue completed repository work without waiting for CI or canonical merge."""
    try:
        worktree = (repo or Path.cwd()).expanduser().resolve()
        # repo is the target project worktree. External repositories do not
        # contain roadmap.sqlite; routing metadata comes from codex-roadmap.
        repository = prompt_repository(ROADMAP_DB, prompt_id)
        return queue_integration(prompt_id, repository, worktree)
    except RepositoryIntegrationError as exc:
        raise RoadmapResultError(str(exc)) from exc


def finish(
    repo: Path,
    prompt_id: str,
    *,
    result: str = "PASS",
    dry_run: bool = False,
    confirm_executed: bool = False,
    integration_timeout: float = 0.0,
):
    # integration_timeout is retained for CLI compatibility but asynchronous
    # workers never wait for repository integration anymore.
    _ = integration_timeout
    integration = "dry-run" if result == "PASS" else "not-applicable"
    integrated = True
    if result == "PASS" and not dry_run:
        integration, integrated = _queue_repo_integration(prompt_id, repo)
        if not integrated:
            return {
                "status": "queued",
                "prompt_id": prompt_id,
                "result": "QUEUED",
                "finish_mode": "async_integration_queue",
                "repo_integration": integration,
                "user_action": "none",
            }
    payload = finish_result(
        repo,
        prompt_id,
        result,
        dry_run=dry_run,
        confirm_executed=confirm_executed,
    )
    return {
        **payload,
        "finish_mode": "remote_single_writer",
        "repo_integration": integration,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Canonical finalizer for PASS/BLOCKED/FAIL/CANCELLED roadmap outcomes.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--result", default="PASS", choices=("PASS", "BLOCKED", "FAIL", "CANCELLED", "UNKNOWN"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-executed", action="store_true")
    parser.add_argument("--integration-timeout", type=float, default=0.0, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        payload = finish(
            Path(args.repo).expanduser(),
            args.prompt_id,
            result=args.result,
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
