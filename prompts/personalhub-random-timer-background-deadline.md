[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=232198 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=4/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Correggere Random Timer: domanda/notifica al deadline casuale anche con app in background o processo chiuso/swipato via. Aprire Timer NON deve essere il trigger. Questa è anche la release finale della campagna PH.

# Lease + sync + helper canonici
1. Repo canonico: `/home/daniele/projects/PersonalHub`. Esegui direttamente `python3 tools/personalhub_task_lock.py acquire --prompt-id 232198`; se non acquisisce, `RESULT=BLOCKED` senza attesa.
2. Subito dopo: richiedi worktree pulito, `git fetch --prune origin && git pull --ff-only origin main`, poi registra lo SHA di `origin/main` come base remota. Se non è possibile fast-forwardare pulitamente, BLOCKED: niente rebase/merge.
3. Per emulator usa solo `python3 tools/android_emulator_control.py status|start|wait|stop`; per install Pixel usa `python3 tools/android_pixel_apk.py install` dopo il build richiesto. Non aprire `AGENTS.md` soltanto per lease/emulator/install e non fare discovery ADB/APK parallela salvo blocker concreto degli helper.
4. Prima del commit/push finale: UNA `git fetch origin`; se `origin/main` è avanzato rispetto alla base registrata, `RESULT=BLOCKED` e STOP senza rebase/merge/rerun dei gate. Non assorbire lavoro PersonalHub concorrente nella sessione di release.
5. Dopo PASS/BLOCKED/FAIL rilascia sempre `python3 tools/personalhub_task_lock.py release --prompt-id 232198`.

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
Prima host/unit: identity, schedule/cancel, duplicate broadcast, overdue/future restore. Failure => leaf fix basato sull'errore + solo test fallito; una sola riconferma finale del set mirato. Poi UNA sessione emulator con androidTest filtrato al Random Timer, usando `--quiet --console=plain`: start breve, lascia Now, verifica chiusura + notifica senza reopen; lock/Doze solo se ottenibile con helper stabile, niente hack/polling.

# Gate finale campagna — NON ripetere PASS inutilmente
1. Verifica una sola volta che i commit PASS delle fasi 1–3 siano antenati dell'HEAD corrente. Per fase 1 considera canonici `3cfd170cc8a2b2155f8f531ce6efcb0fc116247f` + follow-up `99bcf743965d9d9508d33ad50ad97946285d08c8`. Non rileggere i loro report né rifare audit.
2. NON rerunnare test Hub/episodi di fase 1 né migration/check-in di fase 3 se i file/boundary da essi coperti non sono cambiati in fase 4.
3. Per fase 2 rerunna SOLO il test Now direttamente impattato se il diff Random Timer tocca `NowScreen`/controller condivisi; niente intero set QuickStart se non coinvolto.
4. `checkArchitectureBoundaries` solo se il diff di fase 4 cambia wiring/public boundary; usa `--quiet --console=plain`.
5. Dopo i leaf gate necessari: UN solo `./gradlew --quiet --console=plain :app:assembleDebug` finale. Nessun secondo build per install/delivery; su PASS non stampare lista task `UP-TO-DATE`.

# Pixel + release
Dopo host/emulator PASS:
- incrementa `version.txt` una sola volta per la campagna;
- produci l'APK debug canonico `<version>.apk` e trattalo come immutabile;
- installa QUEL file sul Pixel usando `python3 tools/android_pixel_apk.py install`; niente `adb devices`, guessing APK o install non scoped;
- una sola prova reale da 1 minuto: manda app in background/swipala via (NON force-stop), notifica entro tolleranza pratica <=5 s da `expectedEndMs`, tap apre dialog corretto, reopen non duplica;
- consegna lo stesso artifact via Telegram/GitHub prerelease secondo le regole di delivery già presenti in `AGENTS.md`; apri solo quelle righe se il percorso non è già noto, non fare discovery generale;
- push branch canonico una volta. Nessun audit post-PASS.

# Non-goal
Niente redesign Now, nuovo motore Alerts, refactor Timer, statistiche Random Timer, nuova distribuzione o workaround force-stop.

# Acceptance
PASS se deadline è OS-driven/UI-independent, sessione termina a `expectedEndMs`, notifica arriva app non aperta, restore/cancel sono idempotenti, target resta segreto e release usa un solo APK testato/installato/consegnato.

# Stop
Solo dopo acceptance PASS e base remota invariata: commit/push PersonalHub una volta, quindi
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198`.
Se `roadmap_guard` rifiuta il completamento, `RESULT=BLOCKED` anche con codice PASS; non manipolare manualmente la roadmap. Rilascia il lease. Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe.
