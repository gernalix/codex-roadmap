# C2 autonomous drain — 2026-09-27

## Objective
Prepare every currently verified executable C2 work item with canonical executor context, then let the C2 runtime execute the roadmap autonomously until quiescence.

## Constraints
- No guessed execution metadata.
- Preserve true manual/external blockers.
- Ignore imported task_state steps as independent dispatch targets.
- PersonalHub remains externally owned by its running worker.
- Single writer only; supervisor fencing token 13.
- Runtime/watchdog own scheduling, recovery, parallelism and executor lifecycle.

## Plan / checklist
- [x] Acquire supervisor lease and canonical authority token 13.
- [x] Refresh canonical snapshot.
- [x] Realign supervisor runtime worktree to current main; guard healthy.
- [ ] Prepare already-materialized runnable Codex prompts.
- [ ] Materialize/configure verified non-prompt Codex intakes whose only blocker is missing execution context.
- [ ] Configure verified ChatGPT/RDC items that are directly runnable.
- [ ] Start/trigger runtime and verify parallel dispatch.
- [ ] Continue event-driven until quiescence or only real external/manual blockers remain.
- [ ] Record final state and blockers.

## Current step
Prepare canonical execution specs without dispatch.

## Verified facts
- No active C2 runs at start.
- Runtime/path/watchdog units are active+enabled.
- Runtime worktree is healthy and aligned with main 1d1680e37090e8a16e2e9f9f75713c14126c72db.
- Manual prerequisite tasks (Grindr login, MitID, PAT), PH-owned work, billing-gated work and explicit blocked prompts remain excluded.
- Imported task_state descendants are not independent preparation targets.

## Decisions
Prepare only prompt/c2-intake entities with explicit semantic contracts and no real external blocker.

## Completed
Supervisor authority and runtime alignment.

## Remaining
Preparation, autonomous dispatch, quiescence readback.

## Blockers
None for preparation itself.

## Evidence
Canonical snapshot and runtime guard readback.

## Acceptance criteria
C2 has exact execution specs for all currently safe work; runtime dispatches compatible work in parallel; no manual/blocked item is guessed into execution; recovery remains watchdog-driven.

## Next action
Prepare the three runnable prompt-backed Codex tasks and verified non-prompt Codex intakes.
