PROMPT_ID: 681395

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Complete the pending Places work as one coherent substantial goal so Codex reuses the same Place/history/location/map context and performs one final build/install/QA instead of three separate sessions:

1. canonical manual check-in now + retroactive visit creation, overlap disambiguation and `Dov'ero?` history queries;
2. sortable canonical place metrics plus current-location map centering and marker→Place navigation;
3. persistent ENTER/EXIT geofence alerts using Android geofencing, without turning alerts into visits.

These are internal phases of ONE Places goal. Capture the PersonalHub base version once and set `target = base + 1`; increment `version.txt` exactly once. Run narrow checks after each phase, but perform only one explicit final APK build/install/device QA after all phases pass.

# Token/work discipline
- Read only phase-local files when entering a phase; do not front-load the entire union.
- Reuse already verified Place IDs, visit APIs, location state, stats projections, navigation contracts and tests from earlier phases.
- If a listed symbol moved, one targeted search for that exact symbol is allowed; no Places-wide or repo-wide exploration.
- No repeated bootstrap, equivalent location experiments, repeated builds or duplicate QA between phases.
- Report unrelated issues without investigating unless they block acceptance.
- Stop immediately after consolidated PASS.

# Phase A — canonical visits, manual check-in and `Dov'ero?`

## Starting files
Read in grouped passes only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInPolicy.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitMapper.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitUiModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/LuoghiHomeViewModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/home/HomeScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryDialogs.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryScreen.kt`

If current history includes Timer-backed intervals, use the canonical visit/query path already present. Resolve one renamed/new exact API only if directly referenced; no directory scan.

## A1. Overlap disambiguation
- zero in-radius candidates: preserve Unknown;
- exactly one: automatic Match;
- two or more: always explicit Ambiguous selection containing all realistic matching candidates; never auto-pick merely because one center is nearer;
- persist only the user-selected canonical Place ID;
- cancellation creates no check-in.

## A2. Manual check-in now
Add a clear Place action equivalent to “Check-in now”. It must create/update the SAME canonical visit/history model used by automatic and Timer-backed history, not a parallel table or special log.

- Timestamp starts at current time.
- If the canonical model supports open visits, create a safe open visit that can later be checked out/closed through the existing model; otherwise add only the minimum canonical open-visit support needed rather than inventing a point-event surrogate.
- Reject accidental duplicates/conflicts with another active/incompatible visit according to canonical domain rules.
- Manual current check-in must appear in normal history/stats and survive reopen.

## A3. Retroactive manual visit
- Add a clear Place action to create a historical visit with check-in date/time and check-out date/time; allow an open historical visit only if safely supported by the same canonical model.
- Reject checkout-before-checkin, conflicts/overlaps and accidental duplicates according to current domain rules.
- Preserve cheap provenance if already supported, without forking downstream queries.
- Manual visits participate in normal history/stats exactly once.

## A4. `Dov'ero?`
- Provide date+time selection.
- If the instant is inside a canonical visit, show that Place.
- Otherwise show the immediately preceding and following recorded Places and describe the interval as traveling/going from the former to the latter.
- Handle only-previous, only-next and no-data explicitly. Never fabricate a route or actual position.
- Use targeted/indexed lookups; add an index only if the real query justifies it.

Targeted proof: 0/1/2+ overlap including >10m center-distance difference; cancellation and selected persistence; current manual check-in + reopen; valid historical interval, boundary/conflict/duplicate validation; `Dov'ero?` inside, exact boundaries, between, only previous, only next, no data.

# Phase B — list sorting and map navigation

## Starting files
Reuse Phase A files where already read and add only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/places/PlaceListUiModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/places/PlaceListItem.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MapViewerActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/mapviewer/MapViewerRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/location/LocationCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/stats/StatsCapsule.kt`

Known starting facts: `PlaceListUiModel` already exposes total time, visit count and last visit; global map currently centers on marker averages; marker identity exists upstream but is dropped by the overlay model. Reuse the final canonical visit/stats projection from Phase A rather than rediscovering it.

## B1. Sorting
Add compact sorting by:
- distance from current location;
- last visit;
- total time;
- visit count;
with explicit ASC/DESC for each.

Semantics:
- distance ASC nearest, DESC farthest;
- last visit ASC oldest, DESC newest;
- total time/count numeric ASC/DESC;
- unknown distance sorts after known distance in both directions;
- never-visited sorts after known last visit in both directions;
- stable final tie-breaker such as normalized nickname;
- no persisted Place mutation just to sort.

Distance must reuse the existing foreground/current-location pipeline, refresh reasonably when relevant/resumed, calculate straight-line local distance, avoid continuous polling/network routing, and degrade clearly when permission/location is unavailable. Preserve selected sort through normal recreation; persist across restarts only if trivial within an existing preference pattern.

## B2. Map center
When opening the global Places map:
- if foreground location permission + current/recent location are available, center automatically on current position at useful zoom;
- optionally show current-position indicator if cheap with existing osmdroid setup;
- do not keep recentering after user manual pan/zoom;
- if unavailable/denied, safely fall back to current marker-based bounds/centering.

No background permission is added for this foreground map behavior.

## B3. Marker navigation
- Every individual Place marker opens the canonical Place detail by stable UUID.
- Preserve UUID through overlay model; never resolve by title/coordinates.
- Reuse the smallest existing in-app navigation/intent contract; do not export a public Activity unnecessarily.
- Back stack remains coherent.
- Cluster marker never arbitrarily opens one member; preserve/implement sensible cluster zoom/info behavior.

Targeted proof: all sort criteria both directions with deterministic null handling; current-location center + unavailable fallback; individual marker opens correct UUID; cluster does not choose arbitrary member.

# Phase C — geofence ENTER/EXIT alerts

## Starting files
Reuse already-read Places/location files and add only:
- `feature/luoghi/src/main/AndroidManifest.xml`
- `app/src/main/AndroidManifest.xml`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`

Only if it materially reduces code, read exactly these Timer notification-pattern files and nothing else from Timer alerts:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceNotifier.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerScheduler.kt`

Create the minimum new geofence registration/receiver classes required.

Required behavior:
- A canonical Place can configure enabled ENTER, EXIT or both, with a human-readable notification message/settings sufficient for the feature.
- Use Android `GeofencingClient`/platform geofences, never continuous background polling.
- Persist configuration in the canonical PH database; if schema changes, add the safe migration required by current architecture. Do not invent a second DB.
- Request/guide foreground/background location permissions according to target Android rules. Never claim background geofencing works without required permission.
- Reconcile register/unregister idempotently when Places/config changes.
- Restore registrations after reboot and app update; permission revocation must not crash-loop.
- Deduplicate repeated platform transitions so one logical transition does not spam notifications.
- Notification `contentIntent` opens the relevant Place/module.
- Geofence alerts do NOT create visits/check-ins merely because an ENTER/EXIT notification fires. Canonical visit semantics from Phase A remain separate unless an existing explicit product rule already says otherwise.

Targeted proof: configuration persistence, ENTER/EXIT mapping, reconciliation, dedup, permission-disabled state, reboot/update restoration, and one representative transition handling check. If deterministic platform transition simulation is unavailable, verify receiver handling through the narrowest reliable injection and report the platform limitation; do not fake PASS.

# Consolidated final verification
After A+B+C targeted checks pass:
- run the minimum combined Places regression tests covering canonical history/stats, map/location and geofence configuration;
- perform ONE explicit final PersonalHub APK build;
- safely install/update that final APK on the project-required Android targets per the governing PersonalHub protocol;
- perform ONE concise integrated QA pass covering: manual current check-in, retroactive visit, `Dov'ero?`, one sort, map current-location center, marker→detail navigation, geofence configuration/permission state and representative transition handling;
- do not repeat already-proven tests unless final integration contradicts them.

# Non-goals
No map-engine replacement, routes/directions, continuous GPS tracking, generic automation framework, Timer alert redesign, duplicate visit system, broad Places redesign or unrelated statistics cleanup.

# Acceptance / stop
PASS only when all three original Places tasks are satisfied together and the consolidated final verification passes. Stop immediately after PASS; do not inspect later roadmap tasks.

Final output only: `PROMPT_ID`, `RESULT`, canonical manual/retroactive visit semantics, overlap/Dov'ero behavior, sorting/map behavior, geofence config/permissions/dedup, targeted tests, final device QA, version, commit SHA.