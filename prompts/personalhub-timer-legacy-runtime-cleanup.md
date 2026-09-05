PROMPT_ID: 684251

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Remove the remaining legacy MultiTimeTracker runtime assumptions from Timer in one localized pass: use the real PersonalHub host version for app audit, make AutoConsistency revision/retry semantics correct, and remove the obsolete Timer-owned first-run DB backup/restore gate so Timer relies on PersonalHub's single canonical database infrastructure.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/multitimetracker/build.gradle.kts`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AutoConsistencyEngine.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/AppPatchVersion.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/AutoConsistencyCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainActivity.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/FirstRunRestoreContract.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/export/BackupFolderStore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SqliteVault.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/system/ImportExportCapsule.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseNavigation.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `app/build.gradle.kts`
- `version.txt`

Open a directly referenced patch-version asset or `ImportExportCapsuleViewModel.kt` only if required. If a listed symbol moved, one targeted search only; no Timer-wide exploration. Increment `version.txt` exactly once by +1 before code changes.

## Work
- User-facing install/update audit must use the actual host PersonalHub package version/versionCode, never Timer's legacy library BuildConfig version.
- AutoConsistency must use a dedicated monotonic repair/algorithm revision (or equally precise existing mechanism), unrelated to PH release number and legacy Timer version.
- Mark a repair revision complete only after success, proven already-consistent/no-data no-op, or another explicitly safe terminal state. Transient failure remains retryable.
- Opening Timer must never be blocked by legacy MultiTimer SAF setup.
- DB backup/import/restore entry points must route to PersonalHub's global Database & Backup contract, not a Timer-specific folder preference or stub/fake restore path.
- Preserve genuinely separate manual CSV/JSON export only if clearly non-authoritative.
- Retire dead first-run state only as needed. Preserve data, session authority, auto-export/sync semantics. No broad Timer/import-export refactor.

## Tests
Prove: host version differs from legacy Timer version yet audit records host version; failed consistency repair does not advance revision and retries successfully; successful/already-consistent repair does not rerun unnecessarily; fresh PH state opens Timer without legacy SAF prompt; existing data startup remains normal; Timer DB/backup action opens global PH database UI; no Timer-specific path can claim DB restore success through stub behavior.

Stop after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, host-version source, repair-revision/retry semantics, removed legacy backup gate, remaining manual-export semantics, tests, commit SHA.
