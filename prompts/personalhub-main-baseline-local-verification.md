[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=913284 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Verifica SOLO il repair Timer sullo stato reale già persistito nell'AVD `Pixel_8a`. Nessun fix, refactor, audit generale o modifica dati di test preesistenti.

# Già fatto
- Gate architettura, test JVM del repair, quick-start/ranking e façade emulatore sono già PASS: non ripeterli.
- Due run reali su `ae00dfc7` hanno riprodotto `Save failed / Critical persistent data loss blocked: tagSessions: 1 -> 0`.
- Il repair già esistente correva nel post-load asincrono; su dispositivi già bootstrappati poteva non essere applicato prima della prima mutazione.
- `PersonalHub/main` ora esegue il repair anche sincronicamente dopo DB recovery e prima della UI; verifica che `c533c598` sia ancestor di `origin/main`.
- Se il repair resta unresolved, `tools/diagnose_timer_legacy_tag_sessions.py` fornisce la diagnosi DB read-only: usa quello, niente esplorazione manuale.

# Esegui
1. Leggi solo `AGENTS.md`; acquisisci lock PH `913284`; occupato=>`BLOCKED` e STOP, niente polling. Un solo `git fetch origin`; fast-forward sicuro a `origin/main`; vietati stash/reset/force/cleanup. Verifica solo `c533c598` ancestor di `origin/main`.
2. Unica build: `./gradlew :app:assembleDebug --no-configuration-cache --no-daemon`. Primo FAIL=>errore utile+STOP; nessun fix/retry/altro Gradle.
3. Avvia `python3 tools/android_emulator_control.py start --timeout 60`; usa solo `target.serial`. Preserva integralmente stato/DB: vietati `pm clear`, wipe/delete AVD, reset DB, uninstall.
4. Installa l'APK già costruito, senza secondo Gradle: `adb -s <serial> install -r "app/build/outputs/apk/debug/$(cat version.txt).apk"`. Avvia ESCLUSIVAMENTE package `com.gernalix.personalhub`.
5. Apri Timer→Tags. Crea `QA_timed_repair`. Prima di premere Add/Save, verifica dall'albero UI che il campo contenga esattamente `QA_timed_repair`; se l'input non è entrato, correggi l'input una sola volta: non classificare un errore di automazione UI come FAIL app. Poi salva una sola volta.
6. PASS salvataggio = nessun `Save failed`, nessun `Critical persistent data loss blocked`, nessun equivalente `tagSessions: 1 -> 0`, e tag visibile. Poi `force-stop` solo dell'app, riaprila e conferma `QA_timed_repair` ancora presente.
7. Niente logcat di routine. Solo se crash o FAIL senza causa UI: raccogli esclusivamente le righe pertinenti.
8. Se ricompare `tagSessions: 1 -> 0`: `force-stop` app, esegui SOLO `python3 tools/diagnose_timer_legacy_tag_sessions.py --serial <serial>`, conserva l'output JSON e STOP. Nessuna query DB manuale e nessun fix.
9. Arresta AVD con `python3 tools/android_emulator_control.py stop --timeout 60` (**senza `--serial`**); release lock; verifica solo working tree PH invariato.

# PASS
Solo se save + force-stop/reopen persistono il tag:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284`
Poi STOP immediato; nessun audit/status/fetch/task successivo.

# Output
≤6 righe: `RESULT`, `HEAD`, `BUILD`, `TIMER`, `DIAG=not-needed|<counts essenziali>`, `COMPLETION|STOP_REASON`.
