[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=842731 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Fix one bounded Timer `Events` UX defect: after a successful Event-button tap, show exactly `<X> added`, where `<X>` is the human-visible title of the exact tapped Event button. Behavior must match in-app and the configured Android widget, including macros.

Examples: `Coffee` -> `Coffee added`; `Gym` -> `Gym added`.

# Verified current state — do not rediscover
Current `PersonalHub/main` still has the bug on both paths:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/controller/QuickEventsCapsuleViewModel.kt`
  - successful template execution calls `access.showEntryRecorded(ctx)` with no title;
  - successful macro execution calls `access.showMacroRecorded(ctx, result.entryIds.size)`, i.e. generic count-based feedback.
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/system/QuickEventsCapsuleAccess.kt`
  - exposes only generic `showEntryRecorded(context)` / `showMacroRecorded(context, count)` feedback contracts.
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickEventWidgetClickActivity.kt`
  - on `Executed`, still chooses `quick_event_recorded` or `quick_event_macro_recorded` from entry count.

Therefore this prompt is NOT already implemented. Do not start from `QuickEventsScreen.kt` or scan Timer UI: the current success paths are already localized above.

# Scope
Read only the three files above first. Open the directly referenced QuickEvent target/core model and exact string resources only if required by the patch. One targeted lookup for the concrete `QuickEventsCapsuleAccess` implementation is allowed if changing its method signature is necessary. No Timer-wide or repo-wide exploration.

# Required behavior
- Successful template tap: `<template button title> added`.
- Successful macro tap: `<macro button title> added`, never a count.
- Same target/title produces identical wording in-app and widget.
- Resolve the title from the invoked target/template/macro identity, not from an arbitrary created entry payload.
- Sequential different taps must never reuse a stale title.
- Emit success text only after `QuickEventExecutionResult.Executed` / canonical write success.
- `NeedsInput`, `Unavailable`, exceptions/failures keep existing non-success behavior and never emit `<X> added`.
- Preserve execution, audit, persistence/export tracking, widget identity/configuration and all other semantics.
- Prefer one parameterized string resource such as `%1$s added`; keep normal i18n rules.

# Token/work discipline
Make the minimum plumbing change. Do not redesign Events, refactor the executor, change widget preferences, or inspect unrelated Timer surfaces unless a concrete compile/test failure requires it. Reuse current target/core lookup APIs instead of inventing another title store.

# Verification
Use the smallest focused tests proving:
- template `Coffee` -> exactly `Coffee added` in-app;
- same target -> exactly `Coffee added` from widget;
- macro uses its button title, not entry count;
- another title does not reuse `Coffee`;
- failure/NeedsInput/Unavailable never emits success;
- Event writes remain unchanged.

Then one concise Pixel smoke check: one in-app Event and the same configured widget Event. No unrelated Timer QA. Follow the current remote PersonalHub bootstrap for version, final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Stop
Capture current PersonalHub version once and set `target = base + 1` exactly once if code changes. PASS only when both success paths use exactly `<tapped title> added` and targeted checks pass. Stop immediately; do not inspect later roadmap items.

Final output only: `PROMPT_ID`, `RESULT`, in-app toast, widget toast, macro behavior, failure paths, tests, Pixel smoke, version, APK delivery, commit/push, blocker if any.
