[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=483612 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

> Solo verifica locale pre-merge. Il refactor è già stato fatto sul branch remoto `gernalix/PersonalHub:architecture/full-capsule-encapsulation`; non rifare audit, redesign o discovery generale e NON mergiare in `main`.

# Goal
Certificare con toolchain Android + emulatore locali che il branch di capsulizzazione compili, che il nuovo gate architetturale passi e che Home, Timer e WordPulse si avviino senza regressioni dovute ai nuovi confini.

# Starting point verificato
- branch: `architecture/full-capsule-encapsulation`;
- base iniziale: `main` a `b09852bb404fdb90b35a5d508e24094eb17f1cf6`;
- il branch rimuove l'ereditarietà di `PersonalHubApplication` da WordPulse, introduce il runtime WordPulse feature-local, espone `TimerStartupApi`, rende `StartupPerfTrace` interno e rafforza `checkArchitectureBoundaries`;
- documentazione: `docs/CAPSULE_BOUNDARIES.md`;
- nessuna migration DB, nessun bump versione richiesto, nessun merge richiesto.

# Procedura minima
1. Leggi solo `AGENTS.md`; usa il lock/preflight PersonalHub già previsto. Se un altro task PH è attivo => `BLOCKED`, senza polling.
2. Fai un solo `fetch`. Lavora in un worktree separato puntato a `origin/architecture/full-capsule-encapsulation`; non reset/stashare checkout esistenti.
3. Esegui una sola invocazione Gradle: `./gradlew checkArchitectureBoundaries :app:assembleQa --no-configuration-cache`. Non lanciare lint/suite generali o compile equivalenti separati.
4. Se fallisce: correggi solo un errore locale, evidente e direttamente causato dal refactor; altrimenti `BLOCKED` riportando il primo errore utile. Nessun refactor aggiuntivo e nessun retry identico senza nuova evidenza.
5. Solo dopo build PASS, avvia l'emulatore con `python3 tools/android_target_preflight.py --target emulator`; non usare TCL o Pixel reale salvo blocker esplicito del preflight, e in questo task non fare fallback su device fisici.
6. Installa la variante QA appena costruita. Smoke test mirato: apri Home, Timer e WordPulse; torna a Home tra i moduli. Verifica assenza di crash e in logcat di `ClassCastException`, `NoClassDefFoundError` o `IllegalAccessError` collegati a `PersonalHubApplication`, `WordPulseRuntime`, `TimerStartupApi` o `StartupPerfTrace`.
7. Disinstalla la QA. Non modificare dati reali, non creare APK finale, non inviare Telegram, non incrementare `version.txt`, non mergiare e non pushare `main`.
8. Stop immediato dopo PASS. Completa solo `PROMPT_ID=483612` con `roadmap_guard complete`.

# Acceptance
PASS solo se `checkArchitectureBoundaries` passa, `:app:assembleQa` passa e Home/Timer/WordPulse si aprono sull'emulatore senza gli errori runtime sopra. Il branch resta separato da `main`.

Output massimo 6 righe: RESULT, branch/SHA, architecture gate, QA build, emulator smoke, blocker/fix eventuale.
