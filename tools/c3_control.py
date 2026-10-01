#!/usr/bin/env python3
"""C3 control-plane entrypoint for roadmap data and integration status."""
from __future__ import annotations

import argparse
import json

import sqlite3
from contextlib import closing
from c3_storage import CANONICAL_DB
from c2_repository_integration import integration_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("status")
    integration = sub.add_parser("integration-status")
    integration.add_argument("prompt_id")
    integration.add_argument("repository")
    args = parser.parse_args(argv)
    if args.action == "status":
        with closing(sqlite3.connect(CANONICAL_DB.resolve().as_uri() + '?mode=ro', uri=True)) as db:
            print(json.dumps({'database': str(CANONICAL_DB),
                              'integrity': db.execute('PRAGMA quick_check').fetchone()[0],
                              'active_runs': db.execute("SELECT COUNT(*) FROM work_item_runs WHERE state IN ('claimed','running','recovering')").fetchone()[0]}, sort_keys=True))
        return 0
    print(json.dumps(integration_status(args.prompt_id, args.repository), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
