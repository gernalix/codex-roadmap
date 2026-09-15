[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=392659 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD`

# Goal
Portare PersonalHub a una pipeline CI automatica e a basso consumo:
1. GitHub Actions hosted per build/lint/unit test a ogni PR/push rilevante;
2. test Android su emulatore con frequenza controllata;
3. test strumentati completi nightly/manuali;
4. un runner self-hosted Fedora **solo per PersonalHub privato**, manuale e hardenizzato, per smoke test su hardware reale quando Pixel/TCL sono collegati.

Codex deve creare, eseguire e correggere la pipeline autonomamente usando `gh`; Chrome è fallback solo se una configurazione GitHub indispensabile non è disponibile via CLI/API.

# Starting point verificato
- Repo: `/home/daniele/projects/PersonalHub`, branch `main`.
- Esistono già `app/src/test` e `app/src/androidTest`, inclusi test DB/Finance/Hub Context/widget/Datasette: riusali, non riscriverli.
- Al momento della preparazione del task non risultava una `.github/workflows` nel repo.
- Esiste già il workflow locale canonico per avvio emulatore `tools/android_target_preflight.py`.
- Il package reale e i dati del Pixel non devono essere alterati da CI cloud.

# Scope minimo
Prima leggi solo:
- `settings.gradle.kts`, root/app `build.gradle.kts`;
- `.github/workflows/` se nel frattempo esiste;
- nomi dei test in `app/src/test` e `app/src/androidTest`;
- eventuale `.codex/CODE_MAP.tsv` solo per righe CI/test pertinenti.

Non fare audit del codice applicativo.

# CI hosted
Crea il minimo numero di workflow leggibili, con cache Gradle e concurrency cancel-in-progress:
- **host gate** su PR e push a `main`: compile/build debug + unit test esistenti + lint strettamente necessario;
- **emulator smoke** su push a `main` e `workflow_dispatch`, non su ogni PR: usa una piccola selezione di test strumentati già esistenti e stabili;
- **full instrumentation** nightly + `workflow_dispatch`: suite Android strumentata completa sull'emulatore.

Usa versioni correnti e affidabili delle action; evita matrix di JDK/API inutili. Carica report/logcat/screenshot solo su failure. Nessun secret per i test che possono usare fixture/mocks.

Per scegliere i comandi Gradle:
- riusa task noti dal progetto;
- al massimo una `./gradlew tasks --all` se un nome è realmente incerto;
- niente sequenze di `check` equivalenti.

# Runner Fedora reale
Solo dopo PASS della CI hosted:
1. verifica se esiste già un runner repo-level PersonalHub; se sì riusalo;
2. altrimenti registra sul ThinkPad Fedora un runner GitHub **repo-level** per `gernalix/PersonalHub`, con label dedicata `fedora-personalhub-real`;
3. il workflow real-device deve essere solo `workflow_dispatch`, mai `pull_request`, `pull_request_target` o trigger da fork;
4. permessi `GITHUB_TOKEN` minimi e nessun secret stampato;
5. prima di ADB usa il preflight canonico; se nessun device reale autorizzato è presente, termina `SKIPPED`/chiaro, non avvia una caccia ai device;
6. non usare `pm clear`, uninstall o reset dati del package reale; smoke non distruttivo: build/install `-r` solo se esplicitamente sicuro per la variante di test e avvio/health/logcat limitato;
7. non dare al runner accesso ad altri repository privati.

Se la registrazione runner richiede un passaggio browser non ottenibile con `gh`, Codex può controllare Chrome locale una sola volta; non deve copiare cookie/token nel terminale o nei log.

# Ciclo GitHub autonomo
Dopo il push:
- `gh run list`/`gh run watch` per il run pertinente;
- su failure leggi solo il job/log fallito;
- correggi la causa concreta;
- massimo un retry identico per stato invariato;
- appena hosted + workflow manuale syntax/dispatch sono PASS, STOP. Non attendere che un Pixel sia fisicamente collegato per considerare valida la CI hosted.

# Non-goal
- niente feature/refactor PH;
- niente bump `version.txt`, release APK o Telegram;
- niente test Pixel automatici da eventi PR;
- niente installazione di runner globali/organization;
- niente browser automation per testare la UI Android;
- niente test distruttivi su dati reali.

# Acceptance
- PR/push host gate verde;
- emulator smoke avviabile e verde;
- full instrumentation nightly/manuale definito e almeno un run manuale PASS;
- runner Fedora repo-level installato/hardenizzato oppure già esistente e validato;
- real-device workflow solo manuale e non distruttivo;
- documentazione breve dei comandi/runbook nel repo, senza duplicare MegaVault.

# Stop
Dopo PASS completa solo questo task con:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 392659`

Output massimo 8 righe: RESULT, hosted gate, emulator smoke, nightly, runner Fedora, real-device workflow, commit/push, blocker.
