[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742618 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Use one cross-module UI pass to finish three related consistency gaps:
1. home auto-export health indicator;
2. one canonical PersonalHub version footer on every navigable full-page module screen;
3. coherent system light/dark theme support over that same screen inventory.

Build the screen inventory ONCE and reuse it for footer + theme QA. Capture base app version once; `target = base + 1` exactly once. One final build/install/navigation pass only.

# Verified current state — preserve/reuse
Do not rediscover these facts:
- `app/MainActivity.kt` already shows host `BuildConfig.VERSION_NAME` at the bottom-right of the PersonalHub HOME. Keep that behavior; the missing work is module/full-page coverage and shared canonical sourcing.
- `DatabaseVault.autoExportStatus(context)` already exposes `folderConfigured`, current/exported generation, last successful export, last error and stale state. Use it directly for the home indicator; do NOT inspect/rework export scheduling/WorkManager.
- the PersonalHub host `ui/theme/Theme.kt` currently hardcodes a `lightColorScheme` and does not follow system dark mode.
- People `SuperContactsTheme`, Places `LuoghiTheme`, Substances `SostanzeTheme` and WordPulse `WordPulseTheme` already default from `isSystemInDarkTheme()`. PRESERVE those working module theme contracts; do not rewrite them merely for consistency.
- Timer already defines both `LightColors` and `DarkColors`, but `MultiTimeTrackerTheme(darkTheme: Boolean = false)` does not follow the system by default. Fix only the selection/default boundary unless concrete UI evidence requires more.
- Soldi currently hosts `SoldiScreen` inside a plain default `MaterialTheme` with no system-dark selection. Give it the narrowest host-compatible system theme behavior; do not redesign Soldi.
- `SostanzeApp.kt` currently displays `com.gernalix.sostanze.BuildConfig.VERSION_NAME` on its Home, which is a concrete legacy/wrong version source that must be replaced by the host PersonalHub version.
- Timer still exposes its legacy patch version in Info/footer (`AppPatchVersion.current(...)` / `versione_patch_v` / `app_version_footer`), so that visible feature version also needs replacement.

The prompt is therefore partially implemented, not complete. For dark mode, do NOT start by auditing People/Places/Substances/WordPulse themes again; they already follow system dark. Their final navigation check is only regression coverage.

# Starting files / one inventory
First grouped pass only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/ui/theme/Theme.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- module root/router files needed to enumerate full-page destinations;
- for concrete remaining dark-mode work start directly from Timer `ui/theme/Theme.kt` and Soldi `SoldiActivity.kt`; do not reopen the already-correct People/Places/Substances/WordPulse theme implementations unless a targeted final regression fails.

From the already-declared module roots, follow only directly navigable full-page destinations. Do not independently rescan modules for footer and then again for theme. For each concrete dark-mode failure, at most one targeted lookup into that module.

# A. Home auto-export indicator
Add a compact tappable `✅` / `❌` affordance on PersonalHub home using only `DatabaseVault.autoExportStatus()`:
- `✅`: configured, current generation exported, no relevant error;
- `❌`: unconfigured/inaccessible, stale or failed.

Tap opens compact details: last successful export, folder/configured state, current vs exported generation/stale state and last error when present. Add accessible semantic text; emoji cannot be the only label. No export/import/sync architecture changes.

# B. Canonical host version everywhere
Canonical visible version = installed PersonalHub host `versionName`, never feature `BuildConfig`, legacy Timer patch version, DB schema or hardcoded duplicated string.

Reuse the existing correct host-home value through the narrowest shared host contract/composable. Every navigable full-page destination in People, Timer, Places, Substances, Soldi and WordPulse must show exactly one unobtrusive bottom-right host version, with insets/scrolling/FAB overlap handled. Dialogs/sheets do not need their own footer.

Replace concrete legacy displays rather than showing duplicates. In particular remove the visible Substances feature `BuildConfig.VERSION_NAME` and Timer patch-version display.

# C. System light/dark over SAME inventory
Make PH shell + remaining non-system-aware module screens follow Android system light/dark by default, preserving any explicit PH theme preference if one exists at execution time.

Start from the host theme contract. Reuse the already-working system-aware theme contracts in People/Places/Substances/WordPulse without rewriting them. For Timer, wire the existing Light/Dark schemes to system selection. For Soldi, add the narrowest system-aware theme boundary. Patch additional hardcoded/light-only surfaces only when the single navigation matrix exposes a concrete failure. Verify system bars, text/input/error/disabled/overlay contrast and that normal theme recreation does not lose important in-progress state. No global aesthetic redesign or color cleanup.

# Verification
Targeted automated checks first:
- healthy/stale/error/unconfigured indicator semantics;
- every inventoried full-page screen renders exactly one canonical host version and no legacy duplicate;
- host + Timer + Soldi theme selection follows light/dark;
- representative regression coverage confirms People/Places/Substances/WordPulse remain system-aware;
- important state survives theme recreation.

Then ONE final APK build and ONE concise navigation pass through PH home + representative full-page destinations of all six modules, switching system light/dark once. Check indicator, footer placement/duplication, readability and obvious light-only surfaces. Do not run separate footer and theme audits afterward.

Follow the current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Non-goals / stop
No backup architecture changes, navigation refactor, module redesign, typography overhaul, release infra rewrite, general Compose cleanup or unrelated lifecycle work. PASS when the three remaining gaps are verified across the single inventory; stop immediately.

Final output only: `PROMPT_ID`, `RESULT`, auto-export indicator, canonical version source/screens, legacy displays replaced, theme mechanism/modules checked, targeted tests, final device QA, version, APK delivery, commit/push, blocker if any.
