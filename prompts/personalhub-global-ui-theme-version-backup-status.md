PROMPT_ID: 742618

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

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
- `SostanzeApp.kt` currently displays `com.gernalix.sostanze.BuildConfig.VERSION_NAME` on its Home, which is a concrete legacy/wrong version source that must be replaced by the host PersonalHub version.

The prompt is therefore partially implemented, not complete.

# Starting files / one inventory
First grouped pass only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/ui/theme/Theme.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- module root/router/theme files only for People, Timer, Places, Substances, Soldi, WordPulse.

From the already-declared module roots, follow only directly navigable full-page destinations. Do not independently rescan modules for footer and then again for theme. For each concrete dark-mode failure, at most one targeted lookup into that module.

# A. Home auto-export indicator
Add a compact tappable `✅` / `❌` affordance on PersonalHub home using only `DatabaseVault.autoExportStatus()`:
- `✅`: configured, current generation exported, no relevant error;
- `❌`: unconfigured/inaccessible, stale or failed.

Tap opens compact details: last successful export, folder/configured state, current vs exported generation/stale state and last error when present. Add accessible semantic text; emoji cannot be the only label. No export/import/sync architecture changes.

# B. Canonical host version everywhere
Canonical visible version = installed PersonalHub host `versionName`, never feature `BuildConfig`, legacy Timer patch version, DB schema or hardcoded duplicated string.

Reuse the existing correct host-home value through the narrowest shared host contract/composable. Every navigable full-page destination in People, Timer, Places, Substances, Soldi and WordPulse must show exactly one unobtrusive bottom-right host version, with insets/scrolling/FAB overlap handled. Dialogs/sheets do not need their own footer.

Replace concrete legacy displays rather than showing duplicates. In particular remove the visible Substances feature `BuildConfig.VERSION_NAME`; treat Timer's old patch-version display similarly if still visible.

# C. System light/dark over SAME inventory
Make PH shell + those module screens follow Android system light/dark by default, preserving any explicit PH theme preference if one exists at execution time.

Start from the host theme contract; reuse MaterialTheme tokens already used by modules. Patch only concrete hardcoded/light-only surfaces exposed by the single navigation matrix. Verify system bars, text/input/error/disabled/overlay contrast and that normal theme recreation does not lose important in-progress state. No global aesthetic redesign or color cleanup.

# Verification
Targeted automated checks first:
- healthy/stale/error/unconfigured indicator semantics;
- every inventoried full-page screen renders exactly one canonical host version and no legacy duplicate;
- representative theme surfaces/tokens behave in light + dark and important state survives recreation.

Then ONE final APK build and ONE concise navigation pass through PH home + representative full-page destinations of all six modules, switching system light/dark once. Check indicator, footer placement/duplication, readability and obvious light-only surfaces. Do not run separate footer and theme audits afterward.

Follow the current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Non-goals / stop
No backup architecture changes, navigation refactor, module redesign, typography overhaul, release infra rewrite, general Compose cleanup or unrelated lifecycle work. PASS when the three remaining gaps are verified across the single inventory; stop immediately.

Final output only: `PROMPT_ID`, `RESULT`, auto-export indicator, canonical version source/screens, legacy displays replaced, theme mechanism/modules checked, targeted tests, final device QA, version, APK delivery, commit/push, blocker if any.
