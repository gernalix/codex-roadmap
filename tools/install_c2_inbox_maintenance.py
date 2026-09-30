#!/usr/bin/env python3
"""Install the independent bounded C2 Inbox maintenance timer."""
from pathlib import Path
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TARGET = Path.home() / ".config/systemd/user"

def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in ("c2-inbox-maintenance.service", "c2-inbox-maintenance.timer"):
        shutil.copyfile(ROOT / "systemd" / name, TARGET / name)
    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True, env=env)
    subprocess.run(["systemctl", "--user", "enable", "--now", "c2-inbox-maintenance.timer"],
                   check=True, env=env)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
