PROMPT_ID: 802766

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Global activity register — phase 2. Add safe compensating undo on top of the canonical global audit journal, with conflict detection and atomic group reversal. Do not build the final register UI in this phase.

## Prerequisite
Use MegaVault/`AGENTS.md`, then verify narrowly that phase 1 provides the canonical append-only global audit model, semantic before/after snapshots, grouping, stable entity identity, redaction and complete current-module capture. If materially absent, stop `BLOCKED`; do not recreate phase 1.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Undo semantics
Undo must be a compensating domain mutation, never deletion/rewriting of audit history. Executing undo creates a new mutation and a new linked audit event/group; the original remains visible with reverted/conflict/non-reversible status metadata.

Implement inverse behavior only through authoritative module/domain commands:
- original INSERT → remove/archive the created entity only if still safe;
- original UPDATE → restore the prior audited domain fields only if the current state still satisfies the expected post-state precondition;
- original DELETE/archive → restore/recreate from the versioned snapshot only when current FK/domain rules allow it;
- setting change → restore the previous value through the real settings boundary;
- grouped/bulk action → validate every inverse first, then reverse all-or-nothing in one safe transaction where possible;
- install/update/migration/system lifecycle events → explicitly non-undoable.

Do not implement generic raw-row replay if a domain command/invariant exists.

## Conflict safety
Never overwrite newer state blindly. Before applying an inverse, verify an appropriate current-state version/hash/semantic precondition derived from the original after-state. If a later mutation changed the same relevant state, fail closed with a structured human-readable reason and do not mutate data.

Foreign-key/dependency rules from current canonical entities must be respected. Never cascade-delete unrelated history merely to make an undo succeed.

For a grouped action, one failed precondition means the whole group remains unchanged. No partial group reversal.

Undo/retry must be idempotent: the same original event/group cannot be successfully compensated twice.

## Coverage
Provide safe undo handlers for representative persistent INSERT/UPDATE/DELETE semantics in every current mutable module where a meaningful inverse exists, plus reversible Settings changes. Mark truly irreversible operations explicitly instead of fabricating an inverse.

Use phase-1 versioned snapshots; do not start persisting broad new secret/opaque fields merely for undo.

## Read/domain contract
Expose a query/domain result indicating whether an event/group is currently reversible and, on rejection, a concise semantic reason suitable for the later UI.

## Tests
Targeted tests must prove:
- representative INSERT/UPDATE/DELETE/setting undo creates compensating audit history and keeps the original event;
- stale UPDATE undo cannot overwrite a newer edit;
- dependency/FK conflict rejects safely;
- grouped undo is all-or-nothing;
- second/retried undo cannot double-apply;
- non-undoable lifecycle/system events remain immutable;
- undo itself is audited exactly once and does not recurse/export-storm;
- representative handlers across current mutable modules preserve domain invariants.

## Scope / resource discipline
No register/home/filter UI, no event-sourcing rewrite, no raw DB rollback framework, no unrelated module cleanup. Start from phase-1 audit service plus existing domain commands. Expand only to concrete inverse handlers needed for current modules. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, inverse architecture, covered reversible operations, conflict/group semantics, non-reversible cases, tests, commit SHA.
