# TASK_ID C2-SEMANTIC-ROADMAP-CONTRACT-20260926
Objective: make C2 roadmap reorganization explicitly hybrid: deterministic scripts own factual lifecycle/sync/reconciliation; AI owns semantic updating/optimization; single writer owns canonical mutations.
Constraints: compact canonical contract; no duplicate state authority; no AI polling/mechanical sync; no direct DB writes; reuse existing C2 runtime/writer/Inbox.
Checklist:
- [x] Verify current C2 architecture and existing optimizer intent.
- [x] Verify Inbox coverage for all reasoning executors; native is non-reasoning.
- [x] Capture protocol drift in task-state README to C2 Inbox (#1322).
- [x] Add one canonical semantic-vs-deterministic architecture contract.
- [x] Add one reusable standard prompt for semantic roadmap reorganization.
- [x] Link contract from README/AGENTS and align task-state Inbox rule.
- [x] Verify docs; git diff --check PASS.
- [x] Commit and push.
Current step: complete.
Verified facts: C2_SEMANTIC_REORGANIZATION.md is the sole detailed contract and contains the reusable prompt; README and AGENTS only point to it. Task-state discovery capture now routes to Inbox rather than forcing executor-side triage.
Blocker: none.
Acceptance: a user can paste one standard prompt that forces mechanical facts to scripts, semantic judgments to AI, all canonical mutations to writer, and stops after roadmap reorganization rather than task execution.
Evidence: git diff --check PASS; commit 26295637 pushed to origin/feature/c2-executor-result-contract; protocol drift captured as Inbox #1322; guard pack-refs noise captured as Inbox #1324.
Next action: none.
