PROMPT_ID: 416738

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Make Timer alerts usable and durable. Repair only the existing Timer alert subsystem; Places geofence alerts are a separate later task.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerScheduler.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerReceiver.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceNotifier.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/core/TimeFenceAlarmReconciliation.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/controller/AlertsCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/ui/AlertsScreen.kt`
- `feature/multitimetracker/src/main/AndroidManifest.xml`
- `app/src/main/AndroidManifest.xml`

Open `AlertsUiState.kt`, `AlertMessageParser.kt` or `MainViewModelSnapshotCoordinator.kt` only when the listed alert files directly require them for the requested flow/restoration. If an earlier task renamed a listed symbol, resolve it with one targeted search only; do not scan Timer.

## Known evidence
Current code already has TimeFence rules, scheduling, notification delivery and snapshot-time reconciliation. A prior audit found no manifest receiver for `BOOT_COMPLETED`/`MY_PACKAGE_REPLACED`, so scheduled alerts are reconstructed on app load but not autonomously after reboot/update. The intended Timer alert create/manage UI is also known to be functionally incomplete/unusable; verify current state before changing it.

## Work
- Provide a coherent create/edit/delete/enable-disable flow integrated with existing Timer UI conventions.
- Reuse the current TimeFence domain/reconciliation where correct; do not create a second alert engine.
- Ensure rule edits/cancel/delete reconcile existing PendingIntents/notifications idempotently.
- Add the minimum boot/package-replaced restoration mechanism so active Timer alarms are rescheduled from persisted canonical state without requiring the user to open Timer.
- Handle notification/exact-alarm permissions coherently; preserve existing safe fallback behavior where platform rules allow it.
- Avoid duplicate notification firing after reconciliation/reboot.
- No Places/geofence work, generic automation engine or unrelated Timer UI refactor.

## Tests / verification
Targeted tests cover CRUD state, schedule/cancel identity, one-time/always behavior, dedup and persisted-state reconciliation. Add receiver/restoration tests for reboot/package replacement. Perform one focused safe emulator/device notification check if required to prove platform wiring; do not broaden into a notification audit.

## Acceptance
An alert can be created/edited/enabled/disabled/deleted and fires under its intended Timer condition; persisted active alerts are restored after reboot/app update without opening Timer; no duplicate firing.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, Timer alert UX, restoration mechanism, permission behavior, tests/device check, commit SHA.
