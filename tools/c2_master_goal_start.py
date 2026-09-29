#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/daniele/projects/codex-roadmap/tools")
from c2_appserver_rpc import AppServerRPC
from c2_codex_sandbox import workspace_write_policy

sys.path.insert(0, "/home/daniele/.local/lib/c2-master-watchdog")
import c2_master_watchdog as master_watchdog

THREAD = "01a0e719-60ff-7b91-82db-1d7c55787c67"
CWD = "/home/daniele/.local/share/c2-supervisor/worktrees/roadmap-batch-reconciliation-20260928"
OBJECTIVE = (
    "C2 MASTER GOAL: operate the entire C2 autonomously. Before EVERY batching pass: "
    "drain Inbox, then reevaluate ALL WAITING, then reevaluate ALL BLOCKED. Only then "
    "form semantic batches; reconcile one selected batch completely; execute exactly "
    "one batch; post-reconcile; loop to Inbox. Stop only at global quiescence. Full "
    "durable contract: /home/daniele/.local/share/c2-master-goal/objective.txt"
)
PID = Path("/home/daniele/.local/state/c2-master-goal/rpc-worker.pid")


def wake_event() -> dict:
    state = master_watchdog.read_json(master_watchdog.STATE, {})
    db = master_watchdog.db_snapshot()
    runs = [{
        "run_id": row.get("run_id"),
        "work_item_id": row.get("work_item_id"),
        "state": row.get("state"),
        "lease_expired": bool(row.get("lease_expired")),
    } for row in (db.get("active_runs") or [])[:8]]
    authority = db.get("authority") or {}
    counts = db.get("counts") or {}
    return {
        "watchdog_state_key": state.get("state_key"),
        "watchdog_status": state.get("status"),
        "inbox_pending": db.get("inbox_pending"),
        "counts": {key: counts.get(key, 0) for key in ("pending", "waiting", "blocked", "running")},
        "runnable_count": len(db.get("runnable_ids") or []),
        "authority_lease_valid": authority.get("lease_valid"),
        "active_runs": runs,
    }


def build_prompt(event: dict) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return (
        "Adopt the C2 MASTER GOAL objective now. A deterministic watchdog woke this thread "
        "because the local control-plane fingerprint changed or a bounded recovery is required. "
        "You MUST perform one fresh read of canonical C2 state before deciding; do not rely on "
        "the last verified state from an earlier turn. The wake payload is a trigger, not authority: "
        f"DETERMINISTIC_WAKE_EVENT={payload}. "
        "Start at step 1 using the fresh canonical state: Inbox first, then EVERY WAITING, then "
        "EVERY BLOCKED; only after those phases form semantic batches; reconcile the chosen batch "
        "completely; execute exactly one batch; post-reconcile; loop to Inbox. If the fresh state "
        "shows the prior external/fence condition is unchanged, persist that fact and stop; the "
        "watchdog will not wake this thread again until the deterministic fingerprint changes."
    )


def client_message_id(event: dict) -> str:
    state_key = str(event.get("watchdog_state_key") or "unknown")
    return "c2-master-goal-watchdog-" + state_key[:24]


def main() -> int:
    PID.parent.mkdir(parents=True, exist_ok=True)
    PID.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    try:
        with AppServerRPC(timeout=30) as rpc:
            goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
            if goal.get("status") != "paused":
                rpc("thread/goal/set", {"threadId": THREAD, "status": "paused"})

            rpc("thread/resume", {
                "threadId": THREAD,
                "model": "gpt-6-sol",
                "cwd": CWD,
                "config": {"model_reasoning_effort": "medium"},
                "approvalPolicy": "on-request",
                "approvalsReviewer": "auto_review",
                "sandbox": "workspace-write",
            })
            current = rpc("thread/read", {"threadId": THREAD, "includeTurns": True}).get("thread", {})
            turns = current.get("turns") or []
            if turns and turns[-1].get("status") in ("inProgress", "running"):
                turn = turns[-1].get("id")
                print("MASTER_TURN_ATTACHED", turn, flush=True)
                terminal = rpc.wait_for_turn(THREAD, turn, idle_check=20)
                print("MASTER_TURN_TERMINAL", terminal.get("status"), turn, flush=True)
                return 0

            rpc("thread/goal/set", {"threadId": THREAD, "objective": OBJECTIVE, "status": "paused"})
            goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
            if goal.get("objective") != OBJECTIVE or goal.get("status") != "paused":
                raise RuntimeError("master_goal_readback_mismatch")

            event = wake_event()
            prompt = build_prompt(event)
            result = rpc("turn/start", {
                "threadId": THREAD,
                "input": [{"type": "text", "text": prompt, "text_elements": []}],
                "model": "gpt-6-sol",
                "effort": "medium",
                "cwd": CWD,
                "approvalPolicy": "on-request",
                "approvalsReviewer": "auto_review",
                "sandboxPolicy": workspace_write_policy(CWD),
                "clientUserMessageId": client_message_id(event),
            })
            turn = result["turn"]["id"]
            rpc("thread/goal/set", {"threadId": THREAD, "status": "active"})
            goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
            if goal.get("status") != "active":
                raise RuntimeError("master_goal_activation_failed")
            print("MASTER_TURN_STARTED", turn, flush=True)
            terminal = rpc.wait_for_turn(THREAD, turn, idle_check=20)
            print("MASTER_TURN_TERMINAL", terminal.get("status"), turn, flush=True)
            return 0
    finally:
        PID.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
