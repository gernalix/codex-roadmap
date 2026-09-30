# TASK_ID: C3-THREAD-01a0f36b

## Objective
Unblock `codex://threads/01a0f36b-2d26-7e52-843d-026d9e93478a` by restoring canonical C3 Inbox processing so intake #7632 is imported and the thread can continue from real canonical evidence.

## Constraints
- Preserve C3 fencing, ownership, roadmap single-writer, and existing work items.
- Do not edit the runtime-only supervisor worktree directly.
- Reuse existing C3 web-app/control-plane work items; no duplicates.
- Keep the fix minimal and push every meaningful checkpoint.

## Plan / checklist
- [x] Inspect target Codex thread and identify the canonical blocker.
- [x] Register manual executor start against running Inbox triage work item.
- [x] Capture the systemic C3 runtime failure in the Inbox as issue #7640.
- [x] Verify root cause: mutable supervisor authority reused under a stable `ensure_issue_triage` transport key.
- [x] Patch `_writer_submit` so `ensure_issue_triage` transport identity changes when authority changes.
- [x] Add a focused regression test.
- [x] Run focused tests and roadmap DB verification; classify unrelated global-suite failures against `main`.
- [ ] Commit and push the fix branch.
- [ ] Integrate to `main`, protected-pull locally, and sync runtime worktree through the canonical snapshot guard.
- [ ] Restart C3 runtime/inbox timers and verify Inbox triage progresses.
- [ ] Verify #7632 is canonically linked/imported and web-app priority semantics are represented without duplication.
- [ ] Resume/steer the target Codex thread with the new canonical evidence and verify it is no longer blocked.

## Current step
Checkpoint the verified fix, commit it, and push the isolated branch before integration.

## Verified facts
- `c3-runtime.service` failed at 19:28 CEST on `request_key_conflict:c3-inbox-ensure-b8df14c2d5dd3bdd97483f7b9f792046`.
- Work item `wi:adae18fd54de4ec3b04828cd496a0075` is the running Inbox triage item; its prior lease was stale.
- Existing mutation Issues #7613/#7614 used the same semantic key with supervisor authority embedded in the payload.
- `_writer_submit` already changes transport identity on authority renewal for `acknowledge`, `schedule`, and `bind_executor`.

## Decisions
- Fix the generic authorized transport-key handling in `c2_runtime._writer_submit`, not `c3_runtime` call sites.
- Add `ensure_issue_triage` to the existing authority-sensitive operation set and give it a dedicated transport-key prefix.

## Completed
Diagnosis, executor-start receipt, issue capture, isolated worktree, transport-key fix, regression test, relevant 65-test suite, baseline comparison, and roadmap DB verification.

## Remaining
Commit/push, integration/deploy, C3 recovery, canonical readback, and target-thread continuation.

## Blockers
None currently; runtime remains failed until the fix is integrated and deployed.

## Evidence
- Journal traceback from `c3-runtime.service` points to `_writer_submit` → `submit_document` request-key conflict.
- Issues #7613/#7614 show stable key with embedded supervisor authority.
- Target thread explicitly reports #7632 pending and unlinked because C3 Inbox processing is inactive.
- Focused regression: PASS; `tests.test_c2_runtime` + `tests.test_c3_retirement`: 65/65 PASS.
- Full discovery: 577 tests with 5 browser-executor failures; the same 5 fail unchanged on canonical `main`, so they are baseline and unrelated to this patch.
- `python3 tools/roadmap_db.py --repo . verify`: `ok=true`, no problems.

## Acceptance criteria
- Repeated `ensure_issue_triage` calls under unchanged authority reuse the same transport key.
- After authority/lease change, the transport key changes while the canonical operation semantics remain unchanged.
- C3 runtime and Inbox maintenance run without request-key conflict.
- Intake #7632 leaves unlinked pending state via canonical triage/reconciliation.
- Target Codex thread receives the new canonical state and is no longer blocked on import.

## Next action
Commit and push the verified fix branch, then integrate it to `main` through the repository PR path.
