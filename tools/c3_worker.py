#!/usr/bin/env python3
"""Execute C3 claimed Symphony, browser, and native runs only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from c2_worker import run_once


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    result = run_once(args.db, args.run_id,
                      state_root=Path.home() / ".local/state/c3-control/runs",
                      worker_prefix="c3-run:", legacy_codex_allowed=False)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
