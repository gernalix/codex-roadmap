# Operational task state — WhatsApp exporter

TASK_ID: CHATGPT-20260924-WHATSAPP-EXPORTER
Updated: 2026-09-24 17:58 Europe/Copenhagen

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
- [ ] Read operations/task-state/README.md.
- [ ] Read CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md in full.
- [ ] Inspect /home/daniele/projects/whatsapp-watcher and preserve any pre-existing untracked relationship-core.js / relationship-monitor.js work.
- [ ] Reconfirm authenticated WhatsApp Web safe-inspection path and current browser/runtime state.

### Phase 2 — Exporter architecture
- [ ] Decide whether exporter belongs in whatsapp-watcher or a dedicated repo based on scope; prefer a dedicated exporter if transcript/media persistence would overcomplicate the read-receipt extension.
- [ ] Define canonical local storage schema for chats/messages/revisions/media/system events.
- [ ] Define unique identity/deduplication keys and incremental cursor/reconciliation strategy.
- [ ] Define human-readable no-ID view with localized/relative dates.

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
Rehydrate the verified WhatsApp Web discovery and inspect the existing whatsapp-watcher repo plus any untracked relationship-monitor files before choosing whether to extend that repo or create a dedicated exporter.

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

## Decisions
- Start from WhatsApp Web, not Android.
- Reuse verified DOM discovery; do not redo broad exploration unless current selectors fail.
- Preserve raw evidence behind derived block/unblock classifications.
- Prefer a dedicated exporter if transcript/media persistence materially exceeds whatsapp-watcher's narrow read-receipt purpose; otherwise reuse shared DOM utilities without mixing private archive data into source Git.

## Completed
- Persistent exporter state created from prior WhatsApp discovery.
- Existing whatsapp-watcher repo and verified Carlo DOM signals identified.

## Remaining
Architecture decision, source implementation, local storage schema, Carlo-first export, dedupe/reconciliation, tests, deploy, generalization, docs, and final checkpoint.

## Blockers
No confirmed blocker. Must inspect the two untracked whatsapp-watcher relationship files before modifying the repo.

## Evidence
- operations/task-state/CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING.md
- /home/daniele/projects/whatsapp-watcher README/manifest/content.js
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
Read the block-tracking checkpoint and inspect whatsapp-watcher including relationship-core.js and relationship-monitor.js. Then choose the smallest correct exporter architecture and implement Carlo-only incremental export first.
