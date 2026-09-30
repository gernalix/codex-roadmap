#!/usr/bin/env python3
"""C3 control-plane entrypoint for roadmap data and integration status."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import c2_snapshot_sync
from c2_repository_integration import integration_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--repo", type=Path, default=c2_snapshot_sync.DEFAULT_REPO)
    snapshot.add_argument("--output", type=Path, default=c2_snapshot_sync.DEFAULT_OUTPUT)
    integration = sub.add_parser("integration-status")
    integration.add_argument("prompt_id")
    integration.add_argument("repository")
    args = parser.parse_args(argv)
    if args.action == "snapshot":
        print(json.dumps(c2_snapshot_sync.sync(args.repo, args.output), sort_keys=True))
        return 0
    print(json.dumps(integration_status(args.prompt_id, args.repository), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
