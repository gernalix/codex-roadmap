PROMPT_ID: 219746

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Add coherent system light/dark theme support across the current PersonalHub shell and modules, without unrelated UI redesign.

## Requirements
- Follow Android system light/dark mode by default; preserve any existing explicit PH theme preference if one exists at execution time.
- Define reusable theme colors/tokens centrally where the architecture supports it; remove only hardcoded light-only colors that actually break dark mode.
- Cover PH shell plus all current modules/common dialogs/cards/forms present at execution time, including the rebuilt Substances UI and the home auto-export indicator.
- Preserve light-theme appearance/behavior unless proper theming requires a change.
- Ensure Activity recreation caused by theme/configuration changes does not discard important in-progress user state; do not re-fix unrelated lifecycle code already covered by earlier tasks unless a concrete remaining blocker is found.
- Pay attention to system bars, dialogs, text contrast, disabled/error states, input fields, overlays and screens with custom colors.

## Scope / safety
No export work, typography overhaul, navigation refactor, module redesign or general Compose cleanup. Start from PH theme definitions and representative module theme/custom-color files; expand only to surfaces that fail dark-mode verification.

## Acceptance
Build/targeted tests pass. On the project-approved device/emulator switch system light/dark and verify PH home plus representative screens/dialogs from every current module, including People, Timer, Places, Substances, WordPulse and Soldi. Check readability, status/error colors, inputs and no obvious light-only surfaces. Do not perform a general UX audit.

Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, theme mechanism, modules/screens checked, lifecycle issues encountered if any, tests/device checks, commit SHA.
