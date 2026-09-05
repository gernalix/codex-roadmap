PROMPT_ID: 539206

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Remove the obsolete Timer-owned first-run database-folder/restore gate from PersonalHub so the Timer module relies on PH's single global `personalhub.db` backup/import UI.

## Known evidence
Start from:
- Timer `MainActivity.kt` first-run setup flow;
- `export/BackupFolderStore.kt` (`multitimetracker_backup` prefs / legacy `MultiTimer data` semantics);
- `persistence/SqliteVault.kt`;
- PH `DatabaseNavigation`/global backup UI only as needed.

Current state: Timer is a PH library using the canonical `personalhub.db`. Its `SqliteVault` DB-transfer methods are now adapters/stubs that open global Database UI or return no restorable data, but the Timer Activity still contains an active first-run SAF selection/restore gate. On an empty/fresh state this can ask for a Timer-specific folder that does not configure `DatabaseVault` and cannot perform the global restore it appears to offer.

## Work
- In the PersonalHub-hosted Timer flow, opening Timer must never be blocked by legacy MultiTimer SAF setup.
- Database backup/import/restore entry points must route to the existing PH global Database & Backup UI/contract rather than maintain a second folder preference or fake restore path.
- Preserve any genuinely separate manual CSV/JSON export feature only if it is still user-facing and does not masquerade as the authoritative DB backup.
- Remove/retire dead first-run state only to the extent needed to make the behavior unambiguous; no broad import/export rewrite.
- Do not touch Substances/Places backup paths except shared PH navigation primitives if necessary.

## Tests
- fresh/empty PH state → Timer opens normally without SAF prompt;
- existing PH data → unchanged normal startup;
- Timer database/backup action opens the global PH database UI;
- no Timer-specific action can claim DB restore success through the stub `SqliteVault` path.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, removed legacy gate, remaining export semantics, tests, commit SHA.
