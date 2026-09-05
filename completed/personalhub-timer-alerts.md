PROMPT_ID: 416738

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Make Timer alerts usable, durable and deliberately simple: each Timer alert fires as a normal Android notification, never as a forced full-screen alert UI. If the alert text is only a URL/deep link, tapping the notification must route to that target correctly. Repair only the existing Timer alert subsystem; Places geofence alerts and unrelated timed-session notification behavior are separate.

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

Open `AlertsUiState.kt` or `MainViewModelSnapshotCoordinator.kt` only when the listed alert files directly require them for the requested flow/restoration. If a listed symbol moved, resolve it with one targeted symbol search only; do not scan Timer.

## Known evidence
Current `TimeFenceNotifier.notify()` builds the Timer alert around `TimeFenceFullScreenActivity` and can attach the same PendingIntent as a full-screen intent. That conflicts with the required simple-notification behavior. Current code already has TimeFence rules, scheduling, notification delivery and snapshot-time reconciliation. A prior audit found no manifest receiver for `BOOT_COMPLETED`/`MY_PACKAGE_REPLACED`, so scheduled alerts are reconstructed on app load but not autonomously after reboot/update. The intended Timer alert create/manage UI is also known to be functionally incomplete/unusable; verify current state before changing it.

After verifying current state, increment `version.txt` exactly once by +1 before code changes.

## Work
1. Provide a coherent create/edit/delete/enable-disable flow integrated with existing Timer UI conventions.
2. Reuse the current TimeFence domain/reconciliation where correct; do not create a second alert engine.
3. Deliver Timer alerts as standard Android notifications only:
   - no full-screen intent;
   - no forced `TimeFenceFullScreenActivity`, overlay, alarm screen or other custom UI when an alert fires;
   - use ordinary `NotificationCompat` notification behavior and an appropriate reminder/notification category/channel;
   - do not change `notifyTimedSession()` or other timed-session/alarm notification semantics unless the minimum separation is required to keep Timer Alerts simple.
4. Notification tap routing is derived from the alert text:
   - trim leading/trailing whitespace first;
   - link routing applies only when the entire remaining text is exactly one valid absolute URI and contains no other prose;
   - for a normal external `http://` or `https://` URL, tapping opens that exact URL through Android's normal browser flow/default browser; do not hardcode a browser package;
   - for an Android deep link/custom URI intended for another installed app, tapping uses Android's standard resolvable deep-link/ACTION_VIEW flow so the target app opens when a handler exists; do not hardcode specific third-party apps;
   - a message containing prose plus a URL is ordinary alert text and must not be treated as link-only;
   - malformed or unhandled URIs must never crash or launch an unintended component; fall back to the normal Timer-alert tap destination/behavior.
5. Build PendingIntents so different alerts/URLs cannot reuse stale destinations. Preserve immutable/update flags required by the supported Android versions and make identity deterministic.
6. Ensure rule edits/cancel/delete reconcile existing PendingIntents/notifications idempotently.
7. Add the minimum boot/package-replaced restoration mechanism so active Timer alarms are rescheduled from persisted canonical state without requiring the user to open Timer.
8. Handle notification/exact-alarm permissions coherently; preserve existing safe fallback behavior where platform rules allow it.
9. Avoid duplicate notification firing after reconciliation/reboot.
10. No Places/geofence work, generic automation engine or unrelated Timer UI refactor.

## Tests / verification
Targeted tests must cover:
- CRUD state, schedule/cancel identity, one-time/always behavior, dedup and persisted-state reconciliation;
- Timer alert firing creates a normal notification without a full-screen intent/custom alert activity;
- plain-text alert tap follows the normal Timer-alert destination/behavior;
- exact `http`/`https`-only text produces the correct browser ACTION_VIEW target;
- exact resolvable Android deep-link-only text produces the correct app ACTION_VIEW target;
- `testo https://example.com` and other mixed prose+URL are not routed as links;
- malformed/unhandled URI does not crash and uses the safe fallback;
- two alert notifications with different URL/deep-link texts cannot reuse a stale PendingIntent destination;
- reboot/package replacement restores persisted active alerts once, without duplicates.

Perform one focused safe emulator/device notification check only if needed to prove platform routing/restoration; do not broaden into a notification audit.

## Acceptance
An alert can be created/edited/enabled/disabled/deleted and fires under its intended Timer condition as a simple Android notification. Persisted active alerts are restored after reboot/app update without opening Timer and without duplicate firing. If and only if the alert text consists solely of a valid URL/deep link, tapping the notification opens the external URL in the normal/default browser flow or the resolvable target Android app respectively; mixed/plain text keeps normal Timer-alert behavior.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, Timer alert UX, simple-notification behavior, URL/deep-link tap routing, restoration mechanism, permission behavior, tests/device check, commit SHA.
