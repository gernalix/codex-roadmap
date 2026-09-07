PROMPT_ID: 582731

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal

Fix the Timer blocker where confirming **New session** fails with the toast `Canonical entity does not exist` and the running session is not started.

This is a focused regression fix. Do not redesign the Timer modal, Hub Context/Composer UI, tags, People, Places, or the graph architecture; the separate `personalhub-context-composer-redesign.md` task remains responsible for that later redesign.

Increment `version.txt` exactly once by +1.

## Reproduction supplied by the user

On the physical Android app, open Timer → **New session**, configure the session (the reported case had a title, one selected Person and one selected tag), then tap the checkmark. The dialog stays open and a toast says:

`Canonical entity does not exist`

The failure is not specific to the displayed Person/tag values; diagnose/fix the write ordering itself, not the example data.

## Verified root cause on current PersonalHub/main — reuse, do not rediscover broadly

The failing chain is already localized:

1. `NowScreen.kt` represents an unsaved new Timer session as `NEW_SESSION_DRAFT_ID = -1L`.
2. The real session row is created only inside `onSaveMeta`, via `capsule.createNewSession(...)`.
3. `SessionEditDialog.kt` currently handles the checkmark by calling `contextEditor.save(session.id)` **before** `onSaveMeta(...)`.
4. For a new session this therefore calls `saveTimerLinks(-1, ...)` before any real session exists.
5. `HubContextRuntime.saveTimerLinks()` calls `replaceContextForAnchor(HubEntityRef("timer", "session", sessionId.toString()), ...)`.
6. `HubContextRepository.replaceContextForAnchor()` binds the Timer anchor first; `bind()` requires `adapter.exists(canonicalId)` and throws exactly `Canonical entity does not exist` when it is false.
7. `TimerSessionHubAdapter.exists("-1")` is false because there is no persisted session with ID `-1`.
8. `NowCapsuleViewModel.createNewSession(...)` already exposes `onCreated: (SessionUi) -> Unit`, so the real persisted session ID is available after creation; do not invent a second session-creation path.

Treat this chain as established evidence. Do not spend tool calls rediscovering the error string or scanning the repository.

## Exact starting files — verified on PersonalHub/main

Read in one grouped pass only:

- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/now/ui/NowScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/now/controller/NowCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionContextEditor.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRuntime.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/hub/TimerSessionHubAdapter.kt`
- `version.txt`

Expand outside these files only if a directly referenced creation callback/test helper requires it; resolve that exact symbol with one targeted search. No general Timer/Hub/repository exploration.

# Required behavior

Implement the smallest correct orchestration change so that:

- an unsaved draft ID such as `-1` is never passed to Hub Context as a canonical Timer session;
- the Timer session is persisted first and its actual created `SessionUi.id` is the only ID used for new-session Context links;
- valid selected People/Place Context data, if present in the current modal, is saved against that real session rather than silently discarded;
- title, tags and start time are preserved exactly as entered;
- tapping the checkmark creates exactly one running session and dismisses the dialog once the operation is complete;
- editing an already-persisted session keeps working and continues to use its real ID;
- repeated taps / callback timing cannot create duplicate sessions or save Context against the wrong session;
- the fix does not weaken `HubContextRepository.bind()` by accepting nonexistent canonical entities and does not special-case `-1` inside the graph layer.

Prefer fixing the caller/orchestration boundary where the draft becomes a persisted session. The Hub Context invariant that bindings point only to real canonical entities must remain intact.

Do not pre-implement the next Composer redesign and do not remove the current People/Place controls merely to make this bug disappear.

# Tests / verification

Use only targeted coverage needed for this regression:

1. Add/adjust a focused test proving that New session creates the real session before any Context save and that the Context call receives the created positive/real session ID, never `NEW_SESSION_DRAFT_ID`.
2. Verify one new session with no optional Context selection can be started.
3. Verify one new session with a selected existing Person (and, if cheaply available, a Place), title and tag can be started and the valid Context link points to the newly created session.
4. Verify editing an existing session still saves without creating a second session.
5. Use the smallest relevant Android/emulator check; use the Android testing plugin/skill when available. Do not broaden into Timer-wide QA.

PASS requires the reported flow to complete without the `Canonical entity does not exist` toast and without a duplicate/phantom session.

Stop immediately after targeted PASS. Follow the PersonalHub bootstrap for final APK/install/notification requirements; do not add extra audits after PASS.

Final output only: `PROMPT_ID`, `RESULT`, root-cause fix, created session ID/context ordering, targeted tests/device check, version, commit SHA, blocker.
