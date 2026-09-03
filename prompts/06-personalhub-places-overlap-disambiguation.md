PROMPT_ID: 128463

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Add Places check-in disambiguation when the current GPS position is simultaneously inside more than one saved place/geofence.

## Requirements
- Reuse the existing Places location/geofence matching pipeline; inspect only those paths and the check-in UI/state.
- When exactly one place matches, preserve current automatic behavior.
- When multiple places match, do not choose arbitrarily: show a prompt/list containing all matching places and let the user select the intended one.
- Record only the selected canonical place ID.
- Handle cancellation safely without a false check-in.
- Keep background/location behavior efficient; no new continuous polling solely for this feature.

## Scope / safety
Minimal diff; no unrelated Places redesign or geofence tuning. Respect existing guardrails protecting the real installed PH app/data during testing.

## Acceptance
Targeted tests cover zero/one/multiple matches and cancellation. Perform a focused device/emulator check using a safe test state/location simulation where supported: confirm the selector appears for overlapping matches, cancellation creates no check-in, and selecting a place persists the intended canonical place. Do not broaden into unrelated location testing.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, matching/selection behavior, tests, device/emulator checks, commit SHA.