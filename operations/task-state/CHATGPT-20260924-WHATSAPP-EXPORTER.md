# Operational task state — WhatsApp exporter

TASK_ID: CHATGPT-20260924-WHATSAPP-EXPORTER
Updated: 2026-09-25 09:08 Europe/Copenhagen

## Objective
Build a robust incremental WhatsApp exporter starting from WhatsApp Web on Fedora, reusing verified authenticated-browser access and existing whatsapp-watcher DOM discovery, with deduplication, human-readable history, media preservation when accessible, and optional relationship/block-state events for Carlo Visda.

## Constraints
- Use Remote Desktop Commander for Fedora/browser/runtime work.
- Treat Git/codex-roadmap as canonical operational memory; update this state file and checkpoint commit+push after meaningful progress.
- Read and follow operations/task-state/README.md before doing work.
- Do not log out WhatsApp Web, clear browser storage, send messages, or change block state for testing.
- Do not persist unrelated chat contents while discovering selectors.
- Export must be incremental and duplicate-free.
- Prefer stable semantic DOM hooks (data-testid, aria-label, roles, explicit system-message text); do not rely on generated CSS classes unless unavoidable.
- For own block/unblock, record factual events only when WhatsApp UI explicitly proves state.
- For peer block/unblock, store only inferred events with raw evidence and confidence.
- Preserve private chat contents locally; do not commit transcripts/media to public source repositories.
- Avoid touching unrelated dirty worktrees or the current PersonalHub recovery lane.
- No intermediate PRs unless technically required.

## Plan / checklist
### Phase 1 — Rehydrate context
- [x] Read operations/task-state/README.md.
- [x] Read CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md in full.
- [x] Inspect /home/daniele/projects/whatsapp-watcher and preserve any pre-existing untracked relationship-core.js / relationship-monitor.js work.
- [x] Reconfirm authenticated WhatsApp Web safe-inspection path and current browser/runtime state.

### Phase 2 — Exporter architecture
- [x] Decide whether exporter belongs in whatsapp-watcher or a dedicated repo based on scope; dedicated exporter selected.
- [x] Define canonical local storage schema for chats/messages/revisions/media/system events.
- [x] Define unique identity/deduplication keys and incremental cursor/reconciliation strategy.
- [x] Define human-readable no-ID view with localized/relative dates.

### Phase 3 — Carlo Visda first implementation
- [x] Export the Carlo Visda chat incrementally without duplicating previously saved messages.
- [ ] Preserve sender name, timestamps, text, reply relation, media metadata/files when accessible, edited/deleted/system messages, calls if WhatsApp exposes them.
- [ ] Capture own block/unblock system messages/state and peer-block inference evidence.
- [x] Verify re-run is a no-op for unchanged rendered history.
- [x] Avoid exporting unrelated chats during Carlo-only validation.

### Phase 4 — Generalize
- [ ] Generalize from Carlo to selectable WhatsApp chats without weakening privacy/scope.
- [ ] Add focused synthetic/recorded DOM tests.
- [x] Deploy runtime/extension safely into authenticated browser.
- [x] Verify restart/reload resilience and incremental recovery.
- [ ] Document usage and limitations.
- [ ] Commit/push source and final roadmap checkpoint.

## Current step
Media preservation is verified as far as the current Carlo DOM permits: metadata-only media is retained safely, and the accessible-source download/dedupe path is covered end-to-end by tests. A fresh bounded backfill again reaches a fixed top with no older-history control exposed. Continue with relationship-event verification and selectable-chat generalization while treating the currently observable DOM boundary as the history limit unless a safe read-only mechanism becomes available.

## Verified facts
- Existing repo: /home/daniele/projects/whatsapp-watcher, main at b6e3e9f when last inspected.
- whatsapp-watcher is a Manifest V3 Chrome/Chromium extension for read-receipt monitoring and already runs only on https://web.whatsapp.com/.
- At last inspection, whatsapp-watcher had untracked files relationship-core.js and relationship-monitor.js. Do not overwrite/delete them; inspect before deciding ownership.
- Live authenticated WhatsApp Web discovery for Carlo Visda is already documented in CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md.
- Verified semantic DOM signals from that discovery: conversation-panel-wrapper, conversation-info-header, conversation-compose-box-input; composer aria-label like "Type a message to Carlo Visda".
- Contact info exposes data-testid=li-block and aria-label "Block Carlo Visda" when currently unblocked; future "Unblock ..." state can be watched for own block state.
- Rendered conversation contains explicit historical system-message rows "You blocked this person" and "You unblocked this person".
- Current header snapshot at discovery showed Carlo's name but no online/last-seen string; peer-block inference must wait for an observed transition and must remain inferred.
- A temporary read-only copy of the Chrome Default profile was previously used with headless CDP on localhost to inspect authenticated WhatsApp Web without modifying the original browser profile/session.
- Both Firefox and Chrome were running; neither exposed a normal remote-debugging port in the original session.
- Browser content-script/DOM observation was selected over Android/AT-SPI as the preferred first implementation path.
- Current `whatsapp-watcher` worktree is clean except for the two pre-existing untracked relationship drafts; do not delete, overwrite or commit them blindly.
- `relationship-core.js` is a substantial reusable pure-JS relationship-state core. It already implements: own system-event parsing in English/Italian; explicit Block/Unblock control parsing; header-status classification; outgoing delivery-state classification; peer visibility state; inferred peer block after persistent hidden status + single-check delivery; inferred peer unblock when visibility/delivery recovers; Italian human labels and relative-date formatting.
- `relationship-core.js` currently hardcodes a 5-minute confirmation default for inferred peer block transitions and emits both raw signal events (`peer_visibility_hidden/visible`) and derived inferred events (`peer_block_inferred/peer_unblock_inferred`).
- `relationship-monitor.js` is only a 50-line unfinished/untracked draft. It targets `Carlo Visda`, defines storage keys/state constants, but the current bytes appear syntactically incomplete/malformed around DOM selectors. Treat it as partial prior work to preserve and inspect, not as validated code.
- `whatsapp-watcher` main remains at `b6e3e9f` with no tracked modifications from this chat.
- Safe CDP clone is currently running at 127.0.0.1:9222 with user-data-dir /home/daniele/.cache/whatsapp-cdp-profile.
- relationship-core.js is complete and reusable as semantic reference; relationship-monitor.js is an incomplete 50-line untracked fragment and must remain untouched.

- Current validated source head is 6faa3e8; 0cc2991 added target-chat recovery and 6faa3e8 disabled copied-profile Chrome extensions for stability.
- Enabled user services: whatsapp-exporter-browser.service and whatsapp-exporter.service, installed under ~/.config/systemd/user.
- The browser service uses only the isolated authenticated profile ~/.cache/whatsapp-cdp-profile and localhost CDP; normal Chrome/Firefox sessions are untouched.
- After disabling extensions, a fresh clone start passed direct Runtime.evaluate and used about 142 tasks instead of the prior runaway ~489-task state.
- Controlled watcher restart succeeded with a new PID and archive unchanged at 36 Carlo records / one chat.
- Controlled browser restart succeeded: systemd restarted the dependent watcher; after transient startup errors through 09:01:59 the watcher automatically reopened Carlo. A later snapshot was ok with active_chat=Carlo Visda and 19 rendered records; archive remained 36 records and one chat.
- Current validated source head is ced3b39. Live media scope is one Carlo image with no exposed src/blob, MIME or filename and needs_download=true; SQLite preserves it as metadata_only and no local media file exists.
- No WhatsApp media-download control was clicked and no relationship state was changed for media validation.
- Source commit ced3b39 adds end-to-end synthetic coverage proving metadata_only upgrades to downloaded when a source becomes accessible, writes exactly one local file, and does not redownload on an unchanged rerun; focused tests now pass 12/12.
- Fresh post-restart bounded backfill again stopped automatically (9 steps, 0 inserted/revised, 164 unchanged) with archive fixed at 36 Carlo records.
- At the oldest loaded position, scroll_height remained fixed at 2494 and no semantic control for older/earlier/history/sync/phone loading was exposed; the only matching control was the existing media download element.

## Decisions
- Start from WhatsApp Web, not Android.
- Reuse verified DOM discovery; do not redo broad exploration unless current selectors fail.
- Preserve raw evidence behind derived block/unblock classifications.
- Use a dedicated exporter repo/runtime; do not extend whatsapp-watcher for transcript/media persistence.
- Connect the exporter to the authenticated headless Chrome clone via localhost CDP so the normal Chrome/Firefox sessions remain untouched.
- Manage the isolated Chrome clone and watcher with enabled systemd user units for restart recovery.
- Disable extensions in the copied Chrome profile; they are unnecessary for export and caused a high-process/high-CPU CDP hang after restart.
- Store private archive data under the user data directory, outside source Git; source repo contains only code/tests/docs.
- Dedicated source repo created at /home/daniele/projects/whatsapp-exporter and pushed to private GitHub repo gernalix/whatsapp-exporter.
- Source checkpoint ddfebba implements CDP access, conservative Carlo target gating, SQLite records/revisions/events/media, deterministic dedupe, Markdown rendering, backfill/watch CLI and best-effort media download.
- Focused synthetic tests pass 8/8; Python and JavaScript syntax gates pass.
- Live selector compatibility fix pushed as whatsapp-exporter commit 37ee641: current WhatsApp DOM uses data-testid=conversation-panel-messages and data-testid=conv-msg-* wrappers rather than legacy message-in/message-out classes.
- Two consecutive live Carlo scans after the fix are stable no-ops: seen=8, inserted=0, revised=0, unchanged=8; scroll metadata is valid (bottom top=503, height=384, scroll_height=887).
- Bounded scroll verification reaches top 503 -> 103 -> 0 successfully, but the CDP clone still exposes 8 rendered records and does not load older rows; backfill therefore has not yet expanded history.
- Current source repo `/home/daniele/projects/whatsapp-exporter` is clean on `main` at `9bd5ff3` (`origin/main`), including later commits `059b07b` (system dates/media metadata) and `9bd5ff3` (canonical system-row wrappers).
- Focused validation on current source passes 10/10 unittests plus Python compileall and Node syntax checks.
- Private SQLite currently contains only chat `Carlo Visda`: 36 records total (4 message, 29 system, 3 call), 36 revisions, 32 events, and one `metadata_only` media row; no unrelated chat is persisted.
- Two consecutive live Carlo scans on the authenticated CDP clone are stable no-ops: each `seen=16`, `inserted=0`, `revised=0`, `unchanged=16`, `events=0`, `relationship_events=0`.
- Current live scroll metadata is valid (`top=2559`, `height=384`, `scroll_height=2943`).
- Bounded backfill of 10 effective steps reached stable top and stopped automatically with `inserted=0`, `revised=0`, `unchanged=188`; archive remained at 36 records. This verifies dedupe/reconciliation but does not prove that WhatsApp has exposed all older server history.

## Completed
- Persistent exporter state created and pushed.
- README/protocol and Carlo block-tracking checkpoint rehydrated.
- Existing whatsapp-watcher repo and both untracked relationship drafts preserved without modification.
- Dedicated private source repo implemented and pushed; current validated source is ced3b39.
- Carlo-only selector compatibility, canonical system rows, deterministic dedupe, SQLite revisions/events and human-readable Markdown are implemented.
- Test/syntax gates pass (12/12 tests including runtime recovery and media upgrade/download dedupe); repeated live scans/backfill are duplicate-free.
- Live media preservation is verified as far as currently observable: metadata-only media is retained; accessible-source download/dedupe behavior is verified synthetically without forcing a WhatsApp download.
- Verified current private archive contains only Carlo Visda.
- Deployed enabled user services for the isolated browser clone and watcher.
- Verified controlled watcher restart and controlled browser restart with automatic Carlo recovery and no archive duplication.

## Remaining
Factual own-block/control and peer-inference verification from existing/synthetic evidence, selectable-chat generalization without weakening scope gating, focused DOM tests, usage/limitations documentation, final source validation, and final roadmap checkpoint.

## Blockers
No blocker for incremental export. Older-history completeness is bounded by what WhatsApp Web currently exposes in the authenticated clone: repeated top-scrolls do not load older rows and no read-only older-history control is present. An attempted deeper IndexedDB inventory through the remote runtime was blocked by the remote safety layer, so internal database extraction is not being bypassed. relationship-monitor.js remains unfinished/unvalidated and untouched.

## Evidence
- operations/task-state/CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md
- /home/daniele/projects/whatsapp-watcher remains b6e3e9f with only the preserved untracked relationship drafts.
- gernalix/whatsapp-exporter commits ddfebba, 37ee641, 059b07b, 9bd5ff3, 8a030c9, 0cc2991, 6faa3e8, ced3b39.
- 12/12 unittest PASS; Python compileall PASS; Node syntax PASS for both DOM scripts.
- Fresh bounded live backfill: 9 steps, 0 inserted/revised, 164 unchanged; fixed oldest-loaded scroll boundary and no older-history control.
- Live media: one metadata-only Carlo image with no source; no local file and no forced UI download. Synthetic source-available download/dedupe path PASS.
- systemd user browser/watcher deployment enabled; controlled watcher restart PASS.
- Controlled browser restart PASS after extension isolation: direct CDP eval PASS, automatic Carlo reopening observed after startup recovery.
- SQLite scope after restart/media checks: only Carlo Visda, 36 records, no duplicate growth.

## Acceptance criteria
- Carlo Visda history can be exported incrementally with no duplicate messages on repeat runs.
- Human-readable local history exists without technical IDs in the primary view.
- Relevant media/system events are preserved when observable.
- Own block/unblock is factual; peer block/unblock remains explicitly inferred.
- No unrelated chat data is persisted during Carlo-only validation.
- Runtime survives browser reload/restart sufficiently to resume incremental export.
- Source/tests/checkpoint are pushed; private transcript/media are not committed to public source Git.

## Next action
Verify relationship-event semantics from the existing Carlo archive plus focused synthetic tests: historical own block/unblock must be factual, current control state must not create a transition without a baseline change, and peer block/unblock must remain inferred with raw evidence. Do not change the live block state for testing. Then checkpoint and generalize the CLI/runtime from the Carlo default to explicitly selected chats without persisting any unselected chat.
