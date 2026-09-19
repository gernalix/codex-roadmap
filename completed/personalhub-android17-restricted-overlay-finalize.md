PROMPT_ID=491628 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD

# Goal
Integra e verifica SOLO il fix già preparato in PR #23 (`fix/android17-overlay-restricted-settings`) affinché PersonalHub gestisca correttamente Android 16/17 quando `SYSTEM_ALERT_WINDOW` è bloccato da Restricted Settings per un APK sideloaded.

# Starting point
- Repo: `~/projects/PersonalHub`
- PR pronta: #23
- Branch: `fix/android17-overlay-restricted-settings`
- Implementazione già fatta da ChatGPT: rilevamento Android 16+ + install source LOCAL_FILE/DOWNLOADED_FILE; primo passaggio App info con istruzione “⋮ > Allow restricted settings”; al ritorno passaggio normale “Display over other apps”; percorso diretto invariato per store/Android più vecchi; test puri già aggiunti; branch attualmente a versione 58.
Non rifare discovery generale del repo e non riscrivere il fix senza evidenza di un difetto.

# Scope
1. Esegui roadmap_start.py e usa il protocollo PersonalHub/MegaVault.
2. Parti da PR #23 e aggiorna/rebase SOLO quanto necessario sul main corrente. Se il main ha già consumato la versione 58, risolvi il conflitto con la versione corretta secondo AGENTS.md; niente bump arbitrari.
3. Esegui solo i gate minimi: `CallOverlayRequestGateTest`, compile supercontacts e build necessaria alla QA. Riusa i risultati CI già validi; niente suite equivalenti duplicate.
4. Acquisisci il lease solo per integrazione/device QA come da protocollo.
5. Sul Pixel reale, senza clear-data e preservando i dati:
   - installa/aggiorna la build;
   - identifica il package source effettivo;
   - apri People e innesca il flusso overlay;
   - se Restricted Settings è applicato, verifica che il primo step apra App info con l'istruzione corretta; completa “Allow restricted settings” se l'UI di sistema lo consente, torna a PH e verifica che il secondo step apra “Display over other apps” e che il toggle sia abilitabile;
   - verifica lo stato overlay con `Settings.canDrawOverlays` o equivalente;
   - esegui solo lo smoke call-overlay già disponibile.
   Se Android impone una conferma manuale non automatizzabile, non aggirarla: riporta l'unica azione utente esatta necessaria.
6. Se emerge un difetto in-scope, applica il minimo fix sulla PR e ripeti solo il gate fallito.
7. Dopo PASS, integra PR #23 tramite il single-writer; genera poi l'APK finale minificato+firmato e usa lo stesso artefatto per QA/install/delivery secondo AGENTS.md.

# Non-goal
Niente refactor, cleanup, audit globale, modifiche People estranee al call overlay, migrazioni DB, clear-data, emulator matrix, retry identici o test TCL.

# Acceptance
PASS solo se test mirato+compile PASS; il main contiene semanticamente il fix; sul Pixel il flusso non finisce più nel vicolo cieco “App was denied access” ma guida prima ad Allow restricted settings quando necessario e poi a Display over other apps; overlay permission concedibile; call-overlay smoke non regredisce; dati preservati; PR #23 integrata; artefatto finale conforme al pipeline canonico.

# Stop
Dopo PASS finalizza subito. Report conciso: prima riga `PROMPT_ID=491628`, poi RESULT, MAIN_VERSION, INSTALL_SOURCE, RESTRICTED_SETTINGS_FLOW, OVERLAY_GRANTED, CALL_OVERLAY_SMOKE, TESTS, MERGE, APK.
