PROMPT_ID=463817 | project_id=15 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT
WORKDIR=/home/daniele/projects/fedora-system-monitor

# Goal
Chiudi end-to-end l'hardening dei servizi systemd personalizzati Fedora e il monitoraggio Uptime Kuma per servizio. Integra solo le modifiche già preparate, riconcilia il runtime reale, correggi esclusivamente i gap necessari, modifica in modo transazionale il DB Kuma e termina solo quando l'inventario live è coerente.

# Evidenza già verificata da ChatGPT
- MegaVault contiene già la tabella canonica `services`; non crearne una duplicata.
- PR già preparate:
  - MegaVault #7: policy systemd + template canonico.
  - fedora-system-monitor #9: `Restart=always` sui daemon FSM + heartbeat Kuma individuale per servizio + `kuma-configure --service-unit`.
  - telegram_insert_bot #2: hardening daemon.
  - adb-device-keeper #1: hardening daemon.
  - chrome-codex-switcher #21: hardening daemon.
  - workflowy-importer #20: elimina dipendenza .venv da tutte le unità e rende il bridge always-on.
- I servizi timer/event/oneshot NON devono ricevere `Restart=always` meccanicamente.
- MegaVault vieta venv; Python deve usare l'ambiente globale.
- Il monitor aggregato `Fedora Services` resta, ma ogni daemon custom always-on deve avere anche un Push Monitor Kuma indipendente. Per timer/oneshot, se viene creato un monitor individuale deve rappresentare esito/freschezza della run, non `ActiveState=active` continuo.

# Esecuzione vincolata
1. Parti dai file/unità già indicati e dall'inventario live; vietata esplorazione generale dei repo.
2. Integra le PR sopra solo tramite il meccanismo single-writer/integratore canonico di ciascun repo. Non editare direttamente i branch canonici. Se una PR ha CI/failure reale, correggi sul suo branch e riesegui solo i test pertinenti.
3. Sul Fedora reale costruisci un inventario unico dei servizi custom installati:
   - system unit da /etc/systemd/system e /usr/local/lib/systemd/system;
   - user unit da ~/.config/systemd/user e ~/.local/share/systemd/user;
   - unit custom già note a fedora-system-monitor;
   - righe MegaVault `services`.
   Deduplica per scope+unit. Non includere servizi stock Fedora solo perché esistono.
4. Classifica ogni unit come: daemon always-on, oneshot+timer, event-driven, lifecycle/RemainAfterExit oppure optional-disabled.
5. Per ogni daemon always-on:
   - source template e unit installata devono avere `Restart=always`, `RestartSec` bounded, start-rate limit ragionevole e target corretto;
   - deve essere enabled dove previsto e active;
   - user service: linger SOLO se deve vivere senza login; i servizi GNOME/Chrome restano session-scoped;
   - elimina eventuali autostart concorrenti dello stesso runtime.
   Se trovi un daemon custom non coperto dalle PR, applica il minimo fix nel repo proprietario tramite single-writer; se il repo proprietario non è identificabile, correggi in modo tracciabile l'unit installata e registra source_ref/note in MegaVault senza inventare ownership.
6. Per oneshot/timer/event/lifecycle non applicare `Restart=always`. Verifica trigger/timer, idempotenza e `Persistent=true` solo quando una run persa a macchina spenta deve essere recuperata.
7. Riconcilia MegaVault `services` con l'inventario live usando le API/CLI canoniche disponibili, senza SQL ad-hoc se esiste un comando autorevole. Mantieni un solo record per service identity e source_ref verificabile.
8. Uptime Kuma:
   - identifica il DB Kuma autorevole e il suo runtime/container;
   - prima di ogni write fai backup consistente verificabile;
   - modifica il DB in una finestra sicura (ferma Kuma se SQLite/schema lo richiede), senza cambiare monitor non pertinenti;
   - crea un Push Monitor indipendente per ogni daemon custom always-on privo di monitor; per timer/oneshot custom crea monitor individuale solo con semantica di freschezza/esito corretta;
   - usa i nomi `Fedora Service · <systemd identity>` e le chiavi deterministiche prodotte da `service_monitor_key`;
   - genera/recupera i push token senza stamparli e scrivili solo nel credential boundary root-only di fedora-system-monitor;
   - riavvia Kuma e fai readback direttamente dal DB autorevole: monitor attivo, tipo push, token non vuoto, nessun duplicato;
   - aggiorna l'indice MegaVault Kuma con il flusso canonico `kuma-sync-sqlite`/equivalente e mappa ogni monitor al progetto/purpose corretto.
9. Deploya le unità aggiornate, `daemon-reload`, riavvia solo i daemon interessati e abilita ciò che deve essere sempre disponibile. Non riavviare l'intero PC.
10. Gate runtime per ogni daemon always-on: active + enabled/target corretto; termina controllatamente SOLO il processo figlio (non `systemctl stop`) e verifica che systemd lo rilanci e che `NRestarts` aumenti. Fallo sequenzialmente e salta solo un daemon se il test distruttivo sarebbe concretamente pericoloso, motivandolo.
11. Verifica gli heartbeat Kuma: almeno un UP recente per ogni monitor individuale; per almeno un daemon non critico prova una transizione controllata down/recovery o equivalente senza aspettare inutilmente timeout lunghi.
12. Esegui solo test mirati: unit test nuovi/coinvolti, `systemd-analyze verify`, config-check FSM, readback DB e runtime. Nessun audit generale dopo PASS.

# Acceptance
PASS solo se:
- tabella MegaVault usata = `services`, senza registry parallelo;
- tutte le PR preparate sono integrate oppure sostituite da fix equivalenti canonici;
- nessuna unit Workflowy dipende da .venv;
- tutti i daemon custom always-on live rispettano restart/enablement/target;
- oneshot/timer non sono stati trasformati impropriamente in daemon;
- ogni daemon custom always-on ha monitor Push Kuma individuale + heartbeat; timer/oneshot monitorati usano semantica corretta;
- DB Kuma ha backup pre-write e readback post-write;
- token mai in output/Git/MegaVault;
- MegaVault e indice Kuma sono riconciliati;
- test/gate mirati PASS.

# Stop
Dopo PASS finalizza una sola volta con roadmap_finish e fermati. Niente cleanup/refactor fuori scope.

Output massimo 9 righe:
RESULT=PASS|BLOCKED|FAIL
SERVICES=<custom totali; always-on; timer/oneshot>
HARDENING=<pass/fail + eventuali eccezioni>
KUMA=<monitor creati/riusati + readback>
MEGAVAULT=<services/index status>
PRS=<stato PR>
TESTS=<mirati>
RUNTIME=<restart probes>
BLOCKER=<none|testo minimo>
