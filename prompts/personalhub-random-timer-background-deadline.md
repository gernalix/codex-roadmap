[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=232198 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=4/5 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Correggi SOLO Random Timer affinché completi la sessione e notifichi al deadline casuale anche con app in background, processo chiuso/swipato via o device riavviato. Aprire Timer NON deve essere il trigger. Questa fase implementa e verifica la feature; build/install/delivery finali sono demandati alla fase 5/5 già in roadmap.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- `timer.random_timer` in `.codex/CODE_MAP.tsv` è l'entrypoint; amplia solo per una failure concreta;
- `createRandomTimerSession()` salva `expectedEndMs` + `RandomTimerStore`, ma oggi non orchestra un alarm OS;
- `NowScreen` scopre il completamento in composizione;
- riusa `TimeFenceTimerScheduler`, `TimeFenceTimerReceiver`, `TimeFenceRestoreReceiver`: niente secondo scheduler;
- le fasi 1–3 della campagna sono già concluse; non rileggerne report/roadmap.

# Lease + sync
1. `python3 tools/personalhub_task_lock.py acquire --prompt-id 232198`; failure => `BLOCKED` senza attesa.
2. Se il worktree è pulito: `git fetch --prune origin && git pull --ff-only origin main`; registra la base. Non rebase/merge.
3. Prima del push finale fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base => `BLOCKED`, niente rebase/merge/rerun.
4. Rilascia sempre il lease a PASS/BLOCKED/FAIL.

# Implementazione minima
1. `expectedEndMs` è il deadline autorevole; allo start schedula subito un alarm/PendingIntent con identity stabile per sessione.
2. Receiver idempotente: al deadline rileggi la sessione, se random/running chiudila esattamente a `expectedEndMs`, marca l'emissione e invia `Quanto tempo è passato?` senza rivelare la durata reale.
3. Tap notifica → Timer/Now + dialog della sessione corretta. Entrare manualmente può mostrare un dialog pendente, ma non deve creare notifiche tardive/duplicate.
4. Background, lock/Doze, process death e boot/update devono funzionare; `force-stop` resta fuori contratto.
5. Futuri alarm vengono rischedulati; overdue durante device spento viene finalizzato una sola volta al restore. Cancel/delete cancella l'alarm.
6. Se manca una capability notification/exact-alarm indispensabile, blocca lo start con azione esplicita per abilitarla; niente fallback che prometta exact ma arrivi tardi.
7. Distribuzione random 1..max e segretezza target restano invariate. Niente nuove astrazioni generiche.

# Preflight consumer obbligatorio prima di Gradle
Se l'implementazione cambia firma/shape di un tipo, metodo, constructor, DAO o altra API Kotlin/Room consumata altrove, PRIMA del primo Gradle esegui una sola consumer-closure compatta con `python3 tools/android_consumer_preflight.py scan --symbol '<literal-esatto>'` ripetendo `--symbol` per ogni API cambiata. Il tool deve restituire solo path/moduli: apri e correggi tutti i consumer restituiti; niente `rg -n` repo-wide con alternanze generiche. Per simboli rimossi/rinominati richiedi poi `python3 tools/android_consumer_preflight.py gate --forbid '<vecchio-literal>'` PASS. Se il nome resta ma cambia la firma, riesegui `scan` sul nome esatto e verifica ogni consumer. Solo allora esegui il primo compile Gradle quiet del modulo consumer più alto interessato; un eventuale compile FAIL autorizza soltanto una correzione leaf guidata dall'errore, non nuova discovery generale.

# Verification a costo controllato
1. Host/unit mirati: identity, schedule/cancel, duplicate broadcast, overdue/future restore. Un failure => leggi il report mirato, correggi il leaf e riconferma solo ciò che è necessario.
2. Se serve instrumentation usa SOLO `feature/multitimetracker/src/androidTest/java/com/example/multitimetracker/capsules/now/ui/RandomTimerDeadlineInstrumentedTest.kt`.
3. UNA sessione emulator con `android_emulator_control.py start` + `wait`; riusa il serial. Esegui SOLO:
   `ANDROID_SERIAL=<serial> ./gradlew :feature:multitimetracker:connectedDebugAndroidTest -Ppersonalhub.testBuildType=qa -Pandroid.testInstrumentationRunnerArguments.class=com.example.multitimetracker.capsules.now.ui.RandomTimerDeadlineInstrumentedTest --quiet --console=plain`
4. Verifica start breve → lascia Now → chiusura/notifica senza reopen; lock/Doze solo se ottenibile senza hack/polling. Stop emulator una volta.
5. `checkArchitectureBoundaries` solo se cambia wiring/public boundary.
6. **Non** incrementare `version.txt`, non fare final `assembleDebug/assembleRelease`, non installare il package reale Pixel e non inviare APK: la fase 5/5 farà una sola release finale, includendo anche la verifica Pixel del Random Timer.

# Acceptance
PASS se il deadline è OS-driven/UI-independent, la sessione termina a `expectedEndMs`, notifica/dialog funzionano senza duplicati con app non aperta, restore/cancel sono idempotenti, target resta segreto e i test mirati + emulator sono PASS.

# Non-goal
Niente redesign Now, nuovo motore Alerts, refactor Timer, statistiche Random Timer, nuova distribuzione, workaround force-stop, bump versione, Pixel reale o delivery APK.

# Stop
Dopo PASS tecnico commit/push una volta, poi esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 232198 --confirm-executed`

Dopo PASS niente audit aggiuntivi.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `IMPLEMENTATION`, `HOST_TEST`, `EMULATOR`, `BOUNDARY`, `PUSH/GUARD`.