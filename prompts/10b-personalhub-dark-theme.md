PROMPT_ID: 219746

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Add coherent system light/dark theme support across the current PersonalHub shell and modules, without unrelated UI redesign.

## Exact starting files — verified on PersonalHub/main
Read these theme/UI entrypoints in one grouped pass first:
- `app/src/main/java/com/gernalix/personalhub/ui/theme/Theme.kt`
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/theme/LuoghiTheme.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/theme/Theme.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/ui/WordPulseTheme.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/ui/WordPulseScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/AppRoot.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/ui/app/SuperContactsApp.kt`
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt`

From these files, perform at most one targeted search **inside the affected module only** for hardcoded light-only colors/theme definitions that are actually referenced by a failing dark-mode surface. Do not scan all Kotlin/XML files pre-emptively. If a prior task renamed a listed theme/entrypoint, resolve it with one targeted symbol search.

## Requirements
- Follow Android system light/dark mode by default; preserve any existing explicit PH theme preference if one exists at execution time.
- Define reusable theme colors/tokens centrally where the architecture supports it; remove only hardcoded light-only colors that actually break dark mode.
- Cover PH shell plus all current modules/common dialogs/cards/forms present at execution time, including rebuilt Substances UI and home auto-export indicator.
- Preserve light-theme appearance/behavior unless proper theming requires a change.
- Ensure Activity recreation caused by theme/configuration changes does not discard important in-progress user state; do not re-fix unrelated lifecycle code already covered by earlier tasks unless a concrete remaining blocker is found.
- Pay attention to system bars, dialogs, text contrast, disabled/error states, input fields, overlays and screens with custom colors.

## Scope / safety
No export work, typography overhaul, navigation refactor, module redesign or general Compose cleanup. Expand from the exact starting entrypoints only to a concrete surface that fails dark-mode verification.

## Acceptance
Build/targeted tests pass. On the project-approved device/emulator switch system light/dark and verify PH home plus representative screens/dialogs from every current module, including People, Timer, Places, Substances, WordPulse and Soldi. Check readability, status/error colors, inputs and no obvious light-only surfaces. Do not perform a general UX audit.

Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, theme mechanism, modules/screens checked, lifecycle issues encountered if any, tests/device checks, commit SHA.
