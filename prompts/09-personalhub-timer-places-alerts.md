PROMPT_ID: 825174

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Make alerts usable in Personal Hub: repair/redesign Timer alerts so alerts can actually be created and managed, then extend the same alert concept to Places with geofencing triggers.

Known issue: the current Timer alert UI is functionally unusable and alert creation is not possible from the intended flow. Treat existing alert domain code as reusable only after verifying it.

## Timer
- Trace the smallest existing alert domain/UI path.
- Provide a coherent create/edit/delete/enable-disable flow integrated with the Timer UI conventions.
- Ensure an alert can be created from the relevant timer/session context and actually fires under its intended condition.
- Remove or replace broken/dead alert UI only as needed; do not redesign unrelated Timer screens.

## Places
- Reuse the common alert infrastructure where sensible.
- Allow a Place to have geofence-based alerts for entering and/or leaving that canonical place.
- Use Android's appropriate geofencing/background mechanisms rather than continuous location polling.
- Handle permissions and reboot/app-update restoration according to existing PH patterns/platform requirements.
- Avoid duplicate notifications for one transition.

## Safety / scope
Minimal architecture needed to share alert behavior; no generic automation engine, no unrelated notification refactor.

## Acceptance
Targeted tests cover Timer alert CRUD/triggering and Places enter/exit trigger mapping/deduplication. Focused device/emulator checks prove a Timer alert can be created and a representative geofence transition produces the configured Places alert (or, if emulator geofencing cannot be deterministically exercised, verify the platform registration plus trigger handling with the narrowest reliable test).

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, Timer UX fixed, Places geofence behavior, permissions/restoration behavior, tests, commit SHA.