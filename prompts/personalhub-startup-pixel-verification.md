[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=734581 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

> Continuazione diretta del run precedente. Non eseguire `roadmap_guard.py select`, non rileggere roadmap/README/spiegazioni e non ripetere la root-cause discovery già fatta. Usa solo i file/tool direttamente pertinenti.

# Goal
Verificare sul Pixel 8a fisico che il `main` remoto corrente di PersonalHub sia non solo rapido da visualizzare ma anche realmente responsivo dopo il cold start. Correggi al massimo **un** hotspot ulteriore solo se una traccia lo dimostra in modo univoco.

# Fatti già verificati — non ripetere
- Baseline originaria sul Pixel reale: `Displayed ...MainActivity: +13s293ms`, launch timeout e `Skipped 687 frames`.
- Il primo fix remoto ha tolto `LegacyTagSessionRepair` da `Application.onCreate()` e ha abbattuto il tempo di visualizzazione: nel run precedente il `main` remoto ha misurato `1.411 / 1.485 / 2.939 s` su tre cold start.
- Quel run è terminato `BLOCKED`: non c'erano launch timeout, ma sono comparsi ANR `Input dispatching timed out ... FocusEvent` e frame skip massivi.
- Nel run precedente è stato provato **solo localmente e non pushato** un defer arbitrario di 12 s in `PersonalHubApplication.kt`: ha portato i tempi circa a `0.847–1.359 s` ma **non** ha risolto il problema (`Skipped 233/272/504 frames` e un altro input timeout). Quella modifica non è autorevole e non va riusata.
- Il `main` remoto corrente contiene invece il fix strutturale successivo: `HubContextRuntime` materializza `HubContextRepository`/Room solo al primo uso reale; il worker post-first-frame usa `THREAD_PRIORITY_BACKGROUND`; le fasi startup hanno marker Perfetto `PH.*` (`PH.ensureStartupReady`, `PH.hubRuntimeInit`, `PH.bg.timerRepair`, ecc.).
- `DatabaseVault.recoverInterruptedImport()` e `ensureStartupReady()` restano volutamente sincroni per sicurezza dati.
- Package reale: `com.gernalix.personalhub`; il requisito è il Pixel fisico.

# Preflight locale minimo
1. Esegui **un solo** `git status --short` in PersonalHub.
2. Se l'unica modifica locale è il vecchio defer 12 s in `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`, scarta **solo quel file** con `git restore -- <path>`; non usare reset/stash generici.
3. Se esistono modifiche locali diverse/non riconducibili a quel defer, `BLOCKED` e STOP senza toccarle.
4. `fetch` + `pull --ff-only` di `main`; nessun branch.

# Gate host economico
Esegui insieme, senza discovery di task/suite larghe salvo errore reale:
- `:core:hub-context:testDebugUnitTest`
- `:feature:multitimetracker:testDebugUnitTest`
- `:app:compileDebugKotlin`

Se PASS, esegui **una sola** `:app:assembleDebug`; installa esattamente quell'APK con `adb install -r`, senza uninstall/clear/reset dati e senza ricostruirla tra test.

# Gate Pixel — 3 cold start
Per ciascuna delle tre prove:
1. usa una directory temporanea univoca; **non** fare cleanup `rm -rf`;
2. `logcat -c`, `am force-stop`, quindi un solo `am start -W`;
3. osserva per circa **8 s**: è sufficiente a coprire il timeout input di 5 s senza i vecchi sleep da 15 s;
4. salva **una sola** cattura logcat bounded per prova e filtra localmente quel file; non rieseguire `logcat -d` per fare filtri equivalenti;
5. registra una volta lo stato focus/window dopo il display per confermare che `MainActivity` sia realmente focused, non solo “Displayed”.

Raccogli: `Status`, `TotalTime/WaitTime`, focus, `Launch timeout`, `ANR in com.gernalix.personalhub`, `Input dispatching timed out`, `FATAL EXCEPTION`, `Skipped N frames`, marker `PH.*`, `MTT_STARTUP`, `PersonalHubStartup`.

## PASS immediato
PASS e STOP senza Perfetto se **tutte e tre** le prove hanno:
- `Status: ok`;
- `MainActivity` focused;
- nessun launch timeout;
- nessun ANR/input timeout/FATAL;
- nessun frame skip massivo (>=100);
- mediana `TotalTime` <= 2.5 s.

# Solo se una prova fallisce
Acquisisci **una sola** traccia Perfetto/System Trace usando il workflow Android-performance già disponibile. Nella traccia:
- usa i marker `PH.*` per separare le fasi;
- ispeziona il **main thread e scheduler slices** durante focus/input timeout;
- non attribuire causalità a `LegacyTagSessionRepair` o ad altro solo perché un log è temporalmente vicino;
- identifica un hotspot solo se la traccia dimostra thread/lock/CPU/DB contention concreta.

Se c'è un hotspot univoco, applica **un solo** fix minimo, poi ripeti una volta i gate host necessari, build/install della nuova APK e le stesse tre prove. Se l'hotspot non è univoco o il secondo gate resta fallito: `BLOCKED` con evidenza minima e STOP. Nessuna seconda indagine generica.

# Non-goal
- niente defer temporali arbitrari, sleep “risolutivi” o nascondere il lavoro dopo N secondi;
- niente audit/refactor/cleanup generale;
- niente modifica a `DatabaseVault.ensureStartupReady()` senza prova diretta Perfetto;
- niente TCL/emulatore in sostituzione del Pixel;
- niente bump `version.txt`, release, final APK delivery o Telegram;
- niente branch/PR.

# Modello
Resta su **GPT-5.5 low** per preflight/build/ADB. Passa a **GPT-5.5 medium solo se il gate Pixel fallisce e devi interpretare l'unica traccia Perfetto**. Nessun GPT-5.6.

# Stop
Su PASS completa solo questo prompt:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581`

`push_verified=git_push_exit_0` è terminale: niente status/fetch/rev-parse successivi sulla roadmap.

Output massimo 7 righe: RESULT, tempi min/mediana/max, focus+ANR/frame, eventuale hotspot Perfetto+fix, test/build, Pixel install/test, commit/push o blocker.
