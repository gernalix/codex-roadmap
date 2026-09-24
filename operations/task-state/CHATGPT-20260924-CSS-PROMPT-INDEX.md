# Operational task state — CSS prompt-ID search

TASK_ID: CHATGPT-20260924-CSS-PROMPT-INDEX
Status: completed
Updated: 2026-09-24 Europe/Copenhagen

## Objective
Extend `gernalix/chrome-codex-switcher` (CSS) so each persistent Chrome context indexes standalone six-digit PROMPT_ID values visible in the page, exposes them to dashboard search, supports manual add/remove overrides, makes notes the visually dominant dashboard field, and deploy/verify the finished feature on the user's Fedora Chrome runtime.

## Constraints
- Work directly on canonical `main`; no PR unless technically required.
- Preserve existing one-to-one canonical `prompt_bindings` semantics.
- Search associations are many-to-many context metadata and survive tab/browser recreation through persistent `context_id`.
- Manual removal suppresses automatic rediscovery until explicitly re-added.
- Automatically discovered IDs are retained as searchable history if they later disappear from the DOM.
- Scanner is debounced/incremental after the initial full-page scan.
- Follow the repository single-writer guardrail; do not bypass protected `main`.
- Preserve the user's existing Chrome tabs/session while reloading the unpacked extension.
- No unrelated repository/runtime mutation.
- Checkpoint via commit+push after significant runtime/deployment results, fixes, and before risky operations.

## Plan / checklist
### Source implementation
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

### Fedora runtime deployment
- [x] Pull deployed Fedora checkout to the implemented source state.
- [x] Run `install.sh` with the user-session DBus environment explicitly supplied to Remote Desktop Commander.
- [x] Verify systemd daemon enabled+active and localhost health OK.
- [x] Verify deployed extension files report version `0.4.0`.
- [x] Detect/fix package-host version drift (`host/__init__.py` and `pyproject.toml` were still `0.3.8`).
- [x] Respect the local single-writer hook: direct commit to protected `main` was rejected before ref mutation.
- [x] Verify the local writer/reconciler absorbed the version alignment into canonical `origin/main`.
- [x] Reinstall from canonical current main and verify daemon runtime reports `0.4.0`.
- [x] Reload the already-loaded unpacked Chrome extension without losing the existing browser session.
- [x] Verify Chrome extension heartbeat advances from `0.3.8` to `0.4.0`.
- [x] Perform an end-to-end runtime prompt-ID indexing/search check on a real Chrome tab/context: after full extension registration reload, `583902` was automatically indexed from the disposable page.
- [x] Verify manual add/remove and persistent suppression at runtime on disposable context: auto-detected `583902` remained excluded after rescan; manual-only `583904` was added then fully deleted.
- [x] Final runtime status/readback and clean checkout verification.
- [x] Final completion checkpoint.

## Current step

Completed. Source implementation, Fedora deployment, true Chrome extension reload, real-browser functional acceptance, cleanup and final health/readback gates all PASS.

## Verified facts / implementation
- Canonical `prompt_bindings` remains untouched as the 1:1 prompt↔Chrome/Codex binding.
- New SQLite table `context_prompt_ids` stores per-context many-to-many search associations with `auto_detected`, `manual_added`, and `excluded` state.
- Effective indexed IDs are manual additions plus auto-detected IDs not manually excluded.
- Removing an auto-detected ID records an exclusion; later page scans do not restore it. Manual re-add clears the exclusion.
- Removing a manual-only ID deletes that association.
- `/api/list` returns `prompt_ids` and `prompt_id_index` alongside the existing canonical `prompt_id`.
- Content scanning uses an initial page-text scan, then a `MutationObserver` over changed text/subtrees with a 450 ms flush debounce; script/style/noscript and the CSS overlay are excluded.
- Side-panel and localhost fallback dashboard both search indexed IDs and provide `+ ID` / `×` controls.
- Notes render before title/metadata, with larger font, stronger contrast, padding, border/background and greater spacing; title/meta are visually subordinated.
- Extension manifest version is `0.4.0`.
- Fedora install path `~/.local/share/chrome-codex-switcher/extension/manifest.json` reports `0.4.0`.
- Systemd daemon is enabled+active and health is OK after deployment.
- First runtime deployment exposed version drift: daemon package reported `0.3.8` because `host/chrome_codex_switcher/__init__.py` and `pyproject.toml` were still `0.3.8`.
- The version alignment was locally edited, tested (66/66 PASS), then a direct commit attempt was blocked by the expected single-writer reference-transaction hook.
- The canonical local Git writer subsequently reconciled the version change into `origin/main`; current Fedora checkout/origin main is `149f28478dffd57f75bdf7f883444d95b2dc7262`, with both host and pyproject at `0.4.0`.
- Reinstall from current canonical main now yields daemon runtime version `0.4.0`.
- Live Chrome extension heartbeat now reports `0.4.0` with a fresh `seen_at`, confirming the unpacked extension was reloaded successfully without losing the browser session.

## Commits
- `2607fa90c55b964b11b859648bd43c2fc7f76837` — main implementation.
- `b7789319fd1922ff9f6c1a2ef68766cd624011e6` — contract fixes after first full local test run.
- `6b4f9dafb6b4e1977ee56adbe1614658c3d99af5` — explicit fallback dashboard add/remove endpoints.
- `149f28478dffd57f75bdf7f883444d95b2dc7262` — current canonical CSS main after local writer reconciliation, including runtime version alignment.

## Evidence

Source verification:
- Final Fedora checkout: `149f28478dffd57f75bdf7f883444d95b2dc7262`.
- `HEAD == origin/main`; working tree clean.
- Python compile PASS.
- `python -m unittest discover -s tests -q`: 66/66 PASS.
- Manifest JSON and Chrome extension JS syntax PASS.
- `git diff --check` PASS.
- Deployed `extension/` and `host/` match the canonical checkout byte-for-byte (excluding Python `__pycache__`).

GitHub Actions:
- CI run #109, run id `36012778807`, head `149f28478dffd57f75bdf7f883444d95b2dc7262`.
- Overall conclusion: SUCCESS.
- Earlier implementation CI #107 also passed both Python and Selenium E2E jobs.

Runtime deployment/readback:
- `chrome-codex-switcher.service`: enabled + active.
- Daemon health: `ok=true`, version `0.4.0`.
- Live extension heartbeat: version `0.4.0`.
- Chrome Preferences service-worker registration: version `0.4.0`.
- Browser session survived guarded restart; 12 top-level Chrome frames were present after restore, matching the pre-restart count.
- The stale `0.3.8` service worker was resolved by a temporary URL-gated extension-page call to `chrome.runtime.reload()`; the temporary `sidepanel.js` patch was restored and byte-compared equal to canonical source.

Real-browser functional acceptance:
- Automatic scan PASS on disposable `verify.html`: context `61172d07-39ca-49d1-b4f1-e0da2207585f` automatically indexed `827365` and `918274`.
- Manual add PASS: `736455` became `manual_added=1, excluded=0`.
- Manual remove PASS: manual-only `736455` was removed while automatic IDs remained.
- Persistent suppression PASS on disposable context `b0c6c582-5d72-4357-b0e0-4a62d3abe3f3`: auto ID `554433` changed to `auto_detected=1, manual_added=0, excluded=1`; after the same tab reloaded and re-observed the ID, `updated_at` advanced from `1790261518.95922` to `1790261535.47834` while effective-search count remained `0`.
- Live non-test contexts (including Workflowy/Fedora pages) are also automatically receiving visible six-digit IDs.

Cleanup/integrity:
- Targeted extension-page cleanup closed 3 localhost test tabs.
- 5 disposable localhost contexts and 6 disposable prompt-index rows were removed.
- Zero orphan prompt-index rows remain.
- SQLite `PRAGMA quick_check` = `ok`; foreign-key check clean.
- Temporary HTTP server stopped; zero contexts remain for `http://127.0.0.1:8766/%`.
- Temporary test directory, reload patches, logs and Chrome-session rollback backup were removed after successful acceptance.

## Completed

All requested work is complete:
- CSS source implementation and dashboard note prominence changes are on canonical `main`.
- Runtime version alignment is on canonical `main`.
- Fedora daemon/extension deployment is current and healthy.
- Chrome's live unpacked extension and service worker are both truly loaded at `0.4.0`.
- Real-browser automatic scan, manual add/remove and persistent exclusion behavior were verified.
- Disposable tabs, contexts, test server/files, temporary patches/logs and rollback backup were cleaned up.
- Final local gates and GitHub Actions are green.

## Remaining

None.

## Blockers

None.

## Acceptance criteria

- [x] Searching any indexed six-digit PROMPT_ID surfaces the associated context.
- [x] Multiple IDs can coexist on one context and one ID may appear on multiple contexts.
- [x] User can manually add an ID.
- [x] User can remove an ID; an auto-detected removed ID stays suppressed on future scans/reloads.
- [x] Existing canonical prompt binding behavior remains intact.
- [x] Scanner is debounced/incremental and avoids full-page rescans on every mutation.
- [x] Notes are visibly more prominent than title/meta/buttons in both dashboard surfaces.
- [x] Focused/full source tests and CI, including E2E, pass.
- [x] Source changes and runtime version alignment are on canonical CSS `main`.
- [x] Fedora daemon/files are deployed and daemon runtime is `0.4.0`.
- [x] Live Chrome extension runtime and service worker are reloaded to `0.4.0`.
- [x] Real runtime automatic indexing, manual overrides and suppression behavior are verified end-to-end.
- [x] Test artifacts/contexts/tabs are removed.
- [x] Final checkout/runtime state is clean and checkpointed.

## Next action

None. Task complete. Future CSS work should start from canonical `gernalix/chrome-codex-switcher` main at or after `149f28478dffd57f75bdf7f883444d95b2dc7262` and this state file can be used as the runtime acceptance record.
