PROMPT_ID: 833054

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 5/final. Build the coherent user-facing Substances UI/navigation on top of the completed domain phases, then perform focused end-to-end verification on Pixel and TCL.

## Prerequisite
Use MegaVault/`AGENTS.md` and verify narrowly that the preceding Substances phases are present: authoritative mutation commands/stock/archive/name uniqueness, correct scheduling/intake/interactions/countdowns/notifications, rebuilt prescriptions with People/Soldi links, bounded editable History, and global DB import/export integration. If a prerequisite is materially absent, stop `BLOCKED`; do not rebuild backend phases in this task.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/MainActivity.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/theme/Color.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/theme/Theme.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/theme/Type.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/capsules/importexport/SostanzeImportExportCapsule.kt`
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`

Prior phases may have introduced new command/schedule/prescription/history files. Resolve only the exact types imported by `SostanzeViewModel`/`SostanzeApp`; do not scan `feature/sostanze`. Backend files should be read only to consume their public/domain result contracts, not reopened for redesign. If a listed symbol was renamed, one targeted search is allowed.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## UX target
Create a clear responsive module, adapting to the current design system rather than blindly preserving legacy layout.

### Home buttons / intake state
- Tapping a substance button to record a successful intake must never make that button disappear for the rest of the day.
- After the tap, keep the same button/card visible and show only the next recommended intake time, when one exists, as small secondary text inside it.
- Interaction windows must not make any Home substance button disappear or become disabled. A button affected by BLOCK remains tappable; tapping it shows the authoritative blocked result instead of silently disabling it.
- Show active interaction countdowns prominently on Home, each with the name of the substance/button that started it and the remaining time. When a countdown expires, the phase-2 notification fires once.
- Do not duplicate a substance button when a same-name substance/prescription already exists.

Home may group states only if these rules remain true; do not use grouping as a reason to hide taken/blocked buttons.

### Detail + completed capabilities
Provide a focused Substance detail screen exposing:
- current state / next relevant dose;
- explicit Record intake action and domain-result feedback;
- stock + Set stock + adjustment/history access;
- intake History;
- prescription/refill history;
- interactions;
- edit;
- archive/restore navigation where appropriate.

The rebuilt Prescriptions tab must expose the phase-3 nine-field behavior, People doctor autocomplete, Soldi cost picker and read-mode cost exactly through its completed contracts.

Complete the minimum UI for macro and interaction CRUD already supported by domain code; surface partial/per-item macro outcomes clearly. Editing an interaction and pressing OK must wait for a successful write and then show the newly saved values on reopen.

## Contextual `+` FAB
The `+` FAB must do the most logical create action for the currently selected tab and reuse existing canonical data rather than create duplicates:
- Home/substances → new substance;
- History → new/manual intake-history entry through the authoritative command;
- Interactions → new interaction;
- Prescriptions → new prescription using existing-name autosuggestion/reuse;
- if Macros has its own tab/surface with the same FAB, it creates a new macro.
Do not keep one global FAB action that means the wrong thing on another tab.

## UI cleanup in scope
Fix only current Substances usability defects that block/coarsen these flows, including where still present:
- accidental shared search state between unrelated tabs;
- inflexible fixed grid on narrow/wide devices;
- overly dense top bar/tabs;
- undersized touch targets;
- literal `...`, `+`, `!` used where proper icons/semantics are expected, except the intended FAB affordance itself;
- permanent import/export banner when a normal settings/action surface is more appropriate;
- missing loading/error/empty-state feedback;
- dialogs closing before writes actually succeed;
- incomplete Italian labels on touched flows.

Every History row must visibly retain its phase-4 pencil and trash actions.

Restore at least the last useful Substances section/screen when leaving and reopening the module, using the existing PH navigation/state pattern. The displayed version, if any, must use the real PersonalHub version rather than a Substances hardcode.

Do not redesign other PH modules or build a new design system.

## Tests / device verification
Use targeted UI/state tests for critical navigation and command-result handling. Then build the final main PersonalHub debug APK under the existing project rules and update/install the real PersonalHub app safely on both approved devices:
- Pixel
- TCL

Focused checks on both devices:
- module opens and layout is usable/responsive;
- create/edit substance without history loss and duplicate-name creation is rejected;
- successful intake keeps button visible and shows next recommended time in small text;
- interaction BLOCK keeps buttons visible/tappable, shows blocked feedback, starts labeled countdown when appropriate and expiry notification fires once;
- edit the same interaction twice and confirm latest values persist;
- intake + undo/delete representative flow keeps stock and prescription remaining doses coherent;
- insufficient-stock and Set-stock feedback;
- macro result and interaction BLOCK;
- archive/restore;
- multiple same-name prescriptions coexist under one substance button; prescription prefill/People/Soldi surfaces work;
- History pencil/delete basic flow;
- contextual FAB action matches the active tab and creates no duplicate canonical entity;
- navigation/screen restore;
- import UI reaches the real safe global path without destructive live-data import;
- no obvious truncation/touch-target/jank issue on the touched surfaces.

Do not run destructive DB-import tests on live user data. Do not broaden into a whole-app UX audit.

## Resource discipline
This task is presentation/integration only. Use the exact UI/theme entrypoints and only the public backend contracts they import. Do not reopen solved backend architecture unless a failing acceptance check proves a regression. Targeted tests, one final build/install pass, then stop.

Final output only: `PROMPT_ID`, `RESULT`, UI/navigation summary, home button/countdown behavior, prescriptions/History/FAB checks, backend regressions if any, tests, Pixel, TCL, version, commit SHA.
