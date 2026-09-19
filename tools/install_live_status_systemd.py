#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

UNIT_NAMES = (
    "codex-roadmap-live-status.service",
    "codex-roadmap-live-status.timer",
    "codex-roadmap-sync.service",
    "codex-roadmap-sync.timer",
)


class InstallError(RuntimeError):
    pass


def _run(*args: str) -> None:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode:
        raise InstallError(f"{' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()}")


def install(repo: Path, user_unit_dir: Path) -> dict[str, object]:
    repo = repo.expanduser().resolve()
    source_dir = repo / "systemd"
    user_unit_dir = user_unit_dir.expanduser()
    user_unit_dir.mkdir(parents=True, exist_ok=True)

    installed: list[str] = []
    for name in UNIT_NAMES:
        source = source_dir / name
        if not source.is_file():
            raise InstallError(f"unit_missing:{source}")
        target = user_unit_dir / name
        shutil.copy2(source, target)
        installed.append(str(target))

    _run("systemctl", "--user", "daemon-reload")
    _run("systemctl", "--user", "enable", "--now", "codex-roadmap-live-status.timer")
    _run("systemctl", "--user", "enable", "--now", "codex-roadmap-sync.timer")
    _run("systemctl", "--user", "restart", "codex-roadmap-live-status.timer", "codex-roadmap-sync.timer")
    return {"status": "ok", "installed": installed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install/refresh the roadmap live-status and terminal-sync user timers.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--user-unit-dir", default=str(Path.home() / ".config" / "systemd" / "user"))
    args = parser.parse_args(argv)
    try:
        result = install(Path(args.repo), Path(args.user_unit_dir))
    except (OSError, InstallError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
