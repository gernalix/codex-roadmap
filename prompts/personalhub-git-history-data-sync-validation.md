PROMPT_ID=672418 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Valida e, SOLO dove i test locali mostrano un difetto concreto, completa la piattaforma già implementata su PersonalHub main: Git Data Sync opzionale + history/event-sourcing lite + Time Machine globale + pull patch/migrazioni + restore granulare/globale. Questo è un gate di rischio-dati prima del successivo task PH; non ridisegnare la feature.

# Starting point autoritativo
- repo: /home/daniele/projects/PersonalHub, branch canonico main;
- esegui SOLO dopo PROMPT_ID=724615 PASS/finalizzato E dopo che l'utente ha mergiato `feature/salute-canonical-domain` in main: main deve già contenere profili globali + schema timestamp epoch-ms + Salute canonica completa in personalhub.db;
- baseline Git History/Data già implementata: 0efd93ed547ac8dad9d8de69083e572367800aec deve essere antenata di RUN_HEAD; commit successivi non correlati (es. Salute CI) vanno preservati;
- version.txt resta 50: NON fare bump, NON installare il package reale sul Pixel, NON inviare APK; la release resta nel task PH successivo;
- file/boundary già noti: core/database/.../capsules/gitdata/*, DeclarativeMigrations.kt, DatabaseVault.kt, DatabaseGate.kt, PersonalHubDatabase.kt, HubActivityCapture.kt, feature/multitimetracker/.../SnapshotSqlite.kt, app/.../capsules/settings/{HubSettings,GitHistorySettings}.kt, MainActivity.kt, docs/GIT_DATA_HISTORY.md;
- SQLite resta source of truth runtime; Git è solo history/transport; Git OFF è il default; la configurazione Git deve accettare solo repository GitHub PRIVATI e scrivibili;
- manifest state v2 usa JSONL sharded; BLOB in objects/sha256; history JSONL immutabile firmato; local hub_git_history_index è ricostruibile;
- restore globale passa da staging + DatabaseVault; revert granulare crea un nuovo edit e non riscrive history; il preview del revert deve provarlo su una copia coerente senza toccare il DB live;
- con Git ON il legacy HubActivityCapture globale è fallback disattivato; con Git OFF torna il Registro/Activity globale locale. Timer non possiede più Time Machine, Audit Log o Import/Export separati;
- History espone diff tabellare + diff semantico record/campi, restore tramite ref arbitrario, milestone, branch/PR proposta, sandbox preview patch e discard branch `data/*`;
- startup schema upgrade usa prima migration packaged; se l’APK supporta già lo schema target ma manca un path packaged, può usare una chain remota dichiarativa verificata dal repo Git opzionale, sempre su staging.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 672418. Un solo preflight: stato worktree, un fetch origin/main, fast-forward se sicuro; richiedi che la baseline sopra sia antenata del RUN_HEAD. Dirty non sovrapposto non blocca; niente stash/reset. Nessun audit repo-wide.
2. Prima di modificare codice esegui SOLO compile/test leaf pertinenti al boundary sopra. Raccogli tutti gli errori dello stesso failure domain in una volta, correggili in batch, poi rilancia il leaf; niente loop di gradle check.
3. Aggiungi/rafforza test mirati per i contratti seguenti, riusando seam/helper esistenti. Se serve testare HTTP GitHub, aggiungi il minimo seam di injection dell'API base e usa un fake locale; NON creare o usare un repository con dati personali.
   - Git OFF: nessuna richiesta/push automatico; il Registro/Activity globale locale continua a funzionare; Timer resta privo di Time Machine/Audit separati.
   - Git ON: tracking installato, legacy HubActivityCapture rimosso; OFF lo reinstalla.
   - una transazione domain INSERT/UPDATE/DELETE genera event atomico con before/after, author, source, reason/group; rollback non genera history.
   - Salute canonica: una patch health sintetica con sample + più measurement + AI snapshot usa un unico group_id/import_batch, compare nella History, supporta preview/revert del singolo record e dell'intero gruppo e non genera un secondo motore history.
   - tutte le write della stessa outer SQLite transaction ricevono automaticamente lo stesso group_id; write fuori transazione restano eventi singoli; context espliciti remote_patch/history_revert prevalgono senza contaminare la transazione successiva.
   - fault injection sul cleanup del context storico: la outer transaction deve sempre chiudersi/sbloccare; nessun context autore/source può contaminare la transazione seguente e l’esito commit/rollback deve restare non ambiguo.
   - snapshot/snapshot_history/snapshot_payloads e altri technical churn restano sincronizzabili nello state ma NON generano semantic history payload enormi.
   - push debounce 60 s, recovery persistente/offline e ack revision-safe: un edit committato non può sparire prima del push confermato.
   - JSONL deterministico + sharding 1/8/32/128; una modifica limitata non richiede upload di shard invariati.
   - BLOB content-addressed: stesso SHA => stesso object; hash mismatch in restore => FAIL.
   - batch history firmato ECDSA; firma valida PASS e tamper FAIL durante rebuild.
   - local history index ricostruibile da Git; filtri/blame/stats/time window non leggono/replayano tutta Git history a ogni schermata.
   - stats temporali (edit anno, per tabella, durata media field-value) usano proiezione incrementale idempotente; retry stesso event_id non raddoppia aggregati e rebuild index ricostruisce anche la proiezione.
   - anomaly gate: batch distruttivo resta locale/attention finché non viene esplicitamente force-pushato.
   - patch remote: hash + minimum_app_version + optimistic expect + FK; author/source provenance corretta; idempotenza; cherry-pick da ref senza Git merge; preview sandbox deve produrre conteggi +/~/- e tabelle senza mutare il DB live.
   - pull/sync NON applica patch remote: deve solo verificarle e pubblicare gli id pending per review; solo azione esplicita dopo preview può applicare una patch.
   - logical edit group revert: reverse order, atomicità, optimistic stale check e foreign_key_check; il revert genera nuova history; preview closure prova davvero l’inverso su copia e segnala safe/blocked.
   - full restore v1 e v2 sharded: staging, object hash, schema compatibility, declarative/remote migration consentita solo entro schema supportato dall'APK, quick_check/FK, atomic replacement e rollback su failure; restore deve poter risolvere anche un ref arbitrario più vecchio delle revisioni recenti mostrate.
   - Time Machine globale: oltre alla lista recente, ref arbitrario e jump per data `YYYY-MM-DD` devono risolvere la revisione più recente entro fine giornata senza alterare il DB finché l’utente non conferma restore.
   - Timer: le sue normali write sono rappresentate nella History/Time Machine globale PH; nessuna route/capsule Timer reintroduce Time Machine o Audit Log locale.
   - Temporal Search PH: con Git ON include una sezione non selezionabile degli edit Git nello stesso intervallo di Places/Timer/Soldi/Substances/WordPulse/People/Salute; con Git OFF non aggiunge tale sezione.
4. Verifica UI Compose mirata: checkbox Git OFF di default; se attivata senza config apre richiesta repo HTTPS + token; repo pubblico viene rifiutato e repo privato scrivibile accettato; Settings/Home espongono History/Time Machine globali e Timer non le duplica; Home Registro usa Git History solo quando enabled; attention mostra force push; restore globale richiede conferma; deep restore per commit/tag/branch funziona; semantic diff, revert preview, patch pending verificata è visibile ma non auto-applicata; patch sandbox/cherry-pick e discard proposta sono accessibili; nessun token appare in state/log/db.
5. Verifica storage/performance con test sintetico bounded: almeno una tabella >500 righe e una >5k per shard policy, un BLOB ripetuto, almeno 1.000 history event. Richiedi che le normali letture Home/moduli non invochino Git e che nessun full DB binary venga committato. Aggiungi un fixture schema N→N+1 senza migration packaged e verifica che, con Git configurato, la chain remota migri SOLO staging e che con Git OFF fallisca chiuso senza rete/dati persi.
6. Gate host finale UNA volta dopo i leaf PASS: test core/database + app/Timer pertinenti, compile debug e checkArchitectureBoundaries. Non eseguire audit/refactor/cleanup estranei.
7. QA solo AVD canonico Pixel_8a tramite tools/android_emulator_control.py start|wait|stop. Usa dati sintetici/QA, non dati reali:
   - toggle OFF→config→ON;
   - create/update/delete in almeno People, Timer, Places, Substances, Soldi;
   - History mostra autore/provenienza, diff semantico e stats temporali; Temporal Search mostra anche gli edit Git del periodo;
   - granular revert di un logical edit dopo preview sandbox safe; prova anche un revert blocked da FK/stale state;
   - anomaly attention senza perdita;
   - preview di una patch proposta su sandbox, cherry-pick della stessa e discard di un branch `data/*` sintetico;
   - full restore di una revisione QA recente e di un ref QA arbitrario e riavvio;
   - Git OFF ripristina comportamento fallback;
   - nessun crash/log secret.
   Se il test remoto richiede un endpoint, usa fake locale/test seam; nessun repository personale/prod.
8. Documentazione: aggiorna docs/GIT_DATA_HISTORY.md solo se il comportamento verificato differisce dal contratto già descritto. Non aggiungere nuove feature durante il gate.
9. Push main solo per fix/test necessari emersi dai gate. Niente branch persistenti. Rilascia task lock in ogni esito. PASS => stop.

# Acceptance
PASS solo se compile + test mirati + architecture gate + AVD QA sono PASS; Git resta interamente opzionale; repository pubblico è rifiutato; history non duplica technical churn; provenance/undo+preview/restore profondo/diff semantico/timeline unificata/stats incrementali/sharding/BLOB/signature/pull-review-only+patch sandbox+cherry-pick+discard/migration packaged+remote fallback/anomaly e integrazione Timer nella History globale sono verificati; nessun dato reale o credential finisce in Git/log; version.txt resta 50.

# Non-goal
Niente Data Explorer/Datasette Lite, redesign moduli, nuovo backend, repository dati reale, migrazione distruttiva dello storico Timer pre-Git, cancellazione automatica di history legacy, bump/release/install Pixel/delivery, refactor generale o audit.

# Stop
Dopo PASS:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 672418 --confirm-executed

Output massimo 8 righe: RESULT, HEAD, HOST_TESTS, HISTORY, PATCH_RESTORE, TIMER, AVD_QA, BLOCKER.
