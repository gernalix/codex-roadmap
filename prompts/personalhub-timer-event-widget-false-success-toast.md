[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=527418 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Fix the PersonalHub Timer Events widget bug where tapping any Event currently shows the normal success toast even though the Event is not actually recorded.

# Scope
Keep this strictly local to the Timer Event widget tap/dispatch/persistence path and its success feedback. Start from the widget provider/receiver/click handler and the existing Timer Event recording path it is supposed to reuse. Inspect broader Timer code only if a concrete dependency requires it.

Do NOT refactor unrelated Timer UI, widget layout, navigation, database schema, alerts, or other modules.

# Required behavior
- Tapping any Event exposed by the Timer widget must create exactly one normal Event record, using the same semantics/data path as recording that Event from inside Timer.
- Show the existing confirmation toast (`<event title> added`) only after the recording operation has actually succeeded.
- Never show a success toast when persistence/dispatch failed or no Event was created; use the existing error behavior if one already exists, otherwise fail without a false success message.
- A single tap must not create duplicates.
- Preserve the current widget contents, Event titles, and in-app Event button behavior.
- The fix must apply generically to every Timer Event shown by the widget, not to one hard-coded Event.

# Verification
Use the smallest sufficient checks:
- focused test of the widget tap path proving one tap creates exactly one Event;
- focused failure-path check proving no success toast is emitted when no record is created;
- one live Android widget check with at least two different Timer Events, confirming each appears in Timer history/data exactly once and the toast matches the tapped Event.

Follow the current PersonalHub remote bootstrap only as required for the normal version bump, final tested APK, Pixel install, APK delivery, commit/push, and clone cleanup if applicable. Avoid unrelated test suites unless a targeted failure requires expansion.

# Acceptance / stop
PASS only if Timer Event widget taps reliably persist exactly one corresponding Event and the confirmation toast is truthful. Stop immediately after targeted verification passes.

Final output concise: `PROMPT_ID`, `RESULT`, root cause, files changed, widget persistence result, false-success-toast result, tests/device check, version, Pixel install, APK delivery, commit/push, blocker if any.