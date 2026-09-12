[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=913284 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Verifica SOLO il repair Timer sullo stato reale già persistito nell'AVD `Pixel_8a`. Nessun fix, refactor, audit generale o pulizia dello stato.

# Già verificato
- I run precedenti hanno riprodotto `Save failed / Critical persistent data loss blocked: tagSessions: 1 -> 0`.
- La diagnosi read-only dell'AVD ha isolato il caso reale: `examined=1`, `missing_session=1`, `sessions_total=0`, `session_tags_total=1`.
- Il problema non è più da investigare: il record legacy esiste ma manca la sessione moderna a cui collegarlo.
- `PersonalHub/main` contiene ora un repair additivo che, solo quando non esiste alcuna sessione moderna sullo stesso intervallo e quell'intervallo identifica una sola sessione legacy, ricrea la sessione chiusa e ripristina l'edge. I casi ambigui restano unresolved; `CriticalDataGuard` non è stato indebolito.
- Verifica che `457c6b9c` sia ancestor di `origin/main`.
- Niente discovery del codice, architecture audit, smoke di altri moduli o query DB manuali.

# Esegui
1. Vai direttamente nel checkout operativo: `cd /home/daniele/projects/PersonalHub`. Leggi solo `AGENTS.md`; acquisisci lock PH `913284`. Se occupato: `RESULT=BLOCKED` e STOP, niente polling. Un solo `git fetch origin`; fast-forward sicuro a `origin/main`; vietati stash/reset/force/cleanup. Verifica solo `457c6b9c` ancestor di `origin/main`.
2. Unica invocazione Gradle, prima dell'AVD:
   `./gradlew :feature:multitimetracker:testDebugUnitTest --tests com.example.multitimetracker.persistence.LegacyTagSessionRepairTest :app:assembleDebug --no-configuration-cache --no-daemon`
   Primo FAIL => errore utile e STOP. Nessun fix, retry identico o altro Gradle.
3. Avvia `python3 tools/android_emulator_control.py start --timeout 60`; usa solo `target.serial`. Preserva integralmente stato e DB: vietati `pm clear`, wipe/delete AVD, reset DB e uninstall.
4. Installa l'APK già costruito, senza secondo Gradle:
   `adb -s <serial> install -r "app/build/outputs/apk/debug/$(cat version.txt).apk"`
   Avvia esclusivamente `com.gernalix.personalhub`.
5. Apri Timer→Tags e crea `QA_timed_repair`. Prima di Add/Save verifica dall'albero UI che il campo contenga esattamente `QA_timed_repair`; se l'automazione input fallisce, correggila una sola volta. Salva una sola volta.
6. PASS salvataggio = nessun `Save failed`, nessun `Critical persistent data loss blocked`, nessun equivalente `tagSessions: 1 -> 0`, e tag visibile. Poi `force-stop` solo dell'app, riaprila e conferma che `QA_timed_repair` sia ancora presente.
7. Niente logcat di routine. Solo su crash o FAIL senza causa UI raccogli esclusivamente le righe pertinenti.
8. Se ricompare `tagSessions: 1 -> 0`: `force-stop` app, esegui SOLO `python3 tools/diagnose_timer_legacy_tag_sessions.py --serial <serial>`, conserva l'output JSON e STOP. Nessuna query DB manuale e nessun fix.
9. Arresta AVD con `python3 tools/android_emulator_control.py stop --timeout 60`; release lock; verifica solo working tree PH invariato.

# PASS
Solo se test/build + save + force-stop/reopen sono PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284`
Poi STOP immediato; nessun audit/status/fetch/task successivo.

# Output
≤6 righe: `RESULT`, `HEAD`, `BUILD_TEST`, `TIMER`, `DIAG=not-needed|<counts essenziali>`, `COMPLETION|STOP_REASON`.
