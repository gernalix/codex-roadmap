PROMPT_ID: 815367

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 2. On top of the phase-1 safe command/stock/archive foundation, implement coherent scheduling/intake semantics, interaction editing/enforcement, persisted interaction countdowns and durable state-driven notifications.

## Prerequisite
Verify narrowly that phase 1 command boundary, parent-row integrity, canonical substance-name rule, stock ledger and archive lifecycle exist. If materially absent, stop BLOCKED. Do not recreate phase 1.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/UtcDateCodec.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/notifications/SostanzeNotificationScheduler.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/Entities.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/SostanzeDao.kt`
- `feature/sostanze/src/main/AndroidManifest.xml`
- `app/src/main/AndroidManifest.xml`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`

Resolve the phase-1 command/domain type once from exact imports only. No module scan. Increment `version.txt` exactly once by +1.

## Scheduling + intake
Support explicit dose times, applicable days, start/end, forever and PRN; use frequency only with precise semantics. Historical due/taken/missed state must use the regimen valid for that period. Never create future/phantom missed doses or fake midnight timestamps; completion respects dose quantities.

All intake paths use one authoritative atomic command validating active/archive state, therapy/schedule timing, BLOCK/WARN interactions, quantity/unit, stock and duplicate/idempotency. Return explicit outcomes including success, warning, blocked, early dose, insufficient stock and duplicate. Manual historical intake/edit/delete must preserve stock/history invariants.

A successful home intake must not make that substance disappear for the rest of the day. The domain/ViewModel state must continue exposing the same substance plus the next recommended intake timestamp when one exists, so the final UI can show that time in small text inside the same button/card.

## Interactions + countdown
- PRN/macros cannot bypass BLOCK; WARN remains distinct; reject self/invalid/duplicate rules and use the actually most restrictive active rule.
- Interaction state must never require hiding or disabling unrelated home buttons. A BLOCK rule is enforced when the user taps the affected action and returns an explicit blocked result; the button itself remains present and tappable.
- Fix editing persistence: pressing OK after editing an existing interaction must atomically update that exact rule and its targets. Reopen/edit/save repeatedly and the newest values must be the persisted source of truth; never keep the first-ever draft forever.
- When a successful intake starts an interaction wait window, expose/persist enough canonical state to render a live countdown on Home labeled with the triggering substance/button name and its expiry. Support multiple simultaneous active windows without one silently replacing another.
- At expiry, schedule exactly one interaction-end notification. Countdown/notification state must survive process death and be reconciled after reboot, app update, time change and timezone change.
- Macros execute through the same intake command, return per-item outcomes and resist retry/double-tap duplication.

## Notifications
Drive dose, missed-dose and interaction-end reminders from canonical persisted schedule/domain state. Reconcile schedule/cancel/reschedule on relevant mutations and restore after BOOT_COMPLETED, MY_PACKAGE_REPLACED, TIME_SET and TIMEZONE_CHANGED where required. No stale/expired alarms, unrelated PendingIntent collisions or duplicate retries. Permission denial fails gracefully. Use exact alarms only when concretely required. Notifications deep-link into relevant Substances UI.

If schema migration is required, keep it minimal/non-destructive and migration-tested.

## Tests / acceptance
Cover:
- schedule boundaries/midnight/timezone and no future missed doses;
- quantity completion, retry/double-tap and early-dose contract;
- successful intake keeps the substance in home state and exposes the next recommended time;
- BLOCK/WARN and PRN/macro behavior while buttons remain logically available;
- editing the same interaction at least twice persists the latest values after reload;
- overlapping interaction windows expose distinct countdown state;
- interaction-end notification fires once at expiry and cancel/reschedule/reboot/update/time/timezone reconciliation is correct;
- PendingIntent identity and permission-disabled state;
- manual intake inverse behavior and macro per-item outcomes.

Perform only the narrowest emulator/device notification check needed for platform wiring.

## Non-goals
No Prescriptions redesign, People/Soldi integration, History performance project, global import/export cleanup or broad UI redesign. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, schedule/intake semantics, interaction persistence/enforcement, countdown state, notification restoration/permissions, migration if any, tests/device check, commit SHA.
