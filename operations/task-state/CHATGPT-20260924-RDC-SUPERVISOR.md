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
- [x] Current supervisor test suite: 19/19 PASS.

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
- [ ] Verify one newly created mobile/other-desktop chat appears after account sync.
- [x] Automatically bind discovered URLs to an existing registered task when the conversation ID matches known context; leave checkpoint-less chats inventory-only.
- [x] Expose discovery status in CLI and structured events.
- [x] Add focused tests and verify live metadata-only discovery without violating active rate-limit backoff.
- [ ] Deploy/restart the daemon and verify automatic periodic discovery under systemd.

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
Cross-device metadata-only discovery is implemented, tested and pushed in the supervisor repo. Deploy/restart the systemd daemon and verify periodic discovery; then perform one explicit mobile/other-desktop sync acceptance when feasible. The final synthetic rollover acceptance remains queued afterward.

## Verified facts
- Supervisor source repo pushed main: be7742cbc06b36405e7c9d3892002020cec37f4b.
- Cross-device discovery suite: 23/23 PASS.
- Live metadata-only discovery found 21 persisted conversations and automatically bound 4 to registered managed tasks; no model message was sent.
- Discovery stores conversation ID/URL/timestamps/mode only; chat bodies and titles are not persisted.
- Supervisor CCS bridge/readback commits are included through 2e86dac.
- Chrome Codex Switcher pushed main: c40086abb36d8c7eb7bdb1c1f4f100b96f60286c.
- Supervisor current suite: 19/19 PASS.
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

## Decisions
- A chat remains an ephemeral worker; pushed Git state is recovery authority.
- Default checkpoint freshness budget is 10 minutes and default hard worker lifetime is 20 minutes.
- Rate-limit is supervisor-wide: no automatic reload/rollover storm while active.
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
- Live discovery acceptance succeeded with 21 chats inventoried and 4 managed bindings.

## Remaining
- Restart/deploy the supervisor daemon on be7742c and verify automatic periodic discovery under systemd.
- Verify one chat newly created on mobile/another desktop is discovered after account sync.
- Wait for global ChatGPT rate-limit backoff to clear.
- Re-enable only CHATGPT-RDC-SYNTHETIC-ROLLOVER for one controlled forced rollover.
- Verify new persisted supervisor registry URL, rollover_count increment, matching rollover event and CCS continuity status.
- Disable synthetic worker after PASS.
- Update this checkpoint with final acceptance evidence.

## Blockers
- External ChatGPT global rate-limit backoff is active until 2026-09-25T10:16:31+02:00. Additional model-generating rollover tests must not be forced before it clears.

## Evidence
- Supervisor source commits include 32cad56, 5fc87d1, 2e86dac and 3b4fde1.
- CCS source main c40086a contains context_url_supersessions, /api/context/replace-url and context_url_replaced extension handling.
- Supervisor suite 19/19 PASS.
- CCS suite 68/68 PASS.
- Live deployed-file SHA-256 pairs matched for extension/background.js and host/store.py.
- Live CCS services: supervisor=active, ccs=active, pending_ccs=0.
- PersonalHub slow-thinking occurrence was recovered by stopping the generation and sending exactly `continua` in the PersonalHub tab.
- Canonical ADB keeper checkpoint: codex-roadmap b463dd1; task source ff62956; PR #2 remains externally blocked by GitHub Actions billing/spending limit.

## Acceptance criteria
- [x] Supervisor survives its own process crash/restart through systemd.
- [x] Registered-worker policy exposes healthy/stalled/context-risk/human-required states.
- [x] Stale workers recover without depending on prior chat memory.
- [x] Critical-length/age workers select rollover from canonical Git state.
- [x] Retry and repeated-rollover loops are bounded.
- [x] Browser/auth/DOM/rate-limit conditions are surfaced and handled safely.
- [x] Slow-thinking platform notice recovery sends exactly `continua` to the affected registered chat, including during global backoff.
- [x] Chrome Codex Switcher preserves context/note/PROMPT_ID/twin continuity across URL replacement and blocks stale-URL regression.
- [x] Supervisor queues CCS URL synchronization durably when CCS is unavailable.
- [x] Tests pass, services are deployed and source is pushed.
- [ ] One real supervisor-owned fresh-chat rollover updates registry/runtime/event/CCS evidence end-to-end.

## Next action
Restart the systemd supervisor on be7742c, verify service health plus automatic inventory/event updates, then checkpoint the deployment result.
