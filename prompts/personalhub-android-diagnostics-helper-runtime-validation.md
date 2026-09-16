[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=815306 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Validare sul Fedora/Pixel reale e integrare SOLO le 5 modifiche della PR PersonalHub #10 (`chatgpt/android-diagnostics-efficiency`): helper deterministico install APK Pixel + helper query Perfetto + relativi test + regole `AGENTS.md`. Nessuna modifica al comportamento dell'app.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- PR #10 è aperta; head originario `7f0e43a3eb86637354ef53ae85ca58ce64c4a07a`;
- file scope ESATTO: `AGENTS.md`, `tools/android_pixel_apk.py`, `tools/android_perfetto_query.py`, `tools/test_android_pixel_apk.py`, `tools/test_android_perfetto_query.py`;
- GitHub può riportare la PR non mergeable per drift di `main`: non investigare il repo. Integra le stesse 5 modifiche su una branch locale pulita creata dall'attuale `origin/main`; per `AGENTS.md` conserva le regole correnti e aggiungi/retieni solo le istruzioni dei due helper. Conflitto inatteso fuori dai 5 file => BLOCKED.
- il precedente gate Pixel di `734581` è già PASS: non ripetere il fix widget.

# Esecuzione minima
1. Una sola fotografia Git + un solo fetch. Dirty non riconducibile al task => BLOCKED; niente stash/reset. Crea la branch d'integrazione da `origin/main` e applica solo il contenuto della PR #10.
2. Esegui insieme una sola volta:
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_pixel_apk.py`
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_perfetto_query.py`
   - `python3 -m py_compile tools/android_pixel_apk.py tools/android_perfetto_query.py`
   - `git diff --check origin/main...HEAD`
   Failure => solo leaf fix pertinente + una riconferma.
3. Smoke Pixel installer:
   - `./gradlew :app:assembleDebug` UNA volta;
   - usa ESCLUSIVAMENTE `python3 tools/android_pixel_apk.py install`; niente `adb devices`, guessing APK, uninstall/clear/rebuild;
   - PASS con exit=0 + serial Pixel + APK risolto.
4. Smoke Perfetto helper:
   - riusa `benchmark/.../trace_processor_shell_aarch64`; genera `:benchmark:mergeDebugAssets` solo se manca;
   - riusa una `.pftrace` esistente di `734581`; se assente cattura UNA trace minima ~2 s col workflow Android-performance, senza analisi;
   - `python3 tools/android_perfetto_query.py TRACE --query 'select count(*) as slices from slice;'` deve restituire risultato valido.
5. Se PASS, fast-forward del `main` locale alla branch testata, push `main` una volta e chiudi PR #10 come integrata. Non spendere round-trip per rendere verde/aggiornare la branch PR.

# Non-goal
Niente UI/DB/Gradle dependency, emulatore/TCL, benchmark startup, release, Telegram, repo-wide search o cleanup.

# Acceptance
PASS solo con test helper + install Pixel + query Perfetto PASS e le 5 modifiche integrate in `main`/pushate.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, TESTS, PIXEL, PERFETTO, MAIN_SHA/PUSH, BLOCKER.