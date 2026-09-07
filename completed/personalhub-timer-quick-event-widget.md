PROMPT_ID: 314857

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Add a configurable Android home-screen widget for Timer `Events` that, when tapped, activates one preselected Quick Event button using the same canonical behavior as tapping that button inside Timer.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/ui/QuickEventsScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/controller/QuickEventsCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/QuickEventRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetProvider.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetClickActivity.kt`
- `feature/multitimetracker/src/main/res/xml/quick_task_widget_info.xml`
- `app/src/main/AndroidManifest.xml`

Use the existing Quick Session widget only as an Android widget/configuration pattern. Do not redesign or change its semantics. If one exact Quick Events core/executor symbol is needed beyond the files above, resolve it with one targeted symbol search only; no Timer-wide exploration. Increment `version.txt` exactly once by +1.

## Known evidence
- `QuickEventsScreen` renders reusable Quick Event template buttons and macro buttons.
- A normal template tap calls the canonical Quick Events flow; a macro tap executes its ordered actions.
- Some templates/macros require user-supplied fields/customization before a write is valid.
- PersonalHub already ships a separate 1x1 Quick Session widget, but it starts a temporary Timer session and is not an Events widget.

## Work
- Add a separate configurable home-screen widget dedicated to Timer `Events`.
- When the widget is added/configured, show the currently active Quick Event buttons and let the user select exactly one target. Support both template buttons and macro buttons if both are present in the normal `Events` UI.
- Persist the selection per `appWidgetId`, so multiple widget instances can point to different Event buttons.
- The widget must display the selected button's current title clearly enough to identify it.
- For a target that is valid for one-tap execution, tapping the widget must perform the same canonical domain action as tapping that button inside `Events`, including audit/autobackup/mutation side effects already required by the Quick Events flow. Do not duplicate a second write implementation in the widget and do not instantiate a UI ViewModel from the widget; extract/reuse the minimum canonical executor if needed.
- If the selected template/macro requires user input that the normal in-app tap would request, do not invent or silently reuse values. Open Timer directly into the corresponding preselected Quick Event completion/customization flow; write only after the user completes it.
- Success feedback must happen only after the canonical write succeeds. Failure must not create a false success toast/audit/broadcast.
- Renaming a selected Event button must be reflected by the widget on the next refresh/update. If the target is archived/deleted/unavailable, the widget must not create an event; show a concise unavailable/reconfigure state instead.
- Clean up per-widget configuration when an instance is deleted.

## Tests / acceptance
Prove with focused tests/checks:
- adding/configuring a widget and choosing a template;
- two widget instances can target two different buttons;
- one-tap template execution creates exactly one canonical entry;
- one-tap macro execution creates exactly the same ordered entries as the in-app macro action;
- a target requiring input opens the correct preselected flow and performs no write before completion;
- renamed target refreshes its label;
- archived/deleted target cannot write and exposes reconfiguration/unavailable state;
- a forced persistence failure produces no false success;
- the existing Quick Session widget still behaves as before.

No general Quick Events redesign, no new parallel event tables, no unrelated Timer cleanup. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, widget selection model, tap behavior, required-input behavior, failure behavior, tests/device check, commit SHA.
