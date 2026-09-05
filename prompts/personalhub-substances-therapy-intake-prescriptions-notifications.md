PROMPT_ID: 815367

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — therapy execution phase. On top of the phase-1 safe command/stock/archive foundation, implement coherent scheduling and intake semantics together with interactions/macros, prescriptions/refills and durable state-driven notifications.

## Prerequisite
Verify narrowly that phase 1 command boundary, parent-row integrity, stock ledger and archive lifecycle exist. If materially absent, stop BLOCKED. Do not recreate phase 1.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/UtcDateCodec.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/notifications/SostanzeNotificationScheduler.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `feature/sostanze/src/main/AndroidManifest.xml`
- `app/src/main/AndroidManifest.xml`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`

Resolve the phase-1 command/domain file once from exact imports and follow directly referenced schedule/prescription/notification entity/DAO declarations only. No module scan. Increment `version.txt` exactly once by +1.

## Scheduling + intake
Support explicit dose times, applicable days, start/end, forever and PRN; use frequency only with precise semantics. Historical due/taken/missed state must use the regimen valid for that period. Never create future/phantom missed doses or fake midnight timestamps; completion respects dose quantities.

All intake paths use one authoritative atomic command validating active/archive state, therapy/schedule timing, BLOCK/WARN interactions, quantity/unit, stock and duplicate/idempotency. Return explicit outcomes including success, warning, blocked, early dose, insufficient stock and duplicate. Manual historical intake/edit/delete must preserve stock/history invariants.

Interactions: PRN/macros cannot bypass BLOCK; WARN remains distinct; reject self/invalid/duplicate rules; use the actually most restrictive active block. Macros execute through the same intake command, return per-item outcomes and resist retry/double-tap duplication.

## Prescriptions/refills
Support active substances without arbitrary cap, relevant date, quantity/unit, valid recurrence, edit/delete, duplicate prevention and recurring next-refill computation. Preserve history for archived substances while excluding invalid new actions. Do not invent a pharmacy workflow.

## Notifications
Drive dose, missed-dose, interaction-end and refill reminders from canonical persisted schedule/domain state. Reconcile schedule/cancel/reschedule on relevant mutations and restore after BOOT_COMPLETED, MY_PACKAGE_REPLACED, TIME_SET and TIMEZONE_CHANGED where required. No stale/expired alarms, unrelated PendingIntent collisions or duplicate retries. Permission denial fails gracefully. Use exact alarms only when concretely required. Notifications deep-link into relevant Substances UI.

If schema migration is required, keep it minimal/non-destructive and migration-tested.

## Tests / acceptance
Cover schedule boundaries/midnight/timezone, no future missed doses, quantity completion, retry/double-tap, PRN/macro BLOCK, WARN, early-dose contract, manual intake inverse behavior, macro per-item outcomes, recurring refill and prescription CRUD/duplicates, notification mapping/cancel/reschedule/archive, PendingIntent identity, permission-disabled state and boot/update/time/timezone reconciliation. Perform only the narrowest emulator/device notification check needed for platform wiring.

No History performance project, global import/export cleanup or broad UI redesign. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, schedule/intake semantics, interactions/macros, prescriptions/refills, notification restoration/permissions, migration if any, tests/device check, commit SHA.
