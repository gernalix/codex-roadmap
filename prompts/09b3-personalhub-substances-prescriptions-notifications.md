PROMPT_ID: 495552

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 3. Complete prescriptions/refills and make Substances notifications durable, state-driven and correctly restored across Android lifecycle events.

## Prerequisite
Use MegaVault/`AGENTS.md` and verify that the phase-2 scheduling/intake command semantics exist. If materially absent, stop `BLOCKED`; do not recreate prior phases.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Prescriptions / refills
Implement the smallest coherent prescription model/UI flow supporting:
- any active supported substance, not an arbitrary capped subset;
- selectable relevant date, quantity and valid unit;
- valid refill interval/recurrence;
- edit and delete;
- accidental-duplicate prevention;
- next-refill computation and recurring refills rather than a single one-off date;
- archived substances excluded from new refill actions where appropriate while preserving history.

If current schema already supports simple requested/collected state cheaply, complete it; otherwise do not invent a pharmacy workflow.

## Notifications
Use the canonical phase-2 schedule/domain state. Support at least:
- dose reminder;
- missed-dose notification;
- interaction-end notification where a time-bound block/warn ends;
- refill reminder.

Notifications must reconcile from persisted canonical state and be scheduled/cancelled/rescheduled when relevant data changes. Restore/reconcile after `BOOT_COMPLETED`, `MY_PACKAGE_REPLACED`, `TIME_SET` and `TIMEZONE_CHANGED` where platform behavior requires it.

Requirements:
- no stale alarms for archived/deleted/edited schedules;
- no scheduling of already-expired timestamps as fresh future reminders;
- PendingIntent/notification identity cannot collide across unrelated events;
- permission denial must fail gracefully without corrupting domain state;
- retries/reconciliation are idempotent and do not duplicate notifications;
- use exact alarms only if a concrete product/platform requirement justifies them;
- each useful notification has a `contentIntent` into Substances/the relevant substance;
- missed-dose logic must follow phase-2 scheduling rather than a parallel implementation.

## Tests / verification
Targeted tests cover recurring refill, prescription CRUD/duplicate validation, schedule→notification mapping, cancel/reschedule, archive behavior, missed-dose transition, PendingIntent identity, permission-disabled state and boot/update/time/timezone reconciliation. Perform only the narrowest emulator/device notification check needed to prove manifest/platform wiring.

## Scope
No history-performance work, global backup/import work or broad UI redesign. Reuse the existing domain/notification primitives when correct; do not build a generic PH automation engine.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, prescription/refill behavior, notification reconciliation/restoration, permissions, tests/device check, commit SHA.
