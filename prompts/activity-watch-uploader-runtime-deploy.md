PROMPT_ID=643817 | project_id=15 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO il deploy runtime già implementato di ActivityWatch uploader: Fedora → `gernalix/activity-watch-data` → Uptime Kuma. Nessun redesign.

# Starting point autoritativo
- `project_id=15` è solo il routing host/runtime Fedora per questo task: i due repo target sono espliciti qui sotto. NON interrogare MegaVault per riscoprirli né fare inventory generale.
- codice: `gernalix/activity-watch-uploader` main, baseline minima `883e7d657f9c58d8ddbefa9b20e1b7a5f78204e8`;
- dati privati: `gernalix/activity-watch-data` main, baseline minima `fb656dde8386465497f51218262b43f17bc9bf27`;
- path canonici: `~/projects/activity-watch-uploader` e `~/projects/activity-watch-data`;
- precedente ciclo 643817: BLOCKED prima di test/deploy/Kuma. Stato osservato e NON da riscoprire: il path codice conteneva soltanto `activity-watch-uploader/activity-watch-uploader/.git`, origin corretto, branch main, HEAD non materializzato; il path dati mancava;
- il nuovo `scripts/bootstrap_checkouts.py` ripara fail-closed ESCLUSIVAMENTE questo layout annidato, clona il repo dati, valida origin/branch/baseline e fast-forwarda checkout puliti. L'esatta riparazione è autorizzata da questo prompt se e solo se i suoi guard passano; per qualunque altra forma filesystem => BLOCKED;
- output dati: `metadata/buckets.json` + `buckets/<bucket>/YYYY/MM/YYYY-MM-DD.jsonl`; un evento completo/riga; nessun raw ActivityWatch nel repo codice;
- ActivityWatch: `http://127.0.0.1:5600`;
- unità: `activity-watch-uploader.service/.timer`; timer 15 min + `Persistent=true` + `OnBootSec=2min`; service `Restart=on-failure`, `RestartSec=2min`, `TimeoutStartSec=30min`, `KillMode=control-group`;
- Kuma Oracle: compose `/opt/uptime-kuma/docker-compose.yml`, container `uptime-kuma`, data `/opt/uptime-kuma/data`; monitor desiderato `ActivityWatch Git Uploader (Fedora)`, type=push, interval=1200, retry=300, maxRetries=2, upside_down=0;
- VM accesso SOLO via `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh`;
- non stampare/versionare token o credenziali.

# Esecuzione minima

## 1. Ripara/bootstrap checkout: UNA shell call
Non fare `ls`, tree, schema MegaVault o probe equivalenti prima. Usa questa logica bounded:
- se `~/projects/activity-watch-uploader/scripts/bootstrap_checkouts.py` esiste, usalo direttamente;
- altrimenti, solo se esiste l'esatto nested `~/projects/activity-watch-uploader/activity-watch-uploader/.git`: verifica origin=`gernalix/activity-watch-uploader`, poi `timeout 60s git fetch origin main` + `git checkout -B main origin/main` dentro il nested e usa da lì l'helper;
- altrimenti, solo se il path codice non esiste, clona `gernalix/activity-watch-uploader` nel path canonico e usa l'helper;
- qualunque altro stato => BLOCKED, senza cleanup manuale.
Poi esegui UNA volta:
`python3 <helper> --repair-known-nested --code-root ~/projects/activity-watch-uploader --data-root ~/projects/activity-watch-data --code-baseline 883e7d657f9c58d8ddbefa9b20e1b7a5f78204e8 --data-baseline fb656dde8386465497f51218262b43f17bc9bf27`
Il JSON `status=ok` dell'helper è il gate checkout; non ripetere fetch/status/remote/head separati.

## 2. Fedora host gate: UNA shell call
Nel repo codice, fail-fast e senza dump raw:
- `python3 -m unittest discover -s tests -v`;
- `python3 -m py_compile activity_watch_uploader.py scripts/bootstrap_checkouts.py`;
- `systemd-analyze --user verify systemd/activity-watch-uploader.service systemd/activity-watch-uploader.timer`;
- probe bounded `/api/0/buckets` riportando solo HTTP + numero bucket;
- verifica Git non-interattivo del repo dati con un solo `fetch origin main`; il primo push reale resta al run end-to-end.
Failure => BLOCKED e stop prima di Kuma.

## 3. Kuma: un solo preflight/write/readiness transactionale
Sincronizza `vm_oracle/main` con `--ff-only`, poi usa solo `scripts/oracle_ssh.sh`.
In un unico passaggio remoto:
- identifica DB SQLite effettivo sotto `/opt/uptime-kuma/data`, fai backup consistente owner-only;
- leggi una sola volta lo schema minimo di `monitor`, eventuale `monitor_notification` e heartbeat; non indovinare colonne;
- upsert per nome esatto + type=push: 0 crea, 1 aggiorna, >1 BLOCKED;
- genera token casuale solo se assente; imposta 1200/300/2/upside_down=0; se non ambiguo copia binding notifiche dal monitor Fedora #39;
- write in transazione con Kuma fermato solo nella finestra minima, poi restart del solo stack/container e `integrity_check` + readiness bounded;
- su failure ripristina backup, riavvia Kuma, BLOCKED.

## 4. Secret + systemd Fedora: UNA shell call
Trasferisci il token senza stamparlo tramite file/stdin owner-only. `~/.config/activity-watch-uploader/env` deve essere 0600 e contenere almeno:
- `AW_BASE_URL=http://127.0.0.1:5600`
- `AW_DATA_REPO_PATH=${HOME}/projects/activity-watch-data`
- `KUMA_PUSH_URL=<secret>`
Poi:
- abilita/verifica `loginctl enable-linger daniele`;
- `bash scripts/install-user-service.sh`;
- verifica in un solo readback timer enabled+active e i boundary systemd autoritativi sopra. Niente daemon loop.

## 5. Due run end-to-end
Avvia due volte, serialmente, SOLO `systemctl --user start activity-watch-uploader.service`.
Per ciascun run raccogli solo `run_id`, mode, changed_files, exit.
Dopo il primo:
- nel repo dati verifica metadata + almeno un file per ogni bucket corrente e che il full backfill includa anche i bucket storici/unknown presenti nell'export;
- verifica bounded: JSONL UTF-8 valido, una riga=un evento, nessun export monolitico, nessun raw nel repo codice;
- verifica push arrivato a `gernalix/activity-watch-data/main`;
- nel DB Kuma ultimo heartbeat=up e contiene ESATTAMENTE lo stesso `run_id`.
Dopo il secondo: nuovo `run_id`, exit 0, Git coerente, heartbeat aggiornato allo stesso nuovo `run_id`.
Non attendere 15 minuti.

# Acceptance
PASS solo se checkout helper=ok, host gate PASS, Kuma backup/write/integrity/readiness PASS, secret 0600 non esposto, lingering+timer attivi, tutti i dati ActivityWatch nel repo dati, due run reali correlati Git+Kuma PASS.

# Non-goal
Niente refactor/cleanup, nuove feature, nuove credenziali, audit generale, altri monitor Kuma, reboot reale, analisi dei dati, modifiche ActivityWatch/watchers, inventory MegaVault.

# Stop
Al primo blocker non coperto dai guard fermati; niente retry equivalente. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 643817 --confirm-executed`
Poi stop. Output massimo 7 righe: `RESULT`, `CHECKOUTS`, `FEDORA`, `ACTIVITYWATCH`, `GIT`, `KUMA`, `BLOCKER`.
