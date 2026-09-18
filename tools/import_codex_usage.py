#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from roadmap_sync import DEFAULT_REMOTE_BRANCH, DEFAULT_REMOTE_REPO, SyncError, sync


def import_metrics(
    repo: Path,
    source: Path,
    *,
    render_after: bool = True,
    repository: str = DEFAULT_REMOTE_REPO,
    branch: str = DEFAULT_REMOTE_BRANCH,
) -> dict[str, object]:
    """Compatibility wrapper: queue usage mutations; never write roadmap.sqlite locally."""
    _ = render_after
    return sync(repo, source, repository=repository, branch=branch)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Queue codex-usage metadata through the remote roadmap single writer."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source", required=True)
    parser.add_argument("--repository", default=DEFAULT_REMOTE_REPO)
    parser.add_argument("--branch", default=DEFAULT_REMOTE_BRANCH)
    parser.add_argument(
        "--no-render",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        stats = import_metrics(
            Path(args.repo).expanduser().resolve(),
            Path(args.source).expanduser().resolve(),
            render_after=not args.no_render,
            repository=args.repository,
            branch=args.branch,
        )
    except SyncError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(stats, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
