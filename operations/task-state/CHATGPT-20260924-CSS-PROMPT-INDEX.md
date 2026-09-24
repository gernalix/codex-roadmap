# Operational task state — CSS prompt-ID search

TASK_ID: CHATGPT-20260924-CSS-PROMPT-INDEX
Status: in_progress
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
- [ ] Verify manual add/remove and persistent suppression at runtime if feasible without altering meaningful user data; otherwise use a disposable test context.
- [ ] Final runtime status/readback and clean checkout verification.
- [ ] Final completion checkpoint.

## Current step
Chrome was gracefully restarted and relaunched explicitly on Wayland with session restoration; service-worker registration is now `0.4.0`. Repeated disposable-page test is PASS for automatic extraction (`583902` detected within ~1.5 s). Next verify manual remove/suppression and manual-only add/remove.

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
Checkpoint readback 2026-09-24: CSS checkout is clean at `149f28478dffd57f75bdf7f883444d95b2dc7262`, matching `origin/main`; daemon reports `0.4.0`; live extension heartbeat reports `0.4.0` with fresh heartbeat.

Source gates:
- Python compile PASS.
- `python -m unittest discover -s tests -v`: 66/66 PASS.
- Manifest JSON validation PASS.
- Node syntax checks for background/content/sidepanel and GNOME companion PASS.
- GNOME schema validation PASS.
- Shell syntax gates PASS.
- GitHub Actions CI run 107 on `6b4f9da`: python PASS, Selenium E2E PASS, overall SUCCESS.

Runtime automatic-scan PASS:
- Graceful Chrome restart + explicit Wayland relaunch succeeded; service-worker registration now records `0.4.0` and extension heartbeat is fresh.
- Reopening `http://127.0.0.1:43891/index.html` caused real content-script scanning to add `583902` automatically within ~1.5 s. The same regex also indexed `583903` from `x583903y`, because only adjacent digits are excluded by the current six-digit-number rule.

Runtime reload evidence:
- Chrome Preferences points CSS ID `mfpomnbkkfklealhaacbnmelpgpggglg` to the correct unpacked path but `service_worker_registration_info.version` remains `0.3.8`.
- Deployed `content.js` and `background.js` hashes exactly match canonical main and contain the scanner/message routes.
- Direct daemon `POST /api/context/prompts/observe` succeeds, narrowing failure to stale browser-side code registration.
- `chrome://restart` invoked from the existing Chrome process did not change the registered service-worker version.
- Session safety backup created at `~/.local/state/chrome-codex-switcher/session-backup-20260924-164432` containing Chrome `Sessions/` and `Preferences`.

Runtime E2E finding:
- Disposable page `http://127.0.0.1:43891/index.html` containing standalone IDs `583901` and `583902` created real CSS context `057a7d84-a62d-49d7-93f1-d0db13834a0e`, proving the content script can reach `context:get`.
- `/api/list` returned `prompt_ids=[]` for that context over 20 polls / >10 seconds, and SQLite had no matching `context_prompt_ids` rows. Automatic scanning is therefore not runtime-PASS yet.

Runtime deployment:
- `install.sh` succeeded once Remote Desktop Commander shell exported `XDG_RUNTIME_DIR=/run/user/1000` and `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`.
- GNOME companion enabled; global search shortcut remains configured.
- `chrome-codex-switcher.service`: enabled + active.
- Deployed extension file version: `0.4.0`.
- After version alignment/reinstall: daemon version `0.4.0`, health `ok=true`.
- Live Chrome extension heartbeat: `version=0.4.0`; reload confirmed.

## Completed
Repository implementation, source tests/CI, Fedora file deployment, daemon restart/health verification, runtime package version alignment, reinstallation from canonical main, and live Chrome extension reload to `0.4.0`.

## Remaining
Exercise real page prompt-ID indexing/search/manual override behavior, verify clean final state, then mark task completed.

## Blockers
None currently. The stale Chrome service-worker registration was resolved by graceful browser SIGTERM followed by a Wayland relaunch with `--restore-last-session --load-extension=...`.

## Acceptance criteria
- [x] Searching any indexed six-digit PROMPT_ID is implemented to surface the associated context.
- [x] Multiple IDs can coexist on one context and one ID may appear on multiple contexts.
- [x] User can manually add an ID.
- [x] User can remove an ID; an auto-detected removed ID stays suppressed on future scans.
- [x] Existing canonical prompt binding behavior remains intact.
- [x] Scanner is debounced/incremental and avoids full-page rescans on every mutation.
- [x] Notes are visibly more prominent than title/meta/buttons in both dashboard surfaces.
- [x] Focused/full source tests and CI, including E2E, pass.
- [x] Source changes and runtime version alignment are on canonical CSS `main`.
- [x] Fedora daemon/files are deployed and daemon runtime is `0.4.0`.
- [x] Live Chrome extension runtime is reloaded to `0.4.0`.
- [ ] Real runtime search/index behavior is verified end-to-end.
- [ ] Final checkout/runtime state is clean and checkpointed.

## Next action
On disposable context `057a7d84-a62d-49d7-93f1-d0db13834a0e`, remove auto-detected `583902`, reopen the page and verify it remains excluded; then add/remove a manual-only ID and confirm deletion. After PASS, clean disposable runtime artifacts and perform final checkout/runtime readback.
