[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=195098 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
CI minima per i soli Android standalone attivi:
- `gernalix/SuperContacts`
- `gernalix/MultiTimeTracker`
- `gernalix/android-app-template`

`Soldi`, `wordpulse`, `Sostanze`, `Luoghi`, `luoghi-app` sono RETIRE e fuori scope.

# Routing minimo
Per repo leggi una volta: riga matrice visibility, `settings.gradle*`, root/app `build.gradle*`, `.github/workflows` e nomi `src/test`/`src/androidTest`. README solo se manca il comando build. Archived/superseded => SKIPPED.

# Strategia
- **PUBLIC:** hosted standard; PR+push default branch = compile/assemble debug + unit test esistenti + lint necessario. Emulator smoke solo su push default + manuale se esistono test strumentati significativi.
- **PRIVATE:** automatico solo host gate veloce; niente emulator/schedule hosted. Instrumentation manuale/locale solo se già utile; nessun nuovo self-hosted runner.

Sempre: path filter docs-only, Gradle cache, concurrency cancel-in-progress, una sola JDK/API coerente, permissions minime, artifact solo failure <=3 giorni, nessun signing/release secret. Per `android-app-template` basta compilazione/APK valido: non inventare feature test.

# Ciclo
Preflight minimo -> push -> singolo run GitHub canonico. Failure: solo job/log fallito, fix minimo, leaf gate e nuovo run. Niente Pixel/TCL, matrix esplorative, refactor, release o retry identici.

# Acceptance
Ogni repo attivo ha host gate verde; emulator automatico solo quando PUBLIC e utile; PRIVATE non spreca minuti in emulator/schedule.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098`

Output massimo 5 righe: RESULT + una riga per repo + blocker.