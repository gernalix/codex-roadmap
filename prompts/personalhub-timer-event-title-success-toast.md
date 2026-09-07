PROMPT_ID: 842731

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Fix one bounded Timer `Events` UX defect: after a successful Event-button tap, the toast must identify the exact button that was tapped instead of saying generic `Event recorded`.

Required user-visible wording:

`<X> added`

where `<X>` is the human-visible title of the exact Timer `Events` button that the user tapped.

This must behave identically for:
- an Event button tapped inside PersonalHub/Timer;
- the same Event triggered through its configured Android home-screen widget.

Examples:
- button title `Coffee` -> toast `Coffee added`;
- button title `Gym` -> toast `Gym added`.

# Exact starting files — verified on current PersonalHub/main
Read only these first:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/ui/QuickEventsScreen.kt` — in-app Events UI;
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickEventWidgetClickActivity.kt` — widget execution/success toast.

Known current widget evidence: on `QuickEventExecutionResult.Executed`, `QuickEventWidgetClickActivity` currently shows `R.string.quick_event_recorded` for a single entry or generic macro-count wording for multiple entries. Do not rediscover this.

Open only directly referenced QuickEvent target/result models and the exact string resource file if needed. If the in-app success-toast call site is not immediately visible in `QuickEventsScreen.kt`, allow one targeted search for `quick_event_recorded`, `QuickEventExecutionResult.Executed`, or the directly related success callback. No Timer-wide or repository-wide exploration.

# Required behavior
- Replace the generic successful Event toast (`Event recorded` and equivalent generic macro-count wording for this action) with exactly `<tapped button title> added`.
- Use the title attached to the exact target/button the user invoked. Do not derive the title from unrelated entry payload fields when they may differ from the visible button label.
- The in-app path and widget path must produce the same wording for the same Event target.
- If two different Events are tapped sequentially, each toast must use its own current title; no stale title from a prior tap/widget configuration.
- For an Event macro that writes multiple entries, still show `<macro button title> added`; the user explicitly wants the title of the tapped button rather than an entry count.
- Emit `<X> added` only after the canonical Event write succeeds.
- Failure, `NeedsInput`, and `Unavailable` paths must preserve their appropriate non-success feedback/flow and must never emit `<X> added`.
- Preserve Event execution, persistence, audit, export/sync mutation tracking, widget target identity, widget configuration and all existing semantics. This task is feedback-only except for the minimum data plumbing needed to surface the already-known tapped title.
- Prefer a parameterized string resource rather than duplicating hard-coded wording if that matches the existing resource pattern.

# Non-goals
Do not redesign Events, widget configuration, QuickEvent execution, macros, Timer navigation, persistence, audit, sync/export, styling, or unrelated toast copy. Do not refactor/cleanup adjacent code.

# Targeted verification
Use the smallest existing test surface or add the smallest focused coverage needed to prove:
- in-app successful tap on title `Coffee` -> exactly `Coffee added`;
- widget successful tap on the same target -> exactly `Coffee added`;
- another title cannot reuse `Coffee` accidentally;
- a macro uses its button title rather than a generic count;
- failure/NeedsInput/Unavailable never emits the success toast;
- canonical Event write behavior remains unchanged.

Perform one concise real-device Pixel smoke check covering one in-app Event and the same Event through its widget. Do not repeat unrelated Timer QA. Follow the governing PersonalHub device/testing protocol; if a temporary clone/QA app is installed on Pixel, remove it before PASS as required by the roadmap discipline.

# Version / stop
If code changes PersonalHub, capture the current PersonalHub version once and set `target = base + 1`; increment exactly once for this task.

PASS only when both in-app and widget successful Event taps use exactly `<tapped button title> added` and targeted checks pass. Stop immediately after PASS; do not investigate later roadmap items.

Final output only: `PROMPT_ID`, `RESULT`, in-app toast, widget toast, macro behavior, failure-path behavior, targeted tests, Pixel smoke check, version, commit SHA.
