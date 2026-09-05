PROMPT_ID: 412907

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STRICT

# Goal
Harden PersonalHub's canonical DB import/export recovery against process death and SAF-provider failures, fixing only the two concrete transfer defects below. Preserve all existing data-safety guarantees.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabasePreferences.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseRestartActivity.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`

Open another file only if one of these directly references a durability helper/provider seam needed for the fix or a targeted test fails with evidence pointing there. If an earlier roadmap task renamed one of these files, resolve that symbol/class with one targeted search; do not scan the repository.

## Known evidence — reuse, do not rediscover broadly
Current `importDatabase()` writes `personalhub-import.pending` by opening the final marker file directly, writing the backup path, then fsyncing. `recoverInterruptedImport()` immediately `readText()`s the marker and `require()`s that it resolves to a valid backup in the DB directory. A process/power death after truncate/create but before a complete durable write can therefore leave an empty/partial marker that is re-read on every startup.

Current `exportNow()` rotates the prior SAF `personalhub.db` to `.bak`; if publishing the new file fails, rollback calls `renameTo(personalhub.db)` but does not verify that rollback succeeded.

## Work
1. Make creation/update of the import-pending marker atomic and durable: write a temp marker, fsync its content, atomically publish/rename it, and fsync the containing directory using the existing durability helpers/patterns where possible.
2. Make startup recovery fail-safe for empty, malformed, truncated or otherwise invalid markers. Never turn a damaged marker into a permanent startup crash-loop and never delete a potentially useful pre-import backup merely because the marker is unreadable.
3. Preserve the current rule that a valid pending marker restores the last-good DB before feature/database initialization.
4. Harden SAF export rollback: if restoring the previous published name also fails, retain a recoverable last-good copy and record a clear persistent error instead of silently assuming rollback worked.
5. Do not redesign import/export, sync, SAF layout, Room schema or WorkManager.

## Tests
Add the narrowest tests proving:
- valid marker → rollback succeeds and marker is retired;
- empty/truncated/malformed marker → no crash-loop and recoverable backups are preserved;
- interruption around marker publication cannot expose a partially written final marker;
- publish failure preserves the previous valid SAF copy;
- rollback-rename failure is visible/recoverable and does not mark export successful.

Use fake/filesystem/provider seams already available; add a tiny seam only if needed for deterministic failure injection. Do not run destructive tests against the real installed PH data.

## Resource discipline
Use MegaVault/AGENTS first. Inspect only the exact starting files and a directly referenced helper/test when evidence requires it; batch inspections/tests, no general repo audit, no identical retries, no unrelated cleanup. Stop immediately after acceptance passes.

## Acceptance
- no partial final import marker can be produced by the normal write path;
- corrupt marker cannot cause repeated startup failure;
- valid interrupted import still restores last-good data;
- failed SAF publish/rollback preserves recoverability and exposes error state;
- targeted tests/build PASS;
- no unrelated behavior changes.

Final output only: `PROMPT_ID`, `RESULT`, root cause, marker fix, rollback behavior, tests, commit SHA.
