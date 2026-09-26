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
Successor supervisor recovery is live with local/canonical fencing token 2. Non-PH reconciliation repaired stale terminal roots; PROMPT_ID 226672 is materialized but not scheduled.

## Verified facts
- `roadmap.sqlite` in this repository is the canonical task source; the GitHub Actions workflow is its single writer.
- `c2-runtime.path` and `c2-runtime.timer` are active; `c2-runtime.service` is a successful oneshot. The legacy `chatgpt-rdc-supervisor.service` is active.
- The local snapshot contains six work items marked running but no active `work_item_runs` or resource leases. Three are C2 phases; three are imported operational task-state roots.
- The current task id is `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808`.
- Remote Desktop Commander responds on Fedora.
- Current supervisor `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808` holds the real local lease with fencing token 1. The watchdog timer is active.
- Recovery successor `00798a0e-021b-4c66-85ef-8c3eac771b93` acquired a NEW local lease with fencing token 2; canonical writer claim #1198 and renewals #1199/#1200/#1202 were applied.
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
Minimum Phase 0 inspection, lease/watchdog implementation and activation, isolated end-to-end browser recovery, fencing verification, and local runtime gate.

## Remaining
Repair stale 175908 phase descendants; complete ChatGPT/Codex supervision integration and acceptance through PROMPT_ID 226672; then execute only explicitly configured non-PH runnable work.

## Blockers
No Phase 0 blocker. The browser recovery path was verified through direct CDP because the legacy Playwright handshake stalled.

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
- Recovery reconciliation found zero active canonical C2 runs/resource leases; the only enabled legacy ChatGPT supervisor worker is `CHATGPT-20260924-PERSONALHUB-P0`, left unchanged.
- Fenced terminal-state reimport Issue #1201 repaired the three historical non-PH task-state roots; only stale 175908 phase descendants remain running.
- PR #1113 (continuous C2 discovery capture rule) merged with all gates PASS.
- C2 work item `wi:10974cc59a13437fa273b34d83085631` was materialized by writer Issue #1203 as Goal `PROMPT_ID=226672` with exact execution metadata; it remains pending and unscheduled.

## Acceptance criteria
Phase 0 local recovery and canonical writer fencing are verified. Later global C2 criteria remain open.

## Next action
Create an isolated worktree for PROMPT_ID 226672 from canonical remote-main commit 94f1d9d1ab758486d1bc07f6ddaa184763955bd5, configure its exact C2 execution spec, verify it is the only intended schedulable spec, then schedule max-parallel=1 and supervise it through terminal reconciliation. Preserve PH ownership and all devices.
