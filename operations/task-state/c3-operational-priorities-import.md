# C3 operational priorities — completed canonical import

Source: `codex://threads/01a0f36b-2d26-7e52-843d-026d9e93478a`.
Intake: `issue:01a0f36b2d267e52843d026d9e93478a`, captured by #7632.
Import: #7662, request `c3-priorities-import-01a0f36b2d267e52843d026d9e93478a-current-fence`.

Root cause: capture persisted the directives but left the observation pending, with no canonical plan links. The inactive Inbox maintenance path did not import it; the batch next action also prescribed whole-task sequencing instead of independent preparation.

Recovery: executed the existing canonical mutation writer directly in an isolated worktree under the user's explicit self-sufficient recovery instruction. Used the current shared local control identity, validated it with the standard lease helper and renewed it through the canonical writer; reconciled only the existing batch and non-prompt web item and linked the original complete source evidence to batch/web/API items. Existing scheduler authority is preserved. Two rejected non-fast-forward attempts were recovered by reapplying over the newest remote snapshot; their temporary fence claims were never persisted. No worker, supervisor process, Inbox watcher or execution dispatch was needed.

Canonical targets:
- Batch `wi:3c3553e1c2a44de7bc1fc65d1239ca12`: added six acceptance criteria for adaptive pressure-based concurrency, exclusive-resource compatibility, safe backfill, observable slot decisions, P0 web/API scheduling and independent UI preparation.
- Web `wi:8a803b44d02b48528216c0056265e5e0`: preserved all original functional criteria, added independent preparation/testing while the real API prerequisite remains in progress.
- API `wi:8a0d3fd1ad674119829be0b9c8a9bed4`: linked source evidence; preserved its existing P0 priority, prompt and lifecycle.

Verification: SQLite integrity and foreign keys PASS; roadmap verifier PASS with no problems; exact source evidence attached to all three targets; original acceptance preserved; no new work item; dependencies, runs, execution specs and resource leases unchanged; identical mutation replay applied zero operations. Canonical intake is promoted with three decision links and an applied mutation receipt.

The source goal is importing requirements into the normal C3 plan. Production dashboard/API implementation and runtime scheduling remain their separate existing tasks, not acceptance criteria for this import. No residual import blocker; no next action.
