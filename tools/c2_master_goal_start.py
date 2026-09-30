#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".local/lib/c2-master-watchdog"))
from c2_appserver_rpc import AppServerRPC, resolve_model

THREAD = "01a0e719-60ff-7b91-82db-1d7c55787c67"
RUNTIME_WORKTREE = Path.home() / ".local/share/c2-supervisor/worktree"
MODEL = "GPT-6 Luna"
REASONING = "medium"
OBJECTIVE = (
    "C2 MASTER GOAL: maximize useful control-plane throughput with independent Inbox, "
    "planning, execution and integration lanes. Never duplicate a live canonical triage "
    "worker and never make unrelated work wait for Inbox=0 or a full rescan of unchanged "
    "WAITING/BLOCKED items; backfill completed slots promptly under canonical "
    "dependencies, leases, fencing and repository-writer protections. Treat C3/Symphony "
    "migration as P0 and avoid extending legacy C2 Codex orchestration scheduled for "
    "replacement. Full durable contract: "
    "/home/daniele/.local/share/c2-master-goal/objective.txt"
)
PID = Path("/home/daniele/.local/state/c2-master-goal/rpc-worker.pid")


def activate_goal(rpc: AppServerRPC) -> str:
    rpc("thread/goal/set", {
        "threadId": THREAD, "objective": OBJECTIVE, "status": "active"
    })
    goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
    if goal.get("objective") != OBJECTIVE or goal.get("status") != "active":
        raise RuntimeError("master_goal_activation_readback_mismatch")
    return "active"


def rehydrate_thread(rpc: AppServerRPC) -> str:
    """Load the existing Master thread into this one owner without starting a turn."""
    observed = rpc("thread/read", {"threadId": THREAD, "includeTurns": True}).get("thread") or {}
    state = (observed.get("status") or {}).get("type")
    if state != "notLoaded":
        return str(state or "unknown")
    model = resolve_model(rpc, MODEL, REASONING)
    response = rpc("thread/resume", {
        "threadId": THREAD,
        "model": model,
        "cwd": str(RUNTIME_WORKTREE),
        "config": {"model_reasoning_effort": REASONING},
        "approvalPolicy": "on-request",
        "approvalsReviewer": "auto_review",
        "sandbox": "workspace-write",
    })
    thread = response.get("thread") or {}
    if thread.get("id") != THREAD:
        raise RuntimeError("master_goal_resume_readback_mismatch")
    return "resumed"


def own_active_goal(rpc: AppServerRPC, *, poll_seconds: float = 10.0) -> str:
    """Keep the single app-server owner alive while the native Goal is active."""
    rehydrate_thread(rpc)
    activate_goal(rpc)
    while True:
        goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
        status = str(goal.get("status") or "unknown")
        if status != "active":
            return status
        thread = rpc("thread/read", {"threadId": THREAD, "includeTurns": True}).get("thread") or {}
        if (thread.get("status") or {}).get("type") == "notLoaded":
            raise RuntimeError("master_goal_owner_lost_thread")
        time.sleep(poll_seconds)


def main() -> int:
    from c3_retirement import require_not_retired
    require_not_retired()
    PID.parent.mkdir(parents=True, exist_ok=True)
    PID.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    try:
        with AppServerRPC(timeout=30) as rpc:
            status = own_active_goal(rpc)
            print("MASTER_GOAL_STATUS", status, flush=True)
            return 0
    finally:
        PID.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
