# C2 semantic roadmap reorganization — 2026-09-26

## Objective
Semantically reorganize active C2 work under C2_SEMANTIC_REORGANIZATION.md without executing application work or duplicating deterministic control-plane responsibilities.

## Constraints
- Canonical roadmap mutations only through the C2 single writer.
- Deterministic lifecycle/sync/receipt/run binding/dependency readiness/CI-PR-merge/reconciliation/projection stay outside AI judgment.
- Inspect only minimum repo/context needed for semantic classification.
- Do not mutate running work outside lifecycle contract.
- Incidental material discoveries go to C2 Inbox without research/triage.

## Plan / checklist
- [x] Refresh read-only canonical snapshot.
- [x] Confirm no active C2 runs and no queued roadmap mutation before semantic review.
- [x] Review every active root and minimum relevant repo/context.
- [x] Identify semantic obsolete/duplicate work.
- [x] Capture incidental C2 architecture gaps to Inbox.
- [ ] Apply semantic mutations through writer.
- [ ] Verify writer receipts in canonical snapshot.
- [ ] Confirm remaining roots are still semantically valid and stop.

## Current step
Submit two PersonalHub supersessions through the C2 writer.

## Verified facts
- Snapshot refreshed from canonical remote state; the writer has since applied Inbox Issues #1330 and #1331.
- No work_item_runs were claimed/running/recovering before semantic review and no roadmap mutation was queued at that point.
- wi:7009a02364364a099d815911afbe6d19 states no independent implementation remains; its History/Search work and Pixel QA are covered by PersonalHub PR #54/shared gate.
- wi:7b5eb79a939d4b0eb6c96ad5c0c7b25b states no independent implementation remains; origin/main app/build.gradle.kts already includes arm64-v8a in QA ABI filters; remaining Pixel verification is the shared PR #54 gate.
- Successor/shared owner is wi:02cab3c0c0324d0bbda572b81cfc71c3 (Unifica UI link Workflowy in PersonalHub).
- Other active roots checked remain materially valid, conditional, or genuinely waiting/blocked on recorded external prerequisites.
- MegaVault canonical checkout remains detached/dirty and behind origin; its cleanup root remains valid.
- PR #1325 contains the semantic contract and executor-result work but is not merged.
- Inbox captures were submitted as Issues #1330 and #1331.

## Decisions
- Supersede wi:7009a02364364a099d815911afbe6d19 including its imported descendants into wi:02cab3c0c0324d0bbda572b81cfc71c3.
- Supersede wi:7b5eb79a939d4b0eb6c96ad5c0c7b25b into the same shared PH root.
- Do not semantically close PH/global imported umbrella roots; selective stale-descendant reconciliation already has a dedicated valid work item.
- Do not merge the two Workflowy dashboard roots: one is projection latency, the other visibility/UX after sync.
- Do not change prompt/manual-prerequisite lifecycle facts by semantic reasoning.

## Completed
Canonical snapshot refresh, semantic root audit, minimum repo checks, Inbox capture of discovered C2 gaps.

## Remaining
Writer submission and receipt verification for the two PH supersessions.

## Blockers
None for the two intended semantic mutations. The current writer cannot express acceptance-json edits or additive dependency/tag edits; captured to Inbox for future capability work.
## Evidence
- PersonalHub PR #54 includes History/Search shared UI/instrumentation tests and uses the shared QA gate.
- PersonalHub origin/main QA ABI filters include armeabi-v7a, arm64-v8a, x86_64; commit history identifies 1d9e2c68.
- Current C2 active-root evidence is in the canonical roadmap.sqlite snapshot.

## Acceptance criteria
- Obsolete PH duplicate roots are terminal/superseded with canonical relation to the shared PH root.
- Writer receipts are present and canonical snapshot reflects the mutations.
- No application task is executed and no valid active root is semantically removed.

## Next action
Acquire non-published semantic-writer supervisor authority, submit the two c2_reconcile_item mutations, then refresh the snapshot once and verify receipts/status/relations.
