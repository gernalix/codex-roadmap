PROMPT_ID: 846315

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: STANDARD

# Goal

Make the PersonalHub app version visible consistently on every navigable full-page screen of every module. Each screen must show the current canonical PersonalHub version in small secondary text at the bottom-right. Where a module already shows a version inherited from its old standalone app, replace that legacy display instead of adding a second one.

This is a presentation consistency task. Do not redesign module navigation, module layouts, versioning semantics, or release infrastructure.

## Known current evidence — reuse, do not rediscover broadly

Current `PersonalHub/main` already shows:

- `version.txt` is the canonical monotonically increasing PersonalHub app version source used by the host build;
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt` declares the host module routes for People, Timer, Places, Substances, Soldi and WordPulse;
- the same module destinations are also represented by `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`;
- Timer already has a bottom version footer in `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/AppRoot.kt`, but it is tied to the old Timer/`AppPatchVersion` display path and must be replaced by the canonical PersonalHub host version rather than duplicated;
- some other modules may still contain equivalent standalone-app version labels while other screens contain none.

The required value is the installed/current PersonalHub host app version, not a feature/library BuildConfig version, patch revision, schema version or legacy standalone-app version.

## Exact starting files — verified on PersonalHub/main

Read these in one grouped pass:

- `version.txt`
- `app/build.gradle.kts`
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/AppRoot.kt`

From the explicit module route classes in `MainActivity.kt`/`LauncherShortcutsCapsule.kt`, perform only targeted lookups of those six modules' root activities/screens and their directly declared navigable full-page destinations. Do not perform a repo-wide UI scan. If one module delegates navigation to one clearly named root composable/router, inspect that router instead of searching the whole feature.

Before code changes, increment `version.txt` exactly once by +1.

# Required behavior

## A. One canonical version source

- derive/display the actual PersonalHub host `versionName` corresponding to the canonical app version;
- expose it to feature UI through the narrowest existing/shared host contract appropriate to the current architecture;
- do not make a feature depend on its own library `BuildConfig.VERSION_NAME` or standalone-app revision;
- do not duplicate the version value manually in multiple modules;
- preserve the normal `version.txt` → app build version mechanism.

## B. Footer on every module full-page screen

For every navigable full-page destination reachable inside these modules:

- People;
- Timer;
- Places;
- Substances;
- Soldi;
- WordPulse;

show exactly one small version indicator at bottom-right.

Presentation requirements:

- secondary/small typography;
- visually unobtrusive but readable;
- bottom-right aligned;
- respect navigation bars/system insets and existing content padding;
- do not cover FABs, buttons, lists or bottom navigation;
- scrolling screens must still have a coherent footer placement without obscuring content;
- use one shared/reusable footer implementation or contract where that reduces duplication without breaking capsule/module boundaries.

"Every screen" here means navigable full-page application destinations, including module tabs/pages that act as distinct screens. It does NOT require adding the version inside transient dialogs, bottom sheets, dropdowns, snackbars, permission prompts or individual cards unless one of those is actually the module's full-page destination.

## C. Replace legacy standalone version displays

When a screen already displays a legacy version/revision from the pre-PersonalHub standalone app:

- replace it with the canonical PersonalHub version;
- do not leave both old and new indicators;
- remove only the dead display dependency made unnecessary by this change; do not broaden into cleanup of unrelated legacy runtime/version logic that belongs to other roadmap tasks.

In particular, Timer's current `AppPatchVersion` footer must no longer be the user-visible app version after this task. Do not preempt unrelated AutoConsistency/version cleanup owned by `personalhub-timer-legacy-runtime-cleanup.md`.

# Verification

Build a concrete screen inventory from the six authoritative module routes and their directly declared navigation destinations. Keep that inventory local to the task/test/report; do not create a new long-lived registry unless the implementation genuinely requires one.

Targeted verification must prove:

- each discovered navigable full-page destination in all six modules renders exactly one canonical PersonalHub version indicator;
- all indicators show the same current host version;
- known legacy standalone version footers/labels on those screens are replaced rather than duplicated;
- Timer no longer exposes `AppPatchVersion` as its visible app-version footer;
- the footer does not overlap primary controls/navigation at representative compact and scrolling layouts;
- changing the host app version changes the displayed value without per-module edits.

Prefer focused composable/UI tests plus one concise emulator navigation pass if needed to prove placement across modules. Do not run unrelated full-suite UI testing solely for this cosmetic task.

# Acceptance

PASS only when every navigable full-page screen of People, Timer, Places, Substances, Soldi and WordPulse shows exactly one small canonical PersonalHub version at bottom-right, all old standalone-version displays on those screens have been replaced, no module maintains a competing visible version source, and representative layouts remain usable without overlap.

Stop immediately after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, canonical version source, screens/modules covered, legacy version displays replaced, tests/device check, version, commit SHA.
