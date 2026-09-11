[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=762451 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Add a PersonalHub Android home-screen widget for Substances that mirrors the existing Timer Event widget as closely as practical in layout, configuration flow, interaction, feedback, and per-widget behavior.

# Scope
Reuse the existing Timer Event widget implementation as the reference pattern instead of designing a separate widget architecture. Start from the Timer widget provider/configuration/click path and the existing canonical Substances configured-button recording path.

Keep the change local to the new Substances widget and the minimum shared code needed to avoid duplication. Do NOT redesign Substances, Timer, alerts, navigation, database schema, or unrelated widgets.

# Required behavior
- Add a Substances widget to the Android widget picker with the same visual style, footprint, and interaction model as the existing Timer Event widget unless an Android/platform constraint requires a small difference.
- Each widget instance must be configurable to one existing configured Substances button/action, just as each Timer widget instance targets one Timer Event.
- Allow multiple Substances widget instances, each pointing to a different configured button/action.
- The widget must display the selected configured button/action title clearly and stay synchronized when that target is renamed or changed.
- Tapping the widget must execute exactly the same canonical action as tapping that configured button inside Substances, including all normal persistence/stock side effects and current zero-stock behavior. Do not create a parallel recording implementation.
- One widget tap must create exactly one corresponding Substances record/action; never zero because of the widget path and never duplicates.
- Show the same standardized success toast used by Substances/Timer (`<tapped title> added`) only after the action has really succeeded.
- If the configured target no longer exists or is unavailable, do not show a false success toast; render/open the appropriate reconfiguration/unavailable state using the Timer widget behavior as the model.
- Preserve all current in-app Substances behavior.

# Implementation guidance
Prefer adapting/reusing the existing Timer widget structure and patterns rather than introducing a new abstraction unless a tiny shared helper materially removes duplication.

The Substances widget must call the same authoritative Substances action/recording path used by the in-app configured button. If that path is currently UI-bound, extract only the smallest reusable boundary required by both callers.

Do not add polling or a second source of truth.

# Verification
Use the smallest sufficient checks:
- focused test that the selected Substances target survives widget configuration/reload;
- focused tap-path test proving one tap creates exactly one canonical Substances action and preserves the normal stock/zero-stock semantics;
- focused failure/unavailable-path test proving no false success toast;
- real Android launcher-widget check on the Pixel with at least two different configured Substances buttons assigned to two widget instances, verifying that tapping each widget records the correct action exactly once and that the result is visible through the normal Substances UI/data path.

Do not treat directly launching the click Activity or only querying the database as sufficient final acceptance for the launcher-widget behavior.

Follow the current PersonalHub remote bootstrap only as required for the normal version bump, final tested APK, Pixel install, APK delivery, commit/push, roadmap/MegaVault update, and clone cleanup if applicable. Avoid unrelated suites or repository-wide exploration unless a targeted failure requires expansion.

# Acceptance / stop
PASS only if the Substances widget is available from the launcher, can independently target configured Substances buttons, visually/behaviorally matches the Timer Event widget, and real launcher taps reliably record exactly the intended Substances action with truthful feedback.

Stop immediately after targeted verification and the normal delivery workflow pass. Do not start the next roadmap task.

Final output concise: `PROMPT_ID`, `RESULT`, files changed, reuse vs new widget code, configuration result, real launcher tap result, persistence/stock result, false-success result, tests/device check, version, Pixel install, APK delivery, commit/push, blocker if any.