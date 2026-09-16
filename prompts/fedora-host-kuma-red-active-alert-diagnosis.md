[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=812604 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Diagnostica e correggi SOLO il monitor Uptime Kuma Push **“Fedora Host” (#39)**, attualmente rosso/**Spento**. Identifica quale alert attivo produce `system: collectors complete; active alerts=1`, determina se è un problema reale del Fedora host oppure un falso/stale positive del monitor, e applica il minimo fix sicuro. Non forzare mai lo stato verde cancellando/sopprimendo un alert reale.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`;
- MegaVault: progetto `15`, già esistente; non crearne duplicati;
- DB runtime canonico già noto: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- screenshot utente del **2026-09-16 05:54** mostra `kuma.danielegalati.com/dashboard/39`, monitor **Fedora Host #39**, descrizione `Fedora host health: CPU, memory, swap, temperatures and critical kernel events.`;
- stato corrente Kuma: **Spento**, check ogni **180 s**, ping corrente circa **171 ms**;
- toast visibile: **`[Fedora Host] [DOWN] system: collectors complete; active alerts=1`**;
- cronologia visibile: heartbeat prima verdi, poi alcuni arancioni, quindi rossi: il Push continua quindi ad arrivare; la priorità è scoprire l'alert che lo rende DOWN, non investigare genericamente connettività/Kuma;
- boundary remoto già noto: `src/fedora_system_monitor/capsules/collectors/system.py`, `src/fedora_system_monitor/capsules/collectors/periodic.py`, `src/fedora_system_monitor/capsules/alerting/__init__.py`, `src/fedora_system_monitor/capsules/runtime/coordinator.py`; parti da questi solo dopo aver identificato l'alert runtime concreto.

# Esecuzione minima
1. Fai una sola fotografia Git del repo. Usa MegaVault FAST solo per riferimenti pertinenti già esistenti; niente audit generale del progetto/sistema.
2. **Prima di leggere codice**, interroga in sola lettura il DB/runtime per ottenere l'unico `active alert` che determina il DOWN di `system`: nome/tipo, severity, first/last seen, valore/threshold, source/device, fingerprint/id, dettagli ed eventuale evento/metric originario. Usa helper/CLI esistenti se già disponibili; altrimenti fai il minimo query/schema inspection SQLite necessario. Non modificare il DB a mano.
3. Controlla una sola finestra temporale recente dei log dell'unit/timer che esegue il collector `system` per correlare l'alert con il run che ha inviato il Push DOWN. Niente `journalctl` generale.
4. In base **all'alert identificato**, leggi solo il ramo di codice/config direttamente responsabile e stabilisci quale dei casi vale:
   - host condition reale ancora presente;
   - condizione transitoria già rientrata ma alert non chiuso;
   - threshold/hysteresis/clear logic errati;
   - collector/parsing/source data errati;
   - stato Kuma derivato da alert non pertinente/stale.
5. Verifica il dato sorgente reale con **un solo comando mirato** coerente con l'alert (es. temperatura, memoria/swap, load/CPU, kernel event), evitando raccolte diagnostiche generali o comandi equivalenti ripetuti.
6. Applica il fix minimo nel boundary corretto. Se è un bug di codice/config, modifica solo i file necessari e aggiungi/aggiorna il test mirato che riproduce la causa. Se è una condizione host reale ma risolvibile in modo sicuro, non distruttivo e direttamente causale, correggila e documenta il cambiamento. Non riavviare/reinstallare/aggiornare componenti non pertinenti.
7. Se l'alert è reale e richiede hardware, perdita dati, reboot rischioso, modifica distruttiva o decisione dell'utente, **non** silenziarlo: fermati `BLOCKED` con causa, evidenza e singola azione consigliata; il monitor deve restare rosso.

# Verifica
- test mirati solo sui file modificati; non lanciare suite complete salvo failure che dimostri necessità;
- esegui una sola nuova raccolta `system` usando il percorso runtime canonico;
- verifica nel DB che l'alert causale sia chiuso **solo se** la condizione è realmente rientrata;
- verifica che #39 riceva un nuovo Push coerente: **UP** con `active alerts=0` se il problema è risolto, oppure **DOWN** se una condizione reale persiste;
- verifica soltanto che gli altri monitor Fedora non siano stati alterati.

# Non-goal
Niente audit generale Fedora, analisi degli altri monitor (#43 incluso), aggiornamenti di sistema/pacchetti, cleanup/refactor, tuning preventivo di threshold non coinvolti, cancellazione manuale di alert/DB, o modifiche cosmetiche a Kuma.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 812604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 812604`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, ALERT, ROOT_CAUSE, FIX, KUMA_NOW, TEST/BLOCKER.