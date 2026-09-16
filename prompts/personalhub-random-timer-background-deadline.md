[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=232198 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=4/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Correggere Random Timer: la domanda/notifica deve essere emessa al deadline casuale anche se Timer non è aperto, l'app è in background o il processo è stato chiuso/swipato via. L'apertura di Timer NON deve essere il trigger della notifica. Questa è anche la fase finale di release della campagna PH.

# Root cause già verificata
Usa `.codex/CODE_MAP.tsv` (`timer.root`, `timer.sessions`, `timer.alerts`) e apri solo i path pertinenti. In chat è stato verificato che:
- `NowCapsuleViewModel.createRandomTimer()` sceglie i minuti e `SessionOwnerCapsuleViewModel.createRandomTimerSession()` salva una sessione con `expectedEndMs` + `RandomTimerStore.saveRun()`;
- `RandomTimerStore` memorizza id random/target/answered ma NON orchestra un alarm OS;
- `NowScreen.kt` calcola `RandomTimerStore.unansweredCompletedSession(...)` durante la composizione e mostra `RandomTimerResultDialog`: quindi l'apertura di Now è oggi parte del trigger osservabile;
- esiste già infrastruttura `AlarmManager` robusta: `TimeFenceTimerScheduler`, `TimeFenceTimerReceiver`, `TimeFenceRestoreReceiver`, inclusi exact/allow-while-idle, boot/package-replace restore e notification plumbing. RIUSALA: niente secondo scheduler parallelo.

# Comportamento richiesto
1. All'avvio Random Timer persisti il deadline autorevole (`expectedEndMs` già esiste nella sessione) e schedula immediatamente un PendingIntent/alarm identificato stabilmente dalla sessione.
2. Al deadline il receiver OS deve, in modo idempotente:
   - rileggere la sessione autorevole;
   - se è ancora random/running, chiuderla esattamente a `expectedEndMs` (non al momento in cui l'utente riapre l'app);
   - marcare lo stato necessario a evitare doppie emissioni;
   - mostrare una notifica con domanda equivalente a `Quanto tempo è passato?`, SENZA rivelare target o durata reale.
3. Tap notifica -> apre direttamente Timer/Now e il dialog di risposta per quella sessione. Se il dialog viene aperto anche entrando manualmente dopo il deadline va bene, ma l'ingresso nell'app non deve generare una nuova notifica tardiva.
4. Background, screen locked/Doze e processo terminato devono funzionare. `Settings > Force stop` è fuori contratto Android: documentalo, non tentare workaround.
5. Boot / app update: `TimeFenceRestoreReceiver` deve rischedulare i random timer futuri; se un deadline è già passato mentre il device era spento, finalizza una sola volta al primo restore e mostra la domanda senza duplicati.
6. Cancel/delete/undo di un random timer ancora pendente deve cancellare il relativo alarm. Rischeduling e receiver devono essere idempotenti.
7. Garanzia: se notifiche o exact alarms non sono autorizzabili sul device, NON degradare silenziosamente a un comportamento che potrebbe notificare tardi. Prima dello start mostra l'azione necessaria per concedere il permesso/capability; conserva eventuale fallback inexact solo per feature esistenti che già lo usano, non come promessa “exact” del Random Timer.
8. Mantieni segreto il valore random fino alla risposta/flow già previsto. Non cambiare la distribuzione casuale 1..max né il significato del risultato.

# Test mirati
- unit: identity alarm, schedule/cancel, duplicate broadcast idempotente, overdue restore, future restore;
- integration/instrumented: start 1-minute Random Timer, lascia Now; verifica fine sessione + notifica senza riaprire Timer;
- emulator canonico: background + screen lock/Doze se riproducibile senza hack fragili;
- Pixel reale finale: una prova 1 minuto con processo background/swipato via (NON `force-stop`), notifica ricevuta entro tolleranza pratica <=5 s dal `expectedEndMs`, tap apre il dialog corretto e nessuna seconda notifica compare al reopen;
- usa helper Android di `AGENTS.md`; niente ADB discovery duplicata, retry identici o polling ravvicinato.

# Gate campagna + release finale
Questa è la fase finale: integra i risultati delle fasi 1–3 già pushate; non riaprire audit. Esegui leaf test necessari alle modifiche Random Timer, poi i gate consolidati indispensabili della campagna: migration test Luoghi, test Hub/Now mirati, `checkArchitectureBoundaries` se richiesto dai diff e UN solo `:app:assembleDebug` finale. Se un gate fallisce, correggi il leaf failure e ripeti il gate aggregato solo una volta alla fine.

Solo dopo tutti i gate PASS:
- incrementa `version.txt` esattamente una volta per l'intera campagna;
- costruisci il debug APK canonico `<version>.apk` secondo `AGENTS.md` e trattalo come immutabile;
- installa QUEL file sul Pixel, esegui la prova runtime Random Timer sopra, poi consegna lo stesso artifact via Telegram/GitHub prerelease secondo la soglia prevista;
- push branch canonico una sola volta dopo i fix finali e verifica il push tramite il normale gate terminale, senza audit post-PASS.

# Non-goal
Niente redesign Now (fase 2), nuovo motore Alerts, refactor generale Timer, statistiche Random Timer, cambi distribuzione random o workaround per Android force-stop.

# Acceptance
PASS se il deadline è OS-driven e indipendente dalla UI/processo, sessione termina a `expectedEndMs`, notifica domanda arriva anche app chiusa/background, reboot/update/cancel sono idempotenti, nessuna durata viene svelata prima della risposta, test consolidati PASS e l'APK finale è installato/consegnato secondo AGENTS.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 232198`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.