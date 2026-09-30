#!/usr/bin/env python3
"""Host-only Symphony backend entry point and cross-surface status/stop adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from c3_symphony_bridge import DEFAULT_CONFIG, load_config, BridgeError


UNIT = "c3-symphony.service"
PORT = "18765"
STATE_URL = f"http://127.0.0.1:{PORT}/api/v1/state"
PRODUCTION_BINARY = Path.home()/".local/share/c3-symphony/bin/symphony"
PRODUCTION_SHA256 = "25cdc28aaa8009ab1c3ef842b0925baa70923869000a557f8edafabc822b9c2b"


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
    config = load_config(Path((environ or os.environ).get("C3_SYMPHONY_CONFIG", DEFAULT_CONFIG)))
    if config.mode == "legacy":
        raise BackendError("symphony_disabled_in_legacy_mode")
    if config.mode == "production":
        verify_artifact(binary)
    if not binary.is_file() or not workflow.is_file():
        raise BackendError("symphony_binary_or_workflow_missing")
    try:
        document = workflow.read_text(encoding="utf-8")
        settings = json.loads(document.split("---", 2)[1])
        tracker = settings["tracker"]["provider"]["repo"]
        host = settings.get("server", {}).get("host", "127.0.0.1")
    except (ValueError, IndexError, KeyError, TypeError) as exc:
        raise BackendError("workflow_config_invalid") from exc
    if tracker != config.tracker_repo or host != "127.0.0.1":
        raise BackendError("workflow_tracker_or_listener_mismatch")
    env = credential_environment(dict(os.environ if environ is None else environ))
    os.execve(str(binary), [str(binary),
                            "--i-understand-that-this-will-be-running-without-the-usual-guardrails",
                            str(workflow), "--port", PORT], env)


def verify_artifact(binary: Path) -> None:
    if binary.resolve() != PRODUCTION_BINARY.resolve() or not binary.is_file():
        raise BackendError("production_artifact_path_invalid")
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    if digest != PRODUCTION_SHA256:
        raise BackendError("production_artifact_hash_mismatch")


def publish(db: Path, work_item_id: str, *, run_id: str | None = None,
            action: str = "publish", environ: dict[str, str] | None = None) -> None:
    if action not in {"publish", "inspect"}:
        raise BackendError("bridge_action_invalid")
    env = credential_environment(dict(os.environ if environ is None else environ))
    bridge = Path(__file__).with_name("c3_symphony_bridge.py")
    argv = [sys.executable, str(bridge), action,
            "--db", str(db), "--work-item-id", work_item_id]
    if run_id:
        argv += ["--run-id", run_id]
    os.execve(sys.executable, argv, env)


def user_bus_environment(environ: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if environ is None else environ)
    runtime = Path(env.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}")
    if not runtime.is_dir():
        raise BackendError("user_runtime_directory_missing")
    env["XDG_RUNTIME_DIR"] = str(runtime)
    bus = runtime/"bus"
    if not bus.is_socket():
        raise BackendError("user_bus_socket_missing")
    env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus}"
    return env


def systemctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["systemctl", "--user", *args, UNIT],
                          text=True, capture_output=True, check=False,
                          env=user_bus_environment())


def status() -> dict:
    config = load_config(Path(os.environ.get("C3_SYMPHONY_CONFIG", DEFAULT_CONFIG)))
    if config.mode == "production":
        verify_artifact(PRODUCTION_BINARY)
    result = systemctl("show", "--property=ActiveState", "--value")
    if result.returncode:
        raise BackendError("systemd_status_failed")
    active = result.stdout.strip()
    if active != "active":
        return {"backend": "symphony", "mode": config.mode,
                "active_state": active, "api_healthy": False}
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
    return {"backend": "symphony", "mode": config.mode,
            "active_state": active, "api_healthy": True,
            "counts": {key: counts[key] for key in ("running", "retrying", "blocked")
                       if isinstance(counts.get(key), int)}}


def stop() -> dict:
    result = systemctl("stop")
    if result.returncode:
        raise BackendError("systemd_stop_failed")
    return {"backend": "symphony", "stop_requested": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "publish", "inspect", "status", "stop"])
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--work-item-id")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    try:
        if args.action == "run":
            if args.binary is None or args.workflow is None:
                raise BackendError("binary_and_workflow_required")
            run(args.binary, args.workflow)
            raise AssertionError("execve returned")
        if args.action in {"publish", "inspect"}:
            if args.db is None or args.work_item_id is None:
                raise BackendError("db_and_work_item_required")
            publish(args.db, args.work_item_id, run_id=args.run_id, action=args.action)
            raise AssertionError("execve returned")
        result = status() if args.action == "status" else stop()
    except (BackendError, BridgeError) as exc:
        parser.exit(2, f"c3_symphony_backend: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
