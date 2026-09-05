PROMPT_ID: 647218

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Improve the existing Places home/map UX with explicit sortable place metrics and location-centered map navigation, without redesigning Places or changing geofence/check-in semantics.

After verifying the current state and before code changes, increment `version.txt` exactly once by `+1`.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/places/PlaceListUiModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/home/HomeScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/places/PlaceListItem.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MapViewerActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/location/LocationCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/stats/StatsCapsule.kt`

Current `PlaceListUiModel.kt` already exposes `totalTimeMs`, `visitCount`, `lastVisitAt` and hardcodes active/last-visit/name ordering. `MapViewerActivity.kt` currently centers on average marker coordinates. `MapMarkerModel` carries UUID but `MapOverlayMarker` currently drops place identity. These are the decisive starting facts; do not rediscover them.

If a preceding task introduced a new canonical visit/stats projection for Timer-backed Places, resolve it once via the exact symbol referenced by `PlaceListUiModel`/`StatsCapsule`; do not scan the repo. If a listed file was renamed, one targeted symbol search is allowed.

## 1. Places ordering
Add a compact sort control to the Places home/list with these criteria:
- **Distanza da dove sono ora**
- **Ultima visita**
- **Tempo totale**
- **Numero visite**

For every criterion provide an explicit **ascending / descending** option/toggle.

Required semantics:
- distance ASC = nearest first; DESC = farthest first;
- last visit ASC = oldest visited first; DESC = most recently visited first;
- total time/count use numeric ASC/DESC;
- places without coordinates sort after places with known distance in both directions;
- places never visited sort after places with a known last visit in both directions;
- use a deterministic final tie-breaker such as normalized nickname so order does not jump randomly;
- do not mutate persisted Place data merely to sort it.

For distance:
- reuse the existing foreground/current-location mechanism;
- obtain/refresh a reasonable current location when distance sorting becomes relevant or Places home resumes, rather than continuous polling;
- compute local straight-line distance from current coordinates; no Maps/network routing call;
- if permission/location is unavailable, keep the UI usable, explain the unavailable distance state concisely, and do not fabricate distances.

Preserve the selected sort criterion/direction across normal Activity/configuration recreation. Persist it across app restarts only if the existing Places preference/state pattern makes that trivial; do not add a new persistence subsystem solely for this.

## 2. Global Places map centers on current position
When the Places map opens:
- if foreground location permission is granted and a current/recent location is available, automatically center the map on the user's current position;
- use a useful existing/default zoom appropriate for nearby places;
- optionally show the current-position indicator if supported cheaply by the current osmdroid setup;
- do not continuously track location solely to keep recentering after the user manually pans/zooms;
- if permission/location is unavailable, fall back safely to the current marker-based centering/bounds behavior rather than showing a broken map.

Do not add background location permission for this feature.

## 3. Tapping a Place marker opens that Place
For every **individual Place marker**, tapping the marker must open/navigate to the canonical Place detail screen for that marker's UUID.

- Preserve stable Place UUID through the map overlay model instead of resolving by title/coordinates.
- Reuse the existing in-app Places detail navigation with the smallest explicit intent/deep-link/result contract needed between `MapViewerActivity` and Places `MainActivity`; do not expose a public Activity unnecessarily.
- Returning from Place detail/map must behave coherently with the existing back stack.
- A cluster marker representing multiple Places must **not** arbitrarily open one Place. Preserve/implement a sensible cluster action such as zoom/show cluster info using the existing map behavior; only individual markers navigate directly.

## Scope / non-goals
No map-engine replacement, route/directions feature, continuous GPS tracking, geofence-alert work, broad Places redesign, database schema migration, or unrelated statistics refactor.

## Resource discipline
Use only the exact starting files plus the one resolved canonical stats projection if prior tasks created it. Batch reads/searches. No repo-wide scan, no redundant location experiments, no unrelated cleanup. Run targeted unit/UI tests first and one focused emulator/device flow only for map/location/navigation behavior. Stop immediately after PASS.

## Acceptance
- Places can be sorted by distance/current location, last visit, total time and visit count in both ASC and DESC directions;
- null/missing distance and never-visited ordering is deterministic and correct;
- canonical metrics include Timer-backed visits exactly once where the preceding cross-module tasks provide them;
- with a simulated/available current position, opening the global map centers on that position rather than marker-average coordinates;
- location unavailable/denied has a safe marker-based fallback;
- tapping an individual Place marker opens the correct canonical Place detail by UUID;
- cluster markers never arbitrarily select a member;
- targeted tests/build PASS plus one focused safe emulator/device verification of sort + map center + marker navigation.

Final output only: `PROMPT_ID`, `RESULT`, sort semantics/state, current-location behavior, map centering, marker navigation/cluster behavior, tests/device check, commit SHA.
