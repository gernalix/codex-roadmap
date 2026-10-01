#!/usr/bin/env python3
"""Permanent fail-closed boundary for retired C2 orchestration."""
from pathlib import Path

MARKER = Path.home() / ".local/state/c3-control/c2-retired.json"


class RetirementError(RuntimeError):
    pass


def require_not_retired(marker=MARKER):
    # Deleting historical evidence must not re-enable a retired implementation.
    raise RetirementError("c2_retired_permanently")


def retire(**kwargs):
    raise RetirementError("legacy_cutover_retired_permanently")


def main():
    import json
    print(json.dumps({"status": "blocked", "reason": "legacy_cutover_retired_permanently"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
