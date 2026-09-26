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
- [x] Add canonical inbox schema and migration-safe installer.
- [x] Add unfenced capture mutation and minimal executor CLI.
- [x] Add fenced C2 triage with exactly promote/discard outcomes.
- [x] Enforce completed/fixed match => regression/reopen, never discard.
- [x] Preserve history by creating/linking a successor when a terminal item cannot be reopened in place.
- [x] Add tests for capture, dedup-free behavior, promotion, discard and regression invariant.
- [x] Document executor/C2 protocol.
- [ ] Commit, push and integrate through the repository workflow.

## Current step
Finalize the tested implementation and integrate it.

## Completed
- Repository/state inspected; existing canonical write boundary and supervisor fencing verified.
- Design fixed: capture is O(1) and unfenced; triage is fenced and semantic.
- Current uncommitted implementation includes `issue_inbox` schema and capture/promote/discard primitives, a minimal capture CLI, `work_item_executor_bindings`, worker binding submissions, runtime triage-intake draft, mutation routing, and focused tests.
- Existing focused tests previously passed: issue inbox 16, worker 12, mutations 3, runtime 20. These are pre-reconciliation evidence only.
- Checkpoint commit `869c50bd` was pushed to `chatgpt/c2-issue-inbox`; branch rebased cleanly onto `origin/main` as `425238dd`.
- Binding now backfills early capture, rejects identity conflicts, and Codex binds its durable thread before starting the first turn.
- Fenced atomic `ensure_issue_triage` creates at most one runnable P0 semantic item per pending batch. Terminal prior triage permits a new batch; finishing a triage with pending rows is rejected.
- C2 worker injects compact incidental capture instructions; README records the canonical rule.

## Remaining
- Final commit, push and repository integration.

## Blockers
None.

## Evidence
- `work_items` is canonical actionable state; mutation Issues are the sole normal DB writer path.
- `c2_mutations.py` already separates supervisor-fenced operations from other C2 mutations.
- At checkpoint update, branch `chatgpt/c2-issue-inbox` has nine task files changed/untracked and is 18 commits behind `origin/main`; no unrelated dirty files appear in `git status --short`.
- Post-rebase C2 test suite: 153 PASS. `roadmap verify` reports `ok=true`, no problems. `PRAGMA quick_check=ok`, `foreign_key_check=0` on the branch snapshot.

## Acceptance criteria
Every incidental observation can be captured in one command with no C2 scan; each inbox row has one terminal disposition (`promoted` or `discarded`); exact matches to completed fixes are forced back into active work as regressions; tests and DB verification pass.

## Next action
Commit and push the verified changes; use the repository integration path and stop after acceptance evidence is confirmed.
