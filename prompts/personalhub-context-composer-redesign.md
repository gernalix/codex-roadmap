PROMPT_ID: 214756

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Replace the current embedded Hub Context UI with a dedicated top-level PersonalHub **Composer** optimized for fast context construction. Reuse the existing N-ary Hub Context engine, state, adapters, templates and Explorer; do NOT build a second graph/composition architecture.

Capture the PersonalHub base version once; `target = base + 1` exactly once.

# Verified current state — do not rediscover
Current `PersonalHub/main` confirms the redesign is still needed, but substantial composition infrastructure already exists:
- `app/MainActivity.kt` has no top-level Composer destination.
- `SessionEditDialog.kt` still creates `rememberSessionContextEditorState(session.id)`, saves Context during session save and renders `SessionContextEditor(...)` + `HubContextLinks(...)` inside Timer.
- `core/hub-context/.../HubContextComposer.kt` already implements `HubComposerState` with save/restore of members/query/kind/resource fields, adapter-backed search (`adapter.search(query, 20)`), canonical entity/resource creation, Context create/update, Context Types/templates and a current `HubContextComposerDialog` UI.
- that existing dialog already proves basic member add/remove/search/template/resource composition, but it is an `AlertDialog`, exposes raw adapter `entityKind` labels and is not the desired primary UX. Refactor/reuse its state/services rather than replacing them.
- `HubContextComposerDeviceTest` already proves create → save → reopen → add another entity through the current composer. Preserve/reuse that coverage instead of rebuilding the same persistence test.
- existing Hub adapters for People, Timer sessions, Places, Soldi transactions, Substances, WordPulse and Resources are valid infrastructure.

Do not redo prior Hub Context hardening, exact-entity navigation, bounded search, template CRUD, generic composition persistence or adapter work unless a focused acceptance check proves a missing prerequisite.

# Starting files
First grouped pass only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextComposer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextExplorer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/HubContextComposerDeviceTest.kt`

Read `PersonalHubApplication.kt`, DAO/contracts or a specific existing Hub adapter only when a concrete new Composer operation requires it. For current geolocation, do ONE targeted lookup for the existing Places location pipeline. For timestamped Substance data, do ONE targeted lookup for the canonical intake-event DAO/model. No general module scans.

# 1. Restore Timer session editor
Remove Composer/Context editing from New/Edit Session:
- no `SessionContextEditor` or embedded `HubContextLinks` in the session modal;
- Timer save/create/edit must not depend on saving Context;
- keep normal session title/time/tags behavior and existing Context graph data untouched.

If an existing session needs a Context entry point, at most expose a small explicit action outside the New Session modal; Composer remains primary.

# 2. Promote/refactor current Composer into a full-screen top-level UX
Add Composer as a clear top-level PersonalHub home destination, but not a new domain owner or launcher shortcut. Prefer reusing/refactoring `HubComposerState` and current composition services rather than creating parallel state.

Primary full-screen Material 3 layout:
- top app bar;
- compact **Current context** header with time/session + place;
- one search field;
- human-readable type chips only for things the user actually chooses explicitly;
- at most ~5 ranked suggestions for active type;
- compact always-visible selected pieces;
- obvious Save action;
- templates/resources/manual advanced controls in secondary surfaces.

Never show raw IDs or identifiers such as `word_session`, `entityKind` or `HubEntity`. IT/EN strings only.

# 3. Automatic anchors: time/session + place
On open:

**Time**
- if one relevant Timer session is running, preselect it;
- if several make the choice ambiguous, show a compact choice;
- otherwise default to editable `Now`;
- historical session labels must be human-readable date/start/end/title, never `Session 589`;
- long history appears only after user search/picker via existing bounded APIs.

**Place**
- use existing Places location/permission pipeline;
- if current coordinate is clearly inside a saved Place radius, preselect it;
- overlapping matches: show best few, editable;
- no exact match: show at most 5 nearest saved Places with distance;
- denied/unavailable location: degrade to recent/contextual suggestions + search.

Both anchors remain editable so retroactive Context creation needs no separate mode.

# 4. Search + deterministic recommendations
Keep/reuse the current adapter-backed search path, but change default presentation: do not render its current up-to-20 raw result list automatically. An active human-readable type searches only that kind/capability; default suggestions are a small ranked set, with search/pagination for the long tail. Every registered entity kind remains reachable through a secondary `More` / `Add manually` escape hatch.

Implement a simple deterministic ranking over existing Context history, no ML/vector DB. Prefer candidates by:
1. co-occurrence with all selected anchors/pieces;
2. association with selected Place when relevant;
3. recent matching co-occurrence;
4. overall Context frequency;
5. stable human-readable tie-break.

For People, place/context co-occurrence should usually put historically associated people in the first 3–5 when evidence exists.

# 5. Detect facts from selected time
Do not force manual browsing for facts already recorded during the selected interval. Detect compact candidates from:
- Soldi transactions;
- timestamped Substance **intake events**;
- overlapping WordPulse sessions.

If Hub Context currently exposes only generic `substances/substance`, add only the minimum canonical `substances/intake` identity/adapter needed for correct time semantics; do not pretend a Substance identity itself happened at a timestamp.

Show these in **Detected from this time**:
- clear/high-confidence facts may be preselected;
- ambiguous facts remain one-tap suggestions;
- every auto-selection is visible/removable;
- changing time/place recomputes automatic candidates while preserving valid manual selections;
- only currently selected items become Context members on Save.

No silent permanent relationship from weak coincidence.

# 6. Retroactive contexts, templates, resources, Explorer
Changing time/session or place is the retroactive workflow; rerank recommendations/detections immediately. No separate mode.

Preserve current canonical creation/resource support, templates/Context Types and recursive Explorer, but move advanced/template/resource management away from the primary composition surface. Explorer must not open as a nested Timer dialog. Reuse exact-entity navigation already implemented.

# UI quality
Hard requirements:
- no modal-inside-modal composition;
- no nested fighting scroll regions;
- no large default list;
- no raw IDs/internal entity names;
- no IME clipping/overlap;
- denied location permission still leaves Composer usable;
- reuse/extend the current `Saver` behavior so meaningful in-progress state survives Activity recreation;
- basic context creation should usually fit one screen plus at most one focused picker/search action.

During final QA inspect screenshots of: fresh Composer, People suggestions, search, retroactive session picker, detected time facts, selected multi-entity context before Save. Check hierarchy/clipping/scrolling/cryptic labels, not only selectors.

# Tests / acceptance
Extend/reuse existing Composer device coverage; do not duplicate its already-proven generic save/reopen flow unless affected. Add focused unit/query tests for new ranking/detection plus targeted recreation/UI tests, then one consolidated Android QA.

PASS only if:
1. Timer New/Edit Session no longer embeds Context UI or depends on Context save.
2. Composer is a top-level PH home destination.
3. current time/running session and place are inferred when possible and editable.
4. historical session labels are readable; no opaque IDs.
5. People/other suggestions are bounded and deterministic; search handles long tail.
6. no exact Place => at most 5 nearest candidates.
7. transactions, intake events and WordSessions are detected from selected interval with ambiguity visible/editable.
8. changing time/place supports retroactive Contexts and recomputes suggestions.
9. every registered kind remains manually reachable through secondary UI.
10. templates/resources/Explorer remain functional but outside the cluttered primary flow.
11. Save still uses the existing N-ary Context model and reverse traversal works.
12. existing data/export/import/sync/architecture boundaries remain valid.
13. focused tests + recreation + consolidated Pixel QA/screenshot review PASS.

Follow the current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable. Stop immediately after PASS; no unrelated cleanup/audit.

Final output only: `PROMPT_ID`, `RESULT`, Timer restoration, Composer entry/UX, reused existing Composer state, auto anchors, ranking/detection, retroactive flow, schema/adapter impact, tests/screenshots/device QA, version, APK delivery, commit/push, blocker if any.
