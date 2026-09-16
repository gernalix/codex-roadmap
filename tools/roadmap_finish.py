#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil

from roadmap_guard import RoadmapError, complete, git_root, reconcile, run

PROMPT_MISMATCH_PREFIX = "prompt_identity_mismatch:"
MAX_PUSH_RACE_RETRIES = 3
_RETRYABLE_PUSH_MARKERS = (
    "fetch first",
    "non-fast-forward",
    "incorrect old value provided",
)
_FAILED_WORKTREE_RE = re.compile(r"isolated_worktree=([^\s]+)")


def _is_retryable_push_race(exc: RoadmapError) -> bool:
    text = str(exc).lower()
    return text.startswith("push_blocked:") and any(marker in text for marker in _RETRYABLE_PUSH_MARKERS)


def _cleanup_failed_race_worktree(repo: Path, exc: RoadmapError) -> None:
    match = _FAILED_WORKTREE_RE.search(str(exc))
    if not match:
        return
    worktree = Path(match.group(1))
    run(repo, "worktree", "remove", "--force", str(worktree), check=False)
    shutil.rmtree(worktree.parent, ignore_errors=True)


def _finish_once(
    repo: Path,
    prompt_id: str,
    *,
    dry_run: bool,
    confirm_executed: bool,
) -> dict[str, str]:
    try:
        payload = complete(repo, prompt_id, dry_run=dry_run, result="PASS")
        return {**payload, "finish_mode": "complete"}
    except RoadmapError as exc:
        if not str(exc).startswith(PROMPT_MISMATCH_PREFIX):
            raise
        if not dry_run and not confirm_executed:
            raise RoadmapError(
                "finish_requires_confirm_executed_after_roadmap_advance"
            ) from exc

    payload = reconcile(
        repo,
        prompt_id,
        dry_run=dry_run,
        confirm_executed=confirm_executed,
        result="PASS",
    )
    return {**payload, "finish_mode": "reconcile"}


def finish(
    repo: Path,
    prompt_id: str,
    *,
    dry_run: bool = False,
    confirm_executed: bool = False,
) -> dict[str, str]:
    """Finalize one executed PASS task safely even when other tasks finish concurrently.

    Identity races are handled by complete -> reconcile. A concurrent ref-advance push
    is retried from fresh origin/main up to MAX_PUSH_RACE_RETRIES times. Auth, network,
    policy and other push failures remain fail-closed and are never retried.
    """
    retries = 0
    while True:
        try:
            payload = _finish_once(
                repo,
                prompt_id,
                dry_run=dry_run,
                confirm_executed=confirm_executed,
            )
            return {**payload, "push_race_retries": str(retries)}
        except RoadmapError as exc:
            if dry_run or not _is_retryable_push_race(exc) or retries >= MAX_PUSH_RACE_RETRIES:
                raise
            _cleanup_failed_race_worktree(repo, exc)
            retries += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Finalize an already-executed PASS roadmap task in one race-safe invocation."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--confirm-executed",
        action="store_true",
        help="Allow safe reconcile when another task advanced the roadmap first.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = git_root(Path(args.repo).expanduser())
        payload = finish(
            repo,
            args.prompt_id,
            dry_run=args.dry_run,
            confirm_executed=args.confirm_executed,
        )
    except RoadmapError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
