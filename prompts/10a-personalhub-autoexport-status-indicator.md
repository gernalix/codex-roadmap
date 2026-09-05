PROMPT_ID: 263875

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Add the compact old-MultiTimer-style auto-export health indicator to PersonalHub home without changing export architecture.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabasePreferences.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/HubAutoExport.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`

Use the existing status APIs/state exposed by these files. Open a directly referenced status model only if necessary to render the four required states. Do not inspect WorkManager/sync internals. If a prior task renamed a listed symbol, one targeted symbol search is allowed.

## Known state
PH exposes global auto-export status including configured folder, current/exported generation, last successful export, stale/error state. By this roadmap stage the permanent idle poll should already have been removed/reduced; verify current behavior from the exact files rather than reimplementing it.

## Work
- Add a small tappable `✅` / `❌` status affordance on PH home.
- `✅`: configured and current/no relevant error. `❌`: stale, failed, inaccessible/unconfigured when that state means backup is not currently healthy.
- Tapping opens a compact status dialog/sheet showing at least last successful export time, folder/configuration status, current vs exported generation/stale state and last error when present.
- Provide accessible text/content descriptions; emoji alone is not the semantic label.
- Reuse current home/theme components and status APIs.
- No changes to WorkManager, DatabaseVault export logic, sync, backup/import or Settings architecture.

## Acceptance
Targeted UI/state tests cover healthy, stale, error and unconfigured states; a focused emulator/device check confirms the control/dialog is usable. Do not manufacture destructive failures on real data.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, indicator semantics, details shown, tests/device check, commit SHA.
