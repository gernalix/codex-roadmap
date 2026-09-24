# Operational task state — CSS prompt-ID search

TASK_ID: CHATGPT-20260924-CSS-PROMPT-INDEX
Status: completed
Updated: 2026-09-24 Europe/Copenhagen

## Objective
Extend `gernalix/chrome-codex-switcher` (CSS) so each persistent Chrome context indexes standalone six-digit PROMPT_ID values visible in the page, exposes them to dashboard search, supports manual add/remove overrides, and makes notes the visually dominant dashboard field.

## Constraints
- Work directly on canonical `main`; no PR unless technically required.
- Preserve existing one-to-one canonical `prompt_bindings` semantics.
- Search associations are many-to-many context metadata and survive tab/browser recreation through persistent `context_id`.
- Manual removal suppresses automatic rediscovery until explicitly re-added.
- Automatically discovered IDs are retained as searchable history if they later disappear from the DOM.
- Scanner is debounced/incremental after the initial full-page scan.
- No unrelated repository/runtime mutation.

## Plan / checklist
- [x] Inspect CSS data model, content script, background bridge, dashboard UI, daemon API and tests.
- [x] Define a separate many-to-many prompt-index contract with automatic/manual/excluded states.
- [x] Add persistent prompt-index storage and migration-safe schema.
- [x] Add daemon methods/API for automatic observations and manual add/remove.
- [x] Add content-script initial full-page scan plus debounced incremental observation.
- [x] Bridge scanner messages through the MV3 background worker.
- [x] Extend side-panel and fallback dashboard search/rendering to indexed PROMPT_IDs.
- [x] Add dashboard controls for manual PROMPT_ID add/remove with persistent suppression semantics.
- [x] Redesign note presentation so notes dominate card hierarchy via position, padding, size, contrast and spacing.
- [x] Add/update focused tests and documentation/version metadata.
- [x] Verify source/test gates and GitHub Actions.
- [x] Record completion evidence.

## Verified facts / implementation
- Canonical `prompt_bindings` remains untouched as the 1:1 prompt↔Chrome/Codex binding.
- New SQLite table `context_prompt_ids` stores per-context many-to-many search associations with `auto_detected`, `manual_added`, and `excluded` state.
- Effective indexed IDs are manual additions plus auto-detected IDs not manually excluded.
- Removing an auto-detected ID records an exclusion; later page scans do not restore it. Manual re-add clears the exclusion.
- Removing a manual-only ID deletes that association.
- `/api/list` now returns `prompt_ids` and `prompt_id_index` alongside the existing canonical `prompt_id`.
- Content scanning uses an initial page-text scan, then a `MutationObserver` over changed text/subtrees with a 450 ms flush debounce; script/style/noscript and the CSS overlay are excluded.
- Side-panel and localhost fallback dashboard both search indexed IDs and provide `+ ID` / `×` controls.
- Notes render before title/metadata, with larger font, stronger contrast, padding, border/background and greater spacing; title/meta are visually subordinated.
- Extension version is `0.4.0`.

## Commits
- `2607fa90c55b964b11b859648bd43c2fc7f76837` — main implementation.
- `b7789319fd1922ff9f6c1a2ef68766cd624011e6` — contract fixes after first full local test run.
- `6b4f9dafb6b4e1977ee56adbe1614658c3d99af5` — explicit fallback dashboard add/remove endpoints; final CSS `main` SHA.

## Evidence
Local Fedora checkout at final SHA `6b4f9dafb6b4e1977ee56adbe1614658c3d99af5`:
- Python compile PASS.
- `python -m unittest discover -s tests -v`: 66/66 PASS.
- Manifest JSON validation PASS.
- Node syntax checks for background/content/sidepanel and GNOME companion PASS.
- GNOME schema validation PASS.
- Shell syntax gates PASS.
- Final marker: `ALL_SOURCE_GATES_PASS`.

GitHub Actions:
- CI run 107, run id `36012065855`, head SHA `6b4f9dafb6b4e1977ee56adbe1614658c3d99af5`.
- `python` job PASS.
- Selenium `e2e` job PASS.
- Overall workflow conclusion: SUCCESS.

## Completed
All requested CSS prompt-ID indexing/search/manual override work and dashboard note prominence changes are implemented and pushed to `main`, with tests and CI green.

## Remaining
None for the requested repository change. Local installed/unpacked extension deployment/reload was intentionally not performed because this task was scoped to `@GitHub`.

## Blockers
None.

## Acceptance criteria
- [x] Searching any indexed six-digit PROMPT_ID surfaces the associated context.
- [x] Multiple IDs can coexist on one context and one ID may appear on multiple contexts.
- [x] User can manually add an ID.
- [x] User can remove an ID; an auto-detected removed ID stays suppressed on future scans.
- [x] Existing canonical prompt binding behavior remains intact.
- [x] Scanner is debounced/incremental and avoids full-page rescans on every mutation.
- [x] Notes are visibly more prominent than title/meta/buttons in both dashboard surfaces.
- [x] Focused/full tests and CI, including E2E, pass.
- [x] Changes are pushed to CSS `main`.

## Next action
None. If runtime deployment is requested later, deploy/reload CSS from final `main` SHA `6b4f9dafb6b4e1977ee56adbe1614658c3d99af5`.
