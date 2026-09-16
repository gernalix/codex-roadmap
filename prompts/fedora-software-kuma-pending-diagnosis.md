[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=467281 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Diagnostica e correggi in UN SOLO PASS i problemi di heartbeat Uptime Kuma dei monitor Push **“Fedora Storage” (#40)** e **“Fedora Software” (#43)**. Determina se condividono la stessa root cause oppure hanno cause indipendenti e applica solo il minimo fix necessario. Non forzare mai uno stato verde: dopo il ripristino degli heartbeat, eventuali alert reali devono restare visibili.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`;
- MegaVault: progetto `15`, già esistente; non crearne duplicati;
- DB runtime canonico: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- **Storage #40**: screenshot utente del 2026-09-16 06:00 mostra `kuma.danielegalati.com/dashboard/40`, stato **Spento**, check ogni **480 s (8 min)**, cronologia verde→arancio→rosso e toast **`[Fedora Storage] [DOWN] No heartbeat in the time window`**; descrizione `Fedora storage health: free space, inodes, read-only mounts, I/O errors and SMART.`;
- **Software #43**: screenshot utente del 2026-09-16 03:36 mostrava stato **In attesa**, ping `N/D`, intervallo Kuma **5400 s (1 h 30 min)**; ultimo heartbeat verde visibile `2026-09-15 13:00:26`, messaggio `software: collectors complete; active alerts=0`;
- altri monitor Fedora continuano a produrre heartbeat; il problema separato di **Fedora Host #39** (`system: collectors complete; active alerts=1`) ha già un task dedicato: non assorbirlo qui;
- nel repo esistono già collector/storage-software, coordinator, config Kuma e unit/timer systemd: parti dai mapping runtime concreti, non da un audit generale.

# Esecuzione minima
1. Fai una sola fotografia Git del repo. Usa MegaVault FAST solo per riferimenti pertinenti già esistenti. Niente audit generale del repository o del sistema.
2. **Prima del codice**, leggi dal runtime/Kuma lo stato attuale di #40 e #43 e per ciascuno ricava: ultimo heartbeat, età, status/message, intervallo/grace/timeout attesi. Se uno si è già ripreso spontaneamente, conserva la finestra dell'incidente e continua solo quanto basta a determinarne la causa/recurrence risk.
3. Mappa #40 e #43 ai rispettivi collector/runner/unit/timer/path e confronta in una sola tabella mentale:
   - cadenza locale prevista;
   - ultimo run e prossimo run;
   - exit status;
   - ultimo payload Push tentato/inviato;
   - eventuale eccezione che impedisce il Push.
   Limita `systemctl`/`journalctl` alle sole unit rilevanti e alla finestra temporale dell'incidente.
4. Stabilisci subito se la root cause è **comune** (scheduler/coordinator/push/config/network/suspend-resume) o **specifica** di Storage/Software. Confronta con UN solo monitor Fedora funzionante soltanto se necessario per discriminare problema comune vs specifico.
5. Leggi solo il ramo di codice/config direttamente responsabile della failure concreta. Starting points probabili, da usare solo se pertinenti: `src/fedora_system_monitor/capsules/runtime/coordinator.py`, `src/fedora_system_monitor/capsules/collectors/periodic.py`, `src/fedora_system_monitor/capsules/collectors/system.py`, `src/fedora_system_monitor/capsules/collectors/software.py`, config Kuma e unit/timer systemd.
6. Verifica le cause plausibili soltanto se supportate da evidenza: timer/path non attivo, schedule locale incoerente con Kuma, job bloccato/fallito, eccezione che salta il Push, lock/concorrenza, resume/suspend non gestito, URL/config/token obsoleto, timeout/network oppure logica heartbeat/status errata.
7. Applica SOLO il fix minimo nel boundary corretto. Se una sola correzione copre entrambi, non duplicarla. Se serve modificare Kuma/VM, fallo solo dopo evidenza che il difetto è nella configurazione server-side; non stampare Push URL/token/segreti.
8. Non fare update/install/remove di pacchetti e non liberare spazio disco per rendere Storage verde. Se, una volta ripristinato l'heartbeat, #40 resta DOWN per un alert storage reale (per esempio spazio libero), quello è comportamento corretto e va riportato senza silenziarlo.

# Verifica
- test mirati solo sui file modificati;
- esegui **al massimo una** nuova run Storage e **una** Software dopo il fix, riusando lo stesso bootstrap/runtime;
- verifica che #40 e #43 ricevano nuovi Push con status/message coerenti;
- verifica che i prossimi run siano schedulati entro le rispettive finestre Kuma;
- PASS se il problema di heartbeat è risolto: #40/#43 possono restare non-UP solo se il nuovo Push espone una condizione reale distinta dall'assenza di heartbeat;
- verifica soltanto che gli altri monitor Fedora non siano stati alterati.

# Non-goal
Niente audit generale Fedora, task Fedora Host #39, aggiornamenti di sistema/pacchetti, cleanup/refactor, tuning preventivo degli altri monitor, cancellazione manuale di alert/DB, liberazione spazio disco, o modifiche cosmetiche a Kuma.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 467281 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 467281`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, STORAGE_CAUSE, SOFTWARE_CAUSE, FIX, KUMA_STORAGE, KUMA_SOFTWARE, TEST/BLOCKER.