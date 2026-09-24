# Operational task state — WhatsApp Carlo block tracking

TASK_ID: CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING
Updated: 2026-09-24 18:26 Europe/Copenhagen

## Objective
Detect and archive block/unblock state transitions for the WhatsApp Web chat with Carlo Visda, beginning with live DOM/accessibility discovery on Fedora and then implementing the smallest robust detector.

## Constraints
- Use Remote Desktop Commander for Fedora/browser discovery and local runtime work.
- Do not assume WhatsApp DOM selectors; verify live structure first.
- Store raw UI/accessibility evidence needed for future reclassification, but do not persist unrelated private chat contents.
- Own block/unblock may be treated as factual only when explicit WhatsApp UI/state proves it.
- Peer block/unblock must remain inferred; disappearance/reappearance of last-seen alone is not proof.
- Prefer multiple independent signals for peer-block confidence when observable.
- Preserve user browser session; do not log out, clear storage, send messages, or change block state just for testing without explicit need.
- Persist important results with commit + push checkpoints.
- Avoid touching unrelated dirty worktrees or current PersonalHub recovery state.

## Plan / checklist
### Phase 1 — Live discovery
- [x] Create persistent task state.
- [x] Identify the active WhatsApp Web browser/tab and safe inspection path.
- [x] Open/focus the Carlo Visda chat if needed without sending anything.
- [x] Inventory initial stable DOM signals for Carlo title, current own block/unblock UI, own historical block/unblock system messages and the conversation composer; last-seen/online signal still requires transition observation because none is currently visible.
- [x] Record initial availability: chat-list title is visible in list; current own block state is explicit in Contact info (li-block / Block Carlo Visda vs future Unblock); historical own block/unblock events are system-message rows; peer status is only observable when WhatsApp renders online/last-seen in the conversation header.
- [ ] Determine whether Chrome/Firefox extension content-script access is the least-fragile implementation path.

### Phase 2 — Minimal detector
- [ ] Choose the narrowest repo/runtime architecture based on live evidence.
- [ ] Capture snapshots and deduplicated transitions for the Carlo chat only.
- [ ] Persist raw evidence + derived event type/confidence/timestamp.
- [ ] Detect own block/unblock as factual when explicit UI state changes.
- [ ] Infer peer block/unblock only from verified signal combinations; never label certain.
- [ ] Add a human-readable local timeline.

### Phase 3 — Validation/deployment
- [ ] Add focused tests with recorded/synthetic DOM fixtures.
- [ ] Deploy in the authenticated browser/runtime without disturbing normal use.
- [ ] Verify startup/reload resilience and deduplication.
- [ ] Verify no unrelated chat text is persisted.
- [ ] Commit/push code and final roadmap checkpoint.

## Current step
Choose the narrowest implementation architecture based on the verified live DOM: a dedicated browser-side observer that watches only the Carlo chat/contact-info signals, writes deduplicated raw snapshots/events locally, and does not persist unrelated chat contents.

## Verified facts
- Chrome Default profile contains a live WhatsApp IndexedDB (~40 MB). A read-only temporary profile copy was launched headless with CDP on localhost; original Chrome profile/session was not modified.\n- The temporary copy is authenticated and contains the chat Carlo Visda. The chat was opened through a real CDP mouse event without sending content.\n- Current chat DOM exposes conversation-panel-wrapper, conversation-info-header and conversation-compose-box-input; composer aria-label is Type a message to Carlo Visda.\n- Contact info exposes data-testid=li-block with aria-label Block Carlo Visda, proving the current own-block state is unblocked. The same control can be watched for a future Unblock state.\n- The rendered conversation contains explicit system-message nodes for historical own transitions: You blocked this person and You unblocked this person.\n- The header currently shows Carlo's name but no online/last-seen string. Therefore no peer-block inference is made from the current snapshot; peer inference must wait for a verified visibility transition.\n- Both Firefox and Google Chrome are currently running on Fedora.
- Neither browser currently exposes a conventional DevTools/Marionette TCP debugging port.
- The Remote Desktop Commander shell does not inherit the graphical display variables automatically.

## Decisions
- Use a browser content-script/observer rather than AT-SPI for the detector: CDP verified that WhatsApp DOM contains stable semantic hooks (data-testid, aria-labels) while AT-SPI exposure is incomplete.\n- Current own-block state should be derived primarily from the Contact info control (li-block plus aria-label Block… / Unblock…); historical own block/unblock may additionally be harvested from system-message rows.\n- Peer-block/unblock remains inferred from header visibility transitions and optional corroborating delivery/profile signals; no event is created from a single static absence.\n- Perform live UI discovery before selecting selectors or repository architecture.
- Prefer browser-level DOM/accessibility observation over Android UI automation for the first implementation.

## Completed
- Persistent task state initialized.
- Browser-process inventory completed.

## Remaining
Live WhatsApp tab discovery, DOM/accessibility inventory, architecture selection, implementation, tests, deploy and runtime verification.

## Blockers
No confirmed blocker yet. Need a safe inspection path into the already-running browser session without restarting or invalidating it.

## Evidence
- Fedora browser process inventory at task start: active Firefox and Chrome processes; no listeners on common browser-debug ports.

## Acceptance criteria
- Carlo Visda WhatsApp Web state can be observed without sending/changing chat content.
- Own block/unblock transitions are stored only when explicit evidence exists.
- Peer block/unblock transitions are clearly marked inferred and backed by raw observed signals.
- Duplicate observations do not produce duplicate events.
- Runtime is resilient and minimally invasive to normal WhatsApp use.
- Code/tests/checkpoint are pushed; no unrelated private chat contents are stored.

## Next action
Locate any existing WhatsApp-related repo/runtime. If none fits, create the smallest dedicated detector repo/runtime, implement Carlo-only DOM observation plus local SQLite/event dedupe, test it against synthetic fixtures and the live CDP snapshot, then deploy without changing WhatsApp state.
