PROMPT_ID=907314 | PARENT_PROMPT_ID=746193 | project_id=96 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Esegui SOLO il live smoke finale di `gernalix/workflowy-importer`. Tutto il setup, la registrazione progetto e i gate host sono già chiusi da 746193.

# Starting point autoritativo
- 746193: `PROJECT_ID=96`, `HOST_GATES=PASS`, `DRY_RUN=PASS`; unico blocker osservato: `WORKFLOWY_API_KEY` assente;
- checkout canonico già esistente: `/home/daniele/projects/workflowy-importer`, branch `main`, origin `https://github.com/gernalix/workflowy-importer`;
- baseline minima: `47a56a88afdbf6634ec2ea0c7d921a19693662b4`, GitHub CI PASS;
- il repo contiene ora `workflowy-import-smoke`, che in un solo comando crea fixture temporaneo, verifica import/link/todo/NOOP/guard `--replace`/replace e cancella in `finally` tutti i root smoke tracciati;
- il comando non importa file reali dell'utente;
- NON leggere MegaVault, roadmap, README, memoria Codex o sorgenti: nessuna discovery è necessaria.

# Prerequisito fail-fast
Nella prima e unica shell operativa verifica senza stampare il valore:
`test -n "${WORKFLOWY_API_KEY:-}"`
Se manca: `RESULT=BLOCKED`, `BLOCKER=WORKFLOWY_API_KEY missing` e stop immediato. Niente ricerca di secret-ref, filesystem, env file o browser.

# Esecuzione
In UNA shell fail-fast:
1. `cd /home/daniele/projects/workflowy-importer`;
2. verifica solo `main` + origin atteso; `git fetch origin main && git merge --ff-only origin/main`; niente stash/reset;
3. verifica che la baseline minima sia antenata di `HEAD`;
4. riusa `.venv`; esegui solo `.venv/bin/python -m pip install -q -e .`;
5. esegui UNA volta `.venv/bin/workflowy-import-smoke`.
Se lo smoke non stampa `SMOKE=PASS checks=import,links,todo,noop,replace-guard,replace,cleanup`, fermati sul failure esatto: niente retry, debugging, patch o audit.

Solo dopo PASS finalizza UNA volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 907314 --confirm-executed`

# Non-goal / stop
Niente unit test/dry-run già PASS, niente registrazione MegaVault, niente fixture manuale, niente API manuali/curl, niente nodes-export, niente modifiche codice, niente ricerca segreti, niente secondo smoke, niente controlli post-finalizer.

Output massimo 4 righe:
`RESULT=PASS|BLOCKED|FAIL`
`SMOKE=PASS|NOT_RUN|FAIL`
`CLEANUP=PASS|NOT_RUN|FAIL`
`BLOCKER=<none|testo minimo>`
