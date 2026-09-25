# Operational task state — ChatGPT + RDC supervisor

TASK_ID: CHATGPT-20260924-RDC-SUPERVISOR
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Build and deploy a persistent Fedora supervisor that makes long-running ChatGPT + Remote Desktop Commander work resumable without human babysitting by detecting unhealthy workers, enforcing checkpoint freshness, replacing degraded chats from canonical Git state, preserving Chrome Codex Switcher context/note continuity across worker rollover, and automatically discovering ChatGPT conversations created on desktop or mobile through account-synced history.

## Constraints
- Git/checkpoint state is canonical; chat memory is disposable.
- Never persist secrets or raw private chat transcripts.
- Do not blindly replay potentially destructive user prompts.
- Authentication/MFA/CAPTCHA/provider outages and unknown DOM changes must fail safely.
- Recovery/retry/rollover loops are bounded.
- Active user workloads must not be used as destructive acceptance fixtures.
- Normal Chrome/Firefox profiles remain outside supervisor control.
- Global ChatGPT rate-limit backoff suppresses retry/reload/rollover; during backoff only already-open tabs may receive the narrowly scoped slow-thinking `continua` recovery.
- A CCS rollover must preserve the same context identity and notes/PROMPT_ID/twin metadata.
- Auto-discovery must use metadata/URLs only; it must not persist raw chat transcripts.
- Newly discovered chats without a Git checkpoint are inventory-only and must not receive autonomous recovery/rollover actions until safely bound to canonical task state.

## Plan / checklist
### Core and deployment
- [x] Implement registry, state machine, checkpoint inspection, browser adapter, handoff generation and CLI.
- [x] Deploy dedicated Chrome worker on 127.0.0.1:9333.
- [x] Deploy systemd supervisor watchdog and browser health timer.
- [x] Implement offline handling, bounded retry/reload/rollover, global rate-limit backoff and optional ntfy hook.
- [x] Verify supervisor SIGKILL recovery and dedicated-browser restart recovery.
- [x] Complete one-time ChatGPT authentication in the dedicated browser profile.
### Real-worker verification
- [x] Register PersonalHub and observe a real automatic checkpoint request followed by resumed generation.
- [x] Register Grindr against its pushed checkpoint.
- [x] Register Fedora ADB keeper chat against dedicated checkpoint CHATGPT-20260925-ADB-KEEPER-LATENCY.
- [x] Fix transcript-text false positives in platform-error detection.
- [x] Detect ChatGPT rate-limit dialogs and back off globally instead of retrying/reloading.
- [x] Fix explicit "None. ..." blocker parsing.
- [x] Detect the ChatGPT "Our systems are thinking a bit more..." notice and recover by stopping that generation and sending exactly `continua`.
- [x] Allow that specific `continua` recovery even during global rate-limit backoff, but only for an already-open registered tab and once per notice signature.
- [x] Harden slow-notice matching to the latest user-request region so stale historical banners cannot trigger duplicate nudges.
- [x] Detect ChatGPT "Message delivery timed out" and recover by sending exactly 'continua' in the affected registered chat.
- [x] Stop blind all-tab rate-limit sweeps from continually extending stale global backoff; only managed-task inspection may establish provider backoff.
- [x] Current supervisor test suite: 25/25 PASS.

### Chrome Codex Switcher continuity
- [x] Add daemon API to replace one context URL while preserving the same context_id.
- [x] Persist old URL -> new URL supersession aliases so a stale old tab cannot restore the previous URL.
- [x] Preserve note, codex_note, notes_independent, prompt IDs and Codex twin across replacement.
- [x] Emit context_url_replaced and update extension tab-map entries to the new URL.
- [x] Add supervisor CCS bridge that updates CCS on every successful rollover.
- [x] Add durable local retry queue when CCS is temporarily unavailable.
- [x] Verify supervisor bridge readback through /api/list after replacement.
- [x] Run CCS full suite: 68/68 PASS; supervisor suite: 19/19 PASS.
- [x] Deploy CCS daemon/extension files and verify deployed hashes match repository files.
- [x] Verify both chrome-codex-switcher.service and chatgpt-rdc-supervisor.service are active; CCS pending queue is empty.

### Cross-device automatic chat discovery
- [x] Discover persisted conversation IDs/URLs from the dedicated authenticated ChatGPT session without generating model requests.
- [x] Persist a deduplicated metadata-only chat inventory across supervisor restarts.
- [x] Verify newly persisted conversations appear after account sync: inventory grew from 21 to 56 chats without manual URL registration.
- [x] Automatically bind discovered URLs to an existing registered task when the conversation ID matches known context; leave checkpoint-less chats inventory-only.
- [x] Expose discovery status in CLI and structured events.
- [x] Add focused tests and verify live metadata-only discovery without violating active rate-limit backoff.
- [x] Deploy/restart the daemon and verify automatic periodic discovery under systemd.

### Rollover acceptance
- [x] Create and push isolated synthetic Git-backed worker.
- [x] Verify forced context-risk selects rollover from a pushed checkpoint.
- [x] Verify failed attempts preserve original registry URL and do not increment rollover_count.
- [x] Diagnose provisional /c/WEB: behavior and send-button race.
- [x] Preserve autonomous-worker residue on evidence branch before cleanup.
- [x] Correct false PASS claims written by the synthetic/manual worker.
- [ ] Observe one supervisor-owned fresh-chat rollover where registry URL, rollover_count, event log and CCS URL continuity all agree.
- [ ] Disable synthetic worker after verified PASS.
## Current step
Cross-device discovery acceptance is complete. Final synthetic rollover acceptance is temporarily blocked by a real provider rate-limit condition: live read-only inspection at 2026-09-25 16:09 CEST found visible rate-limit state on three registered worker tabs and runtime backoff through 16:39:06 CEST. The supervisor service has been restarted on source c4bd9e5 so the removed all-tab rate-limit sweep cannot keep extending the condition. Do not force model-generating rollover traffic until the live rate-limit condition clears.

## Verified facts
- Supervisor source repo pushed main: c4bd9e5160da38d5989975b1a85c3fb93da9732e.
- Cross-device discovery suite: 23/23 PASS.
- Initial live metadata-only discovery found 21 persisted conversations / 4 managed. Current live CLI inventory reports 56 total / 6 managed / 50 inventory-only, proving post-deployment account-synced discovery without manual URL registration.
- Discovery stores conversation ID/URL/timestamps/mode only; chat bodies and titles are not persisted.
- Supervisor CCS bridge/readback commits are included through 2e86dac.
- Chrome Codex Switcher pushed main: c40086abb36d8c7eb7bdb1c1f4f100b96f60286c.
- Supervisor current suite: 25/25 PASS.
- CCS full suite: 68/68 PASS.
- Slow-thinking DOM acceptance with screenshot wording verified detected=true, stopped generation, and sent exactly `continua`.
- During a real PersonalHub occurrence, the affected PersonalHub tab was identified, its stuck generation stopped, and `continua` was sent in that PersonalHub chat rather than the supervisor chat.
- Global backoff code now still inspects already-open registered tabs for this one slow-thinking condition, while suppressing other model/browser recovery actions.
- CCS live daemon endpoint /api/context/replace-url is deployed and healthy.
- Live idempotent CCS readback on context note `supervisor` succeeded without changing the context URL.
- Deployed CCS extension/background.js hash matches repository file exactly.
- Deployed CCS host store.py hash matches repository file exactly.
- CCS pending replacement queue currently contains zero items.
- Both supervisor and CCS systemd services are active.
- ADB keeper worker CHATGPT-20260925-ADB-KEEPER-LATENCY is registered against a persistent supervisor-owned clone of the canonical codex-roadmap checkpoint; canonical checkpoint commit is b463dd1.
- The supervisor's own worker registration now also uses an isolated persistent codex-roadmap checkpoint clone, currently pinned to canonical checkpoint 72f5c1c, so dirty/behind state in the primary codex-roadmap checkout cannot stale its recovery memory.
- PersonalHub, Grindr, supervisor and ADB keeper are registered workers; synthetic rollover worker remains disabled.
- Raw private chat transcripts are not persisted by the supervisor.
- Delivery-timeout recovery fix was integrated through canonical single-writer PR #2; merge SHA c4bd9e5160da38d5989975b1a85c3fb93da9732e.
- Live dedicated-browser inspection found no current rate-limit dialogs before clearing the stale global backoff.
- Live global rate-limit state is reset to 0.0; supervisor service is active on the merged code.
- Targeted PersonalHub post-fix run returned status=working, action=none, reason="generation active"; no duplicate 'continua' was injected into an already-running generation.

## Decisions
- A chat remains an ephemeral worker; pushed Git state is recovery authority.
- Default checkpoint freshness budget is 10 minutes and default hard worker lifetime is 20 minutes.
- Rate-limit is supervisor-wide when detected on a managed task: no automatic reload/rollover storm while active.
- Unmanaged/stale browser tabs must not establish or extend global backoff through a blind dialog sweep.
- Delivery timeout is a same-chat continuation condition: send exactly 'continua'; do not require a pushed checkpoint or immediately roll over.
- Slow-thinking `continua` is the sole permitted model interaction during rate-limit backoff, and only on an already-open registered tab with a fresh unmatched notice.
- A manual/unregistered new chat never counts as rollover PASS.
- A rollover counts only when registered chat_url changes to a persisted non-WEB /c/ UUID, runtime rollover_count increments, event log records the same rollover, and CCS either reports replaced/not-found or records a durable pending replacement.
- CCS context continuity is identity-based: same context_id is retained while URL changes; notes/PROMPT_ID/twin state must remain unchanged.
- Old CCS URLs are permanent supersession aliases to the newest URL for that context, preventing stale tabs from reverting continuity.
## Completed
- Core supervisor implemented, deployed, tested and pushed.
- systemd self-recovery and browser recovery verified.
- Dedicated ChatGPT login completed.
- PersonalHub checkpoint intervention verified.
- Grindr worker registration verified.
- ADB keeper chat registered with a new canonical checkpoint.
- Transcript false-positive bug fixed.
- Global rate-limit handling implemented.
- Blocker-parser regression fixed.
- Slow-thinking recovery fixed, including correct-target PersonalHub intervention during backoff.
- CCS URL replacement/alias/event flow implemented and deployed.
- Supervisor-to-CCS rollover bridge with durable retry queue implemented.
- CCS note/PROMPT_ID/twin continuity tests and full test suite pass.
- Deployed source hashes and service health verified.
- Synthetic false completion claims corrected.
- Metadata-only chat discovery, deduplication, inventory persistence, task binding and CLI visibility implemented and pushed as be7742c.
- Delivery-timeout exact-'continua' recovery and stale-global-backoff fix merged and deployed as c4bd9e5; 25/25 supervisor tests PASS.
- False global backoff was cleared only after live inspection confirmed no current rate-limit dialog; PersonalHub remained in active generation.
- Live discovery acceptance is complete: inventory grew from the initial 21 chats / 4 managed to 56 chats / 6 managed / 50 inventory-only without manual URL registration.
- systemd deployment verified active; metadata inventory continues refreshing under the daemon.

## Remaining
- After the live provider rate-limit condition clears, re-enable only CHATGPT-RDC-SYNTHETIC-ROLLOVER for one controlled forced rollover.
- Verify new persisted supervisor registry URL, rollover_count increment, matching rollover event and CCS continuity status.
- Disable synthetic worker after PASS.
- Update this checkpoint with final acceptance evidence.

## Blockers
- Real ChatGPT provider rate-limit condition is active on multiple registered tabs; runtime backoff is valid through 2026-09-25 16:39:06 CEST. This is an external transient blocker, not a supervisor-code failure.

## Evidence
- Supervisor source commits include 32cad56, 5fc87d1, 2e86dac, 3b4fde1 and be7742c.
- CCS source main c40086a contains context_url_supersessions, /api/context/replace-url and context_url_replaced extension handling.
- Supervisor suite 25/25 PASS.
- CCS suite 68/68 PASS.
- Live deployed-file SHA-256 pairs matched for extension/background.js and host/store.py.
- Live CCS services: supervisor=active, ccs=active, pending_ccs=0.
- Cross-device discovery deployment initially recorded 21 total / 4 managed / 17 inventory-only; current live CLI readback records 56 total / 6 managed / 50 inventory-only.
- Earlier stale backoff was cleared, but a new real provider rate-limit condition was observed at 16:09 CEST. Current runtime backoff endpoint is 2026-09-25 16:39:06 CEST.
- Recent source HEAD c4bd9e5 merges timeout-continua recovery; 298370d introduced delivery-timeout detection and 5c9cb89 changed its action to `NUDGE_CONTINUE`.
- PersonalHub slow-thinking occurrence was recovered by stopping the generation and sending exactly 'continua' in the PersonalHub tab.
- Delivery-timeout fix: canonical PR #2 merged at c4bd9e5. Supervisor service was restarted again at 16:10 CEST on source c4bd9e5 after confirming a real provider rate-limit modal was present, preventing the old process from continuing the removed all-tab rate-limit sweep.
- Canonical ADB keeper checkpoint: codex-roadmap b463dd1; task source ff62956; PR #2 remains externally blocked by GitHub Actions billing/spending limit.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers recover without depending on prior chat memory.
- [x] Critical-length/age workers select rollover from canonical Git state.
- [x] Retry and repeated-rollover loops are bounded.
- [x] Browser/auth/DOM/rate-limit conditions are surfaced and handled safely.
- [x] Slow-thinking platform notice recovery sends exactly 'continua' to the affected registered chat, including during global backoff.
- [x] Delivery-timeout recovery sends exactly 'continua' to the affected registered chat without requiring rollover/checkpoint.
- [x] Stale/unmanaged rate-limit dialogs cannot perpetually extend global backoff through an all-tab sweep.
- [x] Chrome Codex Switcher preserves context/note/PROMPT_ID/twin continuity across URL replacement and blocks stale-URL regression.
- [x] Supervisor queues CCS URL synchronization durably when CCS is unavailable.
- [x] Tests pass, services are deployed and source is pushed.
- [ ] One real supervisor-owned fresh-chat rollover updates registry/runtime/event/CCS evidence end-to-end.

## Next action
After 2026-09-25 16:39:06 CEST, first verify the rate-limit modal is gone without generating a model request. If clear, run one isolated supervisor-owned synthetic rollover; verify the new persisted chat URL, rollover_count, matching rollover event and CCS URL-continuity result atomically, then disable the synthetic worker and checkpoint final PASS.
