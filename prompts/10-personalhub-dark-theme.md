PROMPT_ID: 219746

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Complete the remaining small PH home/theme UI work in one pass: add dark-theme support and the old-MultiTimer-style auto-export status indicator.

Known state to preserve: PH already has durable generation-based SAF auto-export, recovery/error status, and the idle-loop fix. Do not redesign or reimplement the export engine.

## Requirements
- Follow Android system light/dark mode by default; preserve any existing explicit theme preference if present.
- Define theme colors/tokens centrally; no scattered hardcoded dark colors.
- Cover PH shell plus every current module/common dialog/card/form, including modules present at execution time.
- Preserve light-theme appearance unless proper theming requires a change.
- On PH home, add the small tappable `✅`/`❌` auto-export status indicator equivalent to old MultiTimer. Reuse/adapt MultiTimer's UI semantics where practical.
- Tapping it shows at least last successful export time and relevant current stale/error/folder state, using PH's existing auto-export status APIs.
- Preserve existing no-idle-loop and durable export behavior.

## Scope
No export architecture work, unrelated visual redesign, typography overhaul, component refactor, backup/import redesign, or unrelated settings work.

## Acceptance
Build/tests pass. Focused light/dark visual verification covers PH home and representative screens/dialogs from every current module. Verify the export indicator reflects current vs stale/error state and its tap details. Do not perform a broader auto-export audit.

Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, theme mechanism, export-indicator behavior, screens/modules checked, targeted tests, commit SHA.