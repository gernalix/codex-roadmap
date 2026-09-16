[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=195098 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
CI minima per gli eventuali Android standalone ancora presenti dopo la retention review:
- `gernalix/SuperContacts`
- `gernalix/MultiTimeTracker`
- `gernalix/android-app-template`

# Gate retention
Per ciascun target verifica una sola volta esistenza GitHub + riga matrice. Repo non esistente o `RETIRE` => `SKIPPED_DELETED`, senza ricrearlo, clonarlo o investigarlo. Se tutti sono assenti/RETIRE, completa subito il task come SKIPPED.

# Routing minimo
Per repo rimasto leggi una volta: riga matrice visibility, `settings.gradle*`, root/app `build.gradle*`, `.github/workflows` e nomi `src/test`/`src/androidTest`. README solo se manca il comando build.

# Strategia
- **PUBLIC:** hosted standard; PR+push default branch = compile/assemble debug + unit test esistenti + lint necessario. Emulator smoke solo su push default + manuale se esistono test strumentati significativi.
- **PRIVATE:** automatico solo host gate veloce; niente emulator/schedule hosted. Instrumentation manuale/locale solo se già utile; nessun nuovo self-hosted runner.

Sempre: path filter docs-only, Gradle cache, concurrency cancel-in-progress, una sola JDK/API coerente, permissions minime, artifact solo failure <=3 giorni, nessun signing/release secret. Per `android-app-template` basta compilazione/APK valido: non inventare feature test.

# Ciclo
Preflight minimo -> push -> singolo run GitHub canonico. Failure: solo job/log fallito, fix minimo, leaf gate e nuovo run. Niente Pixel/TCL, matrix esplorative, refactor, release o retry identici.

# Acceptance
Ogni repo rimasto ha host gate verde; emulator automatico solo quando PUBLIC e utile; repo eliminati/RETIRE sono SKIPPED senza essere ricreati.

# Stop
Dopo PASS/SKIPPED:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098`

Output massimo 5 righe: RESULT + una riga per repo + blocker.