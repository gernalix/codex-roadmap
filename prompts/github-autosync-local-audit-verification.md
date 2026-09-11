# github-autosync-local-audit-verification

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=417806 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Verificare localmente i fix già implementati sul remoto `gernalix/github-autosync` dopo il task 684217. Il codice è già stato corretto: **non rifare discovery, redesign o reimplementazione**. Correggi soltanto eventuali failure concrete di test/runtime.

Durante l'esecuzione non inviare progress report narrativi: usa direttamente i tool. Scrivi testo intermedio solo se emerge un blocker che richiede una decisione dell'utente; altrimenti produci soltanto il report finale.

# Stato remoto già preparato
Sul `main` di `gernalix/github-autosync` sono già presenti:

- commit `262598ffd4799d3f05ad1359f1fc46a698c24d32`: gli 11 repo con fingerprint GitHub invariato non vengono più saltati ciecamente; ricevono un audit locale senza fetch che rileva dirty/ahead/diverged e permette il normale auto-push ahead-only;
- nello stesso commit, l'upstream repair comunica al chiamante il fetch già eseguito per evitare il fetch immediatamente duplicato;
- clone di un worktree canonico MegaVault mancante ora usa il path canonico, non crea automaticamente un duplicato in `~/projects/<repo>`;
- `sync_changed_repo(..., dry_run=True)` con upstream mancante usa `show-ref`/`git ls-remote` e non esegue `git fetch` o `branch --set-upstream-to`;
- nuovo contatore JSON `audited_unchanged`, distinto da `skipped_unchanged`;
- `tests/test_github_autosync_regressions.py`, finalizzato nel commit `1a210a57383bbafda9a8545f6018846bda55e2a9`, copre local audit/auto-push path, dirty invariato, canonical clone, dry-run senza fetch e dedup del fetch di upstream repair;
- commit `f5d62c0d9e1fda9c29863a62ee169552edd12505`: README allineato alla allowlist rigida e al nuovo comportamento.

Non ispezionare altri repository per capire questi fix.

# Esecuzione
1. Repo Fedora: `/home/daniele/projects/github-autosync`.
   - Se clean, `git pull --ff-only origin main`.
   - Se dirty/diverged, niente stash/reset/force: riporta BLOCKED e STOP.
2. Esegui una sola suite mirata completa:
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
3. Se fallisce, correggi **solo** la failure concreta in `autosync_core.py` o nei test direttamente coinvolti, poi rilancia la suite una sola volta.
4. Se passa, avvia **una sola** esecuzione controllata di `github-autosync.service` e leggi solo il JSON finale del journal.
5. Verifica che il runtime:
   - usi esattamente gli 11 repo allowlisted;
   - esponga `audited_unchanged`;
   - non torni al blind skip: per checkout invariati esistenti, l'audit locale deve essere contabilizzato prima dello `skipped_unchanged`;
   - non generi issue/deferred falsi;
   - mantenga Telegram deduplicato.
   Non creare commit fittizi nei repo reali per provare l'auto-push: la copertura unit test è sufficiente.

# Scope / stop
Niente refactor, cleanup, inventory generale, MegaVault edit o modifiche agli altri repo salvo una failure concreta che dimostri che il codice remoto preparato è incompatibile col runtime. Nessun secondo giro di verifiche equivalenti.

PASS quando suite + singolo runtime check sono verdi. Se hai dovuto correggere codice, commit/push normale; altrimenti nessun commit artificiale. Finalizza questo task con `roadmap_guard` e STOP.

Output finale conciso: `PROMPT_ID`, `RESULT`, test count/result, runtime JSON essenziale (`managed_repos`, `audited_unchanged`, `skipped_unchanged`, `auto_pushed`, `issues`, `deferred`, `telegram`), eventuale SHA correttivo, blocker.
