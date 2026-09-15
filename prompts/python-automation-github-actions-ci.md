[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=286671 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Aggiungere/normalizzare CI GitHub Actions SOLO per:
- `gernalix/codex-usage-monitor`
- `gernalix/github-autosync`
- `gernalix/workflowy-import`
- `gernalix/codex-roadmap`

**MegaVault è fuori scope:** il workflow esistente `validate.yml` già copre validate + unittest + clean-tree; non rileggerlo né modificarlo salvo blocker diretto di questo task.

# Routing minimo
Per ogni target risolvi una volta project_id/stato e leggi soltanto:
- riga relativa nella matrice `/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`;
- packaging/runtime declaration;
- test runner/test files esistenti;
- `.github/workflows`.

Niente README/source audit generale.

# CI
Se esiste CI equivalente, riusala e non duplicare.
Usa una sola Python version coerente col runtime, niente matrix. PR + push default branch, path filters per evitare docs-only, concurrency cancel-in-progress, output/artifact solo su failure e retention breve.

Visibility/costo:
- PUBLIC: standard GitHub-hosted automatico;
- PRIVATE: mantieni solo suite veloce deterministica su hosted, senza schedule/job pesanti; se esiste già un runner repo-level sicuro puoi riusarlo, ma NON installarne uno nuovo solo per questi test piccoli.

Nessun secret reale: API GitHub/Telegram/Kuma/filesystem Codex/rete esterna devono essere mock/fixture quando necessari.

# Copertura minima per repo
- `codex-usage-monitor`: usa il runner canonico risultante dal task precedente; parsing/archive/publisher/quota/Kuma + secret scan esistente, senza inventare un secondo runner.
- `github-autosync`: test esistenti con repo Git temporanei; `no_upstream`, dirty worktree, dedup, notification state.
- `workflowy-import`: fixture JSON -> parser/SQLite, idempotenza, deep-link/date-node; aggiungi test solo se il comportamento esiste ma manca una regressione mirata.
- `codex-roadmap`: unittest + check read-only 1:1 roadmap/spiegazioni/prompts; mai `complete`/mutation in CI.

# Ciclo efficiente
Niente duplicazione locale dell'intera suite: syntax/preflight minimo -> push -> singolo run GitHub canonico. `gh run watch --exit-status` una volta; su failure leggi solo il job fallito, fix minimo, nuovo run. Nessun retry identico o audit post-PASS.

# Non-goal
Niente refactor parser/monitor, backfill dati, browser, accesso a `~/.codex/sessions`, nuove dipendenze CI se stdlib/runner esistente basta.

# Acceptance
I quattro repo attivi hanno CI verde e ripetibile, senza production secrets e senza workflow duplicati; repo archived sono SKIPPED.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671`

Output massimo 7 righe: RESULT + una riga per repo + test mirato aggiunto eventuale + blocker.