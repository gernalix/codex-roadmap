# C2 issue inbox

TASK_ID=C2-ISSUE-INBOX-20260926

## Objective
Add an append-only, low-cost C2 issue inbox for incidental bugs, bottlenecks, obstacles and improvements. Executors capture without roadmap scans; C2 later triages each entry to exactly promoted or discarded.

## Constraints
- Capture accepts only facts already in the executor's possession: description is the only semantic input required; repo/code location/executor reference are optional when already known. Issue ID, timestamp and state are generated automatically.
- Capture must not require supervisor lease, deduplication, roadmap lookup, severity/priority classification, placement decisions, task merging or any extra reasoning.
- Canonical DB remains single-writer; capture is submitted as one serialized writer mutation.
- A newly observed issue matched to a completed/fixed work item cannot be discarded as already fixed; it must re-enter active work as a regression/reopen while preserving immutable historical PROMPT_ID lifecycle.
- PersonalHub ownership rules remain unchanged.

## Checklist
- [ ] Add canonical inbox schema and migration-safe installer.
- [ ] Add unfenced capture mutation and minimal executor CLI.
- [ ] Add fenced C2 triage with exactly promote/discard outcomes.
- [ ] Enforce completed/fixed match => regression/reopen, never discard.
- [ ] Preserve history by creating/linking a successor when a terminal item cannot be reopened in place.
- [ ] Add tests for capture, dedup-free behavior, promotion, discard and regression invariant.
- [ ] Document executor/C2 protocol.
- [ ] Run focused/full verification; commit and push.

## Current step
Preserve the current implementation in a pushed checkpoint commit, then reconcile the branch with origin/main before completing integration.

## Completed
- Repository/state inspected; existing canonical write boundary and supervisor fencing verified.
- Design fixed: capture is O(1) and unfenced; triage is fenced and semantic.
- Current uncommitted implementation includes `issue_inbox` schema and capture/promote/discard primitives, a minimal capture CLI, `work_item_executor_bindings`, worker binding submissions, runtime triage-intake draft, mutation routing, and focused tests.
- Existing focused tests previously passed: issue inbox 16, worker 12, mutations 3, runtime 20. These are pre-reconciliation evidence only.

## Remaining
- Push checkpoint commit and reconcile the branch, currently 18 commits behind `origin/main`.
- Complete automatic binding, capture identity, event-driven triage, regression invariant, canonical protocol, focused tests and final verification.

## Blockers
None.

## Evidence
- `work_items` is canonical actionable state; mutation Issues are the sole normal DB writer path.
- `c2_mutations.py` already separates supervisor-fenced operations from other C2 mutations.
- At checkpoint update, branch `chatgpt/c2-issue-inbox` has nine task files changed/untracked and is 18 commits behind `origin/main`; no unrelated dirty files appear in `git status --short`.

## Acceptance criteria
Every incidental observation can be captured in one command with no C2 scan; each inbox row has one terminal disposition (`promoted` or `discarded`); exact matches to completed fixes are forced back into active work as regressions; tests and DB verification pass.

## Next action
Commit and push the current task files as a persistent checkpoint; then reconcile with `origin/main` preserving the task changes.
