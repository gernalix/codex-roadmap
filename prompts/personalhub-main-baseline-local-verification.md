[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=913284 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Verifica soltanto `PersonalHub/main`: gate capsule, repair Timer sul vecchio stato AVD persistente e smoke Home→Timer→WordPulse. Nessuna modifica codice/docs.

# Già fatto
Il falso FAIL `contract imports implementation` è stato corretto remotamente in `ae00dfc7`: gli entity importati sono contract-owned ma conservano package legacy condivisi; il gate ora risolve prima il simbolo esatto. Quick-start/ranking/5 suite e façade emulatore 11/11+smoke sono già PASS: non ripeterli.

# Esegui
1. Leggi solo `AGENTS.md`; lock PH `913284`; occupato=>`BLOCKED`, niente polling. Un solo `git fetch origin`; fast-forward sicuro a `origin/main`; vietati stash/reset/force/cleanup. Verifica solo che `ae00dfc7` sia ancestor di `origin/main`.
2. **Prima di avviare AVD**, unico gate host/build:
   `./gradlew checkArchitectureBoundaries :feature:multitimetracker:testDebugUnitTest --tests com.example.multitimetracker.persistence.LegacyTagSessionRepairTest :app:assembleDebug --no-configuration-cache --no-daemon`
   Primo FAIL=>errore utile+STOP; nessun fix/retry identico.
3. Solo dopo PASS avvia `python3 tools/android_emulator_control.py start --timeout 60`; usa solo `target.serial`. Preserva lo stato: vietati `pm clear`, wipe/delete AVD, reset DB e uninstall.
4. Installa **l'APK già costruito**, senza secondo Gradle: `adb -s <serial> install -r "app/build/outputs/apk/debug/$(cat version.txt).apk"`. FAIL=>STOP.
5. Pulisci solo logcat; avvia PH; crea/salva `QA_timed_repair`. PASS Timer = nessun `Save failed|Critical persistent data loss blocked|tagSessions: 1 -> 0` + force-stop/riapertura conserva il tag.
6. Stessa installazione: Home→Timer→Home→WordPulse→Home; zero crash e niente `ClassCastException|NoClassDefFoundError|IllegalAccessError` riferiti a `PersonalHubApplication|WordPulseRuntime|TimerStartupApi|StartupPerfTrace`.
7. Stop emulatore, release lock. Tree invariato. PASS solo se tutto sopra passa.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284`
STOP immediato; nessun audit/status/fetch successivo.

Output ≤6 righe: RESULT, HEAD, host gate/build, Timer persistence/logcat, capsule smoke, blocker/completion.
