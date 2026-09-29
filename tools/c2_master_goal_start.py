#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c2_appserver_rpc import AppServerRPC
from c2_codex_sandbox import workspace_write_policy

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


def pause_if_active(rpc: AppServerRPC) -> str:
    goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
    status = str(goal.get("status") or "")
    if status == "active":
        rpc("thread/goal/set", {"threadId": THREAD, "status": "paused"})
        status = "paused"
    return status


def main() -> int:
    PID.parent.mkdir(parents=True, exist_ok=True)
    PID.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    try:
        with AppServerRPC(timeout=30) as rpc:
            try:
                pause_if_active(rpc)
                rpc("thread/resume", {
                    "threadId": THREAD,
                    "model": "gpt-6-sol",
                    "cwd": CWD,
                    "config": {"model_reasoning_effort": "medium"},
                    "approvalPolicy": "on-request",
                    "approvalsReviewer": "auto_review",
                    "sandbox": "workspace-write",
                })
                current = rpc(
                    "thread/read", {"threadId": THREAD, "includeTurns": True}
                ).get("thread", {})
                turns = current.get("turns") or []
                if turns and turns[-1].get("status") in ("inProgress", "running"):
                    turn = turns[-1].get("id")
                    print("MASTER_TURN_ATTACHED", turn, flush=True)
                    terminal = rpc.wait_for_turn(THREAD, turn, idle_check=20)
                    print("MASTER_TURN_TERMINAL", terminal.get("status"), turn, flush=True)
                    return 0

                rpc("thread/goal/set", {
                    "threadId": THREAD, "objective": OBJECTIVE, "status": "paused"
                })
                goal = rpc("thread/goal/get", {"threadId": THREAD}).get("goal") or {}
                if goal.get("objective") != OBJECTIVE or goal.get("status") != "paused":
                    raise RuntimeError("master_goal_readback_mismatch")

                prompt = (
                    "Adopt the C2 MASTER GOAL objective now. It supersedes every earlier narrower "
                    "ordering rule and stop condition in this thread. Start at step 1 using current "
                    "canonical C2 state: Inbox first, then EVERY WAITING, then EVERY BLOCKED; only "
                    "after those three phases form semantic batches; reconcile the chosen batch "
                    "completely; execute exactly one batch; post-reconcile; loop to Inbox. Do not "
                    "declare completion merely because this thread is blocked/complete or no execution "
                    "spec is currently runnable. Continue autonomously under the Master Goal contract."
                )
                result = rpc("turn/start", {
                    "threadId": THREAD,
                    "input": [{"type": "text", "text": prompt, "text_elements": []}],
                    "model": "gpt-6-sol",
                    "effort": "medium",
                    "cwd": CWD,
                    "approvalPolicy": "on-request",
                    "approvalsReviewer": "auto_review",
                    "sandboxPolicy": workspace_write_policy(CWD),
                    "clientUserMessageId": "c2-master-goal-20260929-v2",
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
                status = pause_if_active(rpc)
                print("MASTER_GOAL_POST_TURN_STATUS", status, flush=True)
    finally:
        PID.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
