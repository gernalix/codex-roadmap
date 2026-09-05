PROMPT_ID: 704291

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Add enter/exit geofence alerts to canonical Places using Android's appropriate background geofencing mechanisms. Do not modify Timer alert UX except to reuse a proven shared notification pattern where genuinely useful.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/location/LocationCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/AndroidManifest.xml`
- `app/src/main/AndroidManifest.xml`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`

Only if sharing the proven Timer notification pattern reduces code, read these post-09a files in the same task:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceNotifier.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerScheduler.kt`

Do not inspect Timer alerts beyond those two files. New geofence registration/receiver classes do not exist yet; create the minimum required. If an earlier task renamed a listed symbol, use one targeted search only.

After verifying current state, increment `version.txt` exactly once by `+1` before code changes.

## Requirements
- A canonical Place can have an enabled alert for ENTER, EXIT, or both with a human-readable message/settings sufficient for the feature.
- Use `GeofencingClient`/platform geofences, not continuous location polling.
- Persist alert configuration in PH's canonical database with a safe migration if schema changes are needed.
- Request/guide foreground/background location permissions according to target Android requirements. Do not claim background geofencing works without the required permission state.
- Register/unregister geofences idempotently when Places/alerts change.
- Restore registrations after reboot and app update; handle permission revocation without crash loops.
- Deduplicate repeated platform transitions so one logical transition does not spam notifications.
- Notification `contentIntent` opens the relevant Place/module.
- Preserve Places check-in/history semantics; geofence alerts do not themselves create check-ins unless an existing explicit product rule already requires it.

## Tests / verification
Targeted tests cover configuration persistence, ENTER/EXIT mapping, registration reconciliation, dedup, permission-disabled state and reboot/update restoration. Perform one focused platform registration + representative transition check. If deterministic geofence transition simulation is unavailable, report that exact limitation and verify receiver handling through the narrowest reliable injection; do not fake PASS.

## Resource discipline
No generic alert/automation framework, route tracking, background polling or unrelated Places redesign. Use only the exact starting files, newly created geofence classes and directly relevant tests. Stop after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/config, geofence registration/restoration, permissions, dedup, tests/device check, commit SHA.
