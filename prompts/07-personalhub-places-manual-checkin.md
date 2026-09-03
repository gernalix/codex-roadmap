PROMPT_ID: 653920

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Add manual historical check-in/out to every saved Place, for visits that cannot be reconstructed from current GPS.

## Requirements
- Add a clear action on each Place to create a manual visit/check-in.
- Let the user specify the relevant check-in and check-out date/time; support an open visit only if the existing Places model already supports it safely.
- Persist the canonical place ID using the same visit/history model as automatic check-ins whenever possible; do not create a parallel history system.
- Validate temporal consistency and prevent accidental duplicate/conflicting records according to existing domain rules.
- Manual records must appear in the same history/query paths as automatic visits and be distinguishable only if provenance is useful and cheap to preserve.

## Scope / safety
Minimal diff. Do not change GPS/geofence behavior. Respect existing guardrails protecting the real installed PH app/data during testing.

## Acceptance
Targeted tests cover historical interval creation, validation and history visibility. On the project-approved device/emulator, perform a focused safe UI check: add a historical visit from a Place without relying on GPS, confirm it appears in normal history, then close/reopen the module/app and confirm persistence. Use disposable/test data where possible and do not broaden into unrelated Places testing.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, persisted model/provenance, tests, device/emulator checks, commit SHA.