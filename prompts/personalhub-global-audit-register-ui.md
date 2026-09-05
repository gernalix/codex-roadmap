PROMPT_ID: 401716

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Global activity register — phase 3. Expose the completed semantic audit + safe-undo system as a human-readable `Registro attività` module/card with scalable history, grouping, filtering and undo affordances.

## Prerequisite
Use MegaVault/`AGENTS.md` and verify narrowly that phases 1–2 provide the canonical paged audit read model, semantic labels/descriptions, grouping and current reversibility/conflict status with safe undo commands. If materially absent, stop `BLOCKED`; do not rebuild backend phases.

## Exact starting files — verified/current boundaries
Read these existing app-shell files in one grouped pass:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/settings/HubSettings.kt`
- `app/src/main/AndroidManifest.xml`

Then locate the phase-1/2 audit read/undo files **once** by the exact audit entity/service names registered in `PersonalHubDatabase.kt`; use only those resolved files. Do not inspect module repositories/business logic in this UI phase. If an app-shell file was renamed, one targeted symbol search is allowed.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Home integration
Add a compact PersonalHub home card/module named `Registro attività`, visually consistent with existing module cards. Tapping opens the register. Do not embed a preview list on the home card.

PH home currently derives module cards from the current module-registration mechanism; integrate without breaking launcher-shortcut settings. If using the standard module registry necessarily implies a launcher shortcut, provide a valid minimal route/alias rather than leaving a broken special-case entry.

## Register UI
Show all stored events through lazy/paged/virtualized loading; no arbitrary historical event-count cap and no eager load of the entire journal.

Each top-level row must show:
- readable date/time;
- module/category;
- concise human-readable semantic description with no unexplained IDs;
- grouped/expandable detail where one user action produced child changes;
- current reverted/conflict/non-reversible status;
- undo affordance only when the phase-2 domain says the event/group is currently reversible.

Use a clear undo icon such as `↩︎` rather than an `X` that could imply deleting history. Accessibility text must say the action is undo/revert. On a rejected stale/conflicting undo, show the domain-provided human-readable reason and leave data/history unchanged.

## Filter
Add compact `🎛️` filter action opening a multi-select modal/dialog. At minimum support current categories equivalent to:
- Tutti
- People
- Timer
- Places
- Substances
- WordPulse
- Soldi
- Impostazioni
- Sistema

Provide clear Apply/Reset semantics. Persist the selected display filter across app restarts. Filtering changes display only; it never alters capture/history. Prefer deriving available categories from registered/current audit categories so future/unknown categories remain visible by default rather than disappearing under an old saved filter.

## UX / state
Preserve scroll/filter/detail state through normal recreation where practical using existing PH patterns. Do not expose raw snapshot JSON as the normal detail UI; show semantic detail fields already provided by the audit read model.

## Tests / device check
Targeted UI/state tests cover paging/lazy history, grouped expansion, filter persistence/new-category visibility, reversible vs non-reversible affordance, successful disposable undo and conflict rejection presentation.

Perform one focused safe device/emulator check: home card → full register → `🎛️` filter → expandable group → one disposable reversible event. Never use irreplaceable live data to prove destructive undo.

## Scope / resource discipline
No audit schema redesign, new inverse engine, module business refactor, theme overhaul or analytics. Use only the exact app-shell files and the phase-1/2 audit files resolved once. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, home integration, register/paging/group UI, filter behavior, undo/conflict UX, tests/device check, commit SHA.
