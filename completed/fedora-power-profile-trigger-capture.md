[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=491736 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Rendi **il watcher root canonico di `fedora-system-monitor`** sufficiente ad attribuire il prossimo switch spontaneo Fedora `Performance → Power Saver`, poi validalo sul runtime reale e rimuovi il watcher utente ad-hoc di `PROMPT_ID=814627`. Non creare un altro sidecar temporaneo e non tentare ancora di cambiare la policy energetica.

# Starting point verificato — niente discovery
- repo: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- backend: `tuned.service` + `tuned-ppd.service`; mapping osservato `power-saver → powersave → platform_profile=low-power`;
- switch spontaneo osservato 2026-09-16 03:36:38, trigger non ancora provato;
- watcher ad-hoc da rimuovere dopo PASS: `/home/daniele/.local/bin/power-profile-watch` + `~/.config/systemd/user/power-profile-watch.service`;
- watcher root canonico: `fedora-system-monitor-events.service` → `src/fedora_system_monitor/capsules/eventing/__init__.py`;
- codice remoto verificato: `_POWER_PROFILE_DBUS_MATCH` oggi cattura **solo** `org.freedesktop.DBus.Properties.Set` sul path `/org/freedesktop/UPower/PowerProfiles`; i test esistenti coprono `Set ActiveProfile` e caller attribution;
- nello stesso file **non** esiste ancora cattura `platform_profile`;
- servono anche `HoldProfile`, `ReleaseProfile`, path `/net/hadess/PowerProfiles` quando presente e cambio reale ACPI `platform_profile`.

Prompt autosufficiente: NON leggere README/roadmap/spiegazioni, MEMORY.md o MegaVault; niente audit repo/sistema.

# Implementazione minima nel repo canonico
1. Una sola fotografia Git + pull ff-only se pulito. Parti direttamente da `eventing/__init__.py`, `tests/test_eventing.py` e dal wiring già noto del watcher in `coordinator.py`; apri altro solo per un blocker concreto.
2. Estendi la cattura D-Bus esistente senza cambiare il formato degli eventi non pertinenti:
   - `Properties.Set ActiveProfile` sui due path supportati;
   - `HoldProfile` e `ReleaseProfile`;
   - per ogni method call registra timestamp, metodo/path, profilo/reason essenziali quando disponibili e caller `sender/PID/UID/process/executable` usando la risoluzione già esistente;
   - niente raw payload/secret o dump D-Bus generale.
3. Aggiungi nel servizio root canonico una cattura a basso rumore del path reale `/sys/firmware/acpi/platform_profile` (o equivalente provato sull'host): persisti **solo il cambio di valore**, con timestamp e stato AC/batteria minimo. Niente polling stretto: usa evento/file-watch se affidabile; altrimenti polling lento nello stesso worker con dedup sul valore.
4. Test host mirati: parser `Set`, `HoldProfile`, `ReleaseProfile`, entrambi i path, caller attribution, dedup/cambio `platform_profile`. Riusa fixture esistenti; niente suite globale.
5. Push del diff una volta solo dopo test host PASS.

# Validazione runtime — una sola sessione
1. Distribuisci i soli moduli modificati col meccanismo minimo del progetto; restart solo `fedora-system-monitor-events.service` se necessario.
2. Verifica servizio root attivo e senza `AccessDenied`/fallback eavesdropping.
3. Esegui **una sola prova controllata reversibile** `performance → balanced → performance` tramite API D-Bus canonica, solo se necessaria; la cattura deve mostrare metodo/path e caller. Non creare hold persistenti.
4. Verifica una volta che il canale `platform_profile` abbia baseline valida e registri solo cambi reali; non forzare `low-power` solo per testarlo se la prova D-Bus già dimostra la pipeline.
5. Profilo finale obbligatorio `performance`.
6. Solo dopo PASS disabilita/rimuovi il vecchio watcher utente e lo script; conserva il log storico ma non lasciare watcher duplicati.
7. NON aspettare il prossimo switch spontaneo. Il PASS è “strumentazione canonica pronta”. Il prossimo evento reale dovrà essere diagnosticabile dal DB/event log senza un nuovo setup.

# Efficienza
- niente `dbus-monitor` generico o `journalctl -b` ampio; output solo del servizio/eventi pertinenti;
- usa i test esistenti come entrypoint, niente ricerca repo-wide;
- raggruppa controlli indipendenti; niente polling manuale/sleep lunghi;
- un test PASS non si ripete; un failure autorizza solo il leaf fix relativo.

# Acceptance
PASS se il watcher canonico versionato copre Set/Hold/Release + entrambi i path + `platform_profile`, la prova controllata attribuisce correttamente il caller, il servizio root è sano, il profilo finale è `performance` e il watcher ad-hoc è rimosso.

# Non-goal
Nessun cambio policy energetica permanente, disabilitazione di protezioni termiche/firmware, update Fedora/TuneD/GNOME, audit generale o attesa del prossimo switch spontaneo.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 491736 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 491736`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, DBUS_COVERAGE, PLATFORM_PROFILE, RUNTIME, OLD_WATCHER, FINAL_PROFILE/BLOCKER.