PROMPT_ID: 361972

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 4. Make canonical History identity-stable, directly editable/deletable and scalable, and remove obsolete Substances-owned authoritative DB transfer behavior so the module uses PersonalHub's single global `personalhub.db` infrastructure.

## Prerequisite
Verify the canonical intake/scheduling command semantics and prescription/intake linkage from the preceding Substances phases. Verify PH remains single-DB with global DatabaseVault/DatabaseGate/auto-export. If materially absent, stop BLOCKED; do not recreate prior phases.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/UtcDateCodec.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/Entities.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/SostanzeDao.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/capsules/importexport/SostanzeDataPorter.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/capsules/importexport/SostanzeImportExportCapsule.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseNavigation.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseVault.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseGate.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/HubAutoExport.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`

Resolve preceding command/schedule files once from exact imports and follow intake/history declarations directly. No module or DB-infrastructure audit. Increment `version.txt` exactly once by +1.

## History correctness / CRUD / performance
- Identify substances by stable IDs, never mutable display name when an ID exists.
- Provide readable temporal grouping, essential search/filter/substance filter, correct timestamp/quantity/unit/missed semantics, and edit/delete routed through authoritative commands.
- Every visible History entry must have:
  - a pencil/edit icon that opens editing for that exact event;
  - a trash/delete icon that deletes that exact event through the authoritative inverse command.
- Editing/deleting an intake must preserve all phase-1 stock invariants and the phase-3 prescription-package dose count: changing/deleting an intake cannot leave stock or remaining package doses inconsistent.
- Keep loading bounded via paging/lazy/targeted queries or equivalent; avoid unbounded history, O(days × history) rescans and materializing years of synthetic missed-dose rows.
- Only clock-dependent state should tick. Preserve historical timestamps without arbitrary midnight/timezone reinterpretation. Add indexes only when justified by actual query patterns.

## Global DB integration cleanup
- A selected Import URI must invoke the real validated/atomic global import path; report success only after verified success/refresh/restart behavior.
- Remove Substances-specific full DB exports after mutation/read/open and duplicate folder/fake restore paths.
- Retire legacy `sostanze.db` authoritative behavior and unsafe/non-atomic porter paths.
- Preserve a genuinely separate human-readable/manual export only if clearly non-authoritative and useful.
- Do not weaken DatabaseVault validation/recovery or central generation/auto-export semantics.

## Tests / acceptance
History tests cover:
- identity after rename, filters/search and time boundaries;
- each rendered row exposes edit/delete actions for the correct event;
- edit/delete routes through commands and correctly adjusts stock plus prescription remaining doses;
- bounded behavior on representative large fixture and no pathological synthetic missed-dose expansion.

DB integration tests prove valid URI uses real global import; invalid/failing import preserves last-good data and does not report success; no Substances mutation/read triggers duplicate full export; no active path treats `sostanze.db` as authoritative; representative writes participate once through central generation/auto-export.

Never test destructive import against irreplaceable live data. No notification rebuild, archive redesign, broad UI redesign, sync redesign or unrelated cleanup. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, history identity/CRUD/performance strategy, import wiring, legacy paths removed/retained, export semantics, tests, commit SHA.
