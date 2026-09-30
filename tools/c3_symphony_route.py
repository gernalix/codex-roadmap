#!/usr/bin/env python3
"""Fenced C2 run handoff to the one host Symphony tracker and repo writer."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import c3_symphony_backend as backend
from c3_symphony_bridge import (DEFAULT_CONFIG, BridgeError, HostConfig, inspect,
                                 load_config, load_item, workflow_text)
from roadmap_finish import _queue_repo_integration

WORKFLOW = Path.home()/".local/share/c3-symphony/WORKFLOW.md"
CREDENTIAL = Path.home()/".config/c3-symphony/credentials/github-token.cred"
OWNERS = Path.home()/".local/state/c3-symphony/ownership"


class RouteError(RuntimeError):
    pass


def routing_mode(path: Path = DEFAULT_CONFIG) -> HostConfig:
    if not path.exists():
        return HostConfig("legacy", None, frozenset())
    return load_config(path)


def eligible(config: HostConfig, *, activity: str, policy: str, repo: str | None) -> bool:
    return (config.mode in {"canary", "production"} and activity == "coding"
            and policy in {"auto", "codex"} and repo in config.source_repos)


def ownership_path(work_item_id: str) -> Path:
    if not work_item_id.startswith("wi:") or len(work_item_id) != 35:
        raise RouteError("work_item_identity_invalid")
    return OWNERS/(work_item_id[3:]+".json")


def reserve_ownership(work_item_id: str, run_id: str, config: HostConfig) -> None:
    path = ownership_path(work_item_id)
    record = {"work_item_id": work_item_id, "run_id": run_id,
              "tracker_repo": config.tracker_repo, "mode": config.mode}
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(record, handle, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        path.chmod(0o600)
    except FileExistsError:
        try:
            prior = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RouteError("symphony_ownership_invalid") from exc
        if prior != record:
            raise RouteError("symphony_ownership_conflict")


def bridge_call(action: str, db: Path, work_item_id: str, run_id: str) -> dict:
    if action not in {"publish", "inspect"}:
        raise RouteError("bridge_action_invalid")
    command = ["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet",
               "--property=LoadCredentialEncrypted=GITHUB_TOKEN:"+str(CREDENTIAL),
               sys.executable, str(Path(__file__).with_name("c3_symphony_backend.py")), action,
               "--db", str(db), "--work-item-id", work_item_id, "--run-id", run_id]
    result = subprocess.run(command, text=True, capture_output=True, check=False,
                            env=backend.user_bus_environment())
    if result.returncode:
        raise RouteError("symphony_"+action+"_failed")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise RouteError("symphony_bridge_invalid_response") from exc


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise RouteError("workspace_git_failed:" + ":".join(args[:2]))
    return result.stdout.strip()


def import_workspace_commit(item, issue_number: int, workspace_root: Path) -> str:
    if not item.prompt_id or not item.worktree:
        raise RouteError("symphony_integration_identity_missing")
    workspace = workspace_root / ("GH-" + str(issue_number))
    source = workspace / "source"
    base_file = workspace / ".c3-source-base"
    target = Path(item.worktree).resolve()
    if not source.is_dir() or not base_file.is_file() or not target.is_dir():
        raise RouteError("symphony_workspace_import_missing")
    branch = "task/" + item.prompt_id
    if _git("branch", "--show-current", cwd=source) != branch:
        raise RouteError("symphony_workspace_branch_mismatch")
    if _git("branch", "--show-current", cwd=target) != branch:
        raise RouteError("canonical_worktree_branch_mismatch")
    if _git("status", "--porcelain", cwd=source):
        raise RouteError("symphony_workspace_dirty_after_terminal")
    if _git("status", "--porcelain", cwd=target):
        raise RouteError("canonical_worktree_dirty_before_import")
    base = base_file.read_text(encoding="utf-8").strip()
    source_head = _git("rev-parse", "HEAD", cwd=source)
    target_head = _git("rev-parse", "HEAD", cwd=target)
    if not base or target_head != base:
        raise RouteError("canonical_worktree_moved_during_symphony")
    ancestor = subprocess.run(["git", "-C", str(source), "merge-base", "--is-ancestor",
                               base, source_head], check=False)
    if ancestor.returncode:
        raise RouteError("symphony_workspace_not_descended_from_base")
    fetch = subprocess.run(["git", "-C", str(target), "fetch", str(source), source_head],
                           text=True, capture_output=True, check=False)
    if fetch.returncode:
        raise RouteError("symphony_workspace_fetch_failed")
    merge = subprocess.run(["git", "-C", str(target), "merge", "--ff-only", "FETCH_HEAD"],
                           text=True, capture_output=True, check=False)
    if merge.returncode:
        raise RouteError("symphony_workspace_fast_forward_failed")
    if _git("rev-parse", "HEAD", cwd=target) != source_head or _git("status", "--porcelain", cwd=target):
        raise RouteError("symphony_workspace_import_readback_failed")
    return source_head


def validate_terminal(value: object) -> dict:
    if not isinstance(value, dict) or value.get("outcome") != "PASS":
        raise RouteError("symphony_terminal_outcome_invalid")
    completed, remaining, evidence = (value.get(key) for key in
                                       ("completed", "remaining", "evidence"))
    if (not isinstance(completed, list) or not isinstance(remaining, list)
            or remaining or not isinstance(evidence, list) or not evidence
            or value.get("blocker") is not None or value.get("next_action") is not None):
        raise RouteError("symphony_terminal_contract_invalid")
    return {"outcome": "PASS", "completed": completed, "remaining": [],
            "evidence": evidence, "blocker": None, "next_action": None,
            "summary": value.get("summary"), "strict_contract": True}


def dispatch(db: Path, run_id: str, work_item_id: str, config: HostConfig,
             *, submit, workflow: Path = WORKFLOW, bridge=bridge_call) -> dict:
    item = load_item(db, work_item_id, config, run_id)
    state = backend.status()
    if state.get("active_state") != "active" or not state.get("api_healthy"):
        raise RouteError("symphony_backend_unhealthy")
    try:
        document = workflow.read_text(encoding="utf-8")
        settings = json.loads(document.split("---", 2)[1])
        root = Path(settings["workspace"]["root"])
    except (OSError, ValueError, IndexError, KeyError, TypeError) as exc:
        raise RouteError("symphony_workflow_missing_or_invalid") from exc
    if document != workflow_text(item, root, config):
        raise RouteError("symphony_workflow_item_mismatch")
    reserve_ownership(work_item_id, run_id, config)
    published = bridge("publish", db, work_item_id, run_id)
    observed = bridge("inspect", db, work_item_id, run_id)
    if observed.get("issue_number") != published.get("issue_number"):
        raise RouteError("symphony_tracker_identity_changed")
    if observed.get("state") == "open":
        return {"run_id": run_id, "executor": "symphony", "phase": "running",
                "tracker_issue": observed["issue_number"]}
    if observed.get("state") != "closed":
        raise RouteError("symphony_tracker_terminal_readback_failed")
    terminal = validate_terminal(observed.get("terminal"))
    imported_head = import_workspace_commit(item, observed["issue_number"], root)
    terminal["evidence"] = [*terminal["evidence"], "C3 imported committed head " + imported_head]
    args = {"run_id": run_id, "prompt_id": item.prompt_id, **terminal,
            "integration_ready": False}
    submit("executor_result", args, "c3-symphony-result-"+run_id)
    _, integrated = _queue_repo_integration(item.prompt_id, Path(item.worktree))
    if integrated:
        submit("executor_result", {**args, "integration_ready": True},
               "c3-symphony-result-final-"+run_id)
    return {"run_id": run_id, "executor": "symphony", "phase": "queued",
            "tracker_issue": observed["issue_number"]}
