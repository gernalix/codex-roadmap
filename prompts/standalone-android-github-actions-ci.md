[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=195098 | project_id=51 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
CI minima per i soli Android standalone attivi:
- `gernalix/SuperContacts`
- `gernalix/MultiTimeTracker`
- `gernalix/android-app-template`

`Soldi`, `wordpulse`, `Sostanze`, `Luoghi`, `luoghi-app` sono RETIRE e fuori scope anche se non ancora cancellati.

# Routing minimo
Per ogni target risolvi una volta project_id/stato e leggi soltanto: riga matrice pubblico/privato, `settings.gradle*`, root/app `build.gradle*`, `.github/workflows`, nomi di `src/test`/`src/androidTest`. README solo se manca il comando build canonico.

Repo archived/superseded => `SKIPPED` senza modifica.

# Strategia per visibility
## PUBLIC
GitHub-hosted standard:
- PR + push default branch: compile/assemble debug + unit test esistenti + lint necessario;
- se ci sono test strumentati significativi: emulator smoke su push default + `workflow_dispatch`, non ogni PR.

## PRIVATE
Per ridurre consumo Actions:
- automatico solo host gate veloce (compile/unit/lint);
- niente emulator hosted automatico/scheduled;
- instrumentation resta `workflow_dispatch` solo se già leggera oppure locale/Codex; non installare nuovi self-hosted runner per questi piccoli repo.

# Efficienza workflow
- path filters: niente run docs-only;
- Gradle cache + concurrency cancel-in-progress;
- una sola JDK/API coerente, niente matrix esplorative;
- report/artifact solo su failure, retention <=3 giorni;
- niente signing/release secrets;
- `android-app-template`: basta che template/config compili e produca APK valido; non inventare feature test.

Non creare shared action cross-repo.

# Ciclo Codex
Niente full gate locale duplicato: preflight minimo -> push -> run GitHub canonico. Osserva solo il run creato; failure -> solo job/log fallito -> fix minimo -> nuovo run. Nessun retry identico, nessun audit post-PASS, nessun Pixel/TCL.

# Non-goal
Niente refactor/cleanup/feature, release/Telegram, matrix multi-API/JDK, nuovi test voluminosi. Al massimo uno smoke se repo totalmente privo di test e serve al bootstrap CI.

# Acceptance
Ogni repo attivo ha host gate verde; emulator CI automatico solo quando PUBLIC e utile; PRIVATE non spreca minuti in emulator/schedule. Archived => SKIPPED.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098`

Output massimo 6 righe: RESULT + una riga per repo + blocker eventuale.