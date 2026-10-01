#!/usr/bin/env python3
"""One-way host command to retire legacy C2 orchestration after C3 preflight."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile

STATE_DIR = Path.home() / ".local/state/c3-control"
MARKER = STATE_DIR / "c2-retired.json"
AUDIT = STATE_DIR / "c2-retirement-audit.json"
USER_UNIT_DIR = Path.home() / ".config/systemd/user"
SNAPSHOT = Path.home() / ".local/state/c2-supervisor/roadmap.sqlite3"
LEGACY_UNITS = (
    "c2-master-goal.service", "c2-master-watcher.service", "c2-master-watcher.timer",
    "c2-runtime.service", "c2-runtime.timer", "c2-runtime.path",
    "c2-inbox-maintenance.service", "c2-inbox-maintenance.timer",
    "c2-supervisor-watchdog.service", "c2-supervisor-watchdog.timer",
    "c2-supervisor-recovery.service", "c2-supervisor-recovery.timer",
    "codex-roadmap-live-status.service", "codex-roadmap-live-status.timer",
    "codex-roadmap-sync.service", "codex-roadmap-sync.timer",
)
C3_REQUIRED = (
    "c3-symphony.service", "c3-roadmap-snapshot.service", "c3-roadmap-snapshot.timer",
    "c3-runtime.service", "c3-runtime.timer", "c3-runtime.path",
    "c3-inbox-maintenance.service", "c3-inbox-maintenance.timer",
)
C3_ACTIVATE = ("c3-roadmap-snapshot.timer", "c3-runtime.timer",
               "c3-runtime.path", "c3-inbox-maintenance.timer")


class RetirementError(RuntimeError):
    pass


def require_not_retired(marker: Path = MARKER) -> None:
    if marker.exists():
        raise RetirementError(f"c2_retired:{marker}")


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                 prefix=".c3-", delete=False) as stream:
        staged = Path(stream.name)
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        staged.chmod(0o600)
        os.replace(staged, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        staged.unlink(missing_ok=True)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["systemctl", "--user", *args], text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise RetirementError("systemctl_failed:" + ":".join(args))
    return result


def _property(unit: str, name: str) -> str:
    return _run("show", unit, "--property=" + name, "--value").stdout.strip()


def _active_runs(snapshot: Path, allow_run_id: str | None = None) -> int:
    """Count blocking runs, optionally permitting exactly the live C3 cutover run.

    The exception is deliberately narrow: one Symphony run, owning a running
    work item tagged c3:cutover, with a production ownership record matching
    both canonical identities. Any additional or mismatched run still blocks.
    """
    if not snapshot.is_file():
        raise RetirementError("roadmap_snapshot_missing")
    with sqlite3.connect(f"{snapshot.resolve().as_uri()}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""SELECT r.run_id,r.work_item_id,r.executor,r.state,
                   w.status AS item_status,
                   EXISTS(SELECT 1 FROM work_item_tags t
                          WHERE t.work_item_id=r.work_item_id
                            AND t.tag='c3:cutover') AS is_cutover
            FROM work_item_runs r JOIN work_items w USING(work_item_id)
            WHERE r.state IN ('claimed','running','recovering')
            ORDER BY r.run_id""").fetchall()
    if not rows or allow_run_id is None:
        return len(rows)
    if len(rows) != 1:
        return len(rows)
    row = rows[0]
    if (row["run_id"] != allow_run_id or row["executor"] != "symphony"
            or row["item_status"] != "running" or not row["is_cutover"]):
        return len(rows)
    from c3_symphony_route import ownership_path
    try:
        ownership = json.loads(ownership_path(row["work_item_id"]).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise RetirementError("allowed_cutover_ownership_missing_or_invalid") from exc
    expected = {"run_id": row["run_id"], "work_item_id": row["work_item_id"],
                "mode": "production"}
    if any(ownership.get(key) != value for key, value in expected.items()):
        raise RetirementError("allowed_cutover_ownership_mismatch")
    return 0


def _stale_triage(snapshot: Path) -> bool:
    with sqlite3.connect(f"{snapshot.resolve().as_uri()}?mode=ro", uri=True) as db:
        return bool(db.execute("""SELECT 1 FROM work_items w
            JOIN work_item_tags t USING(work_item_id)
            WHERE t.tag='c2:issue-triage' AND w.status='running'
              AND NOT EXISTS (SELECT 1 FROM work_item_runs r
                  WHERE r.work_item_id=w.work_item_id
                    AND r.state IN ('claimed','running','recovering')) LIMIT 1""").fetchone())


def _preflight(snapshot: Path, allow_run_id: str | None = None) -> dict:
    from c2_snapshot_sync import sync
    from c3_symphony_backend import status, verify_artifact, PRODUCTION_BINARY
    from c3_symphony_bridge import DEFAULT_CONFIG, load_config
    from c3_symphony_route import WORKFLOW
    config = load_config(DEFAULT_CONFIG)
    if config.mode != "production" or not config.tracker_repo or not config.source_repos:
        raise RetirementError("c3_production_configuration_required")
    try:
        settings = json.loads(WORKFLOW.read_text(encoding="utf-8").split("---", 2)[1])
        tracker = settings["tracker"]["provider"]["repo"]
        host = settings.get("server", {}).get("host", "127.0.0.1")
    except (OSError, ValueError, IndexError, KeyError, TypeError) as exc:
        raise RetirementError("c3_workflow_invalid") from exc
    if tracker != config.tracker_repo or host != "127.0.0.1":
        raise RetirementError("c3_workflow_tracker_or_listener_mismatch")
    verify_artifact(PRODUCTION_BINARY)
    backend = status()
    if backend.get("active_state") != "active" or backend.get("api_healthy") is not True:
        raise RetirementError("c3_symphony_unhealthy")
    if any(backend.get("counts", {}).get(key, 0) for key in ("running", "retrying")):
        raise RetirementError("c3_symphony_runs_still_active")
    for unit in C3_REQUIRED:
        if _property(unit, "LoadState") != "loaded":
            raise RetirementError("c3_unit_not_installed:" + unit)
    sync(output=snapshot)
    if _active_runs(snapshot, allow_run_id):
        raise RetirementError("active_roadmap_runs_must_finish_before_retirement")
    if _stale_triage(snapshot):
        raise RetirementError("stale_inbox_triage_requires_reconciliation")
    if _property("chatgpt-rdc-supervisor.service", "LoadState") != "loaded":
        raise RetirementError("browser_lane_service_missing")
    return {"artifact_sha256": hashlib.sha256(PRODUCTION_BINARY.read_bytes()).hexdigest(),
            "tracker_repo": config.tracker_repo, "source_repos": sorted(config.source_repos),
            "workflow": str(WORKFLOW), "backend": backend,
            "allowed_cutover_run_id": allow_run_id}


def retire(*, marker: Path = MARKER, audit: Path = AUDIT,
           snapshot: Path = SNAPSHOT, allow_run_id: str | None = None) -> dict:
    from c3_storage import local_enabled
    if local_enabled():
        raise RetirementError('pre_migration_cutover_helper_retired')
    if marker.exists():
        if not audit.is_file():
            raise RetirementError("retirement_audit_missing")
        record = json.loads(marker.read_text(encoding="utf-8"))
        if record.get("units") != list(LEGACY_UNITS):
            raise RetirementError("retirement_marker_invalid")
        for unit in LEGACY_UNITS:
            if _property(unit, "ActiveState") == "active" or _property(unit, "UnitFileState") != "masked":
                raise RetirementError("retired_unit_resurrected:" + unit)
        _run("start", "c3-symphony.service")
        _run("enable", "--now", *C3_ACTIVATE)
        _run("start", "c3-roadmap-snapshot.service", "c3-runtime.service",
             "c3-inbox-maintenance.service")
        return {"status": "already_retired", "marker": str(marker)}
    evidence = _preflight(snapshot, allow_run_id)
    _run("stop", "c3-symphony.service")
    before = {unit: {"active": _property(unit, "ActiveState"),
                     "unit_file": _property(unit, "UnitFileState")}
              for unit in LEGACY_UNITS}
    transient = [line.split()[0] for line in
                 _run("list-units", "--all", "--plain", "--no-legend", "c2-run-*.service").stdout.splitlines()
                 if line.split() and line.split()[0].startswith("c2-run-")]
    if transient and any(_property(unit, "ActiveState") == "active" for unit in transient):
        raise RetirementError("legacy_worker_still_active")
    active = [unit for unit, value in before.items()
              if value["active"] not in ("inactive", "failed", "")]
    enabled = [unit for unit, value in before.items()
               if value["unit_file"] in ("enabled", "enabled-runtime", "linked", "linked-runtime")]
    if active:
        _run("stop", *active)
    if enabled:
        _run("disable", *enabled)
    from c2_snapshot_sync import sync
    sync(output=snapshot)
    if _active_runs(snapshot, allow_run_id):
        raise RetirementError("roadmap_run_started_during_retirement")
    archived: dict[str, str] = {}
    archive_dir = marker.parent / "retired-unit-files"
    for unit in LEGACY_UNITS:
        installed = USER_UNIT_DIR / unit
        if installed.exists() or installed.is_symlink():
            archive_dir.mkdir(parents=True, exist_ok=True)
            backup = archive_dir / unit
            if backup.exists() or backup.is_symlink():
                raise RetirementError("retirement_archive_collision:" + unit)
            shutil.move(installed, backup)
            archived[unit] = ("symlink" if backup.is_symlink() else
                              hashlib.sha256(backup.read_bytes()).hexdigest())
    _run("daemon-reload")
    _run("mask", *LEGACY_UNITS)
    after = {unit: {"active": _property(unit, "ActiveState"),
                    "unit_file": _property(unit, "UnitFileState")}
             for unit in LEGACY_UNITS}
    if any(value["active"] == "active" or value["unit_file"] != "masked"
           for value in after.values()):
        raise RetirementError("legacy_unit_still_active_or_unmasked")
    now = datetime.now(timezone.utc).isoformat()
    manifest = {"schema": "c3.c2-retirement.v1", "at": now,
                "c3_evidence": evidence, "c3_units": list(C3_REQUIRED),
                "before": before, "after": after,
                "archived_unit_files": archived,
                "retained_service": "chatgpt-rdc-supervisor.service",
                "preserved": ["roadmap.sqlite", "issue_inbox provenance",
                              "single writer", "repository integration"]}
    _atomic_json(audit, manifest)
    _run("enable", *C3_ACTIVATE)
    _atomic_json(marker, {"schema": "c3.c2-retired.v1", "at": now,
                          "units": list(LEGACY_UNITS), "audit": str(audit)})
    _run("start", "c3-symphony.service")
    _run("start", *C3_ACTIVATE)
    _run("start", "c3-roadmap-snapshot.service", "c3-runtime.service",
         "c3-inbox-maintenance.service")
    return {"status": "retired", "marker": str(marker), "audit": str(audit)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-run-id", help="permit only this verified live C3 cutover run")
    args = parser.parse_args()
    if not args.execute:
        parser.error("retirement requires --execute")
    try:
        print(json.dumps(retire(allow_run_id=args.allow_run_id), sort_keys=True))
    except (OSError, ValueError, sqlite3.Error, RetirementError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
