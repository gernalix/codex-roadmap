[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=232198 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=4/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Correggere Random Timer: domanda/notifica al deadline casuale anche con app in background o processo chiuso/swipato via. Aprire Timer NON deve essere il trigger. Questa è la release finale della campagna PH.

# Starting point autoritativo
- repo/workdir canonico: `/home/daniele/projects/PersonalHub`;
- `timer.random_timer` in `.codex/CODE_MAP.tsv` è l'entrypoint; `timer.alerts` solo se un simbolo condiviso lo richiede;
- `createRandomTimerSession()` salva `expectedEndMs` + `RandomTimerStore`, ma oggi non orchestra un alarm OS;
- `NowScreen` scopre il completamento in composizione;
- riusa `TimeFenceTimerScheduler`, `TimeFenceTimerReceiver`, `TimeFenceRestoreReceiver`: niente secondo scheduler;
- fase 2 Timer Now è già implementata in `82d56960d4e7d83dcca34a230efcd7cdb87a6a4e`; fase 3 deve essere già PASS prima di questa release;
- prompt autosufficiente: NON leggere README/roadmap/spiegazioni/MEMORY/MegaVault salvo blocker concreto.

# Lease + sync
1. `python3 tools/personalhub_task_lock.py acquire --prompt-id 232198`; failure => BLOCKED senza attesa.
2. Worktree pulito → `git fetch --prune origin && git pull --ff-only origin main`; registra SHA di `origin/main`. Non fast-forwardabile => BLOCKED, niente rebase/merge.
3. Prima del commit/push finale fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base, BLOCKED senza rebase/merge/rerun gate.
4. Rilascia sempre il lease a PASS/BLOCKED/FAIL.

# Comportamento richiesto
1. Start: `expectedEndMs` è deadline autorevole; schedula subito alarm/PendingIntent con identity stabile per sessione.
2. Receiver idempotente: al deadline rileggi la sessione, se random/running chiudila esattamente a `expectedEndMs`, marca emissione e invia notifica `Quanto tempo è passato?` senza rivelare durata reale.
3. Tap notifica → Timer/Now + dialog della sessione corretta. Entrare manualmente può mostrare dialog pendente, ma non genera notifica tardiva/duplicata.
4. Background, lock/Doze e process death devono funzionare. `Force stop` resta fuori contratto.
5. Boot/update: futuri rischedulati; overdue mentre device spento finalizzato una sola volta al restore.
6. Cancel/delete cancella alarm; restore/reschedule/broadcast idempotenti.
7. Se manca capability notification/exact-alarm necessaria, blocca lo start con azione esplicita per abilitarla; niente fallback che prometta exact ma arrivi tardi.
8. Distribuzione random 1..max e segretezza target invariati.

# Test host + emulator a costo controllato
1. Host/unit: identity, schedule/cancel, duplicate broadcast, overdue/future restore. FAIL => leaf fix + solo test fallito; riconferma set mirato una volta alla fine.
2. Se serve un nuovo test strumentale, usa/crea SOLO `feature/multitimetracker/src/androidTest/java/com/example/multitimetracker/capsules/now/ui/RandomTimerDeadlineInstrumentedTest.kt`; non inventariare altri androidTest.
3. UNA sessione emulator con `android_emulator_control.py start` + `wait`; riusa il serial.
4. Esegui SOLO:
   `ANDROID_SERIAL=<serial> ./gradlew :feature:multitimetracker:connectedDebugAndroidTest -Ppersonalhub.testBuildType=qa -Pandroid.testInstrumentationRunnerArguments.class=com.example.multitimetracker.capsules.now.ui.RandomTimerDeadlineInstrumentedTest --quiet --console=plain`.
   Verifica start breve → lascia Now → chiusura/notifica senza reopen; lock/Doze solo se ottenibile senza hack/polling.
5. Stop emulator una volta. Nessun `adb devices`, discovery task Gradle, suite instrumentation generale o polling ravvicinato.

# Gate finale campagna
1. Verifica una sola volta che i commit PASS delle fasi 1–3 siano antenati di HEAD; niente lettura dei report precedenti.
2. Non rerunnare Hub/episodi né migration/check-in se i relativi file/boundary non sono cambiati.
3. Rerunna un test Now precedente SOLO se il diff Random Timer tocca direttamente `NowScreen`/QuickStart/controller coperto da quel test.
4. `checkArchitectureBoundaries` solo se cambia wiring/public boundary.
5. Incrementa `version.txt` una sola volta.
6. UN solo `./gradlew --quiet --console=plain :app:assembleDebug` finale. L'artefatto risolto da `app/build/outputs/apk/debug/output-metadata.json` diventa immutabile: nessun rebuild per install/delivery.

# Pixel + release
1. Installa l'esatto debug artifact già costruito con `python3 tools/android_pixel_apk.py install`; usa il path restituito come `FINAL_APK`. Non usare `adb devices`, guessing APK, uninstall/clear.
2. Una sola prova reale da ~1 minuto sul Pixel: avvia Random Timer breve, manda app in background/swipala via (non force-stop), verifica notifica entro tolleranza pratica <=5 s da `expectedEndMs`, tap → dialog corretto, reopen senza duplicato. Usa UI/ADB solo per queste azioni puntuali; niente esplorazione generale.
3. Consegna lo STESSO `FINAL_APK` direttamente con:
   `python3 tools/deliver_personalhub_apk.py "$FINAL_APK" --version "$(cat version.txt)" --telegram-title "PersonalHub APK"`.
   Non leggere `AGENTS.md` per riscoprire il delivery e non creare artifact alternativo per limiti Telegram.
4. Commit/push branch canonico una volta, dopo gate PASS e base remota invariata. Nessun audit post-PASS.

# Non-goal
Niente redesign Now, nuovo motore Alerts, refactor Timer, statistiche Random Timer, nuova distribuzione o workaround force-stop.

# Acceptance
PASS se deadline è OS-driven/UI-independent, sessione termina a `expectedEndMs`, notifica arriva con app non aperta, restore/cancel sono idempotenti, target resta segreto e un solo APK viene buildato/testato/installato/consegnato.

# Stop
Dopo acceptance PASS: push PersonalHub una volta. Prova `roadmap_guard complete --prompt-id 232198 --dry-run`; se ready esegui complete. Solo su `prompt_identity_mismatch` dovuto a task indipendente precedente usa `reconcile --prompt-id 232198 --result PASS` dry-run + `--confirm-executed`. Altri errori guard => BLOCKED. Rilascia il lease.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe.
