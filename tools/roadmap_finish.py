#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from roadmap_result import RoadmapResultError, finish_result


def finish(repo: Path, prompt_id: str, *, dry_run: bool = False, confirm_executed: bool = False):
    payload = finish_result(
        repo,
        prompt_id,
        "PASS",
        dry_run=dry_run,
        confirm_executed=confirm_executed,
    )
    return {**payload, "finish_mode": "remote_single_writer"}


def build_parser():
    parser = argparse.ArgumentParser(description="Compatibility wrapper: queue PASS for the roadmap single writer.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-executed", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        payload = finish(
            Path(args.repo).expanduser(),
            args.prompt_id,
            dry_run=args.dry_run,
            confirm_executed=args.confirm_executed,
        )
    except RoadmapResultError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
