PROMPT_ID: 263875

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Add the compact old-MultiTimer-style auto-export health indicator to PersonalHub home without changing export architecture.

## Known state
PH exposes global auto-export status including configured folder, current/exported generation, last successful export, stale/error state. Use the current APIs; by this roadmap stage the permanent idle poll should already have been removed/reduced, but verify current behavior rather than reimplementing it.

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
