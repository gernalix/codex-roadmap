[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=815306 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Validare **solo sul runtime Fedora/Pixel reale** i due helper Android già integrati in `PersonalHub/main`: install APK Pixel deterministico e query Perfetto. Nessuna integrazione PR, nessuna modifica app salvo failure concreta dell'helper.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- PR #10 è già stata squash-mergeata da ChatGPT in `main` con commit `59a4ee6890f0e76ae33336c278ff4ed6402efa4a`;
- file helper/test già in `main`: `AGENTS.md`, `tools/android_pixel_apk.py`, `tools/android_perfetto_query.py`, `tools/test_android_pixel_apk.py`, `tools/test_android_perfetto_query.py`;
- il precedente gate Pixel di `734581` è PASS; non riaprire quel bug/widget;
- task di validazione locale: se tutto passa, **nessun commit PersonalHub è necessario**.

Prompt autosufficiente: non leggere roadmap/README/MegaVault e non fare discovery repo-wide.

# Esecuzione minima
1. Acquisisci il lease PH. Una sola fotografia Git + `git pull --ff-only origin main` se pulito; verifica solo che HEAD includa `59a4ee6890f0e76ae33336c278ff4ed6402efa4a`.
2. Esegui in un unico batch una sola volta:
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_pixel_apk.py`
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_perfetto_query.py`
   - `python3 -m py_compile tools/android_pixel_apk.py tools/android_perfetto_query.py`
   Failure => correggi esclusivamente l'helper/test fallito e riconferma solo quel gate.
3. Pixel smoke:
   - `./gradlew :app:assembleDebug` **una volta**;
   - usa esclusivamente `python3 tools/android_pixel_apk.py install`; niente `adb devices`, guessing APK, uninstall/clear o secondo build;
   - PASS con exit 0 + serial Pixel + APK risolto.
4. Perfetto smoke:
   - riusa `benchmark/.../trace_processor_shell_aarch64`; genera `:benchmark:mergeDebugAssets` solo se manca;
   - riusa una `.pftrace` esistente; solo se assente cattura UNA trace minima ~2 s col workflow Android-performance, senza analisi aggiuntiva;
   - esegui una sola query `select count(*) as slices from slice;` tramite `tools/android_perfetto_query.py`; nessun probe manuale del trace processor o SQL via `adb shell`.
5. Se nessun file è stato modificato, non creare commit/push PersonalHub. Se una failure concreta ha richiesto un fix, `git diff --check`, commit+push una volta.
6. Rilascia il lease e finalizza la roadmap. Nessuna QA ulteriore dopo PASS.

# Non-goal
Niente UI/DB, emulator/TCL, benchmark startup, widget, release, Telegram, dependency upgrade, PR branch maintenance o audit generale.

# Acceptance
PASS con test helper + install Pixel + query Perfetto verdi sull'attuale `main`; zero modifica app funzionale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 815306`

Output massimo 5 righe: RESULT, TESTS, PIXEL, PERFETTO, FIX/BLOCKER.