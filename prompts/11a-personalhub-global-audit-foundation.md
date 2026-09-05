PROMPT_ID: 205645

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Global activity register — phase 1. Add the canonical semantic audit foundation and complete capture coverage for PersonalHub persistent user-data/settings mutations, without building the final register UI or undo engine yet.

## Starting architecture
Use MegaVault/`AGENTS.md`, then inspect in grouped reads only:
- unified Room DB/migrations and central mutation/export infrastructure;
- current module repository/domain write boundaries for People, Timer, Places, Substances, WordPulse and Soldi;
- persistent PH Settings stores;
- import/sync/background paths that apply user-visible data changes;
- Timer's existing module-local audit only as prior art/integration target.

After verifying current state, increment `version.txt` exactly once by `+1` before code changes.

## Audit model
Add the minimum append-only global audit persistence supporting at least:
- stable event id and timestamp;
- module/category and semantic action;
- entity type + internal stable identity;
- human-readable entity label snapshot captured at event time;
- source/origin (`user`, `import`, `sync`, `worker`, `system`, etc.);
- versioned structured before/after snapshots containing only fields required for understandable history and future safe compensation;
- grouping id for one semantic action producing multiple writes;
- reversibility metadata/status sufficient for phase 2;
- app version/versionCode where relevant;
- payload/schema version.

Internal IDs are allowed in storage but user-facing descriptions/read models must not depend on unexplained IDs. Do not store secrets/tokens/API keys/credentials/large opaque blobs in snapshots.

Do not use raw SQLite triggers as the primary source. Capture semantic mutations at authoritative repository/domain/coordinator boundaries. Audit write + Room mutation should be atomic in the same transaction where practical. Audit must never recursively audit itself.

## Coverage
Capture every semantic persistent user-data/settings change across current modules, including representative INSERT/UPDATE/DELETE, import/sync-applied changes and background user-data mutations where such paths exist. Exclude internal bookkeeping such as sync cursors, export generations, audit rows, caches and equivalent metadata.

One user action may group multiple low-level changes. Preserve inspectable child/detail information without double-logging the same semantic fact.

For settings outside Room, use the safest equivalent ordering and capture before/after values without secrets.

Add system lifecycle events:
- first known install/run: one semantic install event;
- app update: one `vX → vY` event, not repeated each launch;
- actual DB schema migration: one semantic schema-version event, not SQL-statement spam.

## Existing Timer audit
Integrate/bridge/retire the Timer-local audit presentation/storage only enough to ensure the final PH-wide audit has one canonical event source and does not double-log Timer mutations. Preserve any still-useful Timer-specific behavior through the global model where required.

## Export/sync invariants
Audit integration must not reintroduce an idle auto-export loop or create redundant export storms. Audit rows accompanying a mutation should participate in the same semantic transaction/generation where current architecture permits. Do not redesign Datasette sync or SAF backup.

## Required read/query contract
Expose a bounded/paged global audit read API and semantic display/read model sufficient for a later UI. Do not build the home card/register screen yet.

## Tests
Targeted migration/domain tests must prove:
- existing DB migrates safely and passes Room/FK validation;
- representative INSERT/UPDATE/DELETE from each mutable current module emits exactly one coherent semantic event/group;
- representative Settings, import/sync/background mutation capture where applicable;
- deleted entities retain a readable label snapshot;
- grouping preserves detail without duplication;
- install/update/migration lifecycle events are idempotent;
- secrets are absent from persisted snapshots;
- audit does not recursively audit itself or independently create export storms;
- Timer does not double-log.

## Resource discipline
This is cross-cutting but not a generic repo audit. Start from known write boundaries and batch symbol/path discovery. No UI/undo implementation, no unrelated refactor, no post-PASS coverage sweep beyond the explicit current mutation boundaries.

Stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/migration, covered write sources/modules, grouping/snapshots/redaction, lifecycle events, Timer integration, export/no-recursion checks, tests, commit SHA.
