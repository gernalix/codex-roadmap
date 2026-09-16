[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=734581 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | last_result=BLOCKED`

> Continuazione del debugging startup già pre-localizzato. Non eseguire `roadmap_guard.py select`, non rileggere roadmap/README/spiegazioni/MEMORY e non rifare root-cause discovery. Usa solo i file/tool richiesti sotto.

# Goal
Verificare sul Pixel 8a fisico che PersonalHub `main` sia rapido **e realmente responsivo al tocco** dopo cold start. Se il gate fallisce, usa una sola traccia Perfetto e correggi al massimo un hotspot dimostrato.

**Reasoning fisso per l'intera sessione: GPT-5.5 medium. Non tentare di cambiare reasoning durante il task.**

# Fatti verificati — non ripetere
- Baseline originaria: `Displayed ...MainActivity: +13s293ms`, launch timeout, `Skipped 687 frames`.
- Dopo il primo fix: 3 cold start `1.411 / 1.485 / 2.939 s`, ma run `BLOCKED` per `Input dispatching timed out ... FocusEvent` e frame skip massivi.
- Il defer locale di 12 s era un esperimento fallito ed è stato eliminato.
- Il merge conflict successivo è già risolto e pushato in `main`; `:app:compileDebugKotlin` era PASS. Non riaprire quel problema.
- `main` autorevole contiene: Hub repository/Room lazy, worker post-frame `THREAD_PRIORITY_BACKGROUND`, repair Timer off-main e marker Perfetto `PH.*`.
- Recovery DB e `DatabaseVault.ensureStartupReady()` restano sincroni per sicurezza dati.
- Package reale: `com.gernalix.personalhub`.

# Preflight + host gate
1. `git status --short` una volta. Se ci sono modifiche locali, conflitti o file non committati: `BLOCKED` e STOP senza toccarli.
2. `git fetch origin && git pull --ff-only origin main`.
3. Esegui in una sola invocazione Gradle:
   - `:core:hub-context:testDebugUnitTest`
   - `:feature:multitimetracker:testDebugUnitTest`
   - `:app:compileDebugKotlin`
4. Se PASS, una sola `:app:assembleDebug`; installa quella stessa APK con `adb install -r`, senza uninstall/clear/reset dati.

# Pixel gate — 3 cold start + 1 tap innocuo per run
Per ogni prova:
1. `logcat -c` → `am force-stop` → un solo `am start -W`;
2. osserva ~8 s, salva una sola cattura logcat bounded e filtra localmente quel file;
3. verifica una volta focus/window dopo il display;
4. esegui **un solo test di tocco non distruttivo**:
   - acquisisci al massimo un `uiautomator dump` della schermata corrente;
   - scegli un punto **dentro la finestra di PersonalHub ma fuori dai bounds di nodi `clickable=true` o `long-clickable=true`**, quindi invia un solo `adb shell input tap X Y`;
   - non indovinare coordinate se non puoi dimostrare dal dump che il punto è innocuo;
   - dopo il tap attendi ~1 s e verifica che `MainActivity` sia ancora focused e che non siano comparsi `Input dispatching timed out`, ANR o FATAL.
5. non navigare tra moduli, non modificare dati e non eseguire altri tap/swipe.

Registra solo: `Status`, `TotalTime/WaitTime`, focus prima/dopo il tap, esito touch, launch timeout, ANR/input timeout/FATAL, `Skipped N frames`, `PH.*`, `MTT_STARTUP`, `PersonalHubStartup`.

PASS immediato se tutte e 3 le prove hanno:
- `Status: ok` e `MainActivity` focused;
- il tap innocuo viene inviato e `MainActivity` resta focused subito dopo;
- nessun launch timeout, ANR/input timeout o FATAL prima o dopo il tap;
- nessun `Skipped N frames` con N >= 100;
- mediana `TotalTime` <= 2.5 s.

Se in un run non esiste un punto innocuo dimostrabile dal dump, non tappare a caso: marca solo quel sottogate `TOUCH_NOT_PROVABLE`; il task non può PASS finché il touch gate non viene dimostrato in 3/3 run.

# Solo se il gate fallisce
Acquisisci **una sola** Perfetto/System Trace. Usa `PH.*` e main-thread/scheduler slices per attribuire un blocco reale; non inferire causalità dalla sola vicinanza temporale dei log.

Se emerge un hotspot univoco: applica un solo fix minimo, esegui solo i gate host direttamente pertinenti, rebuild/install una volta e ripeti le 3 prove complete incluso il tap. Se la traccia non identifica un hotspot univoco o il secondo gate fallisce: `BLOCKED` e STOP.

# Non-goal
Niente delay/sleep risolutivi, audit/refactor generale, modifica a `ensureStartupReady()` senza prova Perfetto, TCL/emulatore, bump versione, release/Telegram, branch/PR, test suite globali, navigazione funzionale dell'app o retry equivalenti.

# Stop / roadmap
- **PASS:** completa `734581` dichiarando esplicitamente l'esito PASS, poi STOP:
  `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581 --result PASS --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581 --result PASS`
- **BLOCKED/FAIL:** lascia `734581` attivo. **Non spostarlo manualmente in `completed/`, non rinumerare la roadmap e non eseguire `complete`.**
- `push_verified=git_push_exit_0` è terminale: niente status/fetch/rev-parse successivi sulla roadmap.

Output massimo 7 righe: RESULT, tempi min/mediana/max, focus+touch+ANR/frame, eventuale hotspot+fix, test/build, Pixel install/test, commit/push o blocker.
