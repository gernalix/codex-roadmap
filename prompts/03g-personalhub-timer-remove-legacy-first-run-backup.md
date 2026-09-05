PROMPT_ID: 539206

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Remove the obsolete Timer-owned first-run database-folder/restore gate from PersonalHub so Timer relies exclusively on PH's single global `personalhub.db` backup/import UI.

## Known evidence / starting files
Start only from:
- Timer `MainActivity.kt` first-run setup flow;
- `export/BackupFolderStore.kt` (`multitimetracker_backup` prefs / legacy `MultiTimer data` semantics);
- `persistence/SqliteVault.kt`;
- PH `DatabaseNavigation`/global backup UI only as needed.

Current state: Timer is a PH library using canonical `personalhub.db`. Its `SqliteVault` DB-transfer methods are adapters/stubs that open global Database UI or return no restorable data, but Timer Activity still contains an active first-run SAF selection/restore gate. On a fresh state this can ask for a Timer-specific folder that neither configures `DatabaseVault` nor performs the global restore it appears to offer.

Verify only this evidence/current path. Then increment `version.txt` exactly once by `+1` before code changes.

## Work
- Opening Timer in PersonalHub must never be blocked by legacy MultiTimer SAF setup.
- Database backup/import/restore entry points must route to the existing PH global Database & Backup contract rather than a second folder preference or fake restore path.
- Preserve a genuinely separate manual CSV/JSON export only if it is still user-facing and clearly not the authoritative DB backup.
- Remove/retire dead first-run state only as needed to make behavior unambiguous; no broad import/export rewrite.
- Do not touch Substances/Places backup paths except shared PH navigation primitives if strictly necessary.

## Tests
- fresh/empty PH state → Timer opens normally without legacy SAF prompt;
- existing PH data → normal startup unchanged;
- Timer database/backup action opens global PH database UI;
- no Timer-specific action can claim DB restore success through stub `SqliteVault` behavior.

No general Timer audit. Use targeted tests and stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, removed legacy gate, remaining manual-export semantics, tests, commit SHA.
