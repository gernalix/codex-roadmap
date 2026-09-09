[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

PROMPT_ID=842731 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Fix one bounded success-toast UX defect across Timer Events and Substances: after a successful configured-button tap, show exactly <X> added, where <X> is the human-visible title of the exact tapped Event or substance button. Behavior and presentation must match across both modules and every available in-app/widget entry path, including Timer macros.

Examples: Timer Coffee -> Coffee added; Substances Pregabalin -> Pregabalin added.

# Verified Timer state — do not rediscover
Current PersonalHub/main still has the Timer bug on both paths:
- feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/controller/QuickEventsCapsuleViewModel.kt
  - successful template execution calls access.showEntryRecorded(ctx) with no title;
  - successful macro execution calls access.showMacroRecorded(ctx, result.entryIds.size), i.e. generic count-based feedback.
- feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/system/QuickEventsCapsuleAccess.kt
  - exposes only generic showEntryRecorded(context) / showMacroRecorded(context, count) feedback contracts.
- feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickEventWidgetClickActivity.kt
  - on Executed, still chooses quick_event_recorded or quick_event_macro_recorded from entry count.

Therefore the Timer part is NOT already implemented. Do not start from QuickEventsScreen.kt or scan Timer UI: the current success paths are already localized above.

# Scope
Read the three Timer files above first. Open the directly referenced QuickEvent target/core model and exact string resources only if required by the patch. One targeted lookup for the concrete QuickEventsCapsuleAccess implementation is allowed if changing its method signature is necessary.

For Substances, use one targeted search for the configured substance-button tap handlers and their success-toast/widget paths; inspect only the returned directly relevant files and exact string resources. No Timer-wide, Substances-wide, or repo-wide exploration.

# Required behavior
- Timer successful template tap: <template button title> added.
- Timer successful macro tap: <macro button title> added, never a count.
- Substances successful configured-button tap: <substance button title> added; every success toast must contain the exact tapped substance and use the same wording and visual form as Timer.
- The same target/title produces identical feedback wherever it is tapped: in-app and, where configured, widget.
- Resolve the title from the invoked target/template/macro/substance-button identity, not from an arbitrary created entry payload.
- Sequential different taps must never reuse a stale title or substance.
- Emit success text only after canonical write success.
- Needs-input, unavailable, exceptions/failures and rejected writes keep existing non-success behavior and never emit <X> added.
- Preserve execution, audit, persistence/export tracking, stock semantics, widget identity/configuration and all other semantics.
- Prefer one shared or identically defined parameterized string resource such as %1$s added; keep normal i18n rules.

# Token/work discipline
Make the minimum plumbing change. Do not redesign Events or Substances, refactor executors/repositories, change widget preferences, or inspect unrelated surfaces unless a concrete compile/test failure requires it. Reuse current target/core lookup APIs instead of inventing another title store.

# Verification
Use the smallest focused tests proving:
- Timer template Coffee -> exactly Coffee added in-app;
- same Timer target -> exactly Coffee added from widget;
- Timer macro uses its button title, not entry count;
- Substances tap -> exactly <tapped substance> added, with Timer-identical form;
- every available Substances in-app/widget success path identifies the tapped substance;
- a later different Timer or Substances title never reuses the previous one;
- failure/needs-input/unavailable/rejected writes never emit success;
- Timer Event and Substances writes remain otherwise unchanged.

Then one concise Pixel smoke check: one Timer Event in-app and from its configured widget, plus one configured Substances button through each available in-app/widget path. No unrelated QA. Follow the current remote PersonalHub bootstrap for version, final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Stop
Capture current PersonalHub version once and set target = base + 1 exactly once if code changes. PASS only when Timer and Substances success paths use exactly <tapped title> added, Substances always names the tapped substance, presentation matches, and targeted checks pass. Stop immediately; do not inspect later roadmap items.

Final output only: PROMPT_ID, RESULT, Timer in-app/widget toast, macro behavior, Substances in-app/widget toast, failure paths, tests, Pixel smoke, version, APK delivery, commit/push, blocker if any.
