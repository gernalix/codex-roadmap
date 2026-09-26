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
Phase 0 recovery is live; begin non-PH reconciliation from the canonical roadmap snapshot.

## Verified facts
- `roadmap.sqlite` in this repository is the canonical task source; the GitHub Actions workflow is its single writer.
- `c2-runtime.path` and `c2-runtime.timer` are active; `c2-runtime.service` is a successful oneshot. The legacy `chatgpt-rdc-supervisor.service` is active.
- The local snapshot contains six work items marked running but no active `work_item_runs` or resource leases. Three are C2 phases; three are imported operational task-state roots.
- The current task id is `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808`.
- Remote Desktop Commander responds on Fedora.
- Current supervisor `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808` holds the real local lease with fencing token 1. The watchdog timer is active.
- The runtime service now requires the current supervisor ID and fencing token before scheduling, submitting writer requests, or launching a worker.
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
Non-PH roadmap reconciliation, scheduler/control-plane enhancements, and execution of ready non-PH work.

## Blockers
No current blocker. The browser recovery path was verified through direct CDP because the legacy Playwright handshake stalled.

## Evidence
- `tools/c2_runtime.py` reads the verified roadmap snapshot and submits mutations to the single writer.
- `tools/c2_scheduler.py` stores worker leases but has no supervisor lease.
- `systemctl --user` confirms active path/timer and legacy supervisor service.
- `c2-supervisor-watchdog.service` exited successfully with `state=healthy` under the real lease.
- Isolated test DB `/tmp/c2-phase0-recovery-test2.sqlite3`: old token 1 retired, new unique supervisor/token 2 active; stale write rejected.
- `python3 -m unittest` passes focused runtime, scheduler, and supervisor lease tests.
- No additional active local C2 scheduler process was observed after terminating the duplicate TUI. The canonical roadmap writer and PH integration processes were preserved.

## Acceptance criteria
Phase 0: current and successor identities persist; stale fencing rejects old local mutations; heartbeat and progress differ; a real replacement browser conversation reads minimal state and acquires a higher token; no duplicate scheduler, writer, or PH worker. Later global C2 criteria remain open.

## Next action
Inspect the non-PH ready/blocked/running slice and its DAG in canonical `roadmap.sqlite`, then reconcile only relevant non-PH work with live repo/runtime evidence.
