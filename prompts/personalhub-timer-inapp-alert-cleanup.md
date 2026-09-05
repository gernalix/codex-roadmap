PROMPT_ID: 657823

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal

Finish the Timer Alerts migration introduced by current `PersonalHub/main`: Timer Alerts are immediate in-app prompts, not delayed Android notifications. Remove the contradictory Timer-Alert-only scheduling/notification residue and UI delay semantics, while preserving and completing the separate timed-session alarm/full-screen subsystem.

Use the PersonalHub-specialized bootstrap `MegaVault/ai/personalhubdoc.md`. Do not pre-read the full global MegaVault protocol unless that bootstrap explicitly requires a fallback.

## Exact starting files — verified on current PersonalHub/main

Read once in grouped passes:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/controller/AlertsCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/core/TimeFenceAlarmReconciliation.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/alerts/ui/AlertsScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerReceiver.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceRestoreReceiver.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerScheduler.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceNotifier.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimedSessionSupport.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainActivity.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/AlertPopupHost.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/alerts/AlertMessageParser.kt`
- `app/src/main/AndroidManifest.xml`
- `feature/multitimetracker/src/test/java/com/example/multitimetracker/AlertMessageParserTest.kt`
- `feature/multitimetracker/src/test/java/com/example/multitimetracker/TimeFenceAlarmReconciliationTest.kt`
- `feature/multitimetracker/src/test/java/com/example/multitimetracker/TimeFenceRuleDuplicateTest.kt`
- `version.txt`

Open another file only after one targeted symbol search proves it is a direct caller/test of one of these paths. No Timer-wide or repository-wide exploration.

Capture the current `version.txt` once and increment it exactly by +1 once for this goal. Retries, builds and test iterations must not change it again.

## Required behavior

- A matching Timer Alert event while Timer is in the foreground must enqueue/render the centered in-app prompt in the same event path. No `AlarmManager`, system notification, exact-alarm permission, or `timerMinutes` delay may sit on the normal Timer Alert path.
- Remove the Timer Alert delay field from create/edit UI and from the rule summary. New or edited Timer Alert rules must use `timerMinutes = 0`. Existing persisted non-zero values are legacy compatibility data: ignore or normalize them safely, without creating a DB/schema migration unless technically unavoidable.
- Remove only Timer-Alert-specific branches from `TimeFenceTimerScheduler`, `TimeFenceTimerReceiver`, `TimeFenceNotifier`, `TimeFenceRestoreReceiver`, manifest wiring and alarm reconciliation when they no longer serve this behavior. Preserve `TimedSessionSupport`, timed-session alarms, notification/alarm modes, full-screen behavior and acknowledgement paths.
- Repurpose or replace the existing boot/package-replaced reconciliation so running **timed sessions** with a future `expectedEndMs` restore their required alarm after `BOOT_COMPLETED` / `MY_PACKAGE_REPLACED` without opening Timer. Reuse the existing timed-session scheduler; no parallel alarm engine. Reconciliation must be idempotent. Handle already-expired sessions through the existing timed-session reconciliation semantics rather than silently leaving them running.
- If stale pre-migration Timer Alert alarms may still exist on upgraded installations, cancel them idempotently once through the smallest compatibility path; never schedule new Timer Alert alarms.
- Preserve current duplicate semantics exactly: a duplicate is blocked only for the same trigger plus the same normalized tag set.
- Preserve `ALWAYS`/`ONE_TIME`, cooldown and `lastFiredAtMs` semantics, including the stale-save protection already added.
- Keep the prompt centered; X closes it; tap outside closes it; tap inside the card itself does not dismiss it accidentally.
- Preserve clickable valid links and deep links. Naked web URLs display the short host/app label such as `workflowy`, not the full URL. Clickable link text must be visually blue and underlined. Do not reintroduce a pre-resolution check that falsely rejects valid deep links.
- Do not reintroduce Android system notifications for Timer Alerts. If a match can occur while the Timer UI is not foreground, do not silently discard it: use the smallest existing/persistable pending-prompt mechanism to show it on next foreground, or prove with a focused test that the relevant event path cannot occur without the foreground host.

## Verification

Run only focused unit tests for alert matching/state, duplicate semantics, parser/link labels, reconciliation proving no Timer Alert scheduling remains, and timed-session boot/package restoration. Then build once.

For Android acceptance, use one contiguous, scripted device phase. Prefer the existing `Pixel 8a` emulator. Prove: matching Timer Alert → prompt visible immediately; dismiss by X/outside; link/deep link opens; and a future timed-session alarm is reconstructed by the boot/package-replaced receiver without opening Timer. Do not use the physical Pixel unless emulator evidence is technically insufficient. Do not repeat whole UI dumps or coordinate exploration after a stable target is known.

After targeted PASS, perform only the mandatory final PersonalHub install/terminal operations required by the PH bootstrap. Stop; no optional audit.

Final output only: `PROMPT_ID`, `RESULT`, removed Timer-Alert legacy paths, timed-session restore behavior, immediate-prompt behavior, link behavior, tests/device evidence, version, commit SHA.