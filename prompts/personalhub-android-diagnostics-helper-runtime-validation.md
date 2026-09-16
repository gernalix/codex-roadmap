[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=815306 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Validare e integrare SOLO PR PersonalHub #10 (`chatgpt/android-diagnostics-efficiency`), che rende deterministici install APK su Pixel fisico e query Perfetto. Nessuna modifica al comportamento dell'app.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- PR #10 head verificato in chat: `7f0e43a3eb86637354ef53ae85ca58ce64c4a07a`;
- base iniziale: `1f2e4015ac4fb0f412a3ad60acd365bf5096d54c`;
- file nuovi: `tools/android_pixel_apk.py`, `tools/android_perfetto_query.py` + due test; `AGENTS.md` già aggiornato;
- il precedente gate Pixel di `734581` è già PASS: non ripeterlo e non riaprire il fix widget.

# Esecuzione minima
1. Una sola fotografia Git; se dirty non riconducibile al task => BLOCKED. Fetch PR #10 e verifica una sola volta compatibilità con `origin/main`; niente audit/repo-wide search.
2. Sul branch PR esegui insieme:
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_pixel_apk.py`
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_perfetto_query.py`
   - `python3 -m py_compile tools/android_pixel_apk.py tools/android_perfetto_query.py`
   - `git diff --check origin/main...HEAD`
   Failure => solo leaf fix pertinente + una riconferma.
3. Smoke Pixel installer, una sola volta:
   - `./gradlew :app:assembleDebug` una volta;
   - usa ESCLUSIVAMENTE `python3 tools/android_pixel_apk.py install`; niente `adb devices`, niente guessing `app-debug.apk`, niente uninstall/clear/rebuild;
   - verifica solo exit=0 e output strutturato con serial Pixel + APK risolto.
4. Smoke Perfetto helper, una sola volta:
   - assicurati che esista `benchmark/build/intermediates/assets/debug/mergeDebugAssets/trace_processor_shell_aarch64`; se manca, esegui una sola `:benchmark:mergeDebugAssets`;
   - usa una `.pftrace` già disponibile dal run `734581` se esiste; altrimenti cattura UNA trace minima di ~2 s tramite il workflow Android-performance già disponibile, senza analisi prestazionale;
   - esegui `python3 tools/android_perfetto_query.py TRACE --query 'select count(*) as slices from slice;'`;
   - PASS se restituisce una query valida. Non provare binari host/Android Studio alternativi e non fare SQL quoting manuale.
5. Se tutti i gate PASS, integra PR #10 con fast-forward se ancora possibile, push `main` una volta e chiudi il branch se sicuro. Nessun bump `version.txt`, APK delivery, Telegram, benchmark startup o ulteriore QA.

# Non-goal
Niente modifica widget, app startup, UI, DB, Gradle dependencies, emulatore/TCL, full test suite, Perfetto root-cause analysis, release o cleanup generale.

# Acceptance
Test helper PASS; install Pixel serial-scoped con APK da `output-metadata.json`; query Perfetto helper PASS senza discovery manuale; PR #10 integrata in `main` e pushata.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, tests, Pixel install, Perfetto query, main SHA/push, blocker.
