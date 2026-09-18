PROMPT_ID=418763 | project_id=15 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Distribuisci SOLO `gernalix/activity-watch-uploader` sul Fedora reale, crea/configura direttamente nel DB autorevole di Uptime Kuma un unico monitor push dedicato, collega il relativo secret al servizio senza esporlo e chiudi il flusso end-to-end ActivityWatch → JSONL/Git → Kuma. Il codice applicativo e le unit template sono già su GitHub: niente redesign.

# Starting point autoritativo
- repo remoto privato: `gernalix/activity-watch-uploader`, branch `main`; baseline minima da includere: `37e94c39f8c0f56e4eaeeecaca543d91dc762a72`;
- checkout Fedora canonico: `/home/daniele/projects/activity-watch-uploader`;
- ActivityWatch API locale: `http://127.0.0.1:5600`;
- il codice fa full reconcile iniziale/settimanale, refresh rolling degli ultimi 2 giorni UTC, write atomiche, lock anti-overlap, recovery Git, timeout HTTP/Git e push Kuma con `run_id`;
- unità: `activity-watch-uploader.service` + `activity-watch-uploader.timer`; il timer è ogni 15 minuti, `Persistent=true`, `OnBootSec=2min`; il service ha `Restart=on-failure`, restart bounded e `TimeoutStartSec=12min`;
- il timer deve funzionare anche senza login interattivo dopo reboot: usa il normale systemd user manager con lingering dell'utente `daniele`;
- repo VM: `/home/daniele/projects/vm_oracle`; accesso canonico SOLO tramite `scripts/oracle_ssh.sh`;
- Uptime Kuma: Docker Compose canonica `/opt/uptime-kuma/docker-compose.yml`, container `uptime-kuma`, dati persistenti sotto `/opt/uptime-kuma/data`, versione attesa 2.4.x;
- nome monitor desiderato: `ActivityWatch Git Uploader (Fedora)`; tipo `push`; intervallo 1200 s, retry 300 s, max retries 2, non upside-down;
- URL pubblico push: `https://kuma.danielegalati.com/api/push/<token>`;
- non stampare, loggare, versionare o includere nel report token Kuma, credenziali Git/SSH o altri secret.

# Esecuzione minima
1. **Fedora preflight, un batch.** Se il checkout manca, clona direttamente nel path canonico; altrimenti fai solo `fetch` + fast-forward. Richiedi branch `main`, baseline sopra inclusa e nessuna modifica locale non gestita. Esegui una volta:
   - `python3 -m unittest discover -s tests -v`;
   - `python3 -m py_compile activity_watch_uploader.py`;
   - `systemd-analyze --user verify` sulle due unità;
   - probe bounded di `/api/0/buckets` verificando solo HTTP/numero bucket, senza dump di URL/titoli/eventi;
   - verifica che Git verso `origin/main` funzioni non-interattivamente con `GIT_TERMINAL_PROMPT=0`/SSH BatchMode. Non creare PAT, key o credential nuove. Se l'autenticazione unattended non è già sicura e funzionante: `BLOCKED` e stop prima di toccare Kuma.

2. **Kuma preflight + backup, un batch Oracle.** Sincronizza `vm_oracle/main` con `--ff-only`, poi usa soltanto `scripts/oracle_ssh.sh`. Limita l'ispezione a `/opt/uptime-kuma`: identifica il DB SQLite effettivo, fai un backup consistente owner-only prima di ogni write e leggi UNA sola volta lo schema minimo di `monitor`, `monitor_notification` (se presente) e tabelle heartbeat necessarie. Non indovinare colonne e non fare scan filesystem generali.

3. **Upsert DB idempotente.**
   - cerca per nome esatto + tipo `push`; 0 righe => crea; 1 => aggiorna solo i campi necessari; >1 => `BLOCKED`, niente delete/dedup automatico;
   - genera un token crittograficamente casuale SOLO se il monitor non ne ha già uno;
   - imposta active=1, interval=1200, retry=300, max retries=2, upside_down=0 usando i nomi reali dello schema;
   - se il binding notifiche è supportato e non ambiguo, copia il set di notification binding dal monitor Fedora #39, senza leggere/esporre secret;
   - la write deve avvenire in transazione con Kuma fermato solo per la finestra minima necessaria; poi riavvia esclusivamente lo stack/container Kuma e verifica DB integrity + readiness HTTP;
   - se write/integrity/startup falliscono, ripristina subito il backup e riavvia Kuma; poi `BLOCKED`.

4. **Handoff secret senza esposizione.** Il token deve transitare fra Fedora e Oracle tramite file/stdin owner-only, mai come testo stampato o argomento che finisca nel report. Scrivi `~/.config/activity-watch-uploader/env` mode 0600 con almeno `AW_BASE_URL` e `KUMA_PUSH_URL`. Non fare `cat`, `echo` o readback del valore; verifica solo presenza/non-vuoto e permessi.

5. **Deploy resiliente Fedora.**
   - abilita `loginctl enable-linger daniele` se non già attivo e verifica `Linger=yes`;
   - esegui `bash scripts/install-user-service.sh`;
   - verifica che timer sia enabled+active e che i valori effettivi includano: `Persistent=true`, schedule 15 min + boot delay, `Restart=on-failure`, `RestartSec=2min`, `TimeoutStartSec=12min`, `KillMode=control-group`;
   - non trasformare il servizio in daemon loop: timer+oneshot restano il design canonico.

6. **End-to-end reale, due run systemd.**
   - avvia il service tramite `systemctl --user start activity-watch-uploader.service`, non direttamente Python;
   - raccogli solo `run_id`, mode, changed_files ed exit status dal journal/output; non dumpare raw data;
   - verifica che `metadata/buckets.json` e i file `raw/<bucket>/YYYY-MM-DD.jsonl` esistano, che il commit/push sia arrivato su `origin/main`, e che non vi siano modifiche estranee;
   - sul DB Kuma verifica che l'ultimo heartbeat del nuovo monitor sia `up`, recente e contenga ESATTAMENTE quel `run_id`;
   - esegui una seconda volta lo stesso service dopo la chiusura della prima e verifica un `run_id` diverso, exit 0, Git ancora coerente e heartbeat Kuma aggiornato al secondo `run_id`. Questo copre idempotenza/recovery senza attendere inutilmente 15 minuti.

7. **Resilienza.** Non riavviare la macchina. La chiusura richiede evidenza deterministica che reboot/freeze siano coperti da: lingering + timer persistente/OnBootSec, timeout hard del oneshot, restart bounded, lock anti-overlap, timeout/retry applicativi e crash recovery Git già testati. Se emerge un bug reale in questi boundary, applica SOLO il fix minimo nel repo, riesegui il leaf test pertinente, push su `main` e ripeti solo il gate fallito.

# Acceptance
PASS solo se:
- test/compile/unit verify PASS e ActivityWatch risponde;
- Git push unattended è funzionante senza nuove credential;
- esiste esattamente un monitor Kuma push `ActivityWatch Git Uploader (Fedora)` con 1200/300/maxRetries=2 e backup pre-write verificato;
- Kuma torna healthy dopo la write e DB integrity è OK;
- secret locale è owner-only 0600 e non compare in output/report/Git;
- user lingering è attivo; timer enabled+active; unit effettive conservano i boundary di resilienza;
- due run systemd consecutivi finiscono exit 0, pushano/reconciano Git correttamente e producono due heartbeat Kuma correlati ai rispettivi `run_id`;
- nessun raw ActivityWatch viene stampato nel report.

# Non-goal
Niente refactor, cleanup, nuove feature, UI, nuovi branch persistenti, PAT/SSH key nuove, audit generale Fedora/Oracle, modifica di altri monitor Kuma, reboot reale, analisi dei dati ActivityWatch, modifica di ActivityWatch stesso o dei watcher.

# Stop
Al primo blocker concreto fermati senza retry equivalenti. Dopo PASS esegui UNA sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 418763 --confirm-executed`

Niente dry-run separato o audit post-PASS. Output finale massimo 7 righe: `RESULT`, `FEDORA`, `ACTIVITYWATCH`, `GIT`, `KUMA`, `RESILIENCE`, `BLOCKER`.
