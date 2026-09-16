[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=392659 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Portare PersonalHub a CI automatica con **costo GitHub minimo/zero**, scegliendo runner e frequenza in base alla visibility finale applicata da `PROMPT_ID=940316`.

Sorgente decisione:
`/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`

# Gate retention
Prima verifica una sola volta che `gernalix/PersonalHub` esista ancora e non sia `RETIRE` nella matrice. Se è stato eliminato dal task retention: `SKIPPED_DELETED`, completa questo task senza ricrearlo né investigarlo.

# Starting point
- Repo `/home/daniele/projects/PersonalHub`, `main`.
- Riusa `app/src/test`, `app/src/androidTest` e `tools/android_target_preflight.py`; non riscrivere test esistenti.
- Nessun audit applicativo, feature/refactor, release/bump/Telegram.

Leggi una sola volta: riga PH della matrice + `settings.gradle.kts`, root/app `build.gradle.kts`, `.github/workflows` se presente e soli nomi dei test. `.codex/CODE_MAP.tsv` soltanto con grep CI/test mirato.

# Gate visibility — vincolante
Verifica una sola volta la visibility reale con `gh repo view`.

## Se PUBLIC
Usa runner GitHub-hosted standard:
1. **host gate** PR + push `main`: compile/assemble debug + unit test esistenti + lint necessario;
2. **emulator smoke** push `main` + `workflow_dispatch`, non ogni PR;
3. **full instrumentation** schedule notturno + manuale.

NON registrare self-hosted runner su un repo pubblico. Pixel/TCL reali restano QA locale Codex separata, non requisito di questo task.

## Se PRIVATE
Non spendere hosted minutes per job pesanti:
1. registra/riusa un runner Fedora **repo-level PH-only** con label dedicata `fedora-personalhub-ci`;
2. host gate PR/push e emulator smoke girano sul self-hosted;
3. full instrumentation solo `workflow_dispatch`;
4. workflow self-hosted mai `pull_request_target`; permessi token minimi.

Se il runner non è registrabile via CLI/API, Chrome locale è ammesso una sola volta solo per setup; nessun cookie/token nei log.

# Workflow efficiency
Path filter docs-only; Gradle cache; `concurrency` cancel-in-progress; una sola API/JDK; report/logcat/screenshot solo su failure <=3 giorni; nessun secret produzione. `./gradlew tasks --all` massimo una volta solo se necessario.

# Ciclo autonomo
Preflight minimo -> push una volta -> singolo run GitHub canonico. Failure -> solo job/log fallito -> fix minimo -> nuovo run. Niente retry identici o audit post-PASS.

# Sicurezza real-device
Nessun workflow deve fare uninstall, `pm clear`, reset dati o test distruttivi sul Pixel/TCL. La CI usa emulatori; hardware reale resta locale/manuale.

# Acceptance
- PUBLIC: host gate + emulator smoke + full instrumentation hosted definiti e almeno un run manuale/full PASS;
- PRIVATE: runner PH-only validato, host gate + emulator smoke self-hosted PASS, full instrumentation manuale;
- entrambi: path filters, concurrency, artifact failure-only/short retention;
- DELETED/RETIRE: SKIPPED senza ricreare il repo.

# Stop
Dopo PASS/SKIPPED:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659`

Output massimo 7 righe: RESULT, visibility+runner strategy o SKIPPED_DELETED, host gate, emulator, instrumentation, commit/push, blocker.