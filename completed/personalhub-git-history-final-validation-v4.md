PROMPT_ID=707603 | PARENT_PROMPT_ID=825405 | project_id=49 | MegaVault=STRICT

# Goal
Valida e chiudi il sistema Git Data / Global History / Time Machine già implementato sullo schema PersonalHub finale. Correggi solo difetti reali trovati; non riscrivere la feature.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- docs/GIT_DATA_HISTORY.md e core/database/.../gitdata/* descrivono già sync, history, restore, patch, revert e Time Machine;
- esegui dopo 857906 sullo schema PH risultante; l'archivio Obsidian è esterno a PersonalHub e non è più un prerequisito applicativo.

# Esecuzione
1. Usa CODE_MAP + docs/GIT_DATA_HISTORY.md e i test esistenti; niente audit repo-wide.
2. Verifica su DB/schema finale: tracking transazionale, push retry offline, sharding/hash/signature, destructive guard, patch review, revert, restore revision/date, milestone, index rebuild e Time Machine fallback.
3. Verifica esplicitamente che tabelle/stato tecnico ricostruibile (Obsidian, sync journal/cache) non diventino dominio/history utente.
4. Esegui prove distruttive solo su copie/staging; mai sul DB reale. Testa quick_check/FK prima di replacement.
5. Correggi solo failure osservati e riesegui il leaf gate. Smoke AVD mirato per history/restore una volta.

# Acceptance
PASS con test/history/restore/revert/safety sullo schema finale e nessun technical bookkeeping semanticamente versionato. Nessun refactor post-PASS.
