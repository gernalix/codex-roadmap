PROMPT_ID: 742618

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Perform one app-wide UI consistency pass instead of three separate sessions:

1. add the compact PersonalHub home auto-export health indicator;
2. show exactly one canonical PersonalHub version footer on every navigable full-page screen of every current module, replacing legacy standalone version displays;
3. implement coherent system light/dark theme support across the same shell/module screen inventory, including the new status/footer UI.

Build the cross-module screen/theme inventory ONCE and reuse it for all three sub-goals. Capture the PersonalHub base version once and set `target = base + 1`; increment `version.txt` exactly once. Run narrow state/UI checks during implementation, then perform only one explicit final APK build/install/navigation QA.

# Token/work discipline
- Read the app-shell/theme entrypoints first, derive one authoritative inventory, and reuse it; do not independently rescan modules for footer and dark-theme phases.
- From each module root, follow only directly declared navigable full-page destinations and concrete failing theme surfaces. No repo-wide UI scan.
- If a listed symbol moved, one targeted search for that exact symbol is allowed.
- No repeated bootstrap, equivalent screen inventories, equivalent navigation passes or redundant builds.
- No unrelated UI redesign, navigation refactor, typography overhaul or Compose cleanup.
- Stop immediately after consolidated PASS.

# Shared starting files / inventory
Read in grouped passes:
- `version.txt`
- `app/build.gradle.kts`
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- `app/src/main/java/com/gernalix/personalhub/ui/theme/Theme.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabasePreferences.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/HubAutoExport.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/AppRoot.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/theme/LuoghiTheme.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/theme/Theme.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/ui/WordPulseTheme.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/ui/WordPulseScreen.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/ui/app/SuperContactsApp.kt`
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt`

From the explicit module routes in `MainActivity.kt`/`LauncherShortcutsCapsule.kt`, perform targeted lookups of People, Timer, Places, Substances, Soldi and WordPulse root routers/screens and their directly declared full-page destinations. Keep a single task-local screen inventory and reuse it throughout. Do not create a permanent registry unless implementation truly requires one.

# Phase A — auto-export status on PH home
Known state: PH already exposes global auto-export status including configured folder, current/exported generation, last successful export and stale/error state.

Required behavior:
- Add a small tappable `✅` / `❌` status affordance on PH home.
- `✅` means configured and current with no relevant error. `❌` means stale, failed or inaccessible/unconfigured when backup is not currently healthy.
- Tapping opens a compact dialog/sheet showing at least last successful export time, folder/configuration status, current vs exported generation/stale state and last error when present.
- Provide accessible semantic text/content descriptions; emoji is not the only label.
- Reuse existing status APIs and theme components.
- Do NOT modify WorkManager, DatabaseVault export logic, sync, backup/import or Settings architecture.

Targeted proof covers healthy, stale, error and unconfigured UI/state. Do not manufacture destructive failures on real data.

# Phase B — one canonical PersonalHub version footer everywhere
Known state:
- `version.txt` drives the canonical host app version.
- Timer currently has a visible footer tied to old Timer/`AppPatchVersion` semantics.
- Other modules may contain legacy standalone labels or no footer.

## Canonical source
- Display the actual installed/current PersonalHub host `versionName`.
- Expose it through the narrowest shared host contract appropriate to current architecture.
- Never use feature/library `BuildConfig.VERSION_NAME`, standalone patch revisions, DB schema version or duplicated hardcoded values as the visible app version.
- Preserve the normal `version.txt` → host build version mechanism.

## Coverage
For EVERY navigable full-page destination in:
- People
- Timer
- Places
- Substances
- Soldi
- WordPulse

show exactly one small secondary version indicator at bottom-right.

Presentation:
- unobtrusive/readable secondary typography;
- bottom-right aligned with system/navigation insets respected;
- no overlap with FABs, buttons, lists or bottom navigation;
- coherent placement on scrolling screens;
- dialogs/sheets/dropdowns/snackbars do not need their own footer unless they are actual full-page destinations.

Where a legacy standalone version is visible, replace it; never show two competing versions. Timer's old `AppPatchVersion` footer must no longer be the user-visible app version, but do not reopen unrelated AutoConsistency/runtime cleanup if the earlier Timer consolidated task already handled it.

Targeted proof: every destination in the single inventory renders exactly one canonical host version; changing host version propagates without per-module edits; representative compact/scrolling layouts do not overlap controls.

# Phase C — coherent system light/dark theme over the SAME inventory
Required behavior:
- Follow Android system light/dark mode by default; preserve an existing explicit PH theme preference if present at execution time.
- Define/reuse central theme tokens where architecture supports it.
- Expand from each module root only to a concrete hardcoded light-only color/theme surface that actually fails dark-mode verification; at most one targeted search inside that module per concrete failure.
- Cover PH shell plus People, Timer, Places, Substances, Soldi and WordPulse, including dialogs/cards/forms reached in the representative inventory and the new auto-export indicator/version footer.
- Preserve light-theme behavior/appearance unless proper theming requires a change.
- Handle system bars, text contrast, disabled/error states, inputs and overlays.
- Theme-triggered Activity recreation must not discard important in-progress state; do not re-fix unrelated lifecycle work unless a concrete theme-switch blocker is demonstrated.

No export work, layout redesign, navigation changes or general color cleanup beyond actual dark-mode failures.

# Consolidated verification
Use the one inventory to drive one final navigation matrix.

Before the final APK pass, targeted tests prove:
- auto-export indicator healthy/stale/error/unconfigured semantics;
- exactly one canonical host version on every inventoried full-page destination and no legacy duplicate;
- representative theme tokens/surfaces render correctly in light and dark and important state survives normal recreation.

Then:
- perform ONE explicit final PersonalHub APK build;
- safely install/update the final APK on project-required Android targets per the governing PersonalHub protocol;
- perform ONE concise device/emulator navigation pass through PH home and representative destinations from every module, switching system light/dark once and checking the same screens for footer placement, status control, readability, inputs/dialogs, error/disabled states and obvious light-only surfaces;
- do not rerun a second independent footer audit or dark-theme audit after this PASS.

# Non-goals
No backup/export architecture changes, module redesign, navigation refactor, typography overhaul, release-infrastructure redesign, general Compose cleanup or unrelated lifecycle fixes.

# Acceptance / stop
PASS only when the auto-export status control works, every inventoried full-page module screen shows exactly one canonical PersonalHub version, all representative module/theme surfaces are usable in system light/dark, and the consolidated final QA passes. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, auto-export indicator semantics, canonical version source/screens covered, legacy displays replaced, theme mechanism/modules checked, targeted tests, final device QA, version, commit SHA.