PROMPT_ID: 731468

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Fix the current Places/Luoghi regression where valid history mutations can be rejected because an unrelated overlap already exists somewhere else in the user's historical visit data.

User-visible broken operations include manual check-in/check-out, retroactive visit creation and editing visit/event times. Do not redesign Places; fix only the shared validation semantics causing these writes to fail.

# Root cause already localized — do not rediscover broadly
Current `PersonalHub/main`, introduced in the Places history/map/geofencing work at commit `45edd082fe8323478cf7826cabe845129be57ad3`:

- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
  - `validateNewEvents(...)` builds `candidateEvents = existing + newEvents` and rejects whenever `HistorySessionCalculator.hasAnyOverlap(candidateEvents, now)` is true;
  - `validateEventReplacement(...)` was changed from place-scoped overlap checking to the same global `hasAnyOverlap(...)` check;
  - therefore an overlap already present elsewhere in historical data can poison otherwise-valid new/edit operations.
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
  - `hasAnyOverlap(...)` returns true if ANY calculated session has `OVERLAP`.
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInCapsule.kt`
  - manual check-in, manual checkout, retroactive visit and event edit all route into the affected repository validation paths.

Previous regression coverage was insufficient:
- `feature/luoghi/src/test/java/com/gernalix/luoghi/PlacesHistoryMapGeofencingTest.kt` deletes/recreates the DB for each test, so it never exercises a legacy/pre-existing unrelated overlap;
- the previous physical QA used TCL-6102H and only checked read/UI surfaces such as sort, `Where was I?`, and crash absence; it did not actually perform check-in/out or history edits.

Do NOT scan Places generally and do NOT redo map/geofence/sort work.

# Correct semantics
Existing unrelated historical anomalies must not globally block future valid writes.

Validation must remain fail-closed for the operation being attempted:
- reject a new visit/check-in if that operation creates a new overlap, invalid second open visit, duplicate, or invalid timestamp;
- reject an edit if that edit creates or worsens a conflict involving the affected session/event;
- allow a valid independent mutation even when some unrelated historical session is already overlapping;
- allow an edit that resolves or reduces an existing conflict rather than requiring the entire historical DB to be globally clean first;
- preserve checkout-before-checkin, duplicate, orphan-checkout and other current invariants;
- do not silently rewrite, delete, merge or normalize the user's pre-existing overlapping history.

Prefer comparing relevant conflict state before vs after, or otherwise restricting validation to conflicts introduced/affected by the candidate mutation. Do not merely remove overlap validation.

# Starting files
Read only these first:
1. `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
2. `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
3. `feature/luoghi/src/test/java/com/gernalix/luoghi/PlacesHistoryMapGeofencingTest.kt`

Read `CheckInCapsule.kt` only if needed to confirm routing; no change should be required there unless evidence proves otherwise. Read `LuoghiHomeViewModel.kt` only if the failure/result mapping itself is also wrong. No repo-wide search.

# Required regression tests
First reproduce the bug BEFORE patching with a focused fixture containing a pre-existing overlap unrelated to the candidate mutation. Then fix it.

With that pre-existing unrelated overlap still present and unchanged, prove:
1. a new non-overlapping manual visit/check-in succeeds;
2. a valid open visit can be checked out;
3. an independent event timestamp edit succeeds;
4. a new mutation that actually creates an overlap is still rejected as `OVERLAP`;
5. an edit that introduces/worsens overlap is rejected;
6. an edit that resolves/reduces an existing overlap is allowed;
7. existing unrelated overlap rows are not modified as a side effect;
8. geofence automatic ENTER/EXIT still goes through the same canonical safety rules.

Use deterministic repository/domain tests for the matrix above. No schema change should be necessary.

# Physical regression QA
Because the previous physical smoke did not execute mutation paths, perform one focused **Pixel** smoke using an isolated QA package/database/fixture, never destructive edits to the user's real PersonalHub data.

Seed the QA data with a pre-existing unrelated overlap, then through the actual Places UI verify at minimum:
- manual check-in or retroactive valid visit succeeds;
- checkout succeeds where applicable;
- editing an independent event time succeeds;
- an intentionally conflicting mutation is still rejected.

If a temporary QA/clone package is installed on Pixel, remove it before PASS. Do not substitute a read-only navigation smoke for these write assertions.

# Scope / stop
Preserve existing Places history, stats, undo/redo, audit, export/sync, map, geofence and UI behavior outside this validation regression. No cleanup/refactor.

Capture the PersonalHub version once and set `target = base + 1` exactly once. Follow the current remote PersonalHub bootstrap for final tested APK, final Pixel install and APK delivery.

PASS only after the pre-existing-overlap regression is reproduced, fixed, covered by focused automated tests, and the Pixel mutation smoke passes. Stop immediately; do not inspect later roadmap items.

Final output only: `PROMPT_ID`, `RESULT`, reproduced root cause, validation fix, regression matrix, Pixel mutation smoke, version, APK delivery, commit/push, blocker if any.
