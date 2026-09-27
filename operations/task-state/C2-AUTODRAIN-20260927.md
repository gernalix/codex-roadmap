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
Complete the five queued fenced Inbox dispositions (#1884-#1888), close the recovered triage item when pending reaches zero, then verify the next autonomous schedule/ack/launch cycle without duplicate executors.

# Verified facts
- Work item: wi:0b820bf53cfa46ebaef48dd50ed8f4fc; executor_started applied via Issue #1709.
- Recovered local/canonical supervisor: 331e7765-49d7-417d-9ebc-c61f448a4282, fencing token 16; token 15 is expired.
- c2-runtime.timer and watchdog are active; c2-runtime.path is temporarily disabled after detecting a self-trigger/retry loop (Inbox #1725).
- Runtime worktree was safely realigned to main and guard is healthy.
- Runtime worktree branch c2/supervisor-runtime tracks main and has been fast-forwarded to current local main; c2_worktree_guard reports healthy.
- 812553 is terminal: its Codex run and work item are both failed. A real timer-driven triage run 466e02b76c8a4688b801889a675853bf reached executor_started, then was safely quarantined after browser delivery remained unconfirmed; recovery scan found zero persisted TASK_ID sessions, so no duplicate browser executor exists. PersonalHub had no running C2 work item, and Pixel/TCL/emulator were left untouched.
- Current runnable view exposed 20 immediately relevant work items before reactivation; denominator is dynamic.
- Finalizer fix is on current main: no-task-record fails closed.

# Completed
Supervisor recovery through fencing token 16, canonical authority claim/renewal, runtime realignment/guard verification, expired-run recovery, and incident captures #1706/#1710/#1725/#1727/#1869/#1875. Synthetic FAIL/CANCELLED terminalization for Codex turns that end without C2_RESULT is integrated on main; focused worker suite 15/15 PASS; 812553 is terminal failed. The quarantined triage item was evidence-gated back to pending via applied mutation #1877 after proving no persisted browser session exists.

# Remaining
Wait only for the already-queued writer mutations #1884-#1888 to apply, verify pending Inbox reaches zero, close the recovered triage item, then verify continued autonomous scheduling/launch and persistent drain. Fix #1725 before re-enabling path-triggered wakeups; timer remains active meanwhile.

# Blockers
No blocker to timer-driven drain. c2-runtime.path remains disabled to prevent a self-trigger retry loop pending #1725. Browser semantic launch is currently unreliable: the first recovered triage attempt was quarantined with no persisted session; #1875 records the fragility. Manual RDC invocation of c2_runtime also lacks the user DBus environment for systemd-run; #1869 records that separate fallback fragility.

# Evidence
Issues #1707/#1708/#1709 and reconciliation #1877 applied. Commit 708cdd9f (failed-turn terminalization) is an ancestor of origin/main. Canonical supervisor authority is token 16 for 331e7765-49d7-417d-9ebc-c61f448a4282; renewal #1883 is queued. Runtime c2_worktree_guard reports healthy. Run 466e02b76c8a4688b801889a675853bf recorded one executor_started receipt and then canonical quarantine; recovery scan returned phase=starting, chat_url=null, resubmitted=false. Five pending Inbox observations were semantically mapped and fenced promote_issue mutations #1884-#1888 are queued. ADB showed Pixel, TCL and emulator connected and untouched.

# Acceptance criteria
Runtime remains event-driven and fenced; stale runs recover; Codex runnable work is scheduled/launched automatically; no duplicate turns/schedulers; drain survives loss of this chat and stops only at defined quiescence.

# Next action
After the already-queued writer mutations #1884-#1888 apply, pull canonical state once; verify issue_inbox pending=0, complete the recovered triage item with evidence, then let the fenced timer schedule the next runnable non-PersonalHub work and verify no duplicate run/executor is created.
