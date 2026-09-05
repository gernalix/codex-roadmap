PROMPT_ID: 704291

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Add enter/exit geofence alerts to canonical Places using Android's appropriate background geofencing mechanisms. Do not modify Timer alert UX except to reuse a proven shared notification pattern where genuinely useful.

## Starting scope
Use project_id/MegaVault/AGENTS, then inspect only:
- canonical `PlaceEntity`/Places repository and place-detail UI;
- current app manifest/location permission flow;
- the current post-09a alert/notification helpers only if reuse reduces duplication;
- Android geofence registration/receiver/restoration code added by this task.

Do not scan Timer or Substances broadly.

## Requirements
- A canonical Place can have an enabled alert for ENTER, EXIT, or both with a human-readable message/settings sufficient for the feature.
- Use GeofencingClient/platform geofences, not continuous location polling.
- Persist alert configuration in PH's canonical database with safe migration if schema changes are needed.
- Request/guide foreground/background location permissions according to the target Android requirements. Do not claim background geofencing works without the required permission state.
- Register/unregister geofences idempotently when Places/alerts change.
- Restore registrations after reboot and app update; account for permission revocation without crash loops.
- Deduplicate repeated platform transitions so one logical transition does not spam notifications.
- Notification contentIntent opens the relevant Place/module.
- Preserve Places check-in/history semantics; geofence alerts do not themselves create check-ins unless an existing explicit product rule says so.

## Tests / verification
Targeted tests cover configuration persistence, ENTER/EXIT mapping, registration reconciliation, dedup, permission-disabled state and reboot/update restoration. Perform a focused platform registration + representative transition check. If deterministic geofence transition simulation is unavailable, report that exact limitation and verify receiver handling through the narrowest reliable injection; do not fake PASS.

## Resource discipline
No generic alert/automation framework, route tracking, background polling or unrelated Places redesign. Stop after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/config, geofence registration/restoration, permissions, dedup, tests/device check, commit SHA.
