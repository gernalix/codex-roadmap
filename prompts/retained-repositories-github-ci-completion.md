[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=483921 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Per **tutti e soli** i repository che l'utente ha marcato `[x]` nella checklist di retention, rendere GitHub Actions la sede canonica di **tutto il testing deterministico e sandboxabile** ancora mancante, senza duplicare workflow/test già adeguati.

Sorgente autoritativa:
`/home/daniele/projects/MegaVault/ai/repository-retention-checklist.md`

Questo è un task finale di copertura: i task CI precedenti possono aver già sistemato molti repo. Qui devi colmare soltanto i buchi residui.

# Inventory minima
1. Leggi la checklist una sola volta e considera in scope solo righe `- [x] NAME` / `- [X] NAME`.
2. Fai una sola inventory GitHub dei repo owned ancora esistenti con visibility/default branch.
3. Repo `[x]` non più esistente => segnala `MISSING_RETAINED_REPO` e BLOCKED per quel repo, senza ricrearlo.
4. Repo `[ ]` o assente dalla checklist => fuori scope assoluto.

Per ogni repo `[x]`, leggi soltanto ciò che serve a classificare test/runtime e CI esistente: manifest/packaging/build file, directory test, `.github/workflows`, entrypoint/config direttamente testabili. Niente audit generale di codebase, README/storia/issue salvo blocker concreto.

# Regola di delega a GitHub
Ogni test/check deve finire in GitHub Actions se è:
- deterministico o ragionevolmente stabilizzabile con fixture/mock;
- eseguibile in sandbox/container/runner senza dati personali reali;
- indipendente da hardware fisico, sessioni/account reali, secret di produzione o infrastruttura live.

Esempi pertinenti quando presenti:
- unit/integration test;
- compile/build/lint/typecheck/static analysis;
- parser/DB con fixture/temp DB;
- Android build/unit/lint + emulator/instrumentation sandboxabile;
- browser/extension con Chromium headless e fixture locali;
- HTTP/network con mock/local server;
- shell/systemd/YAML/Compose/nginx/config validation;
- backup/restore solo in temp dir;
- regression test per bug già coperti da fixture ripetibili.

NON lasciare un test deterministico/sandboxabile come "solo locale" se può girare su GitHub senza dipendenze reali.

# Cosa resta locale
Restano fuori GitHub soltanto test che richiedono realmente:
- Pixel/TCL o altro hardware fisico;
- account/browser autenticato reale;
- secret/credential di produzione;
- VM/host/dischi/rete/infrastruttura live non simulabile;
- comportamento umano/non deterministico non riducibile a fixture affidabile.

Per ogni esclusione registra una motivazione tecnica concreta; niente esclusioni per comodità.

# Strategia visibility/costo
- **PUBLIC:** usa GitHub-hosted standard; automatizza PR/push per gate veloci e aggiungi schedule/manuale solo quando il valore giustifica il costo/tempo. Emulator/browser/integration deterministici possono essere hosted.
- **PRIVATE:** anche qui GitHub Actions deve contenere tutto il testing deterministico/sandboxabile; gate veloci automatici, job pesanti preferibilmente `workflow_dispatch` se consumerebbero minuti inutilmente. Riusa self-hosted repo-specific già esistenti solo se sicuri; non crearne di general-purpose.

Visibility non giustifica lasciare test deterministici esclusivamente locali: può cambiare solo trigger/runner/frequenza.

# Efficienza
Per ogni repo:
1. se CI esistente copre già tutto il testabile, `NOOP_COMPLETE` e passa oltre;
2. altrimenti aggiungi/modifica il minimo indispensabile, riusando test e comandi esistenti;
3. niente nuovi test se non servono a rendere verificabile un comportamento già esistente e importante;
4. niente matrix esplorative: una sola versione runtime/JDK/API coerente col repo;
5. path filters docs-only, concurrency/cancel-in-progress, permissions minime, cache solo utile, artifact solo failure e retention breve;
6. nessun secret reale nei workflow.

Non creare una shared action cross-repo salvo evidenza che riduca davvero duplicazione senza aumentare coupling.

# Verifica
Non duplicare localmente l'intera CI. Preflight/syntax minimo -> push -> usa il run GitHub come gate canonico.
Per repo modificato: osserva il singolo run pertinente; failure -> leggi solo job/log fallito -> fix minimo -> nuovo run. Niente retry identici o audit post-PASS.

Crea/aggiorna in MegaVault un report conciso `ai/repository-ci-coverage.md` con una riga per ogni repo `[x]`:
- `COMPLETE|PARTIAL_BLOCKED|NOOP_COMPLETE`;
- workflow/gate principali;
- eventuale test rimasto locale + motivo tecnico.

# Non-goal
Niente refactor/cleanup/modernizzazione, feature, release, dependency upgrade generale, security audit, history rewrite, pubblicazione/cambio visibility, test live contro account reali o browser GUI se fixture/headless bastano.

# Acceptance
PASS solo se per ogni repo `[x]` ancora esistente:
- tutto il testing deterministico/sandboxabile ragionevolmente disponibile è eseguito da GitHub Actions oppure esiste blocker tecnico esplicito;
- workflow duplicati sono evitati;
- i workflow modificati sono verdi;
- ciò che resta locale richiede davvero risorse non sandboxabili;
- `repository-ci-coverage.md` rende visibile la copertura finale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483921 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483921`

Output massimo 7 righe: RESULT, retained count, NOOP_COMPLETE count, changed count, blocked count, coverage report, blocker eventuale.