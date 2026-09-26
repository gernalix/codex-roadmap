# TASK_ID C2-EXECUTOR-RESULT-1321
Objective: unify executor terminal reporting so real execution and canonical C2 state cannot silently diverge.
Constraints: single writer; backward-compatible roadmap_finish; no PH changes; minimal scope.
Checklist:
- [x] Confirm current split: Codex terminal_request vs browser checkpoint/evidence.
- [x] Add one writer-owned structured executor-result receipt.
- [x] Make C2 Codex worker emit/parse a compact terminal contract and submit it automatically.
- [x] Make the result writer terminalize/reconcile prompt run atomically and fail closed on inconsistent PASS.
- [x] Preserve roadmap_finish/manual compatibility.
- [x] Add focused tests for receipt, PASS validation, automatic reconciliation, idempotency.
- [x] Update canonical executor protocol docs.
- [x] Run focused tests, commit, push.
Current step: complete; automatic native reconciliation is implemented in the existing C2 runtime advance path.
Verified facts: Runtime queries `repo_single_writer.py status-any --task-id <PROMPT_ID>` only for a persisted PASS receipt on a still-running item; it replays that receipt through the single writer only when both status and integration_state are `merged`. The request key includes receipt identity/hash and merge SHA. No receipt means no lookup or inference. Non-PASS remains on the existing ungated writer path. `roadmap_finish.py` compatibility retained.
Evidence: focused executor/runtime/mutation/scheduler tests 65/65 PASS; C2-focused suite 164/164 PASS; `git diff --check` PASS.
Blocker: none.
Acceptance: one structured terminal receipt contract; writer acknowledgment remains authoritative; PASS completion requires evidence/acceptance receipt plus actual repository merge; native event-driven recovery has no model round-trip; non-PASS terminalization remains ungated.
Next action: none; branch committed and pushed.
