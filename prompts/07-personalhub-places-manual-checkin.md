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

## Scope
Minimal diff. Do not change GPS/geofence behavior.

## Acceptance
Targeted tests cover historical interval creation, validation and history visibility; focused UI verification confirms a visit can be added from a Place without GPS.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, persisted model/provenance, tests, commit SHA.