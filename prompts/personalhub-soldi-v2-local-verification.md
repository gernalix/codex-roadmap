[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=917364 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_SOLDI_V2_PREMERGE_20260913 | type=Prompt`

# Goal
Esegui la verifica **locale pre-merge** della PR PersonalHub `#7` / branch remoto `feature/soldi-ui-v2`: toolchain Android 37, Gradle, schema/migrazione Room 11→12 e QA isolata su emulatore. Correggi solo failure concrete necessarie a far passare questi gate e pusha lo stesso branch. Non fare release.

# Starting point verificato
La review statica remota dei 20 file è già stata fatta: non rifarla. Il branch contiene Soldi v2, `PersonalHubDatabase` schema 12 e `FinanceAdvancedMigration(11,12)`. Il tentativo GitHub Actions non ha eseguito Gradle perché il runner pubblico non offre `platforms;android-37`; quindi la prova richiesta è deliberatamente locale. La PR ha anche un commento di review con regressioni funzionali note: non ampliare il task in un redesign; segnala soltanto se una di esse impedisce i gate locali.

# Sicurezza / scope
- Acquisisci subito il lock PH con `python3 tools/personalhub_task_lock.py acquire --prompt-id 917364`; lock occupato => `BLOCKED`, nessun polling.
- Lavora su `~/projects/PersonalHub`, fetch una volta e usa `origin/feature/soldi-ui-v2`. Worktree sporco non riconducibile al task => `BLOCKED`; non stash/reset.
- **Nessun bump di `version.txt`**, nessun merge in `main`, nessuna installazione del package reale `com.gernalix.personalhub`, nessuna Telegram/GitHub-release delivery.
- Non toccare DB personale reale. Migrazione solo su DB/test copy disposable; QA Android solo package `qa`/ambiente isolato.
- Parti dai file già noti: `PersonalHubDatabase.kt`, `FinanceAdvancedMigration.kt`, `FinanceEntities.kt`, `FinanceCapsule.kt`, test Soldi e `feature/soldi` UI. Niente discovery generale.

# Gate host, in quest'ordine
1. Conferma una volta che SDK/platform Android 37 locale e Java richiesto dal progetto sono disponibili; se manca una dipendenza locale non installabile senza cambiare il progetto => `BLOCKED`.
2. Esegui `./gradlew --no-daemon checkArchitectureBoundaries`.
3. Esegui i test unitari minimi pertinenti: `:core:database:testDebugUnitTest` e `:feature:soldi:testDebugUnitTest`.
4. Esegui `:app:compileDebugKotlin` e poi una sola build isolata `:app:assembleQa --no-configuration-cache` usando la configurazione signing canonica già prevista dal repo.
5. Verifica che KSP produca/aggiorni lo schema Room `12.json`. Se è un output tracked necessario, includilo nel branch; nessuna modifica manuale del JSON.
6. Il test attuale della migrazione è solo contrattuale: aggiungi/rafforza **un test reale 11→12** con DB disposable e validazione Room/schema, preservando almeno una transazione/conta finance rappresentativa. Esegui solo quel test + il minimo necessario. Se fallisce, correggi la migrazione/schema, non usare destructive migration.
7. Su qualunque failure: apri soltanto il file/simbolo direttamente indicato dall'errore, fix minimo, rerun del solo gate fallito; niente refactor/cleanup collaterale.

# QA emulatore isolata
Solo dopo host gate PASS:
- usa `python3 tools/android_emulator_control.py start` / `wait` e il serial restituito; niente discovery ADB parallela;
- installa l'APK **QA** già costruito, senza seconda build;
- smoke Soldi: apertura modulo; tab Transazioni/Overview/Statistiche/Grafici/Calendario; editor Spesa/Entrata/Trasferimento; trasferimento trans-valuta EUR→DKK; ricorrenza giorno fisso e ultimo giorno lavorativo; modifica importo `solo questa` / `questa e successive`; forecast fine mese per valuta; calendario; nessun crash;
- verifica con `tools/android_ui_summary.py --serial <serial>` solo label/errori mirati, niente XML completo salvo blocker;
- esegui almeno una migrazione 11→12 in ambiente disposable e riapertura Room; nessuna perdita dei record campione;
- se la QA evidenzia un bug runtime nuovo e localizzato, fix minimo + gate direttamente correlato. I problemi già elencati nella review PR che richiedono decisione prodotto vanno solo riportati, non reinterpretati.

# Stop / push
PASS solo se architecture + unit test + compile + assembleQa + schema 12 + migrazione reale + smoke emulatore sono tutti PASS. Commit/pusha soltanto modifiche necessarie su `feature/soldi-ui-v2`; verifica push una volta; ferma emulatore e rilascia lock. Non mergiare la PR.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 917364 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 917364`

Output ≤8 righe: RESULT, host gates, Room 11→12/schema12, APK QA, emulator smoke, fix/commit SHA, push, blocker.
