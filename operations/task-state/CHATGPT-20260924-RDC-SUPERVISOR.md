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
- [x] Increase rollover persistence window and systemd watchdog headroom; current source ea8dc9a.
- [x] Re-run suite after rollover hardening: 12/12 PASS.
- [ ] Replace sleep/poll URL persistence detection with Playwright event-driven waiting and verify one real fresh-chat rollover end-to-end.
- [ ] Disable/remove the synthetic worker after PASS and record final acceptance evidence.

## Current step
The synthetic worker is safely isolated and has repeatedly selected the correct proactive rollover action. The remaining defect is limited to detecting when ChatGPT converts the provisional /c/WEB: URL into its persisted UUID: a manual probe showed the UUID immediately after new_chat returned, indicating the current sleep/poll loop can miss the frontend navigation event. Replace that polling with Playwright event-driven waiting, then rerun the same synthetic rollover.

## Verified facts
- Supervisor source repo current pushed main: ea8dc9a.
- Unit suite: 12/12 PASS.
- Dedicated ChatGPT profile is authenticated and CDP is usable.
- PersonalHub worker CHATGPT-20260924-PERSONALHUB-P0 is registered and has already responded to a real supervisor checkpoint request.
- Grindr worker CHATGPT-20260924-GRINDR-WEB-LOGIN-ERROR is registered against a pushed checkpoint and is healthy after the transcript-error detector fix.
- The current supervisor chat itself is also registered as CHATGPT-20260924-RDC-SUPERVISOR and is producing checkpoint requests.
- Synthetic fixture is pushed in chatgpt-rdc-supervisor at commit 6a988b5; its initial persisted chat URL is https://chatgpt.com/c/6ab61996-1c7c-83eb-bf0f-340e4b32767f.
- Synthetic run-once correctly chose action=rollover, reason=proactive context rollover, from pushed checkpoint 6a988b50b750502b8a46ccb6f21f4d61e5875627.
- Failed synthetic rollover attempts did not overwrite the registry URL; they stopped safely as human-required.
- Manual new_chat probe returned provisional https://chatgpt.com/c/WEB:e92896a9-54ef-41cf-a9af-698bc38730fc, and immediately after return the same page reported persisted URL https://chatgpt.com/c/6ab61af3-6f04-83eb-9963-1b5b1b102387 with two turns and title "Continua task worker sostitutivo".
- That probe proves the handoff message is sent and ChatGPT does create the replacement conversation; the unresolved issue is reliable observation of the final URL transition inside new_chat().
- systemd watchdog headroom is now 180 seconds; browser health timer remains independent.
- Browser supervision stores structural metadata only; raw private transcripts are not persisted.

## Decisions
- Treat every chat as an ephemeral worker; replacement from pushed Git state is the primary recovery path.
- Default checkpoint freshness budget remains 10 minutes and default hard worker lifetime 20 minutes.
- Two rollovers on one unchanged checkpoint exhaust the automatic rollover budget.
- Error detection must use platform UI surfaces, never arbitrary conversation text.
- A rollover is successful only after a persisted non-WEB conversation URL is observed.
- Use Playwright event-driven URL/navigation waiting rather than extending fixed sleeps further.
- Final rollover acceptance continues on the synthetic worker only.

## Completed
- Core supervisor implemented, deployed and pushed.
- systemd self-recovery and browser recovery verified.
- Dedicated ChatGPT authentication completed.
- Real PersonalHub checkpoint intervention verified.
- Real Grindr worker registration verified.
- Transcript false-positive detector fixed.
- Provisional URL handling and send-button race fixed.
- Synthetic Git-backed worker created and exercised without touching active user workloads.
- Current source hardening through ea8dc9a deployed.

## Remaining
- Replace the new_chat sleep/poll loop with event-driven persisted-URL waiting.
- Re-run 12-test suite and add/adjust URL-wait regression coverage if practical.
- Reset only the synthetic worker runtime and rerun one forced rollover.
- Verify new persisted URL, registry update, rollover_count increment, event-log rollover record, and checkpoint-based handoff.
- Disable/remove the synthetic worker and checkpoint final PASS.

## Blockers
None. The remaining issue is a bounded frontend synchronization defect isolated to synthetic rollover acceptance.

## Evidence
- Supervisor commits: 1409400, 45f5fa0, f0ee5ea, 6a988b5, 2cedbcf, e3f334c, 0644282, ea8dc9a.
- 12 unittest cases PASS after latest source changes.
- PersonalHub event log recorded action=request-checkpoint followed by status=working.
- Synthetic run-once logs recorded action=rollover with pushed checkpoint, then safe human-required because persisted URL was not observed in time.
- Manual probe proved the replacement chat exists with a persisted UUID immediately after new_chat() returns.
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
- [ ] One real fresh-chat rollover from a pushed checkpoint updates the registry end-to-end.

## Next action
Replace new_chat() fixed sleep/poll URL persistence detection with Playwright event-driven waiting for a non-WEB /c/ conversation URL, rerun the synthetic forced rollover, verify registry/event/runtime updates, then disable the synthetic worker and checkpoint final PASS.
