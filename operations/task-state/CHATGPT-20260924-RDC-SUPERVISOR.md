# Operational task state — ChatGPT + RDC supervisor

TASK_ID: CHATGPT-20260924-RDC-SUPERVISOR
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Build and deploy a persistent Fedora supervisor that makes long-running ChatGPT + Remote Desktop Commander work resumable without human babysitting by detecting unhealthy workers, enforcing checkpoint freshness, and replacing degraded chats from canonical Git state.

## Constraints
- Git/checkpoint state is canonical; chat memory is disposable.
- Never persist secrets or raw private chat transcripts.
- Do not blindly replay potentially destructive user prompts.
- Authentication/MFA/CAPTCHA/provider outage/unknown DOM changes are explicit human-required blockers.
- Recovery is bounded; no infinite model-driven polling loops.
- Active PersonalHub/Grindr work must not be used for destructive rollover tests; use a synthetic disposable worker.
- Normal Chrome/Firefox profiles remain outside supervisor control.

## Plan / checklist
### Phase 1 — Core supervisor
- [x] Create gernalix/chatgpt-rdc-supervisor and Python package.
- [x] Implement task registry, health state machine, checkpoint freshness and recovery policy.
- [x] Implement Playwright/CDP adapter with transcript-free structural telemetry.
- [x] Implement proactive rollover by context size and 20-minute worker lifetime.
- [x] Implement checkpoint-based replacement-chat handoff.
- [x] Implement bounded retry/reload/human-required recovery.

### Phase 2 — Persistence and services
- [x] Deploy dedicated Chrome profile on local-only CDP 127.0.0.1:9333.
- [x] Deploy systemd supervisor with restart policy and watchdog.
- [x] Deploy independent browser/CDP health timer.
- [x] Add CLI register/list/status/run-once/pause/resume/doctor.
- [x] Add structured local event log and machine-readable runtime state.
- [x] Add optional ntfy hook without secrets in Git.
- [x] Add offline detection and bounded rollover-per-checkpoint protection.

### Phase 3 — Verification
- [x] Deterministic policy/checkpoint tests.
- [x] Prove supervisor SIGKILL recovery through systemd.
- [x] Prove dedicated-browser stop/restart recovery.
- [x] Complete one-time ChatGPT login in dedicated profile.
- [x] Register PersonalHub and observe a real automatic checkpoint request followed by resumed generation.
- [x] Register Grindr against its pushed checkpoint.
- [x] Fix transcript-text false positives in platform-error detection; source f0ee5ea.
- [x] Create and push synthetic disposable rollover fixture; source 6a988b5.
- [x] Reject provisional /c/WEB: URLs as successful rollovers; source 2cedbcf.
- [x] Fix send-message race by waiting for the real send button; source e3f334c.
- [x] Increase rollover persistence window and systemd watchdog headroom; source ea8dc9a.
- [x] Replace polling with persisted-URL waiting and complete one real fresh-chat rollover end-to-end.
- [x] Disable the synthetic worker after PASS and record final acceptance evidence.
- [x] Detect `Too many requests` dialogs, dismiss them automatically, and stop automatic reloads on rate-limit responses; source 7eab77e.
- [x] Add account-wide persistent rate-limit backoff, explicit-resume semantics for human-required workers, and bounded failed-rollover accounting; source 19f2fd1.
- [x] Re-run the suite after rate-limit hardening: 13/13 PASS.

## Current step
Core supervisor acceptance is complete. The synthetic rollover worker reached a fresh replacement chat from its pushed checkpoint and is disabled. A later account-wide `Too many requests` incident exposed a new safety gap; the supervisor is now hardened to auto-dismiss that dialog, treat rate limits as non-reloadable stalls, and place all autonomous workers into a persistent global backoff before any more model requests.

## Verified facts
- Supervisor source repo current pushed main: f1eb35d (contains rate-limit hardening 7eab77e + 19f2fd1).
- Unit suite: 14/14 PASS.
- Dedicated ChatGPT profile is authenticated and CDP is usable.
- PersonalHub worker CHATGPT-20260924-PERSONALHUB-P0 is registered and has already responded to a real supervisor checkpoint request.
- Grindr worker CHATGPT-20260924-GRINDR-WEB-LOGIN-ERROR is registered against a pushed checkpoint and is healthy after the transcript-error detector fix.
- The current supervisor chat itself is also registered as CHATGPT-20260924-RDC-SUPERVISOR and is producing checkpoint requests.
- Synthetic fixture is pushed in chatgpt-rdc-supervisor at commit 6a988b5; its initial persisted chat URL is https://chatgpt.com/c/6ab61996-1c7c-83eb-bf0f-340e4b32767f.
- Synthetic run-once correctly chose action=rollover, reason=proactive context rollover, from pushed checkpoint 6a988b50b750502b8a46ccb6f21f4d61e5875627.
- Failed synthetic rollover attempts did not overwrite the registry URL; they stopped safely as human-required.
- Synthetic rollover acceptance is complete: a fresh replacement worker was reached, responded `READY`, and the synthetic task is now disabled.
- During the later rate-limit incident, four visible `Too many requests` dialogs were found across supervised ChatGPT tabs; RDC dismissed them and a follow-up probe reported `rate_limit_dialogs_remaining 0`.
- The global cooldown is persisted in `~/.local/state/chatgpt-rdc-supervisor/global.json`; the deployed supervisor consults it before any autonomous task action.
- systemd watchdog headroom is 180 seconds; browser health timer remains independent.
- Browser supervision stores structural metadata only; raw private transcripts are not persisted.

## Decisions
- Treat every chat as an ephemeral worker; replacement from pushed Git state is the primary recovery path.
- Default checkpoint freshness budget remains 10 minutes and default hard worker lifetime 20 minutes.
- Two rollovers on one unchanged checkpoint exhaust the automatic rollover budget.
- Error detection must use platform UI surfaces, never arbitrary conversation text.
- A rollover is successful only after a persisted non-WEB conversation URL is observed.
- Use persisted conversation URLs only for rollover success; provisional `/c/WEB:` URLs never count as success.
- Treat `Too many requests` as account-wide: auto-dismiss its modal, never reload it automatically, and back off all autonomous workers for the configured cooldown.
- A `human-required` worker is terminal until an explicit `resume`, which resets its recovery state instead of silently retrying.

## Completed
- Core supervisor implemented, deployed and pushed.
- systemd self-recovery and browser recovery verified.
- Dedicated ChatGPT authentication completed.
- Real PersonalHub checkpoint intervention verified.
- Real Grindr worker registration verified.
- Transcript false-positive detector fixed.
- Provisional URL handling and send-button race fixed.
- Synthetic Git-backed worker created and exercised without touching active user workloads.
- Fresh-chat rollover acceptance completed and synthetic worker disabled.
- Rate-limit dialog handling committed and pushed in 7eab77e.
- Global backoff and explicit-resume hardening committed and pushed in 19f2fd1.
- Updated source is deployed; chatgpt-rdc-supervisor.service is active.

## Remaining
- None for the current acceptance scope. If a rate-limit dialog recurs, inspect the new UI surface before changing selectors; do not reintroduce automatic reload/retry storms.

## Blockers
None. The remaining issue is a bounded frontend synchronization defect isolated to synthetic rollover acceptance.

## Evidence
- Supervisor commits include 1409400, 45f5fa0, f0ee5ea, 6a988b5, 2cedbcf, e3f334c, 0644282, ea8dc9a, 7eab77e, 19f2fd1.
- 14 unittest cases PASS on current pushed main f1eb35d; rate-limit hardening commits 7eab77e and 19f2fd1 remain ancestors of HEAD.
- PersonalHub event log recorded action=request-checkpoint followed by status=working.
- Synthetic fixture checkpoint records the rollover task complete and the worker disabled.
- Live RDC probe after mitigation reported zero remaining visible `Too many requests` dialogs.
- `global.json` records the active rate-limit backoff epoch and chatgpt-rdc-supervisor.service is active.
- systemd/browser watchdog recovery evidence remains PASS from prior checkpoint.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers recover without depending on prior chat memory.
- [x] Critical-length/age workers select rollover from canonical Git state.
- [x] Retry and repeated-rollover loops are bounded.
- [x] Browser/auth/DOM blockers are surfaced explicitly.
- [x] Authenticated real-chat checkpoint intervention has been observed.
- [x] Tests pass, services are deployed, source is pushed.
- [x] One real fresh-chat rollover from a pushed checkpoint updates the worker end-to-end.
- [x] Rate-limit dialogs are automatically dismissed and autonomous requests enter a persistent global backoff instead of reloading/retrying.

## Next action
No further action for the current task. Keep the supervisor running with the global backoff in force; only reopen this task if a rate-limit dialog reappears or a registered worker requires explicit resume.
