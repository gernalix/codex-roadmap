# Operational task state — ChatGPT + RDC supervisor

TASK_ID: CHATGPT-20260924-RDC-SUPERVISOR
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Build and deploy a persistent Fedora supervisor that makes long-running ChatGPT + Remote Desktop Commander work resumable without human babysitting by detecting unhealthy workers, enforcing checkpoint freshness, and replacing degraded chats from canonical Git state.

## Constraints
- Use a separate repository so active PersonalHub/infrastructure owners are not disturbed.
- Git/checkpoint state is canonical; chat memory is disposable.
- Never persist secrets or raw private chat transcripts.
- Do not blindly replay potentially destructive user prompts.
- Authentication/MFA/CAPTCHA/provider outage/unknown DOM changes are explicit human-required blockers, not silently bypassed.
- Recovery must be bounded; no infinite model-driven polling loops.
- Do not use active PersonalHub/Grindr work as a destructive rollover test; use a synthetic disposable worker.

## Plan / checklist
### Phase 1 — Core supervisor
- [x] Create gernalix/chatgpt-rdc-supervisor and Python package.
- [x] Implement task registry, health state machine, checkpoint freshness and recovery policy.
- [x] Implement Playwright/CDP ChatGPT adapter with selector fallbacks and transcript-free structural telemetry.
- [x] Implement proactive context rollover by size and a hard 20-minute worker lifetime.
- [x] Implement new-chat handoff prompt generated only from TASK_ID/state-file/checkpoint/Next action protocol.
- [x] Implement bounded transient retry/reload and terminal human-required states.
### Phase 2 — Persistence and service
- [x] Add dedicated Chrome profile launcher on local-only CDP 127.0.0.1:9333.
- [x] Add systemd user supervisor with Restart=always and WatchdogSec=90.
- [x] Add independent browser/CDP health timer that restarts an unhealthy worker browser.
- [x] Add CLI for register/list/status/run-once/pause/resume/doctor.
- [x] Add structured local event log and machine-readable runtime state.
- [x] Add optional ntfy hook without secrets in Git.
- [x] Add offline detection and bounded rollover-per-checkpoint protection.

### Phase 3 — Verification
- [x] Unit-test policy/state transitions/checkpoint handling: 10/10 PASS.
- [x] Simulate frozen/error/context-risk/logout cases in deterministic policy tests.
- [x] Deploy user services on Fedora and prove supervisor crash/restart recovery.
- [x] Prove browser watchdog recovery by stopping the dedicated browser and observing automatic restart/CDP recovery.
- [x] Complete one-time ChatGPT login in the dedicated browser profile.
- [x] Register a real PersonalHub worker and observe a real automatic checkpoint request followed by resumed generation.
- [x] Register a real Grindr worker and validate checkpoint association.
- [x] Fix transcript-text false positives so phrases such as “Something went wrong” inside conversation content are not treated as ChatGPT platform errors.
- [x] Re-run core test suite after the health-detector fix: 10/10 PASS.
- [ ] Verify one complete fresh-chat rollover end-to-end on a synthetic disposable worker, including URL replacement and continuation from pushed checkpoint.

## Current step
Core deployment and authenticated real-worker supervision are operational. The only remaining acceptance item is a controlled fresh-chat rollover using a synthetic worker so active PersonalHub and Grindr lanes are not disrupted.
## Verified facts
- Source repo: gernalix/chatgpt-rdc-supervisor, pushed main f0ee5ea.
- Python 3.14, Playwright and Chrome 153 are available.
- Existing unrelated CDP ports 9222/9223 were not touched; supervisor uses 9333 only on loopback.
- Core tests: 10/10 PASS after the latest detector fix.
- chatgpt-rdc-browser.service and chatgpt-rdc-supervisor.service are enabled/active.
- chatgpt-rdc-browser-health.timer is enabled/active.
- Supervisor systemd WatchdogSec is 90s.
- Forced supervisor SIGKILL recovery PASS: PID changed 2948309 -> 2950358, service active, NRestarts=1.
- Forced browser-stop recovery PASS: PID changed 2895446 -> 2952096 and local CDP returned healthy.
- Dedicated ChatGPT browser profile is authenticated; composer and CDP access are usable.
- PersonalHub worker CHATGPT-20260924-PERSONALHUB-P0 is registered against its canonical task-state file. The supervisor emitted a real request-checkpoint event and the worker resumed generation.
- Grindr worker CHATGPT-20260924-GRINDR-WEB-LOGIN-ERROR is registered against pushed checkpoint f8921b60....
- Initial Grindr supervision exposed a false-positive bug because the conversation itself contains the phrase “Something went wrong”; the detector incorrectly scanned transcript text as a platform error.
- Source commit f0ee5ea fixes this by restricting error detection to visible alert/status/error/toast UI plus retry-associated output instead of arbitrary conversation content. Live reinspection then reported authenticated=true, composer=true, generating=true, error=None.
- Normal Chrome/Firefox profiles are not modified or controlled.
## Decisions
- A chat is an ephemeral worker; replacement from Git is the primary recovery path.
- Default checkpoint freshness budget is 10 minutes; default hard worker lifetime is 20 minutes.
- A fresh pushed checkpoint is preferred before rollover; retries and rollovers are bounded.
- Two rollovers on the same unchanged checkpoint exhaust the automatic rollover budget.
- Local network loss pauses deterministic supervision without consuming model retries.
- The supervisor itself is watched by systemd; the dedicated browser has an independent non-model watchdog.
- Error detection must never classify ordinary transcript text as ChatGPT platform health evidence.
- Authentication secrets/cookies are not copied from the normal browser.
- Final rollover acceptance will use a synthetic disposable task, not an active user workload.

## Completed
- Isolated source repo created, committed and pushed.
- Core recovery policy, browser adapter, registry, handoff generator, CLI and event store implemented.
- Persistent systemd services/timer deployed.
- Self-crash and browser-crash recovery verified.
- Dedicated ChatGPT login completed.
- Real PersonalHub checkpoint-request intervention verified.
- Real Grindr worker registration verified.
- Transcript-text false-positive health bug fixed, tested and pushed.

## Remaining
- Create a synthetic disposable Git-backed worker/checkpoint.
- Register it in the supervisor and force a rollover condition without touching active workloads.
- Verify a new ChatGPT conversation URL is created, registry points to the new URL, the handoff starts from the pushed checkpoint, and no rollover loop occurs.
- Remove/disable the synthetic worker and record final acceptance evidence.

## Blockers
None. The remaining rollover test is intentionally isolated from active user tasks.
## Evidence
- Supervisor source commits: 1409400, 45f5fa0, f0ee5ea.
- 10 unittest cases PASS after latest health-detector changes.
- Systemd live readback previously verified supervisor/browser/timer active and watchdog configured.
- SIGKILL recovery and dedicated-browser stop/restart recovery both PASS.
- PersonalHub structured event log records action=request-checkpoint followed by status=working.
- Grindr checkpoint is pushed on codex-roadmap main; live browser inspection after f0ee5ea reports no platform error.
- All browser telemetry used for supervision is structural; raw private transcripts are not persisted.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers have a recovery path that does not depend on prior chat memory.
- [x] Critical-length/age workers have a rollover policy based on canonical Git state.
- [x] Retry loops and repeated rollover loops are bounded.
- [x] Browser/auth/DOM blockers are surfaced explicitly.
- [x] Tests pass, services are active, source is pushed.
- [x] Authenticated real-chat checkpoint-request intervention has been observed.
- [ ] A real fresh-chat rollover from a pushed checkpoint has been observed end-to-end.

## Next action
Create a synthetic disposable Git-backed worker, register it, force a context-risk rollover, verify the new conversation URL and checkpoint-based handoff end-to-end, then disable/remove the synthetic worker and checkpoint the final PASS evidence.
