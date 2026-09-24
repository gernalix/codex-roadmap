# Operational task state — CSS prompt-ID search

TASK_ID: CHATGPT-20260924-CSS-PROMPT-INDEX
Updated: 2026-09-24 Europe/Copenhagen

## Objective
Extend `gernalix/chrome-codex-switcher` (CSS) so each persistent Chrome context can index all standalone six-digit PROMPT_ID values visible in the page, expose them to dashboard search, allow manual add/remove overrides, and make notes the visually dominant dashboard field.

## Constraints
- Work directly on canonical `main`; no PR unless technically required.
- Do not change the existing one-to-one canonical `prompt_bindings` semantics.
- New search associations are many-to-many context metadata and must survive tab/browser recreation through persistent `context_id`.
- Manual removal must suppress automatic rediscovery until explicitly re-added.
- Automatically discovered IDs are historical/search metadata: later DOM disappearance must not silently erase them.
- Keep scanning bounded/debounced; do not repeatedly rescan the whole DOM on every mutation.
- No PersonalHub or other unrelated repository/runtime mutation.

## Plan / checklist
- [x] Inspect current CSS data model, content script, background bridge, dashboard UI, daemon API and tests.
- [x] Define a separate many-to-many prompt-index contract with automatic/manual/excluded states.
- [ ] Add persistent prompt-index storage and migration-safe schema.
- [ ] Add daemon methods/API for automatic observations and manual add/remove.
- [ ] Add content-script initial scan plus bounded debounced incremental observation.
- [ ] Bridge scanner messages through the MV3 background worker.
- [ ] Extend side-panel and fallback dashboard search/rendering to indexed PROMPT_IDs.
- [ ] Add dashboard controls for manual PROMPT_ID add/remove with persistent suppression semantics.
- [ ] Redesign note presentation so notes dominate card hierarchy via position, padding, size, contrast and spacing.
- [ ] Add/update focused tests and documentation/version metadata if required.
- [ ] Verify source/test gates and read back final main commit.
- [ ] Record completion evidence and final Next action.

## Current step
Implement storage/API first, then wire the extension scanner and dashboard UI against that stable contract.

## Verified facts
- `prompt_bindings.context_id` is UNIQUE and models the canonical one-to-one prompt↔Chrome/Codex binding, so it cannot represent page-level many-to-many search metadata.
- Dashboard search already indexes the canonical `item.prompt_id`, titles and notes; extending it to `prompt_ids` is localized.
- CSS already injects `content.js` on HTTP/HTTPS pages and has a persistent SQLite daemon keyed by `context_id`.
- The daemon exposes both the extension side-panel data path (`/api/list`) and a fallback `/ui/search` dashboard.

## Decisions
- Store prompt-index associations separately from `prompt_bindings`.
- Effective searchable IDs are manual additions plus automatically observed IDs that are not manually excluded.
- Removing an automatically observed ID writes an exclusion instead of allowing immediate re-detection.
- Automatic observations are additive/history-preserving; DOM disappearance alone does not delete them.

## Completed
Architecture inspection and data/override contract.

## Remaining
Implementation, focused tests, main commit, verification and completion checkpoint.

## Blockers
None.

## Evidence
Current CSS main files inspected: `extension/content.js`, `extension/background.js`, `extension/sidepanel.js`, `extension/sidepanel.css`, `host/chrome_codex_switcher/store.py`, `host/chrome_codex_switcher/daemon.py`, `tests/test_core.py`.

## Acceptance criteria
- Searching any indexed six-digit PROMPT_ID surfaces the associated context.
- Multiple IDs can coexist on one context and one ID may appear on multiple contexts.
- User can manually add an ID.
- User can remove an ID; an auto-detected removed ID stays suppressed on future scans.
- Existing canonical prompt binding behavior remains intact.
- Scanner is debounced/bounded and avoids full-page rescans on every mutation.
- Notes are visibly more prominent than title/meta/buttons in both dashboard surfaces.
- Focused tests pass and changes are pushed to CSS `main`.

## Next action
Implement the separate SQLite prompt-index model and daemon API, then checkpoint before wiring browser scanning/UI.
