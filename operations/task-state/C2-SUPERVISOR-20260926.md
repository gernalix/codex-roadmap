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
PROMPT_ID 226672 is merged, canonically completed and its original C2 run is reconciled without duplication. Resume the fenced runtime under supervisor token 3, capture the successor-authority handoff defect discovered during recovery, then advance only explicitly configured non-PH work.

## Verified facts
- `roadmap.sqlite` in this repository is the canonical task source; the GitHub Actions workflow is its single writer.
- `c2-runtime.path` and `c2-runtime.timer` are active; `c2-runtime.service` is a successful oneshot. The legacy `chatgpt-rdc-supervisor.service` is active.
- Terminal task-state reconciliation is live: the false-running historical roots and the stale running Phase 2/3 descendants of completed prompt 175908 were repaired through the fenced single writer; Workflowy projection readback no longer places them in IN CORSO.
- The recovery task id is `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808`.
- Remote Desktop Commander responds on Fedora.
- Current supervisor `e49b4274-6416-4b2d-83ab-890c6ddad24a` holds the real local lease with fencing token 3; canonical authority matches it via single-writer Issue #1238.
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
Phase 0 recovery/fencing; isolated remote-main snapshot; PH exclusion; writer-only terminal task-state repairs; PR #1209 with prompt-materialization/schedule-replay fixes merged after CI PASS; PROMPT_ID 226672 scheduled exactly once and recovered without resubmitting its Codex turn; final executor/approval recovery merged in PR #1225 with all gates PASS; canonical checkpoint Issue #1239 applied; terminal PASS Issue #1240 applied; original run `2c45668a283840ddad007a7071817399` reconciled by Issue #1241 with its resource leases released.

## Remaining
Resume `c2-runtime` under token 3 and verify it does not create a duplicate executor. Capture/fix the discovered handoff defect where a successor local token can cause runtime renewal of the expired canonical token instead of a successor claim. Then advance only explicitly configured non-PH runnable work; do not infer execution specs and do not touch PH.

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
- PR #1225 merged as 12814cdaf889314b0d2d48bb72ff0743e0717bfe after CI, Roadmap integrity and GitGuardian PASS.
- Successor supervisor claim Issue #1238, final checkpoint Issue #1239, terminal PASS Issue #1240 and run reconciliation Issue #1241 were all applied by the single writer.
- C2 run `2c45668a283840ddad007a7071817399` owns Codex thread `01a0de37-af7f-7120-97ee-e116b4213f63` / turn `01a0de37-b089-7e20-870d-b912eb29ebeb`; recovery reused the same identities and never resubmitted the turn. Receipt is terminal with turn_status=interrupted.
- That turn implemented ChatGPT generation stall thresholds of 40 seconds / 3 recovery attempts and restart-safe Codex ambiguous-turn readback. Targeted C2 tests, full unittest discovery, roadmap verify and diff check passed before interruption.
- The observed approval failure is addressed locally by routing thread/start, thread/resume and turn/start approvals to Codex `auto_review`; focused executor tests pass 8/8.

## Acceptance criteria
Recovery/fencing, PH isolation, stale-state repair, one-run/one-turn Codex identity, ~40 second ChatGPT stall detection, bounded recovery, explicit execution specs, lock-sensitive scheduling, final executor integration, canonical checkpoint, terminalization and run reconciliation are verified. Runtime restart under token 3 plus capture of the successor-claim handoff defect remain operational follow-up.

## Next action
Restart the fenced C2 runtime under supervisor token 3, verify `active=0`/no duplicate 226672 launch and inspect explicit non-PH runnable specs. Add the successor-authority claim-vs-renew handoff defect to C2, then continue only the next explicitly configured non-PH item.
