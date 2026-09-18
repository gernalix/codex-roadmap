PROMPT_ID=286419 | project_id=15 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Riprendi SOLO dal blocker di 751306 e chiudi il deploy ActivityWatch uploader. Non ripetere gate già PASS né riscoprire stato noto.

# Starting point autoritativo
- 751306: checkout bootstrap PASS; host gate PASS con 15 test, compile, systemd verify, ActivityWatch HTTP 200/5 bucket e fetch Git dati non-interattivo.
- blocker unico: la transazione Kuma ha tentato un file token fisso in `/tmp`; `sudo python3` ha ricevuto `PermissionError`. Non usare più alcun handoff remoto in `/tmp`.
- codice remoto: `gernalix/activity-watch-uploader` main, baseline minima `bcbad939b9d8b53a5d6e0e7afebc5365ba5f42ac`.
- nuovo helper locale: `scripts/set_kuma_push_url.py`; legge il token da stdin, aggiorna atomicamente `~/.config/activity-watch-uploader/env` mode 0600 e NON stampa il token.
- dati: `gernalix/activity-watch-data` main, checkout canonico `~/projects/activity-watch-data`.
- Oracle helper autoritativo: `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh`. NON aprirlo/catarlo: è già verificato.
- Kuma: compose `/opt/uptime-kuma/docker-compose.yml`, container `uptime-kuma`, DB atteso `/opt/uptime-kuma/data/kuma.db`; monitor `ActivityWatch Git Uploader (Fedora)`, type=push, interval=1200, retry=300, maxRetries=2, upside_down=0; template notifiche monitor #39.
- il monitor può essere assente oppure essere stato parzialmente creato dal tentativo precedente: l'upsert deve essere idempotente per nome esatto+type.
- mai stampare token/credential; niente token in argv, journal o report.

# Esecuzione minima

## 1. Fast-forward + SOLO test nuovi — una shell call
Nel checkout codice canonico:
1. esegui una sola volta `python3 scripts/bootstrap_checkouts.py --code-root ~/projects/activity-watch-uploader --data-root ~/projects/activity-watch-data --code-baseline bcbad939b9d8b53a5d6e0e7afebc5365ba5f42ac --data-baseline fb656dde8386465497f51218262b43f17bc9bf27`;
2. poi SOLO:
   - `python3 -m unittest tests.test_set_kuma_push_url -v`
   - `python3 -m py_compile scripts/set_kuma_push_url.py`
Non rieseguire i 15 test, ActivityWatch probe, systemd verify o Git capability già PASS.

## 2. Kuma transaction — una sola SSH call
Usa direttamente `scripts/oracle_ssh.sh`; niente lettura dell'helper e niente inventory VM.
In un unico script remoto bounded:
- verifica container/DB e fa backup SQLite consistente owner-only PRIMA della write;
- legge una sola volta lo schema minimo necessario;
- upsert idempotente del monitor: se 0 crea clonando il monitor #39 e sovrascrive i campi push; se 1 aggiorna; se >1 o stesso nome non-push => BLOCKED;
- se manca token, genera 32 caratteri alfanumerici e lo salva SOLO in `monitor.push_token`; NON scriverlo su filesystem e NON stamparlo;
- copia i soli binding `monitor_notification.notification_id` da #39 quando la tabella/schema è quello atteso;
- stop Kuma solo per la finestra DB, transazione, `integrity_check`, restart, readiness bounded;
- su qualunque failure dopo il backup: stop se necessario, restore backup con sidecar WAL/SHM gestiti, restart/readiness, poi BLOCKED.
Output remoto consentito: solo status, monitor_id, created/updated, backup path e readiness; mai token.

## 3. Token DB → env Fedora senza file remoto — una shell call
Dopo Kuma PASS, usa UNA pipeline shell: il lato Oracle esegue una query read-only esatta su `kuma.db` che restituisce SOLO `push_token` del singolo monitor; il suo stdout deve essere collegato DIRETTAMENTE allo stdin di:
`python3 ~/projects/activity-watch-uploader/scripts/set_kuma_push_url.py`
Non catturare il token in variabili stampate, file `/tmp`, command args o output tool. La pipeline deve mostrare soltanto `ENV_UPDATED=...`.
Verifica solo mode env=600 e presenza non-vuota di `KUMA_PUSH_URL`, senza mostrarne il valore.

## 4. systemd + due run E2E — massimo due shell call
- abilita/verifica lingering `daniele`;
- `bash scripts/install-user-service.sh`;
- un solo readback: timer enabled+active; `Persistent=true`, 15 min + boot delay; service `Restart=on-failure`, `RestartSec=2min`, `TimeoutStartSec=30min`, `KillMode=control-group`.
Poi avvia serialmente due volte SOLO `systemctl --user start activity-watch-uploader.service`.
Per run raccogli solo `run_id`, mode, changed_files, exit.
Dopo run 1 verifica bounded: tutti i 5 bucket + storici/unknown dell'export nel repo dati, JSONL valido, push su origin/main e heartbeat Kuma `up` con lo stesso run_id.
Dopo run 2: nuovo run_id, exit 0, Git coerente, heartbeat aggiornato allo stesso nuovo run_id.

# Acceptance
PASS solo con Kuma DB/integrity/readiness PASS, env 0600 senza token esposto, systemd/lingering PASS e due run correlati Git+Kuma PASS.

# BLOCKED report
Se fallisce: prima lascia Kuma in stato terminale noto e riporta esplicitamente `KUMA_CONTAINER=running|stopped|unknown`, `DB_ROLLBACK=restored|not_needed|failed|unknown`, `MONITOR_STATE=present|absent|unknown` oltre al blocker. Non lasciare uno stato ambiguo come in 751306.

# Non-goal
Niente refactor, cleanup, nuove credenziali, audit generale, MegaVault discovery, altri monitor, reboot reale, full test suite, analisi dati.

# Stop
Dopo PASS esegui UNA sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 286419 --confirm-executed`
Poi stop. Output massimo 8 righe.
