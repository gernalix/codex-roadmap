#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
LIB = HOME / ".local/lib/c2-master-watchdog"
BIN = HOME / ".local/bin"
USER_SYSTEMD = HOME / ".config/systemd/user"

FILES = {
    ROOT / "tools/c2_master_watchdog.py": LIB / "c2_master_watchdog.py",
    ROOT / "tools/c2_master_goal_start.py": BIN / "c2-master-goal-start",
    ROOT / "tools/c2_master_watcher_view.py": BIN / "c2-master-watcher-view",
    ROOT / "tools/c2_master_executor_view.py": BIN / "c2-master-executor-view",
    ROOT / "tools/c2_roadmap_status.py": BIN / "c2-roadmap-status",
    ROOT / "systemd/c2-master-goal.service": USER_SYSTEMD / "c2-master-goal.service",
    ROOT / "systemd/c2-master-watcher.service": USER_SYSTEMD / "c2-master-watcher.service",
    ROOT / "systemd/c2-master-watcher.timer": USER_SYSTEMD / "c2-master-watcher.timer",
}


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def main() -> int:
    LIB.mkdir(parents=True, exist_ok=True)
    BIN.mkdir(parents=True, exist_ok=True)
    USER_SYSTEMD.mkdir(parents=True, exist_ok=True)
    for src, dst in FILES.items():
        shutil.copy2(src, dst)
    for path in (LIB / "c2_master_watchdog.py", BIN / "c2-master-goal-start", BIN / "c2-master-watcher-view", BIN / "c2-master-executor-view", BIN / "c2-roadmap-status"):
        path.chmod(path.stat().st_mode | 0o111)
    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True, env=env)
    subprocess.run(["systemctl", "--user", "enable", "--now", "c2-master-watcher.timer"], check=True, env=env)
    subprocess.run(["systemctl", "--user", "start", "c2-master-watcher.service"], check=True, env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
