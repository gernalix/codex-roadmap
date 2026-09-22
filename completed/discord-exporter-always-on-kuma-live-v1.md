PROMPT_ID=832152 | project_id=8 | MODEL=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT
WORKDIR=/home/daniele/projects/fedora-system-monitor

# Goal
Rendi `discord-exporter-crawl.service` realmente always-on e autoriparante sul Fedora reale, senza re-scraping dei canali Discord già completi; quindi crea e verifica nel DB SQLite LIVE di Uptime Kuma un Push Monitor dedicato che segnali DOWN quando il servizio è inattivo e UP alla recovery.

# Starting point già verificato
- user unit: `discord-exporter-crawl.service`; in passato è stata lasciata con `Restart=no`, quindi dopo exit/OOM non si riavvia.
- crawler/state: `/home/daniele/projects/discord-exporter`; catalogo `exports/orchestrator/channel_catalog.sqlite`; profilo `browser-profile`.
- invariant già implementata: `full_crawl_complete=1 AND coverage_status=pass` => vietato history recrawl; db-chat è già stato riconciliato complete/pass.
- Fedora System Monitor main contiene già:
  - merge `986ad91e66a183f937b1213fcf1f00dc58e178d2`: `user:discord-exporter-crawl.service` è essential;
  - merge `465a5bd21fc1c988b52211d77f00069973897ab4`: endpoint Kuma dedicato `discord_exporter` + health evaluation/test.
- credenziali Kuma Fedora canoniche: `/home/daniele/.config/codex/secrets/fedora_system_monitor_uptime_kuma.toml` (0600); non stampare mai URL/token.
- VM/Uptime Kuma: usare il repo canonico `~/projects/vm_oracle` e `scripts/oracle_ssh.sh`; Kuma gira via Docker Compose in `/opt/uptime-kuma` con DB persistente nel volume. Non usare browser/JWT se il DB basta.

# Scope stretto
Diagnosi e fix SOLO del lifecycle discord-exporter, deploy dei fix fedora-system-monitor già mergiati, creazione/verifica del monitor Kuma dedicato e wiring secret. Niente audit repo-wide, refactor/cleanup, scraping Discord extra, modifiche ad altri monitor salvo relazioni notification necessarie.

# Esecuzione
1. Avvia il task con `roadmap_start.py` e usa il worktree restituito per eventuali modifiche a fedora-system-monitor. Riusa i fatti sopra; amplia solo se l'evidenza li smentisce.
2. Prima di cambiare unit/codice, raccogli UNA diagnosi bounded dell'ultimo stop reale:
   - `systemctl --user show/status/cat discord-exporter-crawl.service`;
   - journal dell'ultima exit + kernel/OOM nello stesso intervallo;
   - MainPID/ExecMainStatus/Result/ActiveState;
   - stato catalog/checkpoint del crawler.
   Classifica la causa concreta: normal exit, exception, browser exit, OOM, signal, unit policy o altro. Non presumere che ogni stop sia OOM.
3. Correggi l'architettura perché la UNIT resti sempre `active`:
   - preferisci un supervisor/daemon persistente nel repo discord-exporter che resta vivo anche quando non c'è lavoro;
   - il supervisor deve eseguire/resumere il crawl sequenziale quando necessario e restare idle/sleep quando non c'è lavoro;
   - `Restart=always` con `RestartSec`/StartLimit sensati come rete di sicurezza, non come loop operativo;
   - exit normale del singolo `crawl-all` NON deve far oscillare la unit start/stop;
   - un crash/OOM deve far ripartire il supervisor automaticamente.
4. Browser lifecycle:
   - massimo UN persistent Chromium context per singolo ciclo di crawl;
   - niente raffica di launch/close/relaunch;
   - nessun browser durante idle se non necessario;
   - secondo launch nello stesso ciclo deve essere impedito dal guard già esistente;
   - preserva `/home/daniele/projects/discord-exporter/browser-profile`.
5. Resume/data safety:
   - NON riscrapare history di canali `complete+pass`;
   - riprendi partial/running dalla boundary/cursor persistita;
   - overlap solo bounded + dedup;
   - non cancellare DB/state/checkpoint.
6. Se serve modificare discord-exporter, fai il minimo fix + test mirati. Per fedora-system-monitor non riscoprire i fix: verifica che i due merge sopra siano su main, esegui test mirati + suite solo se necessario, poi installa/deploya il runtime con il meccanismo esistente.
7. Verifica always-on sul Fedora reale:
   - unit enabled e active/running;
   - osserva progresso/resume quando c'è lavoro;
   - esegui UNA failure injection sicura sul SOLO processo/supervisor (SIGTERM o equivalente controllato, non OOM artificiale): deve tornare active automaticamente entro un bound ragionevole;
   - dopo recovery checkpoint/count non tornano a zero e nessun complete+pass viene ricrawlato;
   - dopo completamento del lavoro, la unit resta active in idle senza restart loop;
   - NRestarts/backoff coerenti.
8. Uptime Kuma LIVE DB — prima backup, poi mutazione atomica:
   - accedi con `~/projects/vm_oracle/scripts/oracle_ssh.sh`;
   - identifica il file SQLite live del container/volume senza stampare secret;
   - crea backup consistente (SQLite backup API o stop breve del container se necessario) con timestamp e verifica apertura;
   - introspeziona schema/versione e individua un monitor Push esistente compatibile (preferibilmente Fedora Services) + tabelle notification relation;
   - crea nel DB un monitor Push dedicato chiamato chiaramente `Discord Exporter Crawl Service`, copiando SOLO i campi strutturali/default necessari e generando un token push unico;
   - clona le associazioni notification dal monitor Services esistente, senza duplicati;
   - non toccare history/heartbeat di altri monitor;
   - fai la modifica in transazione e riavvia Kuma solo se il DB live lo richiede.
9. Secret wiring:
   - porta il nuovo endpoint/token al Fedora System Monitor senza mai stamparlo o inserirlo in argv/log/git;
   - aggiorna il TOML 0600 aggiungendo `[push].discord_exporter` (o formato esatto già usato) preservando tutte le altre entry;
   - usa file temporanei 0600/STDIN/scp sicuro; elimina temp secret dopo verifica.
10. Deploy Fedora System Monitor e verifica producer reale:
    - il minuto collector deve emettere heartbeat dedicato `discord_exporter`;
    - service active => Push UP;
    - service inactive/failure => Push DOWN;
    - recovery => Push UP;
    - il monitor generico Fedora Services deve continuare a coprire lo stesso servizio come essential.
11. Gate end-to-end Kuma obbligatorio:
    - invia un probe/heartbeat reale con nonce/correlation marker univoco tramite il producer reale, senza mostrare token;
    - readback direttamente dal DB Kuma live/backup recente: stesso monitor, marker e timestamp attesi;
    - verifica una sequenza controllata DOWN -> UP recovery;
    - almeno due cicli reali del monitor;
    - nessun 2xx da solo vale come prova.
12. Se il DB Kuma/schema differisce dallo starting point, fai discovery mirata e adatta la mutazione; NON fare retry identici e NON ricreare il monitor se esiste già (idempotenza per name/type/token mapping).
13. A fine task lascia:
    - discord-exporter service enabled + active;
    - crawler/supervisor sano e non duplicato;
    - Kuma monitor dedicated UP;
    - Fedora Services sano;
    - backup Kuma conservato;
    - working tree/branch puliti secondo il workflow.

# Acceptance criteria
PASS solo se TUTTO vero:
- root cause degli stop recenti identificata con evidenza journal/systemd;
- `discord-exporter-crawl.service` resta always-on anche quando non c'è lavoro;
- crash controllato => auto-restart PASS senza restart loop;
- resume/checkpoint PASS e complete+pass recrawled=0;
- browser launch <=1 per ciclo e nessun relaunch storm;
- fix fedora-system-monitor già mergiati sono deployati;
- monitor Push dedicato esiste nel DB LIVE di Kuma e ha notification mapping valido;
- endpoint secret Fedora configurato 0600 e non esposto;
- producer reale mostra UP, DOWN, recovery UP;
- readback DB Kuma con nonce PASS e >=2 cicli reali PASS;
- monitor generico Fedora Services continua a segnalare correttamente;
- test mirati PASS.

# Non-goal
Nuove feature scraper, rich extraction, nuovi canali, dashboard, refactor, tuning generale RAM, modifiche ad altri monitor/alert, browser automation Kuma.

# Stop / report
Appena gli acceptance criteria sono verificati, finalizza con roadmap_result/roadmap_finish e STOP. Output finale max 12 righe:
PROMPT_ID, RESULT, ROOT_CAUSE, SERVICE_STATE, RESTART_TEST, RESUME, BROWSER_LIFECYCLE, FSM_DEPLOY, KUMA_MONITOR_ID, KUMA_E2E, TESTS, BLOCKER se presente.