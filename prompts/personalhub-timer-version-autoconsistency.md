PROMPT_ID: 184963

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Remove Timer's incorrect dependence on its legacy library version for PH app-version audit and AutoConsistency gating, and make failed consistency repair retryable.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/multitimetracker/build.gradle.kts`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AutoConsistencyEngine.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/AppPatchVersion.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/AutoConsistencyCore.kt`
- `app/build.gradle.kts`
- `version.txt`

Inspect a patch-version asset only if one of these files references it directly. Do not inspect unrelated Timer version constants. If a prior task renamed a symbol, one targeted symbol search is allowed; no repo scan.

## Known evidence
PH's application version comes from the host app (`version.txt` → app version), while Timer's library BuildConfig retains its own historical version. AutoConsistency currently receives that library version as `currentPatch`. It also marks some failure paths as completed, so a failed repair may be considered already run.

## Work
- User-facing install/update audit must use the actual host PersonalHub package version/versionCode, not Timer library BuildConfig.
- AutoConsistency should use a dedicated monotonic repair/algorithm revision (or an equally precise existing mechanism), not the unrelated PH release number nor the legacy Timer app version.
- Mark a repair revision completed only after: successful repair, proven already-consistent/no-data no-op, or another explicitly safe terminal state. A transient failure must remain retryable.
- Preserve existing data and snapshot/session-table authority rules.
- Do not normalize version constants across every module; this task is only for Timer runtime correctness.

## Tests
- host version differs from Timer legacy version → app audit records host version;
- failed `ensureSessionTables`/save does not advance repair revision;
- next startup/run retries and can succeed;
- successful/already-consistent repair does not rerun unnecessarily.

No general Timer refactor. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, host-version source, repair-revision mechanism, retry semantics, tests, commit SHA.
