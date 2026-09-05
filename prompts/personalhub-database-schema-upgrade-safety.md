PROMPT_ID: 592604

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Make PersonalHub database upgrades fail-safe and future-proof. On the first launch after every install/update, the app must verify that the inherited `personalhub.db` is compatible with the APK; if its schema is older, migrate it to the current schema without data loss, validate the result, and only then allow normal writes. Future schema bumps must be unable to ship without a complete tested migration path.

## Known current evidence — reuse, do not rediscover broadly
Current `PersonalHub/main` already has part of the foundation:
- `PersonalHubDatabase` is Room `version = 5`, `SCHEMA_VERSION = 5`, `exportSchema = true`;
- exported Room schemas `1.json` … `5.json` exist;
- migrations currently registered are 1→2 and 2→3 inline, 3→4 in `FinanceMigration`, 4→5 in `FinanceAccountsMigration`;
- `canMigrateFrom(version)` currently returns only `version == SCHEMA_VERSION`, which does not describe the real migration chain;
- `DatabaseVault.validate()` validates version-specific DB structure/integrity for transfer and the import path can upgrade an older staged DB, but that is not a complete first-start-after-APK-update guarantee;
- current `core/database` tests do not contain a comprehensive all-historical-schema → current migration test.

Do not replace working migrations or transfer safety merely to reorganize code.

## Exact starting files — verified on PersonalHub/main
Read in one grouped pass:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `core/database/build.gradle.kts`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceMigration.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceAccountsMigration.kt`
- `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`
- `app/build.gradle.kts`

The schema snapshots are large. Do not read all JSON bodies manually. Use their filenames/Room tooling and inspect only a specific snapshot/section when a failing test or migration implementation requires it. If one listed symbol was moved by an earlier task, one targeted search for that exact symbol is allowed.

Before code changes, increment `version.txt` exactly once by `+1`. This is the app version rule, not the Room schema version. Do **not** bump the Room schema version just because this safety framework is being added; bump it only if an actual schema change is necessary.

## Required design

### 1. One authoritative migration registry
Make the migration set explicit and reusable by normal Room opening, temporary/import opening, compatibility checks and migration tests. Preserve the existing 1→2→3→4→5 behavior.

`canMigrateFrom(version)` or its replacement must answer whether a complete path exists from that schema to `SCHEMA_VERSION`, not merely whether the versions are already equal. Do not assume a contiguous numeric range if the registry has a gap: detect the real path.

Keep `@Database` version and the public schema-version constant sourced from one compile-time value if practical, so they cannot silently diverge.

Never add `fallbackToDestructiveMigration` or any equivalent delete/recreate fallback for user data.

### 2. First-launch/update schema gate
Implement one narrow startup gate for the main process, before feature writes become possible.

On the first launch of a newly installed APK version:
- if no existing `personalhub.db` exists, create/open the current schema normally and validate it;
- if DB schema == current schema, perform the lightweight compatibility/integrity validation and continue without rewriting user data;
- if DB schema < current schema and a complete registered path exists, preserve a recoverable pre-upgrade copy using the existing safe DB/backup primitives, run the Room migration chain, then validate the resulting **current** schema plus SQLite integrity/foreign-key checks before normal writes continue;
- if DB schema < current but no complete path exists, refuse normal DB startup without deleting/recreating the DB;
- if DB schema > current (downgrade / DB from a newer app), refuse to mutate it and report a clear incompatible-newer-database state;
- if migration or post-migration validation fails, the inherited DB must remain recoverable and normal feature writes must not start. Restore the pre-upgrade copy when needed rather than leaving a partially upgraded live DB.

Track the last successfully validated app version/schema so the full first-launch check runs once per APK version, not on every activity open. The schema itself remains the authority for whether a migration is required.

Reuse `DatabaseVault` validation/snapshot/recovery behavior where safe; do not create a second competing backup subsystem. Preserve interrupted-import recovery ordering.

The user-visible failure state can be minimal, but it must clearly say that the local database is incompatible/migration failed and that the app refused to overwrite the data. Do not expose stack traces, IDs or raw SQL.

### 3. Future-schema guardrail
Add automated checks so a future Room schema bump cannot silently omit migration work:
- the exported current schema snapshot must exist;
- every supported historical exported schema must have a complete path to current;
- Room must validate the final migrated schema;
- destructive fallback must remain absent.

Prefer a small dedicated migration test/helper over policy comments alone.

## Tests / acceptance
Use Room migration-testing support and targeted tests only. Create a dedicated migration/upgrade test if cleaner than expanding `GlobalDatabaseInstrumentedTest`.

Must PASS:
- migration from every existing historical schema snapshot `1..SCHEMA_VERSION-1` to current through the real chain;
- representative rows/relationships that existed at each relevant version survive migration, including at least shared core data plus the version-specific Finance changes where applicable;
- final schema is accepted by Room and by existing integrity/foreign-key validation;
- current→current first-launch check is non-destructive/no-op apart from validation metadata;
- fresh install creates a valid current DB;
- a simulated newer-schema DB is rejected without mutation;
- a simulated missing/failed migration path does not replace the inherited DB with an empty one and does not enable normal writes;
- the same authoritative registry is used by production DB opening and tests.

Perform one focused end-to-end upgrade check with a disposable/QA database on an approved Android test target. Never downgrade or mutate the real user's production DB merely to manufacture an old-schema test fixture.

Do not broaden into feature behavior, database capsulization, sync redesign, import/export redesign, or a general startup refactor.

## Stop condition
Stop immediately once the migration registry, first-launch/update gate, failure safety and historical migration tests are all verified. No unrelated cleanup.

Final output only: `PROMPT_ID`, `RESULT`, schema version, supported migration paths, startup-gate behavior, failure/rollback behavior, historical versions tested, tests, Android upgrade check, version, commit SHA.