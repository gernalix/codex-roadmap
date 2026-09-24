PROMPT_ID=620949

# Goal
Unifica il monitoraggio Uptime Kuma di TUTTI i repository GitHub attivi di gernalix sotto un solo control plane canonico. Non aggiungere integrazioni Kuma indipendenti repo-per-repo: usa MegaVault come inventario cross-repository e fedora-system-monitor come controller/prober canonico per Fedora e come amministratore del provisioning/readback Kuma. I target remoti direttamente raggiungibili possono usare probe nativi Kuma; eventuali producer remoti necessari devono usare la stessa policy centrale e non possedere naming/provisioning/inventario.

Questa e' una migrazione end-to-end, inclusi i repository che hanno gia' Kuma. I vecchi producer restano attivi fino a quando il sostituto centrale e' verificato live; solo dopo vengono rimossi per evitare buchi di osservabilita'.

# Baseline gia' implementata da ChatGPT
Non reimplementare alla cieca:
- MegaVault contiene il nuovo registro `monitoring_targets`, vista/CLI relativa e policy "Uptime Kuma: control plane unico"; master include almeno i commit 73205e60682fe4863879a0605e7951147ece93e9, c575bea1f904591895c9517494b60a24bcbb3fea e 52852805bbd278d9c2e831e1edf4521ce775b4b8.
- fedora-system-monitor supporta ora freshness esplicita dei oneshot/timer tramite `services.freshness_seconds`, applica freshness agli heartbeat per-servizio e documenta il control plane unico; main include almeno 63f9112b15d514ec36245c12dc17d7640e9980ee, 91b706cebaa2fb56a33cd53810270e6de06a5178, d4b15380481ca08285c1e6ad8dee04b6f44453b6, df265c8abc6efe1fd10dddb46ed784bc9ecbb003 e 831d6e913bd02be66371f90aaa1f0af0cfc795e8.
- Uptime Kuma autorevole vive sulla Oracle VM ed e' raggiungibile tramite il descriptor canonico `fedora-system-monitor kuma-runtime --json`; non indovinare path.
- Il DB live Kuma va modificato solo dopo backup consistente, con write minima/transazionale e readback.
- Non stampare token o URL push completi.

# Inventario GitHub iniziale
Al momento della creazione di questo goal i 31 repository sono:
datasette5, amici_fb, telegram_insert_bot, logseq_updates, oracle-backup-service, MegaVault, livinggaul-x-downloader, fedora-system-monitor, fedora-t7-backup, vm_oracle, codex-usage-monitor, PersonalHub, codex-roadmap, salute, codex-usage, github-autosync, whatsapp-watcher, workflowy-import, adb-device-keeper, activity-watch-uploader, activity-watch-data, github-autosync-data, workflowy-importer, PersonalHub-data, chrome-codex-switcher, eboks-scraper, prompt-history, fedora-context-data, minsp-export, grindr-export, duplicate-photos-detector.

Fai UNA sola verifica bounded dell'inventario GitHub all'inizio; se sono comparsi nuovi repo non archiviati includili. Non fare discovery generale ripetuta.

# Classificazione obbligatoria
Ogni repo corrente deve terminare con almeno un record `monitoring_targets` che dica MONITORED, EXCLUDED o PENDING con motivazione e source_ref verificabile. I data sink e i repo manuali/interattivi non ricevono monitor artificiali: vanno esclusi o associati al producer che ne determina la salute.

Usa questi criteri:
- daemon always-on: liveness + restart-loop;
- timer/oneshot: esito + freshness dell'ultima run rispetto alla cadenza reale; non usare il semplice inactive/success;
- event-driven: stato semantico solo quando esiste l'evento/condizione attesa; niente timeout wall-clock arbitrario;
- HTTP/server: probe nativo Kuma se e' il segnale piu' semplice e stabile;
- componenti manuali/interattivi/data-only: EXCLUDED con motivo quando un monitor non e' azionabile;
- un monitor per failure domain indipendente, non un monitor per file/unit/repo senza valore operativo.

# Migrazione delle integrazioni Kuma gia' esistenti
Verifica e migra esplicitamente almeno:
- github-autosync;
- activity-watch-uploader;
- codex-usage-monitor;
- fedora-system-monitor, che rimane l'unico controller Fedora/Kuma e non va "de-Kuma-izzato".

Per i primi tre:
1. identifica monitor, producer, token boundary, test, configurazione e docs repo-specifiche esistenti;
2. crea/provisiona il target centrale equivalente usando il control plane;
3. verifica un heartbeat reale dal nuovo percorso + readback nel DB Kuma;
4. solo dopo PASS elimina/disattiva il vecchio producer, il vecchio token/config e il monitor duplicato, insieme a test/docs ormai proprietari;
5. preserva l'eventuale logica applicativa necessaria a far terminare il job con exit status coerente: il controller centrale deve poter distinguere successo/failure senza dipendere da una push interna al repo;
6. cerca altre integrazioni Kuma proprietarie solo nei repo dell'inventario gia' in scope e migra anche quelle se trovate.

Alla fine non devono esistere due monitor/producer equivalenti per lo stesso failure domain.

# Target prioritari da chiudere
Verifica e porta a stato corretto almeno questi failure domain:
- datasette5 su Oracle: health HTTP/API reale, preferibilmente probe nativo Kuma; include la projection PersonalHub solo se e' failure domain indipendente;
- oracle-backup-service: freshness/esito backup e healthcheck reale; deve continuare a essere osservabile anche quando il ThinkPad e' spento. Se serve un producer Oracle, rendilo generico e appartenente al control plane, non al repo backup;
- codex-roadmap: freshness di live-status/sync e stato del single writer;
- workflowy-importer: bridge always-on + freshness roadmap-sync; evita monitor separati per timer secondari non azionabili;
- prompt-history: canonicalizza nel repo le unit systemd runtime che oggi risultano installate ma non versionate, poi monitora freshness sync;
- PersonalHub: verifica il consolidation/deploy watcher. Il tree corrente contiene le unit `personalhub-consolidation.*` ma non il file `tools/personalhub_consolidation_watcher.py` referenziato dalla service: correggi il source/runtime o ritira la unit stale; poi monitora il failure domain reale, non l'APK Android;
- duplicate-photos-detector: chiudi il watcher always-on, rimuovi l'assunzione venv dal template/runtime in favore del Python globale conforme a MegaVault, poi monitor liveness; coordina/sostituisci il vecchio task 817056 senza duplicarne il lavoro;
- fedora-t7-backup: event-driven. Non deve risultare DOWN solo perche' T7 e' scollegato; monitora fallimento/backup atteso quando il device e' presente;
- amici_fb: freshness della run giornaliera;
- livinggaul-x-downloader: freshness della run oraria senza confondere indisponibilita' della sorgente X con crash dell'infrastruttura;
- telegram_insert_bot e adb-device-keeper: daemon liveness;
- chrome-codex-switcher: monitor dedicato solo se reso session-aware; altrimenti EXCLUDED dal dedicato con motivazione e copertura aggregata Fedora;
- logseq_updates: monitor dedicato solo se il failure e' realmente azionabile; altrimenti EXCLUDED con copertura systemd aggregata.

# Repository che normalmente non richiedono monitor dedicato
Valida invece di assumere: MegaVault, vm_oracle come repo, salute, codex-usage, whatsapp-watcher, workflowy-import, activity-watch-data, github-autosync-data, PersonalHub-data, eboks-scraper finche' vuoto/non runtime, fedora-context-data, minsp-export, grindr-export. Se un runtime reale contraddice questa classificazione, aggiorna `monitoring_targets` sulla base dell'evidenza.

# Esecuzione Git/codice
- Usa il single-writer/worktree canonico per ogni repository che richiede modifica; non editare branch canonici manualmente.
- Mantieni questo come un solo goal cross-repo perche' tutte le modifiche appartengono allo stesso cutover. Non creare sotto-task indipendenti salvo hard blocker del writer.
- Parti dai file sopra e dalle unit/service gia' note; amplia solo quando un gate concreto lo richiede.
- Niente refactor, cleanup, modernization o audit estranei.
- Riusa helper e contratti centrali; vietato creare un nuovo framework Kuma in un repo applicativo.
- Per componenti su Oracle usa il canonical SSH helper/runtime gia' registrato.
- Correggi anche i problemi collaterali gia' verificati sopra (PersonalHub watcher stale, prompt-history unit non versionate, duplicate-photos venv) perche' bloccano la copertura corretta.

# Riconciliazione Kuma/MegaVault
1. Migra/valida lo schema MegaVault e popola `monitoring_targets` per il 100% dei repo correnti.
2. Fai snapshot/readback del DB Kuma live e sincronizza `kuma_monitors`.
3. Crea/aggiorna solo i monitor necessari; nomi/purpose devono identificare il failure domain, non l'implementazione temporanea.
4. Per ogni MONITORED collega il target al monitor live corretto; per EXCLUDED non creare monitor.
5. Elimina/disabilita monitor legacy duplicati solo dopo il nuovo probe verificato.
6. Risinc `kuma_monitors`, mapping/purpose, quindi finalizza l'inventario Kuma.
7. Verifica che ogni MONITORED sia BOUND_ACTIVE e ogni EXCLUDED abbia rationale; PENDING e' ammesso solo per un hard blocker esterno non risolvibile e deve essere esplicitamente contato.

# Acceptance
PASS solo se:
- tutti i repo GitHub non archiviati correnti sono classificati nel registro centrale;
- nessuna integrazione Kuma repo-specifica equivalente sopravvive nei repo migrati, salvo compatibilita' temporanea dimostrata necessaria da un blocker esterno;
- github-autosync, activity-watch-uploader e codex-usage-monitor sono migrati davvero, non semplicemente duplicati;
- daemon e job schedulati usano semantica corretta, inclusa freshness;
- target Oracle critici restano monitorabili indipendentemente dall'accensione del ThinkPad;
- PersonalHub watcher, prompt-history systemd ownership e duplicate-photos runtime sono coerenti con il source canonico;
- DB Kuma: backup pre-write, write minima, readback post-write, nessun duplicato inatteso;
- MegaVault: operational-index migrate/validate PASS e monitoring target index completo;
- heartbeat/probe reali verificati end-to-end per ogni nuovo/migrato failure domain;
- test mirati + CI dei repo modificati PASS;
- nessun segreto in Git, MegaVault, log o report.

# Stop
Dopo PASS non fare altri audit. Finalizza una sola volta e STOP.

# Report finale
Massimo 10 righe: PROMPT_ID, RESULT, REPOS_CLASSIFIED, MONITORED/EXCLUDED/PENDING, CENTRAL_CONTROLLER, LEGACY_KUMA_REMOVED, ORACLE_TARGETS, FEDORA_TARGETS, KUMA_READBACK, TESTS/BLOCKER.
