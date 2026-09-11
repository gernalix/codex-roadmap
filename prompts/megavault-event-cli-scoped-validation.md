[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=804316 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Remove recurring MegaVault tool-call waste when Codex records a PersonalHub PASS: it should not need to rediscover SQLite column names, inspect recent rows, hand-write raw INSERT statements, or run a global validator that fails on unrelated pre-existing semantic issues.

# Starting point
A recent PersonalHub run first queried the MegaVault schema because the expected `id` column did not exist, then inspected existing event rows to reconstruct the insert shape, inserted the event manually with SQLite, and finally hit `megavault.py validate` failures caused by unrelated global semantic rules. The new event itself was the only MegaVault diff.

# Scope
Make the smallest reusable improvement in `gernalix/MegaVault` so event recording and validation are stable CLI operations.

Required behavior:
- add or extend a documented CLI command for recording an event without direct SQL/schema introspection; choose the existing CLI style if one exists rather than creating a parallel framework;
- the command must resolve/generate required event identifiers and timestamps itself and accept the normal fields needed by PersonalHub completion events (at minimum project, category/type/status/summary plus optional commit/version/artifact metadata where supported by the schema);
- validate required fields before writing and use a transaction;
- provide a scoped validation path for the just-changed event/project (for example an event/project selector on the existing validator), so unrelated pre-existing global semantic failures do not turn a valid task-local write into a false blocker;
- preserve the existing full/global validation behavior for explicit global audits;
- return clear machine-friendly success/failure status suitable for Codex;
- update only the minimal authoritative documentation/entrypoint needed so future Codex sessions use the CLI instead of rediscovering schema/SQL.

Do NOT migrate the database schema unless strictly required. Do NOT repair unrelated existing MegaVault validation failures. Do NOT redesign the event model.

# Verification
Use targeted tests on a temporary/copy database:
- add one representative project 49 PASS event via the new CLI path;
- prove required IDs/timestamps/fields are written correctly;
- prove scoped validation passes for a valid new event even when an unrelated pre-existing/global issue exists elsewhere;
- prove invalid input fails without partial writes;
- prove full/global validation semantics remain available and unchanged except for any explicitly necessary wiring.

# Acceptance / stop
PASS when future Codex runs can record and validate a PersonalHub completion event with one stable CLI workflow and no raw SQLite schema discovery. Stop after targeted tests and documentation update; do not investigate unrelated validator findings.

Final output concise: `PROMPT_ID`, `RESULT`, canonical event command, canonical scoped-validation command, tests, files changed, compatibility/global-validator result, blocker if any.