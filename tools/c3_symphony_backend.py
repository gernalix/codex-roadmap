#!/usr/bin/env python3
"""Host-only Symphony backend entry point and cross-surface status/stop adapter."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


UNIT = "c3-symphony.service"
PORT = "18765"
STATE_URL = f"http://127.0.0.1:{PORT}/api/v1/state"


class BackendError(RuntimeError):
    pass


def credential_environment(environ: dict[str, str]) -> dict[str, str]:
    directory = environ.get("CREDENTIALS_DIRECTORY")
    if not directory:
        raise BackendError("systemd_credentials_directory_missing")
    credential = Path(directory) / "GITHUB_TOKEN"
    if not credential.is_file():
        raise BackendError("github_credential_missing")
    token = credential.read_text(encoding="utf-8").strip()
    if not token or "\n" in token or "\r" in token:
        raise BackendError("github_credential_invalid")
    return {**environ, "GITHUB_TOKEN": token}


def run(binary: Path, workflow: Path, *, environ: dict[str, str] | None = None) -> None:
    if not binary.is_file() or not workflow.is_file():
        raise BackendError("symphony_binary_or_workflow_missing")
    env = credential_environment(dict(os.environ if environ is None else environ))
    os.execve(str(binary), [str(binary),
                            "--i-understand-that-this-will-be-running-without-the-usual-guardrails",
                            str(workflow), "--port", PORT], env)


def publish(db: Path, work_item_id: str, *, environ: dict[str, str] | None = None) -> None:
    env = credential_environment(dict(os.environ if environ is None else environ))
    bridge = Path(__file__).with_name("c3_symphony_bridge.py")
    os.execve(sys.executable, [sys.executable, str(bridge), "publish",
                             "--db", str(db), "--work-item-id", work_item_id], env)


def systemctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["systemctl", "--user", *args, UNIT],
                          text=True, capture_output=True, check=False)


def status() -> dict:
    result = systemctl("show", "--property=ActiveState", "--value")
    if result.returncode:
        raise BackendError("systemd_status_failed")
    active = result.stdout.strip()
    if active != "active":
        return {"backend": "symphony", "active_state": active, "api_healthy": False}
    try:
        with urllib.request.urlopen(STATE_URL, timeout=3) as response:
            data = json.load(response)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise BackendError("symphony_state_api_unavailable") from exc
    if not isinstance(data, dict):
        raise BackendError("symphony_state_api_invalid")
    counts = data.get("counts", {})
    if not isinstance(counts, dict):
        raise BackendError("symphony_state_api_invalid")
    return {"backend": "symphony", "active_state": active, "api_healthy": True,
            "counts": {key: counts[key] for key in ("running", "retrying", "blocked")
                       if isinstance(counts.get(key), int)}}


def stop() -> dict:
    result = systemctl("stop")
    if result.returncode:
        raise BackendError("systemd_stop_failed")
    return {"backend": "symphony", "stop_requested": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "publish", "status", "stop"])
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--work-item-id")
    args = parser.parse_args()
    try:
        if args.action == "run":
            if args.binary is None or args.workflow is None:
                raise BackendError("binary_and_workflow_required")
            run(args.binary, args.workflow)
            raise AssertionError("execve returned")
        if args.action == "publish":
            if args.db is None or args.work_item_id is None:
                raise BackendError("db_and_work_item_required")
            publish(args.db, args.work_item_id)
            raise AssertionError("execve returned")
        result = status() if args.action == "status" else stop()
    except BackendError as exc:
        parser.exit(2, f"c3_symphony_backend: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
