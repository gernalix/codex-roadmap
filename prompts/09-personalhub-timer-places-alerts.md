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
Minimal architecture needed to share alert behavior; no generic automation engine, no unrelated notification refactor. Respect existing guardrails protecting the real installed PH app/data; device tests must not uninstall/wipe/reset the real app or user data.

## Acceptance
Targeted tests cover Timer alert CRUD/triggering and Places enter/exit trigger mapping/deduplication. On the project-approved device/emulator, focused checks must prove Timer alert create/edit/enable-disable/delete and at least one real notification firing. Verify Places geofence registration/permissions and a representative transition notification; if emulator/device geofencing cannot be deterministically exercised, use the narrowest reliable platform registration + trigger-handling verification and report that limitation rather than faking PASS. Verify relevant behavior survives app reopen/restart where restoration is part of the implementation.

Stop after PASS; no broader notification/location audit.

Final output only: `PROMPT_ID`, `RESULT`, Timer UX fixed, Places geofence behavior, permissions/restoration behavior, tests, device/emulator checks, commit SHA.