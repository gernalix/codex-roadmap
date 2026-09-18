PROMPT_ID=693572 | PARENT_PROMPT_ID=746193 | project_id=96 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Esegui SOLO il live smoke finale di `gernalix/workflowy-importer`. Tutto il setup, la registrazione progetto e i gate host sono già chiusi da 746193.

# Starting point autoritativo
- 746193: `PROJECT_ID=96`, `HOST_GATES=PASS`, `DRY_RUN=PASS`;
- checkout canonico: `/home/daniele/projects/workflowy-importer`, branch `main`, origin `https://github.com/gernalix/workflowy-importer`;
- baseline minima: `8af418720e6a6d35f507d29deefec8a8fdbe9dd1`, GitHub CI PASS;
- secret file canonico: `~/.config/codex/secrets/workflowy-api-key`;
- `workflowy-import-smoke` crea solo dati temporanei, verifica import/link/todo/NOOP/guard `--replace`/replace e ripulisce i root smoke in `finally`;
- NON leggere MegaVault, roadmap, README, memoria Codex o sorgenti: nessuna discovery è necessaria.

# Secret gate fail-closed
Nella prima shell, senza stampare mai il valore della chiave:
1. `KEY_FILE="$HOME/.config/codex/secrets/workflowy-api-key"`.
2. Se `$KEY_FILE` ESISTE:
   - deve essere un file regolare, non symlink, non vuoto;
   - owner UID deve essere `$(id -u)`;
   - permessi devono essere ESATTAMENTE `600`;
   - se una verifica fallisce: `RESULT=BLOCKED`, indica solo il motivo strutturale e STOP. NON usare fallback;
   - se passa: carica il contenuto con `WORKFLOWY_API_KEY="$(<"$KEY_FILE")"`, verifica solo `test -n "$WORKFLOWY_API_KEY"`, quindi `export WORKFLOWY_API_KEY`. Mai `cat`, `echo`, `printf` o tracing del valore.
3. SOLO SE `$KEY_FILE` NON ESISTE, fallback ammesso: usa esclusivamente un `WORKFLOWY_API_KEY` già presente nell'ambiente e non vuoto.
4. Se mancano sia file sia env: `RESULT=BLOCKED`, `BLOCKER=Workflowy API key missing`, STOP.
5. Vietato cercare la chiave altrove, leggere secret-ref, scandire filesystem/env file, aprire browser o scrivere la chiave in Git/log/report.

# Esecuzione
Dopo il secret gate, in UNA shell fail-fast:
1. `cd /home/daniele/projects/workflowy-importer`;
2. verifica solo `main` + origin atteso; `git fetch origin main && git merge --ff-only origin/main`; niente stash/reset;
3. verifica che la baseline minima sia antenata di `HEAD`;
4. riusa `.venv`; esegui solo `.venv/bin/python -m pip install -q -e .`;
5. esegui UNA volta `.venv/bin/workflowy-import-smoke`.
Se lo smoke non stampa esattamente `SMOKE=PASS checks=import,links,todo,noop,replace-guard,replace,cleanup`, fermati sul failure esatto: niente retry, debugging, patch o audit.

Solo dopo PASS finalizza UNA volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 693572 --confirm-executed`

# Non-goal / stop
Niente unit test/dry-run già PASS, niente registrazione MegaVault, niente fixture manuale, niente API manuali/curl, niente nodes-export, niente modifiche codice, niente ricerca segreti, niente secondo smoke, niente controlli post-finalizer.

Output massimo 4 righe:
`RESULT=PASS|BLOCKED|FAIL`
`SMOKE=PASS|NOT_RUN|FAIL`
`CLEANUP=PASS|NOT_RUN|FAIL`
`BLOCKER=<none|testo minimo>`
