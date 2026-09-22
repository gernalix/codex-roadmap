PROMPT_ID=593872 | project_id=15 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=FAST

# Goal
Esegui una diagnosi forense READ-ONLY dell'incidente grafico avvenuto sul Fedora reale la sera del 2026-09-19, subito prima di un arresto forzato. Mentre l'utente stava scrivendo a ChatGPT in Chrome, il display è diventato quasi completamente nero/scuro; continuando a digitare comparivano solo lettere minuscole in un angolo estremo dello schermo. Il sistema non è stato recuperato dalla GUI ed è stato spento forzatamente.

Devi determinare, con evidenza temporale, cosa è successo e quale componente è il candidato root-cause meglio supportato. NON applicare fix in questo task.

# Fonti autoritative
- Fedora runtime reale.
- `/home/daniele/projects/fedora-system-monitor`, MegaVault project 15.
- DB runtime monitor: `/var/lib/fedora-system-monitor/monitor.sqlite3`.
- `/home/daniele/projects/activity-watch-data`; leggi prima `metadata/buckets.json`, poi SOLO i file del 2026-09-19 pertinenti alla finestra dell'incidente.
- Se il mirror ActivityWatch non contiene ancora gli ultimi minuti pre-crash, usa in sola lettura la sorgente ActivityWatch locale già esistente; non avviare backfill o export massivi.
- journal/coredump del boot precedente e del reboot successivo.

# Metodo minimo obbligatorio
1. Avvia il task con il normale `roadmap_start.py`. Non fare discovery generale dei repo e non modificare codice.
2. Ricostruisci prima l'orario esatto dell'incidente:
   - `journalctl --list-boots` per identificare il boot terminato dall'arresto forzato;
   - ActivityWatch per trovare l'ultimo evento/window-focus prima dell'interruzione e le app/window title realmente attive;
   - usa timestamp UTC/CEST correttamente. L'orario indicativo è circa 23:00 CEST, ma l'evidenza deve fissare la finestra reale.
3. Solo dopo aver fissato il timestamp, interroga una finestra stretta (inizialmente ±5 min; allargala una sola volta solo se necessario) nel boot precedente:
   - kernel/DRM/GPU: `amdgpu`, `drm`, ring timeout, GPU reset, page fault, fence timeout, display/atomic commit;
   - GNOME Shell/Mutter/Wayland/GDM/Xwayland: crash, renderer/compositor, monitor reconfiguration, scaling, session restart;
   - systemd-coredump / `coredumpctl` per `gnome-shell`, `mutter`, `Xwayland`, Chrome e processi grafici correlati;
   - OOM/memory pressure/zram/swap e process kill;
   - Chrome solo se i log indicano GPU process crash/hang o se ActivityWatch mostra che era il foreground rilevante.
   Usa query mirate per unità/processo/kernel; vietati dump dell'intero boot salvo assenza totale di segnali e comunque con output bounded.
4. Correlazione fedora-system-monitor, nella stessa finestra:
   - `fedora-system-monitor timeline/events/metrics --json` con il minimo intervallo utile, oppure query SQLite READ-ONLY equivalenti;
   - verifica memoria, swap/zram, CPU, temperature, power/profile, processi top, errori collector, eventi kernel/servizi già catturati;
   - non cambiare alert/config/runtime.
5. ActivityWatch:
   - identifica il bucket window watcher corretto da `metadata/buckets.json`;
   - leggi solo gli eventi vicini all'incidente;
   - riporta app e titolo finestra negli ultimi minuti, durata, ultimo timestamp valido e l'eventuale buco temporale causato dal freeze/reboot.
6. Se trovi un segnale forte, verifica UNA sola evidenza indipendente che lo corrobori. Non inseguire alternative speculative.
7. Classifica il risultato in una delle famiglie: `GPU/DRM`, `GNOME/Mutter/Wayland`, `Chrome/GPU-process`, `OOM/memory-pressure`, `display-hardware`, `other`, oppure `insufficient-evidence`. Non assegnare una causa senza log coerenti.
8. Nessuna modifica a repo, systemd, configurazione, pacchetti, kernel parameters o DB. Se emerge un fix plausibile, riportalo come `NEXT_ACTION` senza applicarlo.

# Acceptance
PASS se il report contiene:
- `INCIDENT_WINDOW` con timestamp CEST e UTC;
- `FOREGROUND` con le app/window realmente osservate da ActivityWatch;
- `ROOT_CAUSE_CLASS` + `CONFIDENCE=high|medium|low`;
- almeno 2 evidenze concrete e temporalmente correlate se `CONFIDENCE` è high/medium;
- distinzione esplicita fra causa, conseguenze e semplici coincidenze;
- `NEXT_ACTION` minimo e specifico oppure `none`;
- nessuna modifica persistente.

Se i dati non bastano, PASS è comunque ammesso con `ROOT_CAUSE_CLASS=insufficient-evidence` solo dopo aver verificato le fonti sopra e indicando esattamente quale telemetria manca.

# Token/time guard
- niente audit generale;
- niente lettura completa di journal o ActivityWatch;
- niente retry identici senza nuova evidenza;
- riusa timestamp e risultati già verificati;
- interrompi appena root cause + corroborazione soddisfano Acceptance.

# Stop
Finalizza una sola volta con:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 593872 --confirm-executed`

Output massimo 10 righe e riga 1 obbligatoria `PROMPT_ID=593872`.