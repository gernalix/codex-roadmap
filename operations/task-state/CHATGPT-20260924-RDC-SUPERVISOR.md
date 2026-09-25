# Operational task state — ChatGPT + RDC supervisor

TASK_ID: CHATGPT-20260924-RDC-SUPERVISOR
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Build and deploy a persistent Fedora supervisor that makes long-running ChatGPT + Remote Desktop Commander work resumable without human babysitting by detecting unhealthy workers, enforcing checkpoint freshness, and replacing degraded chats from canonical Git state.

## Constraints
- Git/checkpoint state is canonical; chat memory is disposable.
- Never persist secrets or raw private chat transcripts.
- Do not blindly replay potentially destructive user prompts.
- Authentication/MFA/CAPTCHA/provider outages and unknown DOM changes must fail safely.
- Recovery/retry/rollover loops are bounded.
- Active user workloads must not be used as destructive acceptance fixtures.
- Normal Chrome/Firefox profiles remain outside supervisor control.

## Plan / checklist
### Core and deployment
- [x] Implement registry, state machine, checkpoint inspection, browser adapter, handoff generation and CLI.
- [x] Deploy dedicated Chrome worker on 127.0.0.1:9333.
- [x] Deploy systemd supervisor watchdog and browser health timer.
- [x] Implement offline handling, bounded retry/reload/rollover, and optional ntfy notification hook.
- [x] Verify supervisor SIGKILL recovery and dedicated-browser restart recovery.
- [x] Complete one-time ChatGPT authentication in the dedicated browser profile.
### Real-worker verification
- [x] Register PersonalHub and observe a real automatic checkpoint request followed by resumed generation.
- [x] Register Grindr against its pushed checkpoint.
- [x] Fix transcript-text false positives in platform-error detection.
- [x] Detect ChatGPT rate-limit dialogs and back off globally instead of retrying/reloading.
- [x] Fix explicit "None. ..." blocker parsing.
- [x] Re-run current test suite: 14/14 PASS.

### Rollover acceptance
- [x] Create and push isolated synthetic Git-backed worker.
- [x] Verify forced context-risk selects rollover from a pushed checkpoint.
- [x] Verify failed attempts preserve the original registry URL and do not increment rollover_count.
- [x] Diagnose provisional /c/WEB: behavior and send-button race.
- [x] Preserve autonomous-worker residue on evidence branch before cleanup.
- [x] Correct false PASS claims written by the synthetic/manual worker.
- [ ] Observe one supervisor-owned fresh-chat rollover where registry URL, rollover_count and event log agree.
- [ ] Disable synthetic worker after verified PASS.

## Current step
Synthetic acceptance is paused because ChatGPT imposed a global "Too many requests / temporarily limited access" condition. The supervisor global backoff is active through 2026-09-25 09:43:03 CEST. Do not force additional ChatGPT requests before that runtime backoff clears.

## Verified facts
- Supervisor source repo current pushed main: b88f8c3ea5856234db9204b0c2ffaf183b3aca21.
- Current unit suite: 14/14 PASS.
- Rate-limit handling is present in current main: platform dialogs are detected and supervisor-wide backoff state is stored under its local state directory.
- Current global rate-limit-until epoch: 1790322183.7725668 = 2026-09-25 09:43:03 CEST.
- Synthetic task is disabled.
- Synthetic registry still points to its original URL https://chatgpt.com/c/6ab61996-1c7c-83eb-bf0f-340e4b32767f.
- Independent runtime/event evidence showed rollover_count=0 and no verified successful registry-changing rollover before this checkpoint.
- Manual replacement-chat creation succeeded and proved the handoff can reach a persisted UUID, but it is explicitly non-authoritative for supervisor acceptance.
- A manual replacement worker incorrectly wrote completion claims and source changes; those claims were disproved against registry/runtime/event evidence.
- Autonomous residue was preserved on pushed branch evidence/synthetic-worker-residue-20260925 at 10781d9 before cleanup/reconciliation.
- The false synthetic completion state was corrected and pushed on main at b88f8c3.
- PersonalHub and Grindr remain separate registered workers; the global backoff prevents the supervisor from generating more browser/model requests while the provider limit is active.
- Raw private chat transcripts are not persisted by the supervisor.

## Decisions
- A chat remains an ephemeral worker; pushed Git state is the recovery authority.
- Default checkpoint freshness budget is 10 minutes and default hard worker lifetime is 20 minutes.
- Rate-limit is a supervisor-wide runtime condition: no automatic reload storm or rollover storm is allowed while active.
- A manual or unregistered new chat never counts as rollover PASS.
- A rollover counts only when the registered task URL changes to a persisted non-WEB /c/ UUID, runtime rollover_count increments, and event log records kind=rollover with the same URL/checkpoint.
- Synthetic acceptance remains isolated from PersonalHub, Grindr and other user work.

## Completed
- Core supervisor implemented, deployed, tested and pushed.
- systemd self-recovery and browser recovery verified.
- Dedicated ChatGPT login completed.
- Real PersonalHub checkpoint intervention verified.
- Grindr worker registration verified.
- Transcript false-positive bug fixed.
- Global rate-limit detection/backoff integrated.
- Blockers parser regression fixed.
- Synthetic false completion claims corrected.
- Current source and corrected fixture pushed.

## Remaining
- After global rate-limit backoff clears, re-enable only CHATGPT-RDC-SYNTHETIC-ROLLOVER for one controlled forced rollover.
- Verify new persisted registry chat_url, rollover_count increment and matching event-log rollover record.
- Disable synthetic worker after PASS.
- Update this checkpoint with final evidence and mark acceptance complete.

## Blockers
- External ChatGPT global rate-limit backoff is active until 2026-09-25 09:43:03 CEST. Additional browser/model requests must not be forced while it is active.
## Evidence
- Source main b88f8c3.
- Unit suite 14/14 PASS after rate-limit and blocker-parser changes.
- PersonalHub event history includes request-checkpoint followed by resumed working state.
- Synthetic attempted-rollover events show safe failure behavior with unchanged registry URL.
- global.json runtime backoff readback returned active=true and rate_limit_until_epoch=1790322183.7725668.
- Evidence branch 10781d9 preserves autonomous synthetic-worker residue for later review if needed.
- Corrected synthetic fixture is on source main and explicitly states that manual replacement does not count as PASS.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers recover without depending on prior chat memory.
- [x] Critical-length/age workers select rollover from canonical Git state.
- [x] Retry and repeated-rollover loops are bounded.
- [x] Browser/auth/DOM/rate-limit conditions are surfaced and handled safely.
- [x] Authenticated real-chat checkpoint intervention has been observed.
- [x] Tests pass, services are deployed and source is pushed.
- [ ] One real supervisor-owned fresh-chat rollover updates registry/runtime/event evidence end-to-end.

## Next action
After the global ChatGPT rate-limit backoff has cleared, re-enable only CHATGPT-RDC-SYNTHETIC-ROLLOVER, force context-risk from the corrected pushed checkpoint, verify registry chat_url + rollover_count + event-log rollover atomically, then disable the synthetic worker and checkpoint final PASS.
