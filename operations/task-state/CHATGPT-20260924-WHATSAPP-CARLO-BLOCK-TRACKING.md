# Operational task state — WhatsApp Carlo block tracking

TASK_ID: CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING
Updated: 2026-09-24 17:56 Europe/Copenhagen

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
- [ ] Identify the active WhatsApp Web browser/tab and safe inspection path.
- [ ] Open/focus the Carlo Visda chat if needed without sending anything.
- [ ] Inventory stable DOM/accessibility signals for contact title, online/last-seen, own blocked/unblocked UI, delivery ticks and profile/avatar evidence.
- [ ] Record which signals are available continuously vs only when chat/profile panes are open.
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
Identify which current browser instance contains WhatsApp Web and establish a safe live inspection mechanism on Wayland.

## Verified facts
- Both Firefox and Google Chrome are currently running on Fedora.
- Neither browser currently exposes a conventional DevTools/Marionette TCP debugging port.
- The Remote Desktop Commander shell does not inherit the graphical display variables automatically.

## Decisions
- Perform live UI discovery before selecting selectors or repository architecture.
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
Use Fedora session/AT-SPI/browser profile inspection to identify the active WhatsApp Web tab and extract a minimal accessibility/DOM snapshot for the Carlo Visda chat.
