PROMPT_ID: 835204

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Build the PersonalHub global activity register END-TO-END in one substantial architectural task instead of splitting backend/undo and UI into separate Codex sessions:

1. canonical semantic audit capture with bounded/paged read model;
2. safe compensating undo with stale/conflict detection and grouping;
3. full `Registro attività` home integration, history UI, filters and undo UX over that same model.

Design the read model once with its final UI consumers in mind. Do not finish a backend phase, discard context, then rediscover it in a second session. Capture the PersonalHub base version once and set `target = base + 1`; increment `version.txt` exactly once. Run phase-local tests as needed, but perform one final build/install/device QA only after the end-to-end feature passes.

# Token/work discipline
- Read authoritative mutation boundaries in grouped passes, following direct command collaborators only. No module-tree scans.
- Reuse the same audit entity/service/read model across backend, undo and UI phases; do not create adapter layers merely because phases were previously separate prompts.
- Reuse already verified module mutation contracts instead of independently re-auditing each module after the capture layer is implemented.
- No repeated bootstrap, equivalent schema inspection, duplicate paging verification or repeated builds.
- If a prior roadmap task moved one exact authoritative command type, resolve that imported type once.
- Stop immediately after consolidated PASS.

# Starting boundaries
Read these authoritative persistence/write boundaries in grouped passes as needed:
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

For final shell/UI integration, read only:
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`
- `app/src/main/AndroidManifest.xml`

Use the existing database migration-safety framework if the earlier roadmap task has completed it; do not redesign that framework here. Any audit schema addition must use the canonical migration mechanism.

# Phase A — canonical semantic audit foundation
Add the minimum append-only global audit persistence needed for understandable history and safe compensation.

Each event/group must support, as appropriate:
- stable event ID and timestamp;
- module/category/action;
- entity type + stable identity;
- human-readable label/description snapshot;
- source/origin;
- versioned structured before/after snapshots sufficient for safe inverse checks and readable detail;
- grouping ID / parent-child relation for one logical user action;
- reversibility metadata/status;
- relevant app version/versionCode and payload/schema version.

Never store secrets/tokens/credentials or large opaque blobs.

## Capture rules
- Capture semantic persistent mutations at authoritative domain/repository boundaries, not generic raw SQLite triggers.
- Audit + domain mutation should be atomic where architecture permits.
- Never recursively audit audit rows.
- Cover meaningful persistent user-data/settings INSERT/UPDATE/DELETE plus applicable import/sync/background mutations; exclude bookkeeping/noise.
- Add idempotent install/update/schema-migration lifecycle events.
- Integrate/bridge/retire Timer's old audit only enough to ensure ONE canonical user-visible source without double logging.
- Expose bounded/paged semantic read APIs suitable directly for the final UI. Do not eager-load the entire journal.

Targeted proof: representative mutation from every mutable module/settings emits one coherent semantic event/group with readable labels, deleted-entity identity remains understandable, secrets are absent, import/sync/background/lifecycle semantics are idempotent, Timer does not double-log.

# Phase B — safe compensating undo
Undo never deletes or rewrites history. It performs a new authoritative domain mutation and creates a linked audit event/group.

Required behavior:
- Implement safe inverses for meaningful representative INSERT/UPDATE/DELETE and reversible Settings operations.
- Lifecycle/system events are explicitly non-undoable.
- Before inverse mutation, verify current-state semantic preconditions/version/hash derived from the original after-state; never overwrite newer changes blindly.
- Respect FK/dependency/archive rules; never cascade unrelated history just to make undo succeed.
- Grouped undo validates all inverses first and is all-or-nothing where possible.
- Retry/double undo is idempotent.
- Use authoritative module commands, never generic raw-row replay when domain invariants exist.
- Expose current reversibility and concise human-readable rejection reason for stale/conflicting/non-reversible events/groups.
- Undo itself audits exactly once without recursion or export storm.

Targeted proof: representative INSERT/UPDATE/DELETE/settings undo; stale update and FK/dependency conflicts fail closed; group all-or-nothing; second undo cannot double-apply; non-undoable events remain immutable; compensating event links are correct.

# Phase C — `Registro attività` UI over the SAME read/undo model
Do not rebuild or wrap the backend with a competing UI-specific store.

## Home integration
- Add a compact PersonalHub home card/module named `Registro attività`, visually consistent with existing module cards.
- Tapping opens the register; no preview list on the home card.
- Integrate through the current module/home routing mechanism without breaking launcher-shortcut settings. If that mechanism necessarily implies a shortcut, provide a valid minimal route/alias rather than a broken special case.

## History UI
Show all stored events through lazy/paged/virtualized loading with no arbitrary historical count cap and no eager full-journal load.

Each top-level row shows:
- readable date/time;
- module/category;
- concise human-readable semantic description with no unexplained raw IDs;
- grouped/expandable detail where one action produced child changes;
- current reverted/conflict/non-reversible status;
- undo affordance only when the domain says the event/group is currently reversible.

Use a clear undo/revert icon such as `↩︎`; accessibility text must say undo/revert. A rejected stale/conflicting undo shows the domain-provided reason and leaves data/history unchanged. Do not expose raw snapshot JSON as normal detail UI.

## Filters
Add compact `🎛️` filtering with multi-select modal/dialog. At minimum support categories equivalent to:
- Tutti
- People
- Timer
- Places
- Substances
- WordPulse
- Soldi
- Impostazioni
- Sistema

Provide Apply/Reset semantics. Persist selected display filter across app restarts. Filtering changes display only. Prefer deriving categories from current audit categories so future/unknown categories remain visible by default rather than disappearing under an old saved filter.

Preserve scroll/filter/expanded-detail state through normal recreation where practical using existing PH patterns.

Targeted UI proof: paging/lazy history, grouped expansion, filter persistence/new-category visibility, reversible vs non-reversible affordance, successful disposable undo, conflict rejection presentation.

# Export/sync invariants
Audit/undo must not create idle loops, recursive logging or export storms. Audit rows accompanying a mutation should participate in the same semantic transaction/generation where architecture permits. Do not redesign Datasette sync or SAF backup.

# Consolidated final verification
After A+B+C targeted checks pass:
- run the minimum end-to-end regression set covering schema/migration, semantic capture, inverse safety, paging/filter UI and no-recursion/export-loop behavior;
- perform ONE explicit final PersonalHub APK build;
- safely install/update that APK on project-required Android targets per the governing PersonalHub protocol;
- perform ONE focused safe device/emulator flow: home card → full register → `🎛️` filter → expandable group → one disposable reversible event → verify compensating history; use disposable data, never irreplaceable live data;
- do not repeat module-by-module audits after the representative coverage has already passed.

# Non-goals
No event-sourcing rewrite, generic rollback engine, raw-row replay framework, analytics, theme overhaul, unrelated module business refactor, Datasette redesign or SAF redesign.

# Acceptance / stop
PASS only when one canonical semantic audit source covers representative persistent mutations across modules/settings, safe undo fails closed on conflicts and records compensating history, and the full paged/filterable `Registro attività` UI uses that same model correctly. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, audit schema/migration/coverage, grouping/redaction, inverse/conflict semantics, register/paging/filter UI, undo UX, export/no-recursion checks, targeted tests, final device QA, version, commit SHA.