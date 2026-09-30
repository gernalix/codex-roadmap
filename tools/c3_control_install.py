#!/usr/bin/env python3
"""Stage C3 user units without enabling them before retirement."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UNITS = {
    "c3-symphony.service": ROOT / "operations/c3-symphony.service",
    **{name: ROOT / "systemd" / name for name in (
        "c3-roadmap-snapshot.service", "c3-roadmap-snapshot.timer",
        "c3-runtime.service", "c3-runtime.timer", "c3-runtime.path",
        "c3-inbox-maintenance.service", "c3-inbox-maintenance.timer")},
}


def install(target: Path) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    for name, source in UNITS.items():
        shutil.copy2(source, target / name)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    return list(UNITS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-unit-dir", type=Path,
                        default=Path.home() / ".config/systemd/user")
    args = parser.parse_args()
    print("staged: " + ", ".join(install(args.user_unit_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
