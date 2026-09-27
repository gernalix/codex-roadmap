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
- [ ] Verify real schedule/ack/launch cycle for runnable Codex work.
- [ ] Leave event-driven drain running independently of this chat.
- [ ] Verify quiescence definition: no runnable/schedulable work and no recoverable run ignored.

# Current step
Run one fenced runtime cycle from the realigned runtime worktree, then verify canonical scheduling/ack/launch behavior without duplicates.

# Verified facts
- Work item: wi:0b820bf53cfa46ebaef48dd50ed8f4fc; executor_started applied via Issue #1709.
- Recovered local/canonical supervisor: 331e7765-49d7-417d-9ebc-c61f448a4282, fencing token 16; token 15 is expired.
- c2-runtime.timer and watchdog are active; c2-runtime.path is temporarily disabled after detecting a self-trigger/retry loop (Inbox #1725).
- Runtime worktree was safely realigned to main and guard is healthy.
- Runtime worktree branch c2/supervisor-runtime tracks main and has been fast-forwarded to current local main; c2_worktree_guard reports healthy.
- 812553 is now terminal: its Codex run and work item are both failed. No C2 systemd worker unit is currently active; PersonalHub has no running C2 work item, and Pixel/TCL/emulator were left untouched.
- Current runnable view exposed 20 immediately relevant work items before reactivation; denominator is dynamic.
- Finalizer fix is on current main: no-task-record fails closed.

# Completed
Supervisor recovery through fencing token 16, canonical authority claim, runtime realignment/guard verification, expired-run recovery, and incident captures #1706/#1710/#1725/#1727. Synthetic FAIL/CANCELLED terminalization for Codex turns that end without C2_RESULT is integrated on main; focused worker suite 15/15 PASS; 812553 is terminal failed.

# Remaining
Verify one real fenced runtime cycle, continued scheduling/ack/launch, and persistent autonomous drain. Fix #1725 before re-enabling path-triggered wakeups; timer remains active meanwhile.

# Blockers
No blocker to timer-driven drain. c2-runtime.path remains disabled to prevent a self-trigger retry loop pending #1725.

# Evidence
Issues #1707/#1708/#1709 applied. Commit 708cdd9f (failed-turn terminalization) is an ancestor of origin/main. Canonical supervisor authority is token 16 for 331e7765-49d7-417d-9ebc-c61f448a4282. Runtime c2_worktree_guard reports healthy. ADB showed Pixel, TCL and emulator connected and untouched.

# Acceptance criteria
Runtime remains event-driven and fenced; stale runs recover; Codex runnable work is scheduled/launched automatically; no duplicate turns/schedulers; drain survives loss of this chat and stops only at defined quiescence.

# Next action
Launch one fenced c2-runtime cycle with supervisor token 16, pull the resulting canonical snapshot once, and verify schedule/ack/launch plus absence of duplicate/recovering 812553.
