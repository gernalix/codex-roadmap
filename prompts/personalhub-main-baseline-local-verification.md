[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=913284 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Verifica soltanto il `PersonalHub/main` già mergiato: (A) repair Timer del vecchio `tagSessions` sullo stato AVD persistente; (B) confini capsule/runtime Home→Timer→WordPulse. Nessuna modifica sorgenti/docs.

# Fatti già verificati
`main` contiene `LegacyTagSessionRepair`, `TimerStartupApi`, `WordPulseRuntime`, `checkArchitectureBoundaries` e la façade `tools/android_emulator_control.py`. Ranking/5 suite quick-start e implementazione capsule sono già fatti. La façade emulatore è già stata verificata 11/11 + smoke reale: NON benchmarkarla/retestarla.

# Esegui
1. Leggi solo `AGENTS.md`; acquisisci lock PH per `913284`; occupato => `BLOCKED`, niente polling.
2. Un solo `git fetch origin`; porta il checkout a `origin/main` solo con fast-forward sicuro. Vietati stash/reset/force/cleanup.
3. Preserva lo stato AVD che riproduceva il blocker: vietati `pm clear`, wipe/delete AVD, reset DB o uninstall che cancelli dati.
4. `python3 tools/android_emulator_control.py start --timeout 60`; usa solo il `target.serial` JSON restituito.
5. Un solo Gradle gate:
   `ANDROID_SERIAL=<serial> ./gradlew :feature:multitimetracker:testDebugUnitTest --tests com.example.multitimetracker.persistence.LegacyTagSessionRepairTest checkArchitectureBoundaries :app:installDebug --no-configuration-cache --no-daemon`
   Primo FAIL => riporta errore utile e STOP; niente fix/retry identico.
6. Pulisci solo logcat. Avvia PH; crea/salva un nuovo timed tag `QA_timed_repair`; verifica: niente `Save failed`, `Critical persistent data loss blocked` o `tagSessions: 1 -> 0`; force-stop+riapertura conserva il tag.
7. Sulla stessa installazione smoke Home→Timer→Home→WordPulse→Home; zero crash e niente `ClassCastException|NoClassDefFoundError|IllegalAccessError` riferiti a `PersonalHubApplication|WordPulseRuntime|TimerStartupApi|StartupPerfTrace`.
8. Stop emulatore, release lock. PASS solo se tutti i check sopra passano e il tree resta invariato.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 913284`
Poi STOP: nessun audit/status/fetch successivo.

Output ≤6 righe: RESULT, HEAD, Gradle, Timer persistence/logcat, capsule smoke, blocker/completion.
