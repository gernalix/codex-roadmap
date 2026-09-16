#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from roadmap_guard import RoadmapError, complete, git_root, reconcile

PROMPT_MISMATCH_PREFIX = "prompt_identity_mismatch:"


def finish(
    repo: Path,
    prompt_id: str,
    *,
    dry_run: bool = False,
    confirm_executed: bool = False,
) -> dict[str, str]:
    """Finalize one executed PASS task even if the roadmap advanced concurrently.

    Normal case: complete the currently selected prompt. If another prompt advanced the
    roadmap first, fall back to the guard's explicit reconcile path. The mutating
    fallback remains fail-closed unless the caller explicitly confirms that the target
    task was already executed.
    """
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Finalize an already-executed PASS roadmap task in one invocation."
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
