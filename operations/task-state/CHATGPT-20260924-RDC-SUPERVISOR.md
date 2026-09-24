# Operational task state — ChatGPT + RDC supervisor

TASK_ID: CHATGPT-20260924-RDC-SUPERVISOR
Updated: 2026-09-24 19:58 Europe/Copenhagen

## Objective
Build and deploy a persistent Fedora supervisor that makes long-running ChatGPT + Remote Desktop Commander work resumable without human babysitting by detecting unhealthy workers, enforcing checkpoint freshness, and replacing degraded chats from canonical Git state.

## Constraints
- Use a separate repository so active PersonalHub/infrastructure owners are not disturbed.
- Git/checkpoint state is canonical; chat memory is disposable.
- Never persist secrets or raw private chat transcripts.
- Do not blindly replay potentially destructive user prompts.
- Authentication/MFA/CAPTCHA/provider outage/unknown DOM changes are explicit human-required blockers, not silently bypassed.
- Recovery must be bounded; no infinite model-driven polling loops.

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
- [x] Live-smoke CDP connection and identify one-time ChatGPT login prerequisite.
- [x] Push implementation checkpoints to source repo.
- [ ] After one-time login, register one safe worker and verify authenticated end-to-end checkpoint request + rollover.

## Current step
Implementation and service deployment are complete. Await one-time ChatGPT login in the dedicated Chrome worker, then run the authenticated end-to-end acceptance check.

## Verified facts
- Source repo: gernalix/chatgpt-rdc-supervisor, current pushed main 45f5fa0.
- Python 3.14, Playwright and Chrome 153 are available.
- Existing unrelated CDP ports 9222/9223 were not touched; supervisor uses 9333 only on loopback.
- Core tests: 10/10 PASS.
- chatgpt-rdc-browser.service and chatgpt-rdc-supervisor.service are enabled/active.
- chatgpt-rdc-browser-health.timer is enabled/active.
- Supervisor systemd WatchdogSec is 90s.
- Forced supervisor SIGKILL recovery PASS: PID changed 2948309 -> 2950358, service active, NRestarts=1.
- Forced browser-stop recovery PASS: PID changed 2895446 -> 2952096 and local CDP returned healthy.
- Dedicated ChatGPT page is currently unauthenticated; structured inspection reports error_kind=login and stores no transcript.
- Normal Chrome/Firefox profiles are not modified or controlled.

## Decisions
- A chat is an ephemeral worker; replacement from Git is the primary recovery path.
- Default checkpoint freshness budget is 10 minutes; default hard worker lifetime is 20 minutes.
- A fresh pushed checkpoint is preferred before rollover; retries and rollovers are bounded.
- Two rollovers on the same unchanged checkpoint exhaust the automatic rollover budget.
- Local network loss pauses deterministic supervision without consuming model retries.
- The supervisor itself is watched by systemd; the dedicated browser has an independent non-model watchdog.
- Authentication secrets/cookies are not copied from the normal browser; login remains an explicit one-time human prerequisite.

## Completed
- Isolated source repo created, committed and pushed.
- Core recovery policy, browser adapter, registry, handoff generator, CLI and event store implemented.
- Persistent systemd services/timer deployed.
- Self-crash and browser-crash recovery verified.

## Remaining
- User signs into ChatGPT once in the dedicated Chrome worker window.
- Register a safe real worker and run one authenticated end-to-end recovery/rollover acceptance test.

## Blockers
- One-time ChatGPT authentication is required in the dedicated Chrome profile. This cannot be safely bypassed or copied from the user's normal browser profile.

## Evidence
- Source commits: 1409400 (initial supervisor), 45f5fa0 (watchdogs/resilience).
- 10 unittest cases PASS on 2026-09-24.
- Systemd live readback: supervisor active with WatchdogUSec=1min30s.
- SIGKILL recovery and dedicated-browser stop/restart recovery both PASS.
- CDP doctor PASS; ChatGPT structured state currently reports login required.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers have a recovery path that does not depend on prior chat memory.
- [x] Critical-length/age workers roll over using canonical Git state.
- [x] Retry loops and repeated rollover loops are bounded.
- [x] Browser/auth/DOM blockers are surfaced explicitly.
- [x] Tests pass, services are active, source is pushed.
- [ ] Authenticated real-chat checkpoint + rollover acceptance is observed once.

## Next action
User logs into ChatGPT in the dedicated Chrome worker window. Then register one safe worker and verify a real checkpoint request and fresh-chat rollover before declaring full end-to-end acceptance.
