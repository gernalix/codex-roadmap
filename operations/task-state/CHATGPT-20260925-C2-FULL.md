# Operational task state — Checklist 2.0 full implementation

TASK_ID: CHATGPT-20260925-C2-FULL
Updated: 2026-09-25 12:56 Europe/Copenhagen
Related canonical prompt: 175908
Primary repo: gernalix/codex-roadmap

## Objective
Implement Checklist 2.0 as the single canonical work-item control plane: one SQLite work_items hierarchy replacing separate roadmap/checklist state, with Workflowy + Obsidian projections and RDC event-driven orchestration. Integrate past-chat evidence through shared prompt-history data, not by merging collector repositories. Add a dedicated aggregate C2 Uptime Kuma monitor in source configuration and the live Kuma database/runtime.

## Constraints
- PersonalHub is parked by explicit user override; do not compile/test/install another PH APK/DB until the remaining PH task chain is complete.
- PROMPT_ID 175908 remains pending and is the later canonical cutover/finalizer; do not falsify prerequisite completion.
- Canonical lifecycle mutations remain single-writer only.
- No second canonical checklist, no dual-write after cutover, no model polling.
- Keep ChatGPT/Codex collectors separate; share normalized data through prompt-history.sqlite.
- Preserve current running prompts and rollback from roadmap.sqlite backup.
- Use direct ChatGPT + RDC; use Codex only for a true blocker.

## Plan / checklist
### Phase 0 — State and architecture
- [x] Park PH and switch master priority to C2.
- [x] Correct C2 identity: Checklist 2.0 / PROMPT_ID 175908, not codex-usage-monitor.
- [x] Decide collector architecture: separate collectors, shared prompt-history warehouse.
- [ ] Checkpoint this operational task and branch.
### Phase 1 — Shared history datasource
- [x] Extend prompt-history ChatGPTExporter ingestion to accept a parent directory containing multiple ChatGPTExport-* archives.
- [x] Add timestamp normalization, content-hash file checkpoints and bounded PROMPT_ID linking.
- [x] Stream Session Bandit JSONL rather than materializing the full export list.
- [x] Version/deploy split prompt-history systemd runtime: lightweight 15m sync + hourly heavy transcript refresh with one SQLite flock.
- [x] Verify live sync and existing nonzero ChatGPT/Codex source coverage.
### Phase 2 — Canonical work_items schema
- [ ] Add work_items + required evidence/checkpoint/run/lease schema and migration from prompts/task-state.
- [ ] Preserve PROMPT_ID, dependencies, status history, executions and relations.
- [ ] Add compatibility views/projections for legacy roadmap consumers.
- [ ] Add rollback/integrity/FK/idempotency fixture tests.
### Phase 3 — Checklist import and projections
- [ ] Import Completed/Remaining/Blockers/Evidence/Next action from task-state losslessly.
- [ ] Derive progress from actionable descendants and enforce one current/next action per executable branch.
- [ ] Generate Workflowy UX from work_items.
- [ ] Generate Obsidian notes with tags, parents/children, backlinks and wikilinks.
### Phase 4 — RDC orchestration
- [ ] Add event-driven scheduler reading work_items, dependencies, leases and repo writer ownership.
- [ ] Implement deterministic executor_policy auto|codex|rdc|chatgpt|human.
- [ ] Route Codex claims/finalization only through roadmap single-writer APIs.
- [ ] Prevent same-repo incompatible workers; bounded parallelism across independent failure domains.
- [ ] Resume crash/freeze from checkpoint without rediscovery.
### Phase 5 — C2 shared context and repo data contracts
- [ ] Add read-only prompt-history consumer for past ChatGPT/Codex context retrieval.
- [ ] Evaluate/select shared-data adapters for other repos without merging unrelated code.
- [ ] Document canonical ownership and datasource boundaries.
### Phase 6 — Uptime Kuma
- [ ] Add versioned C2 aggregate health logic and push contract in code.
- [ ] Create/update dedicated C2 push monitor in live Kuma DB with rollback backup.
- [ ] Configure secret push URL outside Git and verify real UP heartbeat/readback.
### Phase 7 — Synthetic cutover
- [ ] Run synthetic migration + rollback + scheduler collision/crash tests.
- [ ] Cut over live roadmap only after fixtures PASS; do not mutate already-running prompts.
- [ ] Verify Workflowy/Obsidian/RDC all read the same work_items source.
- [ ] Finalize canonical 175908 only once after acceptance.

## Current step
Shared-history datasource milestone is complete and deployed. Begin Phase 2: introduce the canonical work_items schema and migration/compatibility layer in codex-roadmap without cutting over live writers yet.

## Verified facts
- Canonical 175908 prompt explicitly requires one work_items hierarchy, Workflowy + Obsidian projections and RDC scheduler.
- roadmap.sqlite currently exposes v_runnable_prompts for pending prompts with satisfied dependencies.
- prompt-history.sqlite already contains historical ChatGPT and Codex messages; current runtime sync omitted the ChatGPTExporter path.
- ChatGPTExporter archive currently lives under ~/Documents/ChatGPT/ChatGPTExport-*.
- Uptime Kuma has legacy disabled codex-usage monitor ID 44 and service-liveness monitor ID 60; no dedicated C2 aggregate monitor exists.

## Decisions
- Do not merge ChatGPT/Codex exporter repositories into C2.
- prompt-history.sqlite is the shared derived conversation/evidence warehouse; collector repos remain replaceable sources.
- C2 owns orchestration and reads roadmap/work-item state plus prompt-history; it does not own raw transcript capture or token telemetry.
- Keep single-writer lifecycle mutation boundary intact.

## Completed
PH parked and checkpointed; priority switched to C2. Shared-history architecture chosen. prompt-history branch `chatgpt/c2-shared-history` is pushed through `ad8dcd3f091b3ca715a01d34bf2da0d7ef348c5e`: parent-directory ingestion, millisecond timestamps, per-file checkpoints, bounded linker, streaming Session Bandit, versioned split systemd units. All 11 tests PASS. Live units are deployed; lightweight sync and hourly transcript timer are active.

## Remaining
All unchecked phases above.

## Blockers
No current blocker. PROMPT_ID 175908 itself remains pending due existing roadmap dependencies, so direct ChatGPT implementation proceeds on isolated branches without falsely claiming that prompt.

## Evidence
codex-roadmap checkpoint aaff5458f1ad53a1ebfb9ac79f4ad07ddd6b874d parks PH. prompt-history `ad8dcd3f091b3ca715a01d34bf2da0d7ef348c5e`; 11/11 tests PASS. Live prompt_history.sqlite contains ChatGPT and Codex sources. Deployed lightweight sync PASS; heavy transcript refresh is isolated to hourly timer and both writers share one flock. Kuma DB readback shows no C2 aggregate monitor.

## Acceptance criteria
One canonical work_items tree; legacy roadmap/checklist cannot diverge; migration/rollback/FK/integrity/idempotency PASS; Workflowy and Obsidian project the same source; RDC schedules deterministically without model polling; same-repo collision prevention PASS; past-chat context is available through prompt-history; dedicated C2 Kuma monitor is live; running prompts are not mutated; synthetic E2E and live cutover PASS.

## Next action
Implement work_items schema + migration helpers + legacy compatibility views on the isolated codex-roadmap C2 branch; prove migration/rollback/FK/integrity/idempotency on fixtures before any live cutover.
