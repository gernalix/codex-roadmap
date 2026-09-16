[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=638914 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Diagnostica e correggi SOLO il monitor Uptime Kuma Push **“Fedora Storage” (#40)**, attualmente rosso/**Spento** con `No heartbeat in the time window`. Ripristina il flusso heartbeat senza riaprire o rieseguire il già completato `PROMPT_ID=467281` su Fedora Software #43 e senza mascherare eventuali alert storage reali.

Nello stesso pass, chiudi un unico hardening residuo emerso da `467281` nel coordinator condiviso: il fallback che recupera un risultato `ok/partial` già persistito dal worker deve correlare **quel nuovo run**, non una riga trovata soltanto tramite una finestra temporale. Questo hardening va validato sul runtime Fedora reale e quindi resta in questo task locale; non è una nuova diagnosi Software.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`;
- MegaVault: progetto `15`, già esistente; non creare duplicati e non fare discovery dello schema MegaVault;
- DB runtime canonico: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- `origin/main` contiene il fix Software `97a2a732de44e86d17f46e650dff6dfad1d493cf` o successivo: il worker `daily` aveva persistito `partial`, mentre il parent lo riclassificava falsamente `error`; #43 è poi tornato UP. Non ripetere quella diagnosi;
- nel fix attuale `_run_isolated_scope()` recupera il risultato persistito tramite `_latest_persisted_scope_result(...)`; verifica solo quel boundary. Se usa ancora una tolleranza temporale, sostituiscila con correlazione deterministica rispetto all'ultimo `collector_runs.id` esistente **prima** dello spawn: il fallback può accettare solo un nuovo run dello stesso scope creato dopo quel boundary;
- quando il subprocess è realmente non-OK, conserva diagnostica strutturata minima (`returncode`, `timed_out`, stderr redatto/troncato) senza trasformarla automaticamente in alert se il worker ha comunque persistito un risultato valido;
- screenshot utente del **2026-09-16 06:00** mostra `kuma.danielegalati.com/dashboard/40`, monitor **Fedora Storage #40**, descrizione `Fedora storage health: free space, inodes, read-only mounts, I/O errors and SMART.`;
- stato Kuma: **Spento**, check ogni **480 s (8 min)**, cronologia verde→arancio→rosso, toast **`[Fedora Storage] [DOWN] No heartbeat in the time window`**;
- il problema Fedora Host #39 ha un task separato; non assorbirlo.

# Esecuzione minima
1. Una sola fotografia Git e `git pull --ff-only` se pulito. Il prompt è autosufficiente: **non leggere MEMORY.md, README/roadmap/spiegazioni né fare query esplorative MegaVault**.
2. Hardening coordinator, scope chiuso a `src/fedora_system_monitor/capsules/runtime/coordinator.py` e test diretto in `tests/test_app.py`:
   - cattura il boundary ID prima di lanciare `collect-worker`;
   - recupera solo un `ok/partial` dello stesso scope con ID successivo al boundary; niente matching identitario basato solo su ±secondi;
   - su vero failure conserva return code/timeout/stderr tramite redazione esistente;
   - regressioni minime: nuovo `partial` viene recuperato; una vecchia riga recente non viene riusata; nessun nuovo run => resta failure reale.
   Non cambiare heartbeat policy, soglie o Kuma.
3. Esegui **una sola volta** i test mirati appena sopra con `PYTHONPATH=src`; non fare prima un tentativo noto destinato a fallire senza `PYTHONPATH`, non ripetere un PASS e non lanciare suite globale salvo failure concreta che lo richieda.
4. Distribuisci sul runtime soltanto il file/modulo modificato con il meccanismo minimo già usato dal progetto; evita `install.sh` se introdurrebbe backfill/restart fuori scope. Verifica import/compile una volta.
5. **Poi Storage #40:** ricava in un unico batch dal runtime/Kuma ultimo heartbeat, età, status/message, intervallo/grace/timeout e inizio della finestra senza heartbeat. Per il DB locale usa la CLI/reporting del progetto oppure URI SQLite `mode=ro&immutable=1`; non usare `sqlite3 -readonly` sul WAL e non ripetere lo stesso errore read-only.
6. Per Kuma remoto usa direttamente l'helper canonico `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh` con `sudo sqlite3 /opt/uptime-kuma/data/kuma.db` in sola lettura. Sono già noti monitor `#40/#43`: niente Docker probe preliminare o tentativo non-sudo. Se una colonna non è certa, una sola `PRAGMA table_info` e poi una sola query corretta; niente tentativi a indovinare nomi di colonna.
7. Mappa #40 al solo collector/runner/unit/timer che produce il Push Storage e controlla una sola volta ultimo/prossimo run, exit status, durata, ultimo payload Push ed eccezione. Limita `systemctl`/`journalctl` all'unità pertinente e alla finestra dell'incidente; niente `rg`/dump ampi che producano migliaia di token.
8. Se il diff `97a2a73` è direttamente pertinente, riusalo come evidenza; non riaprire #43, non rieseguire i suoi test e non interrogare altri monitor salvo una singola sentinella finale di non-regressione.
9. Determina la root cause #40 e applica SOLO il fix minimo. Se è server-side Kuma/VM, modifica solo dopo aver escluso il runner locale. Non stampare URL/token/segreti.
10. Non liberare spazio disco e non alterare threshold SMART/storage per rendere il monitor verde. Se il nuovo heartbeat espone un alert storage reale, deve restare visibile.

# Verifica
- hardening coordinator: regressioni mirate PASS e nessun falso recupero di una riga preesistente;
- una sola nuova run Storage dopo il fix;
- verifica che #40 riceva un nuovo Push entro la finestra prevista;
- PASS se `No heartbeat in the time window` scompare e il monitor riflette correttamente lo stato reale: può restare DOWN solo per un alert storage reale distinto dall'assenza di heartbeat;
- una sola sentinella finale: #39/#43 non alterati. Nessuna esplorazione dopo PASS.

# Non-goal
Niente nuova diagnosi Software #43 / `PROMPT_ID=467281`, niente Fedora Host #39, audit generale Fedora/MegaVault, update/install/remove pacchetti, cleanup/refactor, tuning preventivo, cancellazione manuale di alert/DB o modifiche cosmetiche a Kuma.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 638914 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 638914`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, ROOT_CAUSE, FIX, KUMA_NOW, TEST, CHANGES/BLOCKER.