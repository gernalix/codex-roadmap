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
- [x] Reconcile non-PH roadmap and executors; implement and activate the improved C2 runtime.
- [x] Re-audit every non-terminal root C2 task from repository/runtime evidence and apply one verified canonical optimization batch.
- [ ] Execute only explicit ready non-PH work to applicable acceptance criteria.

## Current step
The user-directed takeover retired supervisor token 5 and acquired supervisor `245fc2d9-037a-41cb-9747-ce5b428051c0`, fencing token 6, via Issue #1264. The 34-root repository/runtime audit is recorded in `C2-ROOT-AUDIT-20260926.md`; PR #1270 added the fenced reconciliation operation. Issues #1271/#1272 applied classification and readiness-blocker batches. Three distinct newly observed C2 weaknesses were captured through Issue #1273, with readiness blockers submitted in Issue #1274. Workflowy and C2 runtime readback pass: `active=0`, `ready=0`; path/timer/watchdog are active. No C2 work was dispatched; PersonalHub prompt 669941 remains externally owned and running. Push this checkpoint and stop.

## Verified facts
- `roadmap.sqlite` in this repository is the canonical task source; the GitHub Actions workflow is its single writer.
- `c2-runtime.path` and `c2-runtime.timer` are active; `c2-runtime.service` is a successful oneshot. The legacy `chatgpt-rdc-supervisor.service` is active.
- Terminal task-state reconciliation is live: the false-running historical roots and the stale running Phase 2/3 descendants of completed prompt 175908 were repaired through the fenced single writer; Workflowy projection readback no longer places them in IN CORSO.
- The recovery task id is `01a0ddaf-99f5-7fa1-82c2-6d5a26a84808`.
- Remote Desktop Commander responds on Fedora.
- Current supervisor `245fc2d9-037a-41cb-9747-ce5b428051c0` holds the real local lease with fencing token 6; canonical authority matches it via single-writer Issues #1264 and #1269.
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
Root audit and canonical optimization are complete. Ten current code/incident intakes are now waiting with precise execution-context or human/RDC blockers; none remains falsely pending without a spec. Future C2 implementation work must be separately dispatched only after an explicit non-PH execution spec is prepared. Preserve the current PH worker and the waiting/manual lanes.

## Blockers
No blocker to this audit. Scheduling remains intentionally idle: pending non-PH code intakes have no explicit `work_item_execution_specs` rows. Waiting/manual and PH-owned work retain their own blockers and ownership. The observed Codex app-server user-approval request caused one earlier worker interruption; the final patch routes approvals through `approvalsReviewer=auto_review` while keeping `approvalPolicy=on-request`.

## Evidence
- `226672` canonical work item and run are both `completed`; original run `2c45668a283840ddad007a7071817399` has no active worker/lease.
- Backlog audit found 317 non-terminal rows before cleanup: 77 `unknown`, 65 `blocked`, 175 `pending`; 92 root prompt placeholders have no canonical prompt materialization and are historical noise rather than executable work.
- First optimization batch was atomically rejected before application because 653776 had already become terminal `blocked`; no partial roadmap mutation occurred.
- 653776 Codex run `994868eb88d24b5384de2f513351bf24` performed no code/test work; its only blocker was a missing remote branch during `roadmap_start`.
- Local claim-vs-renew fix in `tools/c2_runtime.py` now claims an expired/missing different canonical authority, renews only an exact matching authority, and fences an unexpired different authority before scheduling.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_c2_*.py' -v`: 121 tests PASS; `roadmap_db.py verify` PASS; `git diff --check` PASS.
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
- Successor-authority fix merged in PR #1256 at commit `d5df4e96`; runtime claimed fencing token 5 through single-writer Issue #1261.
- Backlog optimization receipt `c2-backlog-optimize-20260926-v3` / Issue #1260 is applied: `unknown=0`, `blocked=36`, `pending=175`, and no non-terminal unmaterialized root prompts remain.
- Reconciliation under token 5 found zero active runs, zero resource leases and zero `running` work items; PersonalHub workers/devices were not touched.
- Runtime readback at 18:31 CEST used canonical snapshot `0672242c4b0ece20971dca86d85cbff3b5860b2c`, exited successfully with `active=0`, `ready=0`; timer/path are active again.
- User-directed takeover: legacy C2 workers were already disabled; the PH worker and legacy daemon were preserved. Only C2 runtime path/timer/watchdog were paused. Issue #1264 retired token 5 and claimed token 6; Issue #1269 renewed token 6. Before Issue #1271 there were zero active C2 runs/resource leases and zero running non-PH work items.
- PR #1270 merged with 125 focused C2 tests, roadmap verify and GitGuardian PASS. Its `c2_reconcile_item` operation requires the fenced supervisor authority, non-prompt root, repository evidence and no active run.
- Root audit Issue #1271 closed/applied at 2026-09-26T17:12:41Z: 24 root classifications plus prompt 812553 explanation correction. Local preflight on a copy of the canonical snapshot passed 25/25 operations and foreign-key check. Issue #1272 closed/applied at 2026-09-26T17:18:41Z: ten intake readiness corrections, preflight 10/10. Snapshot `fa92d20c59ef201834fc863612a0c52c140af371` has zero unconfigured pending intake roots; roadmap verify PASS.
- Pending prompt model/reasoning metadata was reviewed: existing GPT-5.6 Terra/Sol selections are appropriate for the unresolved browser/code scopes; blocked GPT-6 Luna and running PH metadata were preserved. Prompt text was not changed.
- Workflowy roadmap sync finished with `Result=success`, `ExecMainStatus=0`, zero warnings. API cache readback places PH prompt 669941 in IN CORSO, PH Workflowy and implemented auto-spec intake in COMPLETATI RECENTEMENTE, ntfy and the unconfigured cross-chat lease intake in IN ATTESA.
- After Issue #1272, the periodic Workflowy sync finished with `Result=success`, `ExecMainStatus=0`, `warnings=0`; fresh API cache readback places PH 669941 in IN CORSO, PH Workflowy in COMPLETATI RECENTEMENTE, and current unconfigured C2 intakes 84f3/f2d5/ff254 in IN ATTESA.
- C2 runtime path/timer/watchdog were restarted after canonical `configured_runnable=0` and `active_runs=0` checks. The first triggered service used snapshot `fa92d20c59ef201834fc863612a0c52c140af371`, exited `Result=success`, `ExecMainStatus=0`, and reported `active=0`, `ready=0`, `events=[]`.
- User-requested obstacle capture: existing f2d5 Git hook, cdab Workflowy sync-lag and e2dd intake-visibility tasks were reused. Issue #1273 registered only three distinct gaps: selective imported-descendant reconciliation, pending-prompt repo-routing mutation, and deterministic Codex intake preparation. Issue #1274 provided explicit waiting blockers for these new roots; no task was dispatched.

## Acceptance criteria
Recovery/fencing, PH isolation, stale-state repair, one-run/one-turn Codex identity, ~40 second ChatGPT stall detection, bounded recovery, explicit execution specs, lock-sensitive scheduling, final executor integration, canonical checkpoint, terminalization and run reconciliation are verified. Successor-authority handoff is merged. The 34-root repository audit, writer receipts, roadmap verification, Workflowy projection and idle runtime readback under token 6 are PASS.

## Next action
After this checkpoint is pushed, stop this audit without dispatching a new queue item. In the next C2 turn, capture any new unique obstacle in the roadmap after checking for an existing intake; then choose one current non-PH intake from `C2-ROOT-AUDIT-20260926.md`, prepare its explicit deterministic execution spec, and respect current fencing and ownership.
