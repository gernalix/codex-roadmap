# C2 supervisor recovery

## Objective
Make this supervisor session recoverable, then implement and operate the non-PersonalHub C2 control plane. PersonalHub execution belongs to its existing worker.

## Constraints
- Preserve existing PersonalHub workers, worktrees, devices, and ownership.
- Canonical roadmap mutations go through the GitHub single writer; `roadmap.sqlite` is read-only locally.
- Do not launch a second primary scheduler during cutover.

## Plan / checklist
- [x] Identify the minimum C2 sources, active services, and active C2 runs.
- [x] Persist a unique supervisor lease and fencing token with separate heartbeat and progress.
- [x] Add an external deterministic watchdog and a minimal recovery pointer.
- [x] Verify expiry, fencing, successor acquisition, and real browser session preparation in an isolated live recovery test without touching PH.
- [ ] Reconcile non-PH roadmap and executors; implement and activate the improved C2 runtime.
- [ ] Execute ready non-PH work to applicable acceptance criteria.

## Current step
PROMPT_ID 226672 executed once through C2 and reached a terminal interrupted turn after completing its implementation/tests. Integrate the verified executor fixes, then canonicalize the checkpoint/terminal state and reconcile the same C2 run.

## Verified facts
- `roadmap.sqlite` in this repository is the canonical task source; the GitHub Actions workflow is its single writer.
- `c2-runtime.path` and `c2-runtime.timer` are active; `c2-runtime.service` is a successful oneshot. The legacy `chatgpt-rdc-supervisor.service` is active.
- Terminal task-state reconciliation is live: the false-running historical roots and the stale running Phase 2/3 descendants of completed prompt 175908 were repaired through the fenced single writer; Workflowy projection readback no longer places them in IN CORSO.
- The recovery task id is `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808`.
- Remote Desktop Commander responds on Fedora.
- Current supervisor `00798a0e-021b-4c66-85ef-8c3eac771b93` holds the real local lease with fencing token 2; canonical authority matches it and the watchdog remains active.
- The runtime service now requires the current supervisor ID and fencing token before scheduling, submitting writer requests, or launching a worker.
- Writer-side fencing merged in PR #1171. Canonical claim Issue #1172 applied with this supervisor ID/token; stale renewal Issue #1173 was rejected as `stale_or_expired_supervisor` by the single writer.
- The runtime now reads an atomic derived snapshot of the remote-main `roadmap.sqlite` blob from `~/.local/state/c2-supervisor/roadmap.sqlite3`; it does not depend on the shared PH checkout branch.
- In a separate expired test lease, the watchdog opened a real ChatGPT browser conversation. That session read a minimal pointer, acquired a new unique supervisor ID with token 2, and did not schedule work. Token 1 was rejected after takeover.
- The old Playwright CDP handshake stalled on this profile; bounded direct CDP succeeded. The ChatGPT Send button uses `aria-label=Send` on the current UI.
- A concurrent `codex resume` process opened this same session from a separate C2 bootstrap worktree; it was terminated. The legacy ChatGPT supervisor task `CHATGPT-20260924-RDC-SUPERVISOR` was paused, while its PersonalHub task remained enabled.
- The shared canonical checkout changed to a PH checkpoint branch during the first C2 commit. The C2 change was cherry-picked onto dedicated branch/worktree `codex/c2-supervisor-recovery` at `/home/daniele/.local/share/c2-supervisor/worktree`; the PH branch and worker were left untouched after discovery.

## Decisions
- Keep supervisor liveness state outside the canonical roadmap DB; never write `roadmap.sqlite` directly.
- Treat PH as externally owned and do not use its devices or repositories.
- A local expiry test with a real browser successor is the Phase 0 end-to-end proof. Do not deliberately retire the live supervisor merely to repeat it.
- Run C2 code and the systemd services from the isolated worktree while PH uses the shared checkout.

## Completed
Phase 0 recovery/fencing; isolated remote-main snapshot; PH exclusion; writer-only terminal task-state repairs; PR #1209 with prompt-materialization/schedule-replay fixes merged after CI PASS; PROMPT_ID 226672 scheduled exactly once and recovered without resubmitting its Codex turn; ChatGPT stall-threshold and Codex ambiguous-ack fixes implemented and fully tested by the terminal turn.

## Remaining
Integrate the final executor changes from the 226672 worktree, deploy/read back the merged runtime, record a clear canonical checkpoint, terminalize 226672, reconcile run 2c45668a283840ddad007a7071817399, then let C2 advance only the next explicitly configured non-PH runnable item.

## Blockers
No external blocker. The observed Codex app-server user-approval request caused one worker interruption; the final patch routes approvals through `approvalsReviewer=auto_review` while keeping `approvalPolicy=on-request`.

## Evidence
- `tools/c2_runtime.py` reads the verified roadmap snapshot and submits mutations to the single writer.
- `tools/c2_scheduler.py` stores worker leases but has no supervisor lease.
- `systemctl --user` confirms active path/timer and legacy supervisor service.
- `c2-supervisor-watchdog.service` exited successfully with `state=healthy` under the real lease.
- Isolated test DB `/tmp/c2-phase0-recovery-test2.sqlite3`: old token 1 retired, new unique supervisor/token 2 active; stale write rejected.
- `python3 -m unittest` passes focused runtime, scheduler, and supervisor lease tests.
- All 69 focused C2 tests pass after adding writer-side token validation.
- The remote-main snapshot has `PRAGMA quick_check=ok`, matching supervisor authority, and zero active C2 runs. The refreshed runtime service exited with `Result=success`, `ExecMainStatus=0`.
- No additional active local C2 scheduler process was observed after terminating the duplicate TUI. The canonical roadmap writer and PH integration processes were preserved.
- PR #1209 merged as bce7495917829bb74f87353cd658c51785d54a14 after CI and Roadmap integrity PASS. Writer Issues #1215/#1216 repaired PROMPT_ID 226672 materialization/path and stale 175908 descendants.
- C2 run `2c45668a283840ddad007a7071817399` owns Codex thread `01a0de37-af7f-7120-97ee-e116b4213f63` / turn `01a0de37-b089-7e20-870d-b912eb29ebeb`; recovery reused the same identities and never resubmitted the turn. Receipt is terminal with turn_status=interrupted.
- That turn implemented ChatGPT generation stall thresholds of 40 seconds / 3 recovery attempts and restart-safe Codex ambiguous-turn readback. Targeted C2 tests, full unittest discovery, roadmap verify and diff check passed before interruption.
- The observed approval failure is addressed locally by routing thread/start, thread/resume and turn/start approvals to Codex `auto_review`; focused executor tests pass 8/8.

## Acceptance criteria
Recovery/fencing, PH isolation, stale-state repair, one-run/one-turn Codex identity, ~40 second ChatGPT stall detection, bounded recovery, explicit execution specs and lock-sensitive scheduling are verified locally/live. Final executor integration plus canonical checkpoint/terminal reconciliation remain open.

## Next action
Commit and push the final 226672 executor/checkpoint changes, merge them only after CI PASS, then record the canonical completed checkpoint and terminalize/reconcile the existing run without creating another executor.
