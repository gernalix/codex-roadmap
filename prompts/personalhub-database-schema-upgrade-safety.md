[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Make PersonalHub database upgrades fail-safe: on first launch of a newly installed/updated APK, validate the inherited `personalhub.db`, migrate older supported schemas through the real Room chain before feature writes, reject newer/unsupported/broken databases without destructive replacement, and enforce tested migration coverage for future schema bumps.

# Verified current baseline — do not rediscover
Current `PersonalHub/main` has advanced beyond the older roadmap assumptions:
- `PersonalHubDatabase` is now Room `version = 10` and `SCHEMA_VERSION = 10`.
- exported schema snapshots `1.json` through `10.json` all exist.
- production `build()` already registers migrations covering 1→2→3→4→5→6→7→8→9→10.
- `canMigrateFrom(version)` is currently `version in 1..SCHEMA_VERSION`; this is better than the old equality check but still only assumes contiguity and does NOT prove a real path from the registered migration graph.
- `DatabaseVault.validate()` already performs version-specific schema checks plus SQLite `quick_check`, FK checks, indices/triggers/photo integrity and import rollback/recovery. Reuse it; do not build a competing validator/backup system.
- `PersonalHubApplication.onCreate()` recovers interrupted imports, initializes normal app/module infrastructure and defers cleanup/export/sync, but there is no explicit inherited-schema startup gate before normal feature DB use.
- `GlobalDatabaseInstrumentedTest` already exercises export/import/rollback integrity, but there is no dedicated all-historical-schema → current Room migration suite.

This prompt remains necessary, but do not redo the migrations, snapshots, import rollback or integrity validator that already exist.

# Narrow starting files
Read in one grouped pass:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`
- `core/database/build.gradle.kts` and `app/build.gradle.kts` only for migration-test support.

Inspect the existing Finance migration classes or one specific schema JSON only if implementation/test failure requires it. Do not manually read all schema snapshots or rescan feature modules.

Capture the current PersonalHub app version once and set `target = base + 1` exactly once. Do NOT increment Room schema merely for this safety framework.

# Required design
## A. Authoritative migration graph
Expose the exact production migration objects through one reusable registry/list used by normal Room opening, temporary/import opening, migration-path checks and tests. Preserve current migration behavior.

Replace the range-based migration claim with a real graph/path check: `canMigrateFrom(v)` (or replacement) is true only when `v == current` or a complete registered path reaches current. A future missing edge must be detected automatically.

No `fallbackToDestructiveMigration` or delete/recreate fallback.

## B. First-launch/update gate
Before normal feature writes on a new APK version:
- fresh DB: create/open current schema and validate;
- current DB: lightweight current-schema/integrity validation, then continue;
- older DB + complete path: create a recoverable pre-upgrade copy using existing safe primitives, migrate through Room, validate the resulting current DB, then enable normal app DB use;
- older DB + missing path: refuse startup without replacing user data;
- newer DB: refuse mutation as incompatible downgrade;
- migration/post-validation failure: keep/restore a recoverable inherited DB and do not enable normal feature writes.

Preserve interrupted-import recovery ordering. Reuse `DatabaseVault` snapshot/validation/rollback pieces instead of duplicating them. Track successful validation per app-version/schema so the expensive first-launch gate does not rerun on every Activity open; schema remains authoritative.

Expose only a concise user-readable incompatible/migration-failed state; no raw SQL/stack traces.

## C. Future guardrail/tests
Add focused migration tests driven by the exported snapshots and the same production registry:
- every historical snapshot 1..9 has a complete path to 10;
- Room accepts the final migrated schema;
- representative pre-existing core + version-specific Finance/Substances/Hub Context/Places data survives where those tables/columns exist;
- current→current is non-destructive;
- fresh install is valid;
- simulated newer DB is rejected without mutation;
- simulated missing/failing path cannot replace the DB with an empty one or enable writes;
- destructive fallback remains absent.

Use Room migration-testing support if needed. Perform one focused Android upgrade check with a disposable/QA DB only; never manufacture an old schema by downgrading the user's real DB.

# Token/work discipline
Do not reorganize working migrations for aesthetics, rewrite transfer/import, scan all entities, or test every table. Implement the registry/gate once, use representative survival fixtures, and stop when the guardrail proves all historical paths.

# Acceptance / stop
PASS only when production opening and tests share one migration graph, first-launch/update is fail-safe for older/current/newer/failing DBs, snapshots 1..10 are guarded, existing import recovery remains intact and focused Android upgrade verification passes. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, schema version, migration graph/path coverage, startup gate, failure/rollback behavior, historical versions tested, Android check, version, Pixel install/APK delivery if required by bootstrap, commit/push, blocker if any.
