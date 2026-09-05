PROMPT_ID: 948126

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Build the global PersonalHub activity-register backend end-to-end in one architectural task: canonical semantic audit capture plus safe compensating undo with conflict detection. Do not build the final register/home/filter UI; that remains a separate task.

## Exact starting boundaries — verified on PersonalHub/main
Read grouped authoritative write/inverse boundaries only:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseGate.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/sync/SyncJournal.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/sync/DatasetteSync.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/settings/HubSettings.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceCapsule.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactsRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AuditLogSqlite.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/data/WordRepository.kt`

Follow direct mutation/command collaborators only. If prior tasks introduced a newer authoritative command boundary, resolve the exact imported type once. No module-tree scans. Increment `version.txt` exactly once by +1.

## Canonical audit foundation
Add minimum append-only global audit persistence with stable event ID/timestamp, module/category/action, entity type+stable identity, human-readable label snapshot, source/origin, versioned structured before/after snapshots sufficient for understandable history and safe compensation, grouping ID, reversibility metadata/status, relevant app version/versionCode and payload/schema version. Never store secrets/tokens/credentials/large opaque blobs.

Capture semantic mutations at authoritative domain/repository boundaries, not raw SQLite triggers. Audit + Room mutation should be atomic where practical; never recursively audit audit rows. Cover semantic persistent user-data/settings INSERT/UPDATE/DELETE plus applicable import/sync/background mutations, excluding bookkeeping. Add idempotent install/update/schema-migration lifecycle events. Integrate/bridge/retire Timer's old audit only enough to ensure one canonical source without double logging. Expose bounded/paged semantic read APIs for the later UI.

## Safe compensating undo
Undo never deletes/rewrites history: it performs a new authoritative domain mutation and creates a linked audit event/group. Implement safe inverses for meaningful representative INSERT/UPDATE/DELETE and reversible Settings operations; lifecycle/system events are explicitly non-undoable.

Before inverse mutation, verify current-state semantic preconditions/version/hash derived from the original after-state. Never overwrite newer changes blindly. Respect FK/dependency/archive rules and never cascade unrelated history just to make undo succeed. Grouped undo validates all inverses first and is all-or-nothing where possible. Retry/double undo is idempotent. Use authoritative module commands, never generic raw-row replay when domain invariants exist.

Expose whether an event/group is currently reversible and a concise semantic rejection reason suitable for the later UI.

## Export/sync invariants
Audit/undo must not create idle loops, recursive logging or export storms. Audit rows accompanying a mutation should participate in the same semantic transaction/generation where architecture permits. Do not redesign Datasette sync or SAF backup.

## Tests / acceptance
Migration preserves current DB and passes Room/FK validation. Representative mutation from every mutable module/settings emits one coherent semantic event/group with readable deleted-entity label and no secrets. Import/sync/background/lifecycle capture is correct and idempotent; Timer does not double-log. Representative INSERT/UPDATE/DELETE/settings undo creates compensating history; stale update and FK/dependency conflicts fail closed; grouped undo is all-or-nothing; second undo cannot double-apply; non-undoable events remain immutable; undo itself audits exactly once without recursion/export storm.

No register/home/filter UI, event-sourcing rewrite, generic rollback framework or unrelated module cleanup. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, audit schema/migration/coverage, grouping/redaction, inverse architecture, conflict/group semantics, non-reversible cases, export/no-recursion checks, tests, commit SHA.
