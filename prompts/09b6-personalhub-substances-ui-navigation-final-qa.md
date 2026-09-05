PROMPT_ID: 833054

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — final phase. Build the coherent user-facing Substances UI/navigation on top of the completed domain phases, then perform focused end-to-end verification on Pixel and TCL.

## Prerequisite
Use MegaVault/`AGENTS.md` and verify narrowly that the preceding Substances phases are present: authoritative mutation commands/stock/archive, correct scheduling/intake/interactions/macros, prescriptions/notifications, bounded History, and global DB import/export integration. If a prerequisite is materially absent, stop `BLOCKED`; do not rebuild backend phases in this task.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## UX target
Create a clear responsive module, adapting to the current design system rather than blindly preserving legacy layout.

Home should make the current dosing state immediately understandable, with coherent sections equivalent to:
- Da prendere
- Più tardi
- Bloccate
- Assunte
- Al bisogno

A `TAKEN` substance must not disappear merely because it was taken. A whole card must not accidentally record an intake when the expected action is opening details.

Provide a focused Substance detail screen exposing the completed capabilities:
- current state / next relevant dose;
- explicit Record intake action and domain-result feedback;
- stock + Set stock + adjustment/history access;
- intake History;
- prescription/refill;
- interactions;
- edit;
- archive/restore navigation where appropriate.

Complete the minimum UI for macro and interaction CRUD already supported by domain code; surface partial/per-item macro outcomes clearly.

## UI cleanup in scope
Fix only current Substances usability defects that block/coarsen these flows, including where still present:
- ambiguous global FAB/action semantics;
- accidental shared search state between unrelated tabs;
- inflexible fixed grid on narrow/wide devices;
- overly dense top bar/tabs;
- undersized touch targets;
- literal `...`, `+`, `!` used where proper icons/semantics are expected;
- permanent import/export banner when a normal settings/action surface is more appropriate;
- missing loading/error/empty-state feedback;
- dialogs closing before writes actually succeed;
- incomplete Italian labels on touched flows.

Restore at least the last useful Substances section/screen when leaving and reopening the module, using the existing PH navigation/state pattern. The displayed version, if any, must use the real PersonalHub version rather than a Substances hardcode.

Do not redesign other PH modules or build a new design system.

## Tests / device verification
Use targeted UI/state tests for critical navigation and command-result handling. Then build the final main PersonalHub debug APK under the existing project rules and update/install the real PersonalHub app safely on both approved devices:
- Pixel
- TCL

Focused checks on both devices:
- module opens and layout is usable/responsive;
- create/edit substance without history loss;
- intake + undo/delete representative flow;
- insufficient-stock and Set-stock feedback;
- macro result and interaction BLOCK;
- archive/restore;
- prescription/refill surface;
- History/filter basic use;
- navigation/screen restore;
- import UI reaches the real safe global path without destructive live-data import;
- no obvious truncation/touch-target/jank issue on the touched surfaces.

Do not run destructive DB-import tests on live user data. Do not broaden into a whole-app UX audit.

## Resource discipline
This task is presentation/integration only. Do not reopen solved backend architecture unless a failing acceptance check proves a regression. Targeted tests, one final build/install pass, then stop.

Final output only: `PROMPT_ID`, `RESULT`, UI/navigation summary, backend regressions if any, tests, Pixel, TCL, version, commit SHA.
