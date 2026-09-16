[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=483921 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Per **tutti e soli** i repository marcati `[x]` nella checklist di retention, rendere GitHub Actions la sede canonica di **tutto il testing deterministico/sandboxabile ragionevolmente disponibile**, senza duplicare CI già adeguata.

Sorgente autoritativa:
`/home/daniele/projects/MegaVault/ai/repository-retention-checklist.md`

Questo task sostituisce le precedenti campagne CI separate per Python/Android/browser/Fedora/PersonalHub. `codex-usage-monitor` può avere già CI dal cutover precedente e `codex-roadmap` ha già CI: in tal caso verifica il minimo necessario e marca `NOOP_COMPLETE`.

# Inventory minima
1. Leggi la checklist una sola volta; scope = sole righe `- [x] NAME` / `- [X] NAME`.
2. Una sola inventory GitHub owned con visibility/default branch.
3. `[x]` non più esistente => `MISSING_RETAINED_REPO`, blocker solo per quel repo; non ricrearlo.
4. `[ ]` o assente => fuori scope assoluto.
5. Per ogni `[x]` leggi solo manifest/build/packaging, directory test, `.github/workflows` ed entrypoint/config direttamente necessari a capire come testarlo. Niente audit generale, history, issue o README salvo blocker concreto.

# Principio vincolante
Un check va su GitHub Actions se è deterministico o stabilizzabile con fixture/mock e può girare senza dati personali, hardware fisico, account/sessioni reali, secret di produzione o infrastruttura live.

Non lasciare locale un test sandboxabile solo per comodità.

Copri quando applicabile:
- unit/integration/regression test;
- compile/build/lint/typecheck/static analysis;
- parser/DB con fixture o DB temporanei;
- Android build/unit/lint + emulator/instrumentation sandboxabile;
- browser/extension con Chromium headless + fixture locali;
- HTTP/network con mock/local server;
- shell/systemd/YAML/Compose/nginx/config validation;
- backup/restore esclusivamente in temp dir.

# Routing per tipologia — niente task separati
## Android / PersonalHub
- Riusa task Gradle e test esistenti; una sola JDK/API coerente, niente matrix esplorative.
- PUBLIC: host gate PR+push; emulator smoke su push/main o manuale; instrumentation più pesante manuale/schedule solo se utile.
- PRIVATE: host gate veloce automatico; emulator/instrumentation pesanti definiti comunque in Actions ma preferibilmente `workflow_dispatch` per contenere i minuti. Riusa un self-hosted repo-specific già sicuro se esiste; non creare runner general-purpose.
- Pixel/TCL restano locali solo perché hardware fisico.

## Python / script / automazioni
- Riusa unittest/pytest esistenti, temp repo/DB/filesystem e mock per GitHub/Telegram/Kuma/rete quando necessari.
- Una sola versione Python coerente col runtime; niente test contro account o servizi reali.

## Browser / downloader / extension
- Chromium/Playwright headless con fixture HTML e server HTTP locali/mock.
- Niente profili, cookie, account o siti live se il comportamento è riproducibile con fixture.
- Browser autenticato reale resta locale solo quando una failure concreta non è riproducibile in sandbox.

## Fedora / servizi / backup
- Python/shell syntax e test, `bash -n`, shellcheck solo se già compatibile, parse/validation di systemd/YAML/Compose/nginx tramite fixture/temp dir.
- Backup→restore solo in temp dir; mai mount/dischi reali, SSH, VM, restart host o secret di produzione.

# Strategia visibility/costo
- **PUBLIC:** GitHub-hosted standard; gate veloci automatici PR+push, job più costosi solo con frequenza utile.
- **PRIVATE:** anche qui tutto il testing sandboxabile deve essere definito in Actions; gate veloci automatici, job pesanti preferibilmente manuali. Visibility cambia trigger/frequenza, non la copertura disponibile.

# Efficienza per repo
1. Se CI esistente copre già tutto: `NOOP_COMPLETE` e passa oltre.
2. Altrimenti modifica il minimo, riusando test/comandi esistenti.
3. Aggiungi nuovi test solo per comportamento esistente importante che altrimenti non sarebbe verificabile.
4. Path filter docs-only, concurrency/cancel-in-progress, permissions minime, cache solo utile, artifact failure-only con retention breve.
5. Preflight locale minimo -> push -> singolo run GitHub canonico. Failure: solo job/log fallito -> fix minimo -> nuovo run. Vietati retry identici e audit post-PASS.
6. Chiudi un repo appena raggiunge COMPLETE; non riaprirlo nella stessa sessione.

Se i repo `[x]` sono numerosi, processali serialmente ma senza rileggere checklist/inventory globale: mantieni la stessa inventory in memoria e apri solo il prossimo repo. Non fare discovery trasversale.

# Esclusioni locali ammesse
Solo test che richiedono realmente hardware fisico, account/browser autenticato reale, secret di produzione, VM/host/dischi/rete live non simulabili o comportamento umano non riducibile a fixture affidabile. Per ogni esclusione registra una motivazione tecnica concreta.

# Report finale
Crea/aggiorna `/home/daniele/projects/MegaVault/ai/repository-ci-coverage.md` con una riga per ogni `[x]`:
- `COMPLETE|NOOP_COMPLETE|PARTIAL_BLOCKED`;
- workflow/gate principali;
- eventuale test rimasto locale + motivo tecnico.

Non duplicare dettagli dei log CI.

# Non-goal
Niente refactor/cleanup/modernizzazione, feature, release, dependency upgrade generale, security audit, history rewrite, cambio visibility, test live quando fixture/headless bastano, shared action cross-repo salvo beneficio concreto già evidente.

# Acceptance
PASS solo se ogni repo `[x]` esistente ha tutto il testing deterministico/sandboxabile ragionevolmente disponibile in GitHub Actions oppure un blocker tecnico esplicito; workflow modificati verdi; nessuna CI duplicata; ciò che resta locale richiede davvero risorse non sandboxabili; report finale completo.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483921 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483921`

Output massimo 7 righe: RESULT, retained count, NOOP_COMPLETE, changed, blocked, coverage report, blocker eventuale.