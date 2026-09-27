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
- [ ] Realign runtime worktree to canonical main and pass guard.
- [ ] Update runtime supervisor env; enable path/timer/watchdog.
- [ ] Recover expired runs without duplicate turns.
- [ ] Verify real schedule/ack/launch cycle for runnable Codex work.
- [ ] Leave event-driven drain running independently of this chat.
- [ ] Verify quiescence definition: no runnable/schedulable work and no recoverable run ignored.

# Current step
Realign the dedicated runtime worktree and reactivate the event-driven runtime.

# Verified facts
- Work item: wi:0b820bf53cfa46ebaef48dd50ed8f4fc; executor_started applied via Issue #1709.
- Local/canonical supervisor: a9fd7222-6cd5-4eef-b205-39126fa09262, fencing token 15.
- c2-runtime.path and c2-runtime.timer are inactive; watchdog timer is active.
- Runtime guard is unhealthy: dirty_worktree + runtime_code_drift.
- Runtime worktree branch c2/supervisor-runtime tracks main, is 66 commits behind, and its only local modification is roadmap.sqlite.
- Two Codex runs are still active in canonical state with expired leases: prompts 812553 and 328371.
- Current runnable view exposed 20 immediately relevant work items before reactivation; denominator is dynamic.
- Finalizer fix is on current main: no-task-record fails closed.

# Completed
Supervisor recovery, canonical authority claim, current task intake/start boundary, and incident captures #1706/#1710.

# Remaining
Runtime realignment/reactivation, expired-run recovery, real scheduling/launch verification, then persistent autonomous drain.

# Blockers
Runtime guard currently prevents service start; no other blocker known.

# Evidence
Issues #1707/#1708/#1709 applied. Guard JSON reports dirty=true, ahead=0, issues=[dirty_worktree,runtime_code_drift]. Runtime worktree status shows only M roadmap.sqlite and branch behind 66.

# Acceptance criteria
Runtime remains event-driven and fenced; stale runs recover; Codex runnable work is scheduled/launched automatically; no duplicate turns/schedulers; drain survives loss of this chat and stops only at defined quiescence.

# Next action
Reset only the dedicated runtime worktree to local main, verify guard healthy, then update runtime.env and start c2-runtime.path/timer.
