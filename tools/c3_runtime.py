#!/usr/bin/env python3
"""Fenced C3 scheduler for Symphony and non-Codex roadmap lanes."""
from __future__ import annotations

import argparse
from contextlib import closing
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import c2_runtime as core
from c2_supervisor_lease import (DEFAULT_DB, acquire, connect, publish_runtime_identity,
                                 snapshot, update)
from c3_retirement import MARKER

LOCK = Path.home() / ".local/state/c3-control/runtime.lock"
from c3_storage import local_enabled, database
SNAPSHOT = database()


class C3RuntimeError(RuntimeError):
    pass


def authority(db):
    """Transfer the sole local fence after retirement, retaining its token."""
    if not MARKER.is_file():
        raise C3RuntimeError("retirement_marker_required")
    row = snapshot(db)
    now = time.time()
    if row and row["state"] == "active" and row["lease_expires_at"] > now:
        if row["lease_owner"] != "c3-runtime":
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE supervisor SET lease_owner='c3-runtime' WHERE singleton=1 AND fencing_token=?",
                       (row["fencing_token"],))
            db.commit()
        row = update(db, supervisor_id=row["supervisor_id"],
                     token=row["fencing_token"], action="c3-runtime", ttl=300)
    else:
        row = acquire(db, owner="c3-runtime", pointer="c3-control",
                      minimum_token=int(row["fencing_token"]) if row else 0, ttl=300)
    publish_runtime_identity(row)
    return row


def _launch(run_id: str, db_path: Path) -> None:
    unit = "c3-run-" + run_id
    result = subprocess.run(["systemd-run", "--user", "--collect", "--unit=" + unit,
                             sys.executable, str(Path(__file__).with_name("c3_worker.py")),
                             "--run-id", run_id, "--db", str(db_path)],
                            capture_output=True, text=True, env=core._user_systemd_environment())
    if result.returncode and not _worker_active(run_id):
        raise C3RuntimeError("c3_worker_launch_failed")


def _worker_active(run_id: str) -> bool:
    result = subprocess.run(["systemctl", "--user", "is-active", "--quiet",
                             "c3-run-" + run_id], capture_output=True,
                            env=core._user_systemd_environment())
    return result.returncode == 0


def _notify(event_key: str) -> None:
    unit = "c3-notify-" + hashlib.sha256(event_key.encode()).hexdigest()[:24]
    result = subprocess.run(["systemd-run", "--user", "--collect", "--unit=" + unit,
                             sys.executable,
                             str(Path(__file__).with_name("c2_notify_worker.py")),
                             "--event-key", event_key], capture_output=True, text=True,
                            env=core._user_systemd_environment())
    if result.returncode and "already exists" not in result.stderr.lower():
        raise C3RuntimeError("c3_notification_launch_failed")


def run(db_path: Path = SNAPSHOT, *, inbox_only: bool = False) -> dict:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with closing(connect(DEFAULT_DB)) as lease:
            row = authority(lease)
            def guard():
                current = snapshot(lease)
                if (not current or current["supervisor_id"] != row["supervisor_id"]
                        or current["fencing_token"] != row["fencing_token"]
                        or current["state"] != "active"
                        or current["lease_expires_at"] <= time.time()):
                    raise C3RuntimeError("c3_authority_lost")
            def submit(operation, arguments, key):
                guard()
                return core._writer_submit(operation, arguments, key)
            with closing(core._open_snapshot(db_path)) as db:
                route = core._coding_route()
                if route["mode"] != "production":
                    raise C3RuntimeError("production_symphony_configuration_required")
                route["no_legacy_codex"] = True
                guard()
                result = core.advance(db, submit=submit, launch=lambda run_id: _launch(run_id, db_path),
                                    launch_notify=_notify, worker_active=_worker_active,
                                    repo_task_status=core._repo_task_status,
                                    supervisor_authority={"supervisor_id": row["supervisor_id"],
                                                          "fencing_token": row["fencing_token"],
                                                          "lease_expires_at": row["lease_expires_at"]},
                                    worker_prefix="c3-run:", coding_route_override=route,
                                    control_only=inbox_only)
                if any(event[0] in ("claim_supervisor", "supervisor_fenced")
                       for event in result.get("events", [])):
                    return result
                pending = [r[0] for r in db.execute(
                    "SELECT issue_id FROM issue_inbox WHERE state='pending' ORDER BY observed_at_ms,issue_id LIMIT 25")]
                if inbox_only:
                    return {"inbox_pending": len(pending), "triage_requested": bool(pending)}
                result["inbox_pending"] = len(pending)
                return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=SNAPSHOT)
    parser.add_argument("--inbox-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.db, inbox_only=args.inbox_only), sort_keys=True))
    if local_enabled():
        # Delivery is asynchronous and never a prerequisite for local work.
        subprocess.run(['systemctl', '--user', 'start', '--no-block', 'c3-remote-ingress.service'],
                       capture_output=True, env=core._user_systemd_environment())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
