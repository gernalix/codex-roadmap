PROMPT_ID: 214756

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Replace the current Hub Context UI with a dedicated top-level PersonalHub section, temporarily named **Composer**, designed for extremely fast context construction with location/time-aware suggestions.

The current Hub Context engine, N-ary model, adapters, templates and recursive Explorer are valid infrastructure and MUST be reused. This goal is a UX/product redesign plus a small deterministic recommendation layer, not a second graph implementation.

The previous roadmap task `personalhub-hub-context-hardening.md` is a prerequisite. Verify its acceptance state; do not redo its work.

Increment `version.txt` exactly once by +1.

## Product intent
The Composer should feel like assembling a small puzzle whose obvious pieces are already filled in by the app.

Most use should require only a few taps:
1. open Composer;
2. current time/session and likely place are already inferred;
3. tap a data-type chip such as People;
4. choose one of a handful of high-probability suggestions or search;
5. save.

The more Context history exists, the better the next suggestions should become through simple deterministic co-occurrence statistics. No ML framework is required.

## Current UI anti-reference — explicitly DO NOT reproduce
The user supplied six screenshots of v29 as examples of what must disappear. Treat these descriptions as hard anti-patterns:
- Hub Context controls embedded inside Timer’s already-large “New session” dialog;
- a “People and place” mini-editor nested inside the Timer editor with long scrollable person/place lists;
- a second “Context / + Link / Explore related” card embedded inside the same dialog;
- nested dialogs/sheets inside dialogs, including “Related explorer” over Timer;
- generic “Link entities” dialog exposing raw technical chips such as `person`, `session`, `place`, `transaction`, `substance`, `word_session`, `resource`;
- long undifferentiated lists such as `Session 589`, `Session 588`, etc.; raw IDs are meaningless to the user;
- resource controls, template controls and entity selection all packed into one vertically endless modal;
- excessive scrolling, poor hierarchy, cryptic labels and large empty/disabled areas.

These are not styling bugs to polish. The embedded/nested interaction model itself must be removed.

## Exact starting files — current PersonalHub/main
Start only from:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextComposer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextExplorer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextLinks.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRepository.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRuntime.kt`
- `contracts/database/src/main/java/com/gernalix/personalhub/contracts/database/HubEntityAdapter.kt`
- `contracts/database/src/main/java/com/gernalix/personalhub/contracts/database/HubContextDao.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/hub/TimerSessionHubAdapter.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/hub/PlacesHubAdapter.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/hub/PeopleHubAdapter.kt`
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/hub/SoldiTransactionHubAdapter.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/hub/SubstanceHubAdapter.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/hub/WordSessionHubAdapter.kt`

For geolocation, perform ONE targeted search for the existing Places/current-location pipeline and reuse it; do not create a second location stack. For time-bearing Substance data, perform ONE targeted search for the canonical intake-event DAO/model if needed.

## 1. Restore Timer’s original session editor
Remove the Hub Context/People/Place embedded UI from `SessionEditDialog` and restore the Timer session dialog to its pre-Hub-Context purpose: session title/time/tags and its original controls.

Specifically:
- no `SessionContextEditor` inside New/Edit Session;
- no embedded `HubContextLinks` card inside the Timer dialog;
- saving a Timer session must not require saving Context UI first;
- basic Timer start/create/edit must regain its simple pre-campaign interaction cost.

The Hub Context graph remains integrated with Timer underneath. Existing Context links must not be deleted merely because the embedded editor disappears.

If an existing session needs a Context entry point, expose at most a small explicit action from an appropriate session detail/overflow surface OUTSIDE the New Session modal; the dedicated Composer remains the primary UI.

## 2. Dedicated top-level Composer
Add **Composer** as a clear top-level PersonalHub home destination. It is an app-level Hub feature, not a new domain owner and not a copy of any module.

Use a full-screen Material 3 screen with strong visual hierarchy, not a nested AlertDialog.

Recommended structure:
- top app bar: `Composer`, back/close as appropriate;
- compact **Current context** header;
- one search field near the top;
- human-readable type/category chips below the search field;
- compact ranked suggestions for the selected type;
- selected puzzle pieces always visible in a concise area;
- sticky/obvious Save action;
- templates/advanced/manual override moved to a secondary surface, not mixed into the primary flow.

No raw internal identifiers (`word_session`, DB IDs, enum names) may be shown to the user. Localize labels in IT/EN using normal resources.

## 3. Automatic current context: time/session + place
Immediately on Composer open, resolve as much context as possible.

### Time/session
- If a relevant Timer session is currently running, preselect it as the default temporal anchor.
- If multiple running sessions make the answer ambiguous, show a compact choice rather than silently guessing badly.
- If no running session exists, default to “Now”/current time as an editable temporal anchor.
- The temporal anchor is ALWAYS tappable/changeable for retroactive Context creation.

When choosing a historical Timer session, display a useful label such as:
`6 Sep 2026 · 16:55–17:42 · Walk`
or equivalent localized date/start/end/title.
Never display `Session 589` as the primary identity.

Search historical sessions only after the user asks/searches; use bounded/paginated query APIs from the hardening task.

### Place
Obtain current device location through the existing Places location pipeline/permission model.
- If one saved Place clearly contains the current coordinate within its radius, preselect it.
- If several overlap, show the best few compactly; prefer nearest/best-radius match but keep the choice editable.
- If none contains the coordinate, show up to the **5 nearest saved Places** with distance as suggestions; do not dump all Places.
- If location permission is unavailable/denied, degrade gracefully to recent/contextual Places + search.

The auto-selected Place is always tappable/changeable for retroactive Context creation.

Session/time and current Place are part of the **Current context header**, not ordinary type chips that the user must redundantly select.

## 4. Search + type chips without endless lists
One search field sits above the type chips.

When a type chip is active, search only that entity kind/capability.

Primary chips should represent things the user may genuinely need to choose explicitly, using human names such as:
- People
- Resources
- any future non-obvious/manual entity kinds that the registry exposes

Do NOT clutter the primary chip row with data already represented/inferred in the Current context header or deterministic time-derived section.

Provide a secondary `More` / `Add manually` escape hatch so every registered Hub entity kind remains reachable when the automatic inference is wrong or the user wants an unusual Context. Flexibility must not force clutter into the default path.

Never initially render hundreds of candidates. Show at most about **5 high-value suggestions** for a type, then rely on search/pagination.

## 5. Simple recommendation algorithm — no ML
Implement a cheap deterministic ranking service over existing Context history.

As more pieces are selected, rank candidates of the next type using this priority tuple (or an equivalent simple deterministic implementation):
1. number of historical Contexts containing the candidate together with **all currently selected explicit/automatic anchors**;
2. association with the currently selected Place when relevant;
3. most recent matching co-occurrence;
4. candidate’s overall historical Context frequency;
5. stable human-readable tie-breaker.

This naturally implements the desired behavior:
“If A of type X and B of type Y were selected together often, after selecting A and opening type Y, B should be near the top.”

### People-specific behavior
When People is selected:
- top suggestions should strongly favor people historically associated with the selected/current Place and current selected scope;
- the correct person should usually be among the first 3–5 when history supports that;
- if not, the user searches; do not optimize endless scrolling beyond the first small suggestion set.

No opaque AI/embedding/vector database.

## 6. Time-derived automatic candidates
Do not make the user manually browse type chips for facts that can often be discovered from the selected time interval.

Use the selected temporal anchor to detect already-recorded facts such as:
- Soldi transactions whose occurrence time falls in/relevantly matches the selected interval;
- Substance **intake events** recorded in the selected interval;
- WordPulse sessions overlapping the selected interval.

Important semantic rule:
- generic `Substance` identity is not equivalent to a time-stamped intake; if the graph currently exposes only `substances/substance`, add the minimum canonical `substances/intake` Hub adapter/identity needed for correct temporal inference instead of pretending the substance itself happened at that time.

Present these in a compact **Detected from this time** section, not as noisy default type chips.
- high-confidence detected facts may be preselected;
- every auto-selection is visibly marked and removable;
- ambiguous candidates remain one-tap suggestions rather than silently asserted truth;
- changing the time/session or place recomputes automatic candidates while preserving clearly manual selections where valid;
- only members still selected when Save is pressed become explicit Context members, preserving normal bidirectional traversal.

Do not silently create permanent relationships from weak coincidence without showing the user what will be saved.

## 7. Retroactive Contexts are first-class
The default is “now”, but creating a Context for the past must be easy.

Tapping the time/session anchor lets the user choose a historical interval/session by readable date/time/title.
Tapping the place anchor lets the user choose another Place.
After either change:
- People recommendations rerank;
- detected transaction/intake/WordSession facts recompute;
- existing selected pieces remain only when still sensible/valid.

No special “retroactive mode” maze is required; editing the anchors is enough.

## 8. Templates and Explorer
Keep Context Types/templates and recursive Explorer functionality, but remove them from the primary composition surface unless directly relevant.

- Template management belongs in a secondary `Templates`/settings surface.
- Explorer remains reachable after/before composing but must not open as a tiny dialog nested inside Timer.
- Reuse the hardened exact-entity navigation.

## 9. UI quality requirements
The dedicated Composer must be visually coherent with PersonalHub and usable one-handed on the Pixel 8a.

Hard requirements:
- no modal-inside-modal Composer flow;
- no nested scroll regions fighting each other;
- no huge list dumped by default;
- no raw database IDs/entity-kind identifiers;
- no clipped/overlapping controls with IME;
- primary flow understandable without technical knowledge of “HubEntity”, “Context Type”, “adapter”, etc.;
- state survives normal Activity recreation;
- denied location permission still leaves a fully usable Composer;
- basic context creation should usually fit on one screen plus at most one focused picker/search action.

Use the Android testing plugin/skill and capture/inspect screenshots of at least these states during QA:
1. fresh Composer with automatic current time/place;
2. People suggestions;
3. search results;
4. retroactive session picker with readable date/time labels;
5. detected time-based facts;
6. selected multi-entity Context before Save.

The final screenshots must be inspected for hierarchy, clipping, excessive scrolling and cryptic labels; merely passing UIAutomator selectors is insufficient.

## Non-goals
- no new graph architecture;
- no generic AI recommender;
- no map redesign;
- no Places geofence work;
- no global full-text search outside Composer;
- no rewrite of Timer/People/Places domain logic;
- no automatic assertion of uncertain relationships without user visibility;
- no unrelated aesthetic cleanup.

## Acceptance
PASS only if:
1. Timer New Session no longer contains any embedded Hub Context/People/Place Composer UI and is restored to a focused Timer editor.
2. PersonalHub home has a dedicated top-level Composer destination.
3. Composer attempts current geolocation immediately and uses it to prefill/rank Places.
4. Current/running Timer time is automatically represented and editable.
5. Historical session chooser uses human date/start/end/title, never opaque IDs.
6. People suggestions rank by current scope/place history and show only a small top set; search handles the long tail.
7. Places show at most 5 nearest candidates when no exact place is inferred.
8. Candidate ranking improves deterministically as selected Context pieces accumulate.
9. transactions, intake events and WordSessions are detected from the selected time interval without requiring default type-chip browsing; ambiguity remains user-visible/editable.
10. Retroactive Context creation works by changing time/place anchors and recomputes suggestions.
11. Every registered entity kind remains manually reachable through a secondary escape hatch.
12. Templates/Explorer remain functional but are no longer crammed into Timer or the main Composer flow.
13. Save produces normal N-ary Context members and reverse traversal still works.
14. targeted unit/query tests + recreation tests + Pixel QA + screenshot review PASS.
15. existing data, migrations, export/import, SyncJournal and architecture boundaries remain valid.

Follow the PersonalHub bootstrap for final APK/install on Pixel and notification. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, Timer restoration, Composer entry/UX, auto time/place behavior, recommendation algorithm, time-derived detection, retroactive flow, QA screenshots/device test, migration/schema impact, commit SHA, blocker.