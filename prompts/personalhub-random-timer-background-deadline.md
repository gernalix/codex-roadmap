[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=232198 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=4/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Correggere Random Timer: domanda/notifica al deadline casuale anche con app in background o processo chiuso/swipato via. Aprire Timer NON deve essere il trigger. Questa è anche la release finale della campagna PH.

# Routing verificato — niente discovery
Usa `.codex/CODE_MAP.tsv` riga `timer.random_timer`. Apri SOLO i path mappati; `timer.alerts` solo se un simbolo condiviso richiede contesto. Facts già verificati:
- `createRandomTimerSession()` salva `expectedEndMs` + `RandomTimerStore`, ma non orchestra un alarm OS;
- `NowScreen` oggi scopre il completamento in composizione e mostra il dialog;
- esistono già `TimeFenceTimerScheduler`, `TimeFenceTimerReceiver`, `TimeFenceRestoreReceiver`: RIUSALI, niente secondo scheduler.

# Comportamento richiesto
1. Start: deadline autorevole = `expectedEndMs`; schedula subito un alarm/PendingIntent con identity stabile per sessione.
2. Receiver idempotente al deadline: rileggi sessione, se ancora random/running chiudila a `expectedEndMs`, marca emissione per evitare duplicati, invia notifica `Quanto tempo è passato?` senza durata reale.
3. Tap notifica -> Timer/Now + dialog della sessione corretta. Entrare manualmente può mostrare il dialog pendente, ma NON genera una notifica tardiva/duplicata.
4. Background, lock/Doze e process death devono funzionare. Android `Force stop` è fuori contratto: documenta, niente workaround.
5. Boot/update: rischedula futuri; overdue durante device spento -> finalizza una volta al restore e mostra domanda una sola volta.
6. Cancel/delete di random timer pendente cancella alarm; restore/reschedule/broadcast idempotenti.
7. Se notification/exact-alarm capability necessaria manca, blocca lo start con azione per abilitarla; non promettere exact usando fallback tardivo.
8. Distribuzione random 1..max e segretezza del target restano invariati.

# Test mirati
Prima host/unit: identity, schedule/cancel, duplicate broadcast, overdue/future restore. Poi UNA sessione emulator con androidTest filtrato al Random Timer: start breve, lascia Now, verifica chiusura + notifica senza reopen; lock/Doze solo se ottenibile con helper stabile, niente hack/polling.

# Gate finale campagna — NON ripetere PASS inutilmente
1. Verifica una sola volta che i commit PASS delle fasi 1–3 siano antenati dell'HEAD corrente. Non rileggere i loro report né rifare audit.
2. NON rerunnare test Hub/episodi di fase 1 né migration/check-in di fase 3 se i file/boundary da essi coperti non sono cambiati in fase 4.
3. Per fase 2 rerunna SOLO il test Now direttamente impattato se il diff Random Timer tocca `NowScreen`/controller condivisi; niente intero set QuickStart se non coinvolto.
4. `checkArchitectureBoundaries` solo se il diff di fase 4 cambia wiring/public boundary.
5. Dopo i leaf gate necessari: UN solo `:app:assembleDebug` finale. Nessun secondo build per install/delivery.

# Pixel + release
Dopo host/emulator PASS:
- incrementa `version.txt` una sola volta per la campagna;
- produci l'APK debug canonico `<version>.apk` e trattalo come immutabile;
- installa QUEL file sul Pixel usando helper canonico;
- una sola prova reale da 1 minuto: manda app in background/swipala via (NON force-stop), notifica entro tolleranza pratica <=5 s da `expectedEndMs`, tap apre dialog corretto, reopen non duplica;
- consegna lo stesso artifact via Telegram/GitHub prerelease secondo `AGENTS.md`;
- push branch canonico una volta. Nessun audit post-PASS.

# Non-goal
Niente redesign Now, nuovo motore Alerts, refactor Timer, statistiche Random Timer, nuova distribuzione o workaround force-stop.

# Acceptance
PASS se deadline è OS-driven/UI-independent, sessione termina a `expectedEndMs`, notifica arriva app non aperta, restore/cancel sono idempotenti, target resta segreto e release usa un solo APK testato/installato/consegnato.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.