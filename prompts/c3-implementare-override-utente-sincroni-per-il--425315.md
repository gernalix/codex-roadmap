PROMPT_ID=425315

Implement the canonical C3 user-override control path required by the C3 Control web app.

Scope:
- synchronous pause/resume/stop/cancel/delete/force-priority/move operations;
- dependency-impact analysis and downstream closure before destructive actions;
- explicit confirmation contract for destructive dependency impact;
- DAG-safe best-effort reordering with exact blocking prerequisite reported when a move cannot be fully applied;
- atomic/fail-closed canonical mutation, executor pause/stop propagation, and immediate event/UI readback;
- keep autonomous normal mutations on the ordinary fenced path; explicit user intent must not wait behind that queue.

Acceptance:
- User override and destructive override are structurally distinct from normal autonomous mutations.
- Dependency closure is computed before destructive actions and requires explicit confirmation for downstream impact.
- Reordering never violates the DAG and reports the exact blocking prerequisite when a requested move cannot be fully applied.
- Override mutation, affected executor control, canonical state update and UI/event readback are atomic or fail closed.
- Focused control-plane tests cover pause, stop, cancel, delete, force-priority and constrained move semantics.

Preserve the C3 production architecture and retired-C2 invariant. Do not resurrect C2 daemons or legacy Codex orchestration.