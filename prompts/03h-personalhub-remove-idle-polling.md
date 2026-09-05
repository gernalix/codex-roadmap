PROMPT_ID: 872451

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Remove or substantially reduce PersonalHub's permanent 2-second in-process dirty/sync poll without weakening durable SAF auto-export or Datasette sync recovery.

## Known evidence
Start only from:
- `core/database/.../HubAutoExport.kt`
- `DatabaseGate.kt`
- `capsules/sync/DatasetteSync` / `SyncJournal` scheduling paths directly reached from mutations;
- existing auto-export durability/sync tests.

`HubAutoExport.start()` currently creates a daemon scheduled executor with `scheduleWithFixedDelay(..., 0, 2s)` that repeatedly calls `dirty()`/`request()` and `DatasetteSync.checkForChanges()`. Canonical writes already pass through DB generation triggers/`DatabaseGate.afterMutation()`, and durable WorkManager recovery exists. Do not assume Datasette has an equivalent event trigger: verify the narrow mutation→sync scheduling path before removing its poll dependency.

## Work
1. Map only the canonical mutation → generation/journal → export/sync trigger chain.
2. If export no longer needs in-process polling, remove that polling dependency.
3. If Datasette currently depends on the 2s loop for prompt scheduling, replace it with the smallest event-driven trigger at the canonical mutation/journal boundary; retain periodic WorkManager recovery as a safety net where appropriate.
4. Preserve the commit-before-enqueue/process-death recovery guarantee. A crash window may be recovered by durable/periodic work, but SAF/sync must not silently remain stale for hours.
5. Avoid creating one WorkManager job per low-level write when a transaction/group can be coalesced.
6. Do not redesign export, sync protocol, Datasette API or database schema.

## Tests
Prove with targeted tests:
- canonical Room and Timer-legacy writes still schedule/produce export without the permanent poll;
- sync journal changes still trigger/recover Datasette work;
- rapid writes coalesce reasonably;
- process death/restart or missed immediate enqueue is recovered by durable fallback;
- clean idle process performs no 2-second DB/network polling loop.

## Resource discipline
This is not a second auto-export audit. Reuse completed durability evidence, inspect only the files above, batch commands and stop immediately after the invariants pass.

Final output only: `PROMPT_ID`, `RESULT`, removed polling, event trigger, recovery fallback, tests, commit SHA.
