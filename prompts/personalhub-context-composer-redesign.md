PROMPT_ID: 214756

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Replace the current embedded Hub Context UI with a dedicated top-level PersonalHub **Composer** optimized for fast context construction. Reuse the existing N-ary Hub Context engine, adapters, templates and Explorer; do NOT build a second graph/recommender architecture.

Capture the PersonalHub base version once; `target = base + 1` exactly once.

# Verified current state — do not rediscover
Current `PersonalHub/main` confirms the redesign is still needed:
- `app/MainActivity.kt` only renders existing `HubModule` destinations; there is no top-level Composer.
- `LauncherShortcutsCapsule.kt` has only People, Timer, Places, Substances, WordPulse and Soldi; Composer is not a normal module and need not become a launcher shortcut.
- `SessionEditDialog.kt` still creates `rememberSessionContextEditorState(session.id)`, saves Context during session save and renders both `SessionContextEditor(...)` and `HubContextLinks(...)` inside the Timer dialog.
- existing Hub Context runtime/adapters for People, Timer sessions, Places, Soldi transactions, Substances, WordPulse and Resources are already valid infrastructure and must be reused.

Do not redo prior Hub Context hardening, entity navigation, bounded search or adapter work unless a focused acceptance check proves a missing prerequisite.

# Starting files
First grouped pass only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`
- `core/hub-context/.../HubContextComposer.kt`
- `core/hub-context/.../HubContextExplorer.kt`
- `core/hub-context/.../HubContextRepository.kt`
- `core/hub-context/.../HubContextRuntime.kt`
- `contracts/database/.../HubEntityAdapter.kt`
- `contracts/database/.../HubContextDao.kt`
- `feature/multitimetracker/.../ui/components/SessionEditDialog.kt`
- existing Hub adapters for Timer, Places, People, Soldi, Substances and WordPulse only as needed by a concrete Composer operation.

For current geolocation, do ONE targeted lookup for the existing Places location pipeline and reuse it. For timestamped Substance data, do ONE targeted lookup for the canonical intake-event DAO/model if needed. No general module scans.

# 1. Restore Timer session editor
Remove Composer/Context editing from New/Edit Session:
- no `SessionContextEditor` or embedded `HubContextLinks` in the session modal;
- Timer save/create/edit must not depend on saving Context;
- keep normal session title/time/tags behavior and existing Context graph data untouched.

If an existing session needs a Context entry point, at most expose a small explicit action outside the New Session modal; Composer remains primary.

# 2. Dedicated full-screen Composer
Add Composer as a clear top-level PersonalHub home destination, but not a new domain owner. Use a full-screen Material 3 surface, not nested dialogs.

Primary layout:
- top app bar;
- compact **Current context** header with time/session + place;
- one search field;
- human-readable type chips for things the user actually chooses explicitly (not raw module/entity identifiers);
- at most ~5 ranked suggestions for active type;
- compact always-visible selected pieces;
- obvious Save action;
- templates/manual advanced controls in a secondary surface.

Never show raw IDs or identifiers such as `word_session`/`HubEntity`. IT/EN strings only.

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
One search field sits above type chips. An active type searches only that kind/capability. Do not dump large lists; show a small ranked set then search/pagination. Every registered entity kind remains reachable through a secondary `More` / `Add manually` escape hatch.

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

# 6. Retroactive contexts, templates, Explorer
Changing time/session or place is the retroactive workflow; rerank recommendations/detections immediately. No separate maze.

Keep templates/Context Types and recursive Explorer functional, but move them away from the primary composition surface. Explorer must not open as a tiny nested Timer dialog. Reuse exact-entity navigation already implemented.

# UI quality
Hard requirements:
- no modal-inside-modal composition;
- no nested fighting scroll regions;
- no hundreds-item default list;
- no raw IDs/internal entity names;
- no IME clipping/overlap;
- usable with denied location permission;
- normal Activity recreation preserves meaningful in-progress Composer state;
- basic context creation should usually fit one screen plus at most one focused picker/search action.

During final UI QA inspect screenshots of at least: fresh Composer, People suggestions, search results, retroactive session picker, detected time facts, selected multi-entity context before Save. Inspect hierarchy/clipping/scrolling/cryptic labels, not only selectors.

# Tests / acceptance
Use focused unit/query tests for ranking/detection plus targeted recreation/UI tests, then one consolidated Android QA. PASS only if:
1. Timer New/Edit Session no longer embeds Context UI or depends on Context save.
2. Composer is a top-level PH home destination.
3. current time/running session and place are inferred when possible and editable.
4. historical session labels are readable; no opaque IDs.
5. People/other suggestions are bounded and deterministic; search handles long tail.
6. no exact Place => at most 5 nearest candidates.
7. transactions, intake events and WordSessions are detected from selected interval with ambiguity visible/editable.
8. changing time/place supports retroactive Contexts and recomputes suggestions.
9. every registered kind remains manually reachable through secondary UI.
10. templates/Explorer remain functional outside the cluttered Timer flow.
11. Save produces normal existing N-ary Context members and reverse traversal still works.
12. existing data/export/import/sync/architecture boundaries remain valid.
13. focused tests + recreation + consolidated Pixel QA/screenshot review PASS.

Follow the current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable. Stop immediately after PASS; no unrelated cleanup/audit.

Final output only: `PROMPT_ID`, `RESULT`, Timer restoration, Composer entry/UX, auto anchors, ranking/detection, retroactive flow, schema/adapter impact, tests/screenshots/device QA, version, APK delivery, commit/push, blocker if any.
