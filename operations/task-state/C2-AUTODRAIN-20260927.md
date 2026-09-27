TASK_ID=C2-AUTODRAIN-20260927

# Objective
Keep C2 draining autonomously through the canonical fenced control plane until quiescence, with Codex as executor and ChatGPT as supervisor only when intervention is needed.

# Constraints
- C2/Git remain canonical; no model-driven polling.
- Preserve one supervisor authority and existing work/run identities.
- Runtime worktree is disposable runtime state only; development uses isolated worktrees.
- Do not duplicate schedulers or Codex turns.
- Report progress as completed X/Y currently runnable; denominator may change as dependencies unblock or new work is captured.

# Checklist
- [x] Inspect current canonical backlog, active runs, units and supervisor authority.
- [x] Capture expired supervisor/runtime failure to C2 Inbox.
- [x] Acquire local supervisor lease token 15 and claim matching canonical authority.
- [x] Register this non-prompt work item and executor_started.
- [x] Realign runtime worktree to canonical main and pass guard.
- [x] Update runtime supervisor env; keep timer/watchdog enabled and path disabled pending #1725.
- [x] Recover expired runs without duplicate turns.
- [x] Integrate failed-Codex-turn terminalization and reconcile stuck run 812553.
- [x] Verify real schedule/ack/launch cycle for runnable Codex work.
- [ ] Leave event-driven drain running independently of this chat.
- [ ] Verify quiescence definition: no runnable/schedulable work and no recoverable run ignored.

# Current step
Canonicalize successor fencing token 17, then supervise the already-existing Codex leaf 999198 through its pending commit approval, integration and terminal C2 receipt without creating another thread or worktree.

# Verified facts
- Work item: wi:0b820bf53cfa46ebaef48dd50ed8f4fc; executor_started applied via Issue #1709.
- Token 16 expired during recovery. Successor local lease is supervisor 8f69f68e-2c6e-4f3b-86a1-87a0a671e568 with fencing token 17; canonical claim mutation #1918 is queued and must be observed applied before new scheduling.
- c2-runtime.timer and watchdog are active; c2-runtime.path is temporarily disabled after detecting a self-trigger/retry loop (Inbox #1725).
- Runtime worktree was safely realigned to main and guard is healthy.
- Runtime worktree branch c2/supervisor-runtime tracks main and has been fast-forwarded to current local main; c2_worktree_guard reports healthy.
- 812553 is terminal failed. C2 Inbox triage completed on attempt 2 (run 67ce771f0377431788c45fd5824b7bf8) via executor PASS #1907; execution override was cleared by #1909. PersonalHub had no running C2 work item, and Pixel/TCL/emulator were left untouched.
- Codex leaf 999198 was auto-configured (#1905), started (#1906/#1910) and registered executor_started (#1908) on existing thread 01a0e1cc-1b21-7521-9a32-8982e78dade8. Its worktree checkpoint records 72 pertinent tests PASS. The existing c2rpc app-server PID 786634 owns the thread; a second writer correctly failed with active-writer protection. The live turn is waitingOnApproval only for `git commit`, so do not relaunch it.
- Current runnable view exposed 20 immediately relevant work items before reactivation; denominator is dynamic.
- Finalizer fix is on current main: no-task-record fails closed.

# Completed
Supervisor recovery through token 16, runtime realignment/guard verification, expired-run recovery, Inbox drain to zero and triage terminal PASS #1907, override cleanup #1909, real Codex schedule/start/executor acknowledgement for 999198, and incident captures #1706/#1710/#1725/#1727/#1869/#1875. Synthetic FAIL/CANCELLED terminalization for Codex turns that end without C2_RESULT is integrated on main; 812553 is terminal failed. The mistaken resume-bug observation #1913 was corrected after identifying the legitimate active writer; discard #1916 is queued.

# Remaining
Observe canonical claim #1918 for token 17, finish the already-running 999198 leaf through commit/integration/terminal receipt, reconcile the corrected false-positive Inbox observation #1916, then continue priority drain. Fix #1725 before re-enabling path-triggered wakeups; timer remains active meanwhile.

# Blockers
No blocker to timer-driven drain. c2-runtime.path remains disabled pending #1725. 999198 is intentionally paused at an app-server command approval for its tested `git commit`; approval must be sent through the existing c2rpc owner after token 17 is canonical. Manual RDC invocation of c2_runtime lacks the user DBus environment for systemd-run (#1869).

# Evidence
Issues #1707/#1708/#1709/#1877/#1883-#1888/#1907/#1909 applied. Commit 708cdd9f is on main and runtime c2_worktree_guard is healthy. New local lease token 17 was acquired atomically and claim #1918 is queued. 999198 checkpoint: focused regression reproduced the FK failure before the fix; 72 pertinent tests PASS after the fix; rollout is owned by c2rpc PID 786634 and reports `waitingOnApproval` for the commit. Duplicate CLI/app-server resume was rejected before any new turn. ADB showed Pixel, TCL and emulator connected and untouched.

# Acceptance criteria
Runtime remains event-driven and fenced; stale runs recover; Codex runnable work is scheduled/launched automatically; no duplicate turns/schedulers; drain survives loss of this chat and stops only at defined quiescence.

# Next action
After canonical claim #1918 applies, use the existing c2rpc owner to approve the pending 999198 commit (do not start a new Codex writer), supervise integration and terminal receipt, then reconcile canonical state and continue the highest-priority eligible non-PersonalHub leaf. Grindr Favorites Monitor may run normally; other Grindr repos remain excluded per goal 660629.
