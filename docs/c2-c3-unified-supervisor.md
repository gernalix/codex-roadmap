# C2/C3 Unified Supervisor

This document preserves the reusable contract for the hourly ChatGPT scheduled
automation. The account-specific schedule and its active prompt remain in the
ChatGPT automation. Keep its per-user state under
`${XDG_STATE_HOME:-$HOME/.local/state}/c2-c3-unified-monitor/`.

## Persistent state and logging

- `state.json` tracks `initialized`, `last_run_at`, `last_successful_run_at`,
  the C3 batch watermark, and the last relevant master-goal state. Read it at
  run start; update it only after final checks pass. Preserve existing fields.
- `live.log` is append-only. Timestamp each line in the user's local timezone
  and record `RUN_START`, `RUN_END`, check start/results, one
  `TASK_ANALYZED` per canonical active run, fixes, errors, and newly reported
  C3 batches. Never truncate it or log credentials, tokens, or full dumps.
- Use Remote Desktop Commander `write_file` first. If the platform rejects
  that call, use its `start_process` tool with Python to append to `live.log`.
  For `state.json`, use Python to write a temporary file in the same directory
  and replace it atomically with `os.replace`; read back and validate both
  writes. Do not use shell redirection or heredocs. Report a persistence
  blocker only if both supported paths fail; do not repeat an identical
  rejected write.

## Each run

1. Check C2 and C3 health from their canonical control-plane and runtime
   evidence: worker/supervisor, leases, recovery, watchdog, recent progress,
   queue, dependencies, writer ownership, and runtime processes. Make only
   minimal, authorized corrections and verify them.
2. Enumerate every canonical `claimed`, `running`, or `recovering` work item
   and execution. Report each by ID, run ID, title, executor/worker, lease
   state, latest progress, relevant backlog, dependencies/gates, subordinate
   processes, and operational judgment. Distinguish stale lease bookkeeping
   from a dead executor. Do not restart a progressing worker solely because
   its lease is stale. If there are none, say so explicitly.
3. Check the configured master-goal thread on every run after initialization.
   Skip it only when `initialized` is false. Assess current activity and
   recovery state; use authorized steering/restart mechanisms only when
   canonical evidence supports intervention.
4. Determine whether C3 is operational from canonical evidence. If so, report
   only batches completed since the saved watermark, including outcome,
   transitions, retries/recovery/overrides, and final result; advance the
   watermark after reporting. Do not claim C3 operation from design/backlog
   evidence alone.
5. Write final state only after all checks and report data are verified. Set
   `initialized=true` only after a successful first run. End with a concise
   operational report and only genuine unresolved blockers.

## Verification record

On 2026-09-30, the persistence fallback was exercised and read back
successfully. A manual automation run then completed with `RUN_START`, health
checks, an individual `TASK_ANALYZED`, `RUN_END`, and a valid updated
`state.json`. The active C2 execution was reported as progressing with stale
lease bookkeeping; no restart was warranted. C3 remained unproven as an
operational runtime, so no C3 batch was reported.
