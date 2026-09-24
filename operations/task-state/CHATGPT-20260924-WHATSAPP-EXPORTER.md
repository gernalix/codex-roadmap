# Operational task state — WhatsApp exporter

TASK_ID: CHATGPT-20260924-WHATSAPP-EXPORTER
Updated: 2026-09-24 19:13 Europe/Copenhagen

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
- [ ] Export the Carlo Visda chat incrementally without duplicating previously saved messages.
- [ ] Preserve sender name, timestamps, text, reply relation, media metadata/files when accessible, edited/deleted/system messages, calls if WhatsApp exposes them.
- [ ] Capture own block/unblock system messages/state and peer-block inference evidence.
- [ ] Verify re-run is a no-op for unchanged history.
- [ ] Avoid exporting unrelated chats during Carlo-only validation.

### Phase 4 — Generalize
- [ ] Generalize from Carlo to selectable WhatsApp chats without weakening privacy/scope.
- [ ] Add focused synthetic/recorded DOM tests.
- [ ] Deploy runtime/extension safely into authenticated browser.
- [ ] Verify restart/reload resilience and incremental recovery.
- [ ] Document usage and limitations.
- [ ] Commit/push source and final roadmap checkpoint.

## Current step
Run the first Carlo-only live scan against the authenticated CDP clone, verify a second unchanged scan is duplicate-free, then perform bounded upward backfill and validate local archive/media behavior before deployment.

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
- Safe CDP clone is currently running at 127.0.0.1:9222 with user-data-dir /home/daniele/.cache/whatsapp-cdp-profile.
- relationship-core.js is complete and reusable as semantic reference; relationship-monitor.js is an incomplete 50-line untracked fragment and must remain untouched.

## Decisions
- Start from WhatsApp Web, not Android.
- Reuse verified DOM discovery; do not redo broad exploration unless current selectors fail.
- Preserve raw evidence behind derived block/unblock classifications.
- Use a dedicated exporter repo/runtime; do not extend whatsapp-watcher for transcript/media persistence.
- Connect the exporter to the authenticated headless Chrome clone via localhost CDP so the normal Chrome/Firefox sessions remain untouched.
- Store private archive data under the user data directory, outside source Git; source repo contains only code/tests/docs.
- Dedicated source repo created at /home/daniele/projects/whatsapp-exporter and pushed to private GitHub repo gernalix/whatsapp-exporter.
- Source checkpoint ddfebba implements CDP access, conservative Carlo target gating, SQLite records/revisions/events/media, deterministic dedupe, Markdown rendering, backfill/watch CLI and best-effort media download.
- Focused synthetic tests pass 8/8; Python and JavaScript syntax gates pass.

## Completed
- Persistent exporter state created from prior WhatsApp discovery.
- Existing whatsapp-watcher repo and verified Carlo DOM signals identified.
- Rehydration complete; watcher untracked files preserved.
- Dedicated CDP exporter architecture selected.
- Exporter core implemented and pushed at ddfebba; synthetic dedupe/relationship tests PASS 8/8.

## Remaining
Live Carlo validation/backfill, media verification, runtime deployment/restart resilience, generalization, docs, and final checkpoint.

## Blockers
No confirmed blocker.

## Evidence
- operations/task-state/CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md
- /home/daniele/projects/whatsapp-watcher README/manifest/content.js
- gernalix/whatsapp-exporter commit ddfebba; 8/8 unittest PASS plus py_compile/node --check PASS
- Prior live CDP discovery recorded in the block-tracking checkpoint.

## Acceptance criteria
- Carlo Visda history can be exported incrementally with no duplicate messages on repeat runs.
- Human-readable local history exists without technical IDs in the primary view.
- Relevant media/system events are preserved when observable.
- Own block/unblock is factual; peer block/unblock remains explicitly inferred.
- No unrelated chat data is persisted during Carlo-only validation.
- Runtime survives browser reload/restart sufficiently to resume incremental export.
- Source/tests/checkpoint are pushed; private transcript/media are not committed to public source Git.

## Next action
Run one live Carlo-only scan via 127.0.0.1:9222, inspect only counts/paths and parser diagnostics, repeat unchanged scan to prove no duplicate insertion, then start bounded backfill if the target gate and scroll container are valid.
