PROMPT_ID=672418 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Valida e, SOLO dove i test locali mostrano un difetto concreto, completa la piattaforma già implementata su PersonalHub main: Git Data Sync opzionale + history/event-sourcing lite + Time Machine globale + pull patch/migrazioni + restore granulare/globale. Questo è un gate di rischio-dati prima del successivo task PH; non ridisegnare la feature.

# Starting point autoritativo
- repo: /home/daniele/projects/PersonalHub, branch canonico main;
- baseline Git History/Data già implementata: 3558ab39fb7f51f39a09c43e6d90b18ae3319b07 deve essere antenata di RUN_HEAD;
- version.txt resta 48: NON fare bump, NON installare il package reale sul Pixel, NON inviare APK; la release resta nel task PH successivo;
- file/boundary già noti: core/database/.../capsules/gitdata/*, DeclarativeMigrations.kt, DatabaseVault.kt, DatabaseGate.kt, PersonalHubDatabase.kt, HubActivityCapture.kt, feature/multitimetracker/.../SnapshotSqlite.kt, app/.../capsules/settings/{HubSettings,GitHistorySettings}.kt, MainActivity.kt, docs/GIT_DATA_HISTORY.md;
- SQLite resta source of truth runtime; Git è solo history/transport; Git OFF è il default;
- manifest state v2 usa JSONL sharded; BLOB in objects/sha256; history JSONL immutabile firmato; local hub_git_history_index è ricostruibile;
- restore globale passa da staging + DatabaseVault; revert granulare crea un nuovo edit e non riscrive history;
- con Git ON il legacy HubActivityCapture è fallback disattivato e Timer non aggiunge nuovi snapshot_history; date pre-Git mantengono fallback locale.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 672418. Un solo preflight: stato worktree, un fetch origin/main, fast-forward se sicuro; richiedi che la baseline sopra sia antenata del RUN_HEAD. Dirty non sovrapposto non blocca; niente stash/reset. Nessun audit repo-wide.
2. Prima di modificare codice esegui SOLO compile/test leaf pertinenti al boundary sopra. Raccogli tutti gli errori dello stesso failure domain in una volta, correggili in batch, poi rilancia il leaf; niente loop di gradle check.
3. Aggiungi/rafforza test mirati per i contratti seguenti, riusando seam/helper esistenti. Se serve testare HTTP GitHub, aggiungi il minimo seam di injection dell'API base e usa un fake locale; NON creare o usare un repository con dati personali.
   - Git OFF: nessuna richiesta/push automatico, legacy Activity/Timer Time Machine continuano a funzionare.
   - Git ON: tracking installato, legacy HubActivityCapture rimosso; OFF lo reinstalla.
   - una transazione domain INSERT/UPDATE/DELETE genera event atomico con before/after, author, source, reason/group; rollback non genera history.
   - snapshot/snapshot_history/snapshot_payloads e altri technical churn restano sincronizzabili nello state ma NON generano semantic history payload enormi.
   - push debounce 60 s, recovery persistente/offline e ack revision-safe: un edit committato non può sparire prima del push confermato.
   - JSONL deterministico + sharding 1/8/32/128; una modifica limitata non richiede upload di shard invariati.
   - BLOB content-addressed: stesso SHA => stesso object; hash mismatch in restore => FAIL.
   - batch history firmato ECDSA; firma valida PASS e tamper FAIL durante rebuild.
   - local history index ricostruibile da Git; filtri/blame/stats/time window non leggono/replayano tutta Git history a ogni schermata.
   - anomaly gate: batch distruttivo resta locale/attention finché non viene esplicitamente force-pushato.
   - patch remote: hash + minimum_app_version + optimistic expect + FK; author/source provenance corretta; idempotenza; cherry-pick da ref senza Git merge.
   - logical edit group revert: reverse order, atomicità, optimistic stale check e foreign_key_check; il revert genera nuova history.
   - full restore v1 e v2 sharded: staging, object hash, schema compatibility, declarative/remote migration consentita solo entro schema supportato dall'APK, quick_check/FK, atomic replacement e rollback su failure.
   - Timer: con Git ON writeSnapshot non cresce snapshot_history; loadAsOf usa Git per date coperte e fallback locale pre-Git.
4. Verifica UI Compose mirata: checkbox Git OFF di default; se attivata senza config apre richiesta repo HTTPS + token; Settings espone History/Time Machine; Home Registro usa Git History solo quando enabled; attention mostra force push; restore globale richiede conferma; nessun token appare in state/log/db.
5. Verifica storage/performance con test sintetico bounded: almeno una tabella >500 righe e una >5k per shard policy, un BLOB ripetuto, almeno 1.000 history event. Richiedi che le normali letture Home/moduli non invochino Git e che nessun full DB binary venga committato.
6. Gate host finale UNA volta dopo i leaf PASS: test core/database + app/Timer pertinenti, compile debug e checkArchitectureBoundaries. Non eseguire audit/refactor/cleanup estranei.
7. QA solo AVD canonico Pixel_8a tramite tools/android_emulator_control.py start|wait|stop. Usa dati sintetici/QA, non dati reali:
   - toggle OFF→config→ON;
   - create/update/delete in almeno People, Timer, Places, Substances, Soldi;
   - History mostra autore/provenienza;
   - granular revert di un logical edit;
   - anomaly attention senza perdita;
   - full restore di una revisione QA e riavvio;
   - Git OFF ripristina comportamento fallback;
   - nessun crash/log secret.
   Se il test remoto richiede un endpoint, usa fake locale/test seam; nessun repository personale/prod.
8. Documentazione: aggiorna docs/GIT_DATA_HISTORY.md solo se il comportamento verificato differisce dal contratto già descritto. Non aggiungere nuove feature durante il gate.
9. Push main solo per fix/test necessari emersi dai gate. Niente branch persistenti. Rilascia task lock in ogni esito. PASS => stop.

# Acceptance
PASS solo se compile + test mirati + architecture gate + AVD QA sono PASS; Git resta interamente opzionale; history non duplica technical churn; provenance/undo/restore/sharding/BLOB/signature/patch/migration/anomaly/Timer fallback sono verificati; nessun dato reale o credential finisce in Git/log; version.txt resta 48.

# Non-goal
Niente Data Explorer/Datasette Lite, redesign moduli, nuovo backend, repository dati reale, migrazione distruttiva dello storico Timer pre-Git, cancellazione automatica di history legacy, bump/release/install Pixel/delivery, refactor generale o audit.

# Stop
Dopo PASS:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 672418 --confirm-executed

Output massimo 8 righe: RESULT, HEAD, HOST_TESTS, HISTORY, PATCH_RESTORE, TIMER, AVD_QA, BLOCKER.
