[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=392659 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Portare PersonalHub a CI automatica con **costo GitHub minimo/zero**, scegliendo runner e frequenza in base alla visibility già applicata da `PROMPT_ID=643812`.

Sorgente decisione:
`/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`

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
3. full instrumentation solo `workflow_dispatch` (nessun nightly se il laptop può essere offline);
4. workflow self-hosted mai `pull_request_target`; permessi token minimi.

Se il runner non è registrabile via CLI/API, Chrome locale è ammesso una sola volta solo per setup; nessun cookie/token nei log.

# Workflow efficiency
- path filters: niente run per docs-only; modifica workflow/build/test/code deve triggerare;
- Gradle cache e `concurrency` con cancel-in-progress;
- una sola API/JDK coerente col progetto, niente matrix esplorative;
- report/logcat/screenshot solo su failure, retention breve (<=3 giorni);
- nessun secret di produzione;
- riusa task Gradle noti; `./gradlew tasks --all` massimo una volta solo se realmente necessario.

# Ciclo autonomo
Non duplicare in locale l'intera CI. Fai solo syntax/preflight minimo necessario a evitare un push palesemente rotto, poi push una volta e usa il run GitHub come gate canonico.

Per ciascun workflow pertinente:
- identifica il singolo run creato;
- `gh run watch --exit-status` una volta;
- failure -> leggi solo job/log fallito -> fix minimo -> nuovo run;
- niente retry identico o audit post-PASS.

Per il self-hosted emulator usa il preflight canonico; non fare discovery AVD/SDK alternativa finché non fallisce con evidenza concreta.

# Sicurezza real-device
Nessun workflow deve fare automaticamente uninstall, `pm clear`, reset dati o test distruttivi sul Pixel/TCL. La CI usa emulatori; hardware reale resta locale/manuale.

# Acceptance
- PUBLIC: host gate + emulator smoke + full instrumentation hosted definiti e almeno un run manuale/full PASS; nessun self-hosted runner collegato al repo.
- PRIVATE: runner PH-only validato; host gate + emulator smoke self-hosted PASS; full instrumentation manuale avviabile; nessun hosted job pesante ricorrente.
- in entrambi: workflow path-filtered, concurrency attiva, artifacts failure-only/short retention.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659`

Output massimo 7 righe: RESULT, visibility+runner strategy, host gate, emulator, full instrumentation, commit/push, blocker.