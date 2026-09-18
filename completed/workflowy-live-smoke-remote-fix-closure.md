PROMPT_ID=856234 | PARENT_PROMPT_ID=418906 | project_id=96 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi il follow-up di 418906: sincronizza il checkout locale di `workflowy-importer` col fix remoto già verificato e riesegui il live smoke reale con la chiave locale. Non rifare audit o setup.

# Starting point autoritativo
- checkout: `/home/daniele/projects/workflowy-importer`, branch `main`, origin `https://github.com/gernalix/workflowy-importer`;
- `418906` ha ottenuto `SMOKE=PASS` e `CLEANUP=PASS` dopo un fix locale, ma quel fix non è stato commit/pushato;
- il remoto ora contiene il fix strutturale:
  - `2ed772399046f339c3d9499f4b9ba2fce49820f3`: lo smoke deriva gli argomenti dal parser CLI reale;
  - `913a76cefa36c190532eb9b37cbd5b7e2631e64b`: test di regressione;
- GitHub CI sul commit `913a76c`: PASS su Python 3.11 e 3.13;
- secret canonico: `~/.config/codex/secrets/workflowy-api-key`;
- non leggere roadmap, README, MegaVault, memoria o sorgenti non coinvolte.

# Esecuzione minima
1. In una sola raccolta iniziale verifica branch/origin e `git status --short`; fai `git fetch -q origin main`. Se esistono diff locali, ispeziona SOLO i path coinvolti dal recovery di 418906 (`src/workflowy_importer/smoke.py`, `src/workflowy_importer/cli.py`, `tests/test_importer.py`) e preserva qualunque lavoro non correlato.
2. Porta `main` al remoto in modo non distruttivo. Se un vecchio workaround locale di 418906 si sovrappone al fix remoto, riconcilialo autonomamente col remoto senza perdere altri cambiamenti. Richiedi che `913a76cefa36c190532eb9b37cbd5b7e2631e64b` sia antenato di HEAD.
3. Esegui SOLO:
   `.venv/bin/python -m unittest tests.test_importer.SmokeHelperTests.test_import_args_inherit_cli_defaults -v`
4. Secret gate fail-closed, senza stampare il valore: se il file esiste deve essere regular, non symlink, non vuoto, owner corrente e mode 600; caricalo in `WORKFLOWY_API_KEY`. Solo se il file non esiste è ammesso un `WORKFLOWY_API_KEY` già presente e non vuoto. Altrimenti BLOCKED.
5. Esegui una volta `.venv/bin/workflowy-import-smoke`. PASS richiede esattamente `SMOKE=PASS checks=import,links,todo,noop,replace-guard,replace,cleanup`.
6. Se il leaf o lo smoke falliscono, diagnostica il minimo failure domain e correggi autonomamente solo codice/test/config pertinenti. Rilancia solo il gate invalidato; se il recovery modifica file tracciati, un solo commit/push finale è obbligatorio prima del PASS.
7. PASS solo con baseline remota presente, test PASS, smoke+cleanup PASS e nessun diff tracciato in-scope necessario rimasto solo localmente. Poi:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 856234 --confirm-executed`

# Non-goal / stop
Niente dry-run/import manuale/API curl, niente audit generale, niente refactor, niente reinstall dipendenze salvo errore concreto dell'entry point, niente controlli post-finalizer.

Output massimo 5 righe:
RESULT=PASS|BLOCKED|FAIL
HEAD=<sha>
UNIT=<PASS|FAIL|NOT_RUN>
SMOKE=<PASS|FAIL|NOT_RUN>
BLOCKER=<none|testo minimo>
