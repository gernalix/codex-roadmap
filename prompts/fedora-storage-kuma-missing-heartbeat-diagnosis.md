[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=638914 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Diagnostica e correggi SOLO il monitor Uptime Kuma Push **“Fedora Storage” (#40)**, attualmente rosso/**Spento** con `No heartbeat in the time window`. Ripristina il flusso heartbeat senza riaprire o rieseguire il già completato `PROMPT_ID=467281` su Fedora Software #43 e senza mascherare eventuali alert storage reali.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`;
- MegaVault: progetto `15`, già esistente; non crearne duplicati;
- DB runtime canonico: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- screenshot utente del **2026-09-16 06:00** mostra `kuma.danielegalati.com/dashboard/40`, monitor **Fedora Storage #40**, descrizione `Fedora storage health: free space, inodes, read-only mounts, I/O errors and SMART.`;
- stato Kuma: **Spento**, check ogni **480 s (8 min)**, cronologia verde→arancio→rosso, toast **`[Fedora Storage] [DOWN] No heartbeat in the time window`**;
- il problema Fedora Host #39 ha un task separato; non assorbirlo;
- `PROMPT_ID=467281` è già stato eseguito/completato: non ripetere la diagnosi Software #43. Se il suo report/diff locale contiene evidenza direttamente riusabile su scheduler/coordinator/Kuma, leggila una sola volta e riusala invece di rifare discovery.

# Esecuzione minima
1. Fai una sola fotografia Git del repo. Usa MegaVault FAST solo per riferimenti pertinenti già esistenti; niente audit generale.
2. **Prima del codice**, ricava per #40 dal runtime/Kuma: ultimo heartbeat ricevuto, sua età, ultimo status/message, intervallo/grace/timeout attesi e orario in cui è iniziata la finestra senza heartbeat.
3. Mappa #40 al solo collector/runner/unit/timer che produce il Push Storage e controlla una sola volta: ultimo run, prossimo run, exit status, durata, ultimo payload Push tentato/inviato ed eventuale eccezione. Limita `systemctl`/`journalctl` alle unit pertinenti e alla finestra dell'incidente.
4. Se il run 467281 ha già modificato scheduler/coordinator/config condivisi, confronta solo quel diff/report con l'incidente #40; non rieseguire i suoi test né riaprire #43.
5. Leggi soltanto il ramo di codice/config direttamente responsabile della failure concreta. Starting point plausibili solo se pertinenti: `src/fedora_system_monitor/capsules/runtime/coordinator.py`, `src/fedora_system_monitor/capsules/collectors/periodic.py`, `src/fedora_system_monitor/capsules/collectors/system.py`, config Kuma e unit/timer systemd.
6. Determina la root cause con evidenza concreta, ad esempio: timer non attivo, schedule/grace incoerenti, job bloccato/fallito, eccezione che salta il Push, lock/concorrenza, suspend/resume, timeout/network o mapping/config Push errato.
7. Applica SOLO il fix minimo. Se il difetto è server-side Kuma/VM, modificalo solo dopo aver escluso il runner locale. Non stampare URL/token/segreti.
8. Non liberare spazio disco e non alterare threshold SMART/storage per rendere il monitor verde. Se il nuovo heartbeat espone un alert storage reale, deve restare visibile.

# Verifica
- test mirati solo sui file modificati;
- una sola nuova run Storage dopo il fix;
- verifica che #40 riceva un nuovo Push entro la finestra prevista;
- PASS se `No heartbeat in the time window` scompare e il monitor riflette correttamente lo stato reale: può restare DOWN solo per un alert storage reale distinto dall'assenza di heartbeat;
- verifica soltanto che #39 e #43 non siano stati alterati.

# Non-goal
Niente nuova diagnosi Software #43 / `PROMPT_ID=467281`, niente Fedora Host #39, audit generale Fedora, update/install/remove pacchetti, cleanup/refactor, tuning preventivo, cancellazione manuale di alert/DB o modifiche cosmetiche a Kuma.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 638914 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 638914`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, ROOT_CAUSE, FIX, KUMA_NOW, TEST, CHANGES/BLOCKER.