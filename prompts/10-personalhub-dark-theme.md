PROMPT_ID: 219746

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Add complete dark-theme support to Personal Hub and all current modules using the app's existing UI/theme stack.

## Requirements
- Follow Android system light/dark mode by default; preserve any existing explicit theme preference if PH already has one.
- Define theme-level colors/tokens centrally; do not scatter hardcoded dark colors through screens.
- Cover PH shell/navigation plus every current module and common dialogs/cards/forms, including newly migrated modules present at execution time.
- Ensure readable contrast and no light-only surfaces/text/icons in dark mode.
- Preserve light-theme appearance unless a change is required for proper theming.

## Scope
No unrelated visual redesign, typography overhaul or component refactor.

## Acceptance
Build/tests pass; focused visual verification in both light and dark system modes covers PH home/navigation and representative screens/dialogs from every current module, with no obvious unreadable or light-only surfaces.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, theme mechanism, screens/modules checked, tests, commit SHA.