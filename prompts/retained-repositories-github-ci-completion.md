PROMPT_ID=483921 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD

# Goal
Per tutti i repository **esistenti e non RETIRE** già consegnati dall'handoff MegaVault, più il repository `adb-device-keeper` creato dopo quell'audit, rendere GitHub Actions la sede canonica di **tutto il testing deterministico/sandboxabile ragionevolmente disponibile**, senza duplicare CI già adeguata.

Sorgente autoritativa principale:
`/home/daniele/projects/MegaVault/ai/repository-ci-handoff.json`

Il file corrente usa `schema_version=2`; usa sempre la versione presente nel checkout sincronizzato al momento dell'esecuzione perché task precedenti possono aver aggiornato singole entry di pubblicabilità. Non rifare `gh repo list`, non rivalutare PUBLIC/PRIVATE e non riaprire l'audit sicurezza.

Supplemento post-handoff già verificato:
- `adb-device-keeper`, visibility `PRIVATE`, default branch `main`;
- il repo esiste già e ha CI deterministica; se al momento del task la CI copre già tutto, marcarlo `NOOP_COMPLETE` senza nuova implementazione.

`codex-usage-monitor`, `codex-roadmap`, `fedora-system-monitor` e altri repo toccati dai task precedenti possono avere CI già completa: verifica il minimo necessario e marca `NOOP_COMPLETE` quando appropriato.

# Gate handoff
1. Leggi e parsea `repository-ci-handoff.json` una sola volta.
2. Richiedi `schema_version=2` e una lista `repositories` valida/non vuota. Non bloccare in base a uno specifico `generated_by_prompt_id`: è metadata storico e non definisce lo scope operativo corrente.
3. Scope = esattamente le entry `repositories` dell'handoff + `adb-device-keeper` se non già presente; deduplica per `name`.
4. Se una push/fetch mirata dimostra che un repo dello scope non esiste più, `MISSING_RETAINED_REPO` solo per quel repo; non fare inventory globale e non ricrearlo.
5. Per ogni repo leggi solo manifest/build/packaging, directory test, `.github/workflows` ed entrypoint/config direttamente necessari a capire come testarlo. Niente audit generale, history, issue o README salvo blocker concreto.

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
- Per eseguire test esistenti usa il comando/runner già dichiarato dal repo o dal workflow CI; non inventare una nuova invocation che cambi cwd, `PYTHONPATH` o import semantics. Se manca un comando canonico, ricavalo dai test/packaging una volta e mantienilo stabile.

## Browser / downloader / extension
- Chromium/Playwright headless con fixture HTML e server HTTP locali/mock.
- Niente profili, cookie, account o siti live se il comportamento è riproducibile con fixture.
- Browser autenticato reale resta locale solo quando una failure concreta non è riproducibile in sandbox.

## Fedora / servizi / backup
- Python/shell syntax e test, `bash -n`, shellcheck solo se già compatibile, parse/validation di systemd/YAML/Compose/nginx tramite fixture/temp dir.
- Backup→restore solo in temp dir; mai mount/dischi reali, SSH, VM, restart host o secret di produzione.

# Strategia visibility/costo
Usa `visibility` dell'handoff e la visibility verificata sopra per `adb-device-keeper`, senza query ridondanti:
- **PUBLIC:** GitHub-hosted standard; gate veloci automatici PR+push, job più costosi solo con frequenza utile.
- **PRIVATE:** anche qui tutto il testing sandboxabile deve essere definito in Actions; gate veloci automatici, job pesanti preferibilmente manuali. Visibility cambia trigger/frequenza, non la copertura disponibile.

# Efficienza per repo
1. Se CI esistente copre già tutto: `NOOP_COMPLETE` e passa oltre.
2. Altrimenti modifica il minimo, riusando test/comandi esistenti.
3. Aggiungi nuovi test solo per comportamento esistente importante che altrimenti non sarebbe verificabile.
4. Path filter docs-only, concurrency/cancel-in-progress, permissions minime, cache solo utile, artifact failure-only con retention breve.
5. Preflight locale minimo -> push -> singolo run GitHub canonico. Failure: solo job/log fallito -> fix minimo -> nuovo run. Vietati retry identici e audit post-PASS.
6. Chiudi un repo appena raggiunge COMPLETE; non riaprirlo nella stessa sessione.

Mantieni in memoria l'handoff e processa i repo serialmente; nessuna discovery trasversale, nessuna rilettura globale tra un repo e l'altro.

# Esclusioni locali ammesse
Solo test che richiedono realmente hardware fisico, account/browser autenticato reale, secret di produzione, VM/host/dischi/rete live non simulabili o comportamento umano non riducibile a fixture affidabile. Per ogni esclusione registra una motivazione tecnica concreta.

# Report finale JSON
Crea/aggiorna `/home/daniele/projects/MegaVault/ai/repository-ci-coverage.json` con `schema_version: 1`, `generated_by_prompt_id: 483921`, `generated_at_utc` e una entry per ogni repo dello scope effettivo (handoff + supplemento post-handoff) con:
- `status`: `COMPLETE|NOOP_COMPLETE|PARTIAL_BLOCKED`;
- workflow/gate principali;
- eventuale test rimasto locale + motivo tecnico.

Ordina per `name`. Non duplicare dettagli dei log CI e non creare un nuovo Markdown di report in MegaVault.

# Non-goal
Niente refactor/cleanup/modernizzazione, feature, release, dependency upgrade generale, security audit, history rewrite, cambio visibility, inventory globale, test live quando fixture/headless bastano, shared action cross-repo salvo beneficio concreto già evidente.

# Acceptance
PASS solo se ogni repo dello scope ancora esistente ha tutto il testing deterministico/sandboxabile ragionevolmente disponibile in GitHub Actions oppure un blocker tecnico esplicito; workflow modificati verdi; nessuna CI duplicata; ciò che resta locale richiede davvero risorse non sandboxabili; report JSON parseabile e completo.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 483921 --confirm-executed`

Non fare dry-run separati né controlli Git equivalenti dopo finalizzazione.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `RESULT`, `RETAINED`, `NOOP_COMPLETE`, `CHANGED`, `BLOCKED`, `COVERAGE_REPORT`, `BLOCKER`.
