[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=812604 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Chiudi in **un solo pass locale** il recovery/correctness dei monitor Uptime Kuma Fedora **Host #39** e **Storage #40**, condividendo una sola fotografia runtime, un solo checkout e un solo deploy del repo `fedora-system-monitor`. Nello stesso diff chiudi l'hardening residuo del coordinator emerso da `PROMPT_ID=467281`.

Il criterio non è “rendere tutto verde”: un monitor può restare DOWN se il nuovo heartbeat espone una condizione reale. PASS significa monitoraggio corretto, root cause determinata e nessun falso DOWN/no-heartbeat introdotto dal coordinator.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`; DB runtime: `/var/lib/fedora-system-monitor/monitor.sqlite3`; MegaVault project `15` già esistente;
- `origin/main` contiene `97a2a732de44e86d17f46e650dff6dfad1d493cf` o successivo: Software #43 aveva un worker `daily` persistito `partial` ma il parent lo riclassificava falsamente `error`; #43 è poi tornato UP;
- il fallback attuale `_latest_persisted_scope_result()` può ancora correlare il worker tramite finestra temporale: va reso deterministico rispetto al nuovo `collector_runs.id` creato dopo lo spawn boundary;
- **Host #39**: Push continua ad arrivare ma è DOWN con `system: collectors complete; active alerts=1`; quindi non investigare genericamente connettività/Kuma: identifica l'alert attivo concreto;
- **Storage #40**: screenshot 2026-09-16 06:00 mostra DOWN con `No heartbeat in the time window`, intervallo Kuma 480 s; qui va ricostruita la catena runner → Push → Kuma;
- **Software #43 è chiuso**: usalo solo come sentinella finale di non-regressione, senza nuova diagnosi.

Questo prompt è autosufficiente: NON leggere MEMORY.md, README/roadmap/spiegazioni, MegaVault o fare inventory generale salvo blocker reale.

# Esecuzione minima
1. Una sola fotografia Git + `git pull --ff-only` se pulito. Dirty non pertinente => BLOCKED; niente stash/reset.
2. Prima del codice, acquisisci **un'unica fotografia runtime** raggruppando le letture indipendenti:
   - DB locale: alert attivi, ultimi run pertinenti a system/storage e dati necessari a #39/#40;
   - systemd: sole unit/timer che producono Host/Storage, ultimo/prossimo run ed exit status;
   - Kuma remoto: una sola query per configurazione + heartbeat recenti di #39/#40 e una sola riga sentinella #43.
   Per il DB locale usa helper/reporting del progetto oppure SQLite `mode=ro&immutable=1`; non usare `sqlite3 -readonly` sul WAL. Per Kuma usa direttamente `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh` + `sudo sqlite3 /opt/uptime-kuma/data/kuma.db`. Se una colonna non è certa: **una** `PRAGMA table_info`, poi la query corretta; niente column guessing/retry equivalenti.
3. **Hardening coordinator**, solo se non già presente in HEAD:
   - prima dello spawn salva l'ultimo `collector_runs.id` dello scope;
   - il fallback può recuperare solo un nuovo `ok/partial` dello stesso scope con `id > boundary_id`; niente matching identitario basato solo su ±secondi;
   - se nessun nuovo run valido esiste, conserva diagnostica minima del subprocess (`returncode`, `timed_out`, stderr redatto/troncato) e tratta il failure come reale;
   - aggiungi solo 3 regressioni: nuovo `partial` recuperato; vecchia riga recente NON riusata; nessun nuovo run => failure reale.
4. **Host #39**: dal DB identifica l'unico alert che genera `active alerts=1`. Leggi solo il ramo di codice/config relativo e fai un solo probe della sorgente reale. Se è stale/bug, fix minimo; se è una condizione reale, NON silenziarla né cancellarla manualmente. Una condizione reale correttamente diagnosticata può restare DOWN ed è comunque compatibile con PASS del task.
5. **Storage #40**: dalla fotografia runtime determina dove si interrompe il heartbeat (schedule/run/coordinator/push/Kuma). Leggi solo il boundary responsabile e applica il fix minimo. Non liberare spazio, cambiare threshold SMART/storage o modificare Kuma per mascherare uno stato reale.
6. Applica in batch le sole modifiche necessarie a coordinator/Host/Storage. Niente refactor o cleanup collaterale.
7. Esegui una sola volta i leaf test impattati, sempre con `PYTHONPATH=src`; niente tentativo preliminare noto destinato a fallire, niente suite globale. Failure => fix del leaf concreto + una sola riconferma.
8. Distribuisci **una sola volta** i moduli runtime modificati con il meccanismo minimo già usato dal progetto; evita `install.sh` se introdurrebbe backfill/restart fuori scope. Compile/import una volta.
9. Verifica con al massimo una nuova raccolta pertinente per Host e una per Storage. Poi fai **un unico readback Kuma finale** per #39/#40 + sentinella #43. Nessuna esplorazione post-PASS.

# Efficienza vincolante
- niente `rg` ricorsivi/dump repo generali: usa i path già noti e limita output/log alla finestra dell'incidente;
- niente probe senza privilegi quando l'helper canonico privilegiato è già noto;
- raggruppa query/comandi indipendenti nella stessa tornata tool; evita catene di micro-round-trip;
- dopo un errore di schema/permesso/import, cambia approccio usando la nuova evidenza: vietati retry quasi equivalenti;
- non ripetere un test PASS e non verificare due volte lo stesso stato Kuma.

# Acceptance
PASS quando tutte queste condizioni sono vere:
- coordinator non può riusare un vecchio `collector_run` e conserva diagnostica del vero subprocess failure;
- #39 riflette il dato reale: UP se l'alert era falso/rientrato, oppure DOWN con alert reale identificato e verificato;
- #40 non è più DOWN per `No heartbeat in the time window`; può restare DOWN solo per una condizione storage reale riportata da un nuovo Push;
- #43 resta coerente e non è stato modificato;
- test mirati e push repo PASS.

# Non-goal
Niente nuova diagnosi Software #43, audit generale Fedora/MegaVault, aggiornamenti di sistema/pacchetti, cleanup/refactor, tuning preventivo, cancellazione manuale di alert/DB, liberazione spazio, modifiche cosmetiche Kuma o interventi hardware distruttivi.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 812604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 812604`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, COORDINATOR, HOST_CAUSE, STORAGE_CAUSE, FIX, KUMA_NOW, TEST/BLOCKER.