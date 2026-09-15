[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=195098 | project_id=51 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Aggiungere CI GitHub Actions minimale ai repository Android standalone ancora attivi che erano stati indicati come candidati:
- `gernalix/SuperContacts`
- `gernalix/MultiTimeTracker`
- `gernalix/android-app-template`
- `gernalix/luoghi-app`

NON includere `Soldi`, `wordpulse`, `Sostanze`, `Luoghi`: sono stati ritirati nel task precedente.

# Routing / starting point
Per ogni slug risolvi una sola volta il vero `project_id` con `megavault.py project <slug>` e lo stato attivo. Se MegaVault lo marca già archived/superseded, riportalo `SKIPPED` e non modificarlo.

Per ogni repo attivo leggi soltanto:
- `settings.gradle*`, root/app `build.gradle*`;
- `.github/workflows/` se presente;
- directory `src/test` e `src/androidTest`;
- README solo se serve a identificare il comando build canonico.

Nessun audit applicativo.

# Implementazione per repo
Applica lo stesso schema senza forzare test che il repo non possiede:
1. workflow PR + push `main` con checkout, JDK/Android setup, Gradle cache;
2. compile/assemble debug + unit test esistenti + lint disponibile;
3. se esistono test strumentati significativi, aggiungi emulator job su push `main`/manuale; non renderlo obbligatorio su ogni PR se aumenta molto i minuti;
4. per `android-app-template` il gate richiesto è che il template/config corrente compili e produca un APK valido; non inventare feature test;
5. artifact/report solo su failure o quando utile per diagnosticare;
6. concurrency con cancellazione dei run superseded;
7. niente release/signing secrets.

Non creare una shared-action cross-repo: per quattro repo piccoli è più semplice e robusto mantenere workflow locali minimali.

# Verifica efficiente
Per ciascun repo:
- un solo gate locale economico corrispondente al workflow;
- commit/push;
- osserva con `gh` solo il run appena creato;
- se fallisce, leggi solo log/job fallito e correggi la causa;
- dopo PASS passa al repo successivo senza audit post-PASS.

Raggruppa le sole letture indipendenti; non lanciare quattro emulatori in parallelo sul laptop.

# Non-goal
- nessun refactor/cleanup;
- niente modifiche funzionali alle app;
- niente Pixel/TCL, release, Telegram;
- niente matrix multi-API/JDK salvo requisito già presente;
- niente nuovi test voluminosi: aggiungi al massimo uno smoke test se il repo è completamente privo di test e serve a validare il bootstrap;
- niente Chrome.

# Acceptance
Ogni repo attivo deve avere un workflow verde coerente con i test realmente disponibili. Repo archived sono `SKIPPED`, non "ripristinati".

# Stop
Dopo PASS completa:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 195098`

Output massimo 8 righe: RESULT + una riga per repo con hosted/emulator/SKIPPED + commit/push/blocker.
