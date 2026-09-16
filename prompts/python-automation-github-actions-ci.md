[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=286671 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Aggiungere/normalizzare CI GitHub Actions **solo** per gli eventuali target ancora presenti dopo la retention review:
- `gernalix/github-autosync`
- `gernalix/workflowy-import`

Fuori scope perché già coperti altrove:
- `codex-usage-monitor`: CI incorporata nel cutover `PROMPT_ID=472913`;
- `codex-roadmap`: CI aggiunta direttamente da ChatGPT;
- MegaVault: CI già sufficiente.

# Gate retention
Per ciascun target verifica una sola volta esistenza GitHub + riga matrice. Repo non esistente o `RETIRE` => `SKIPPED_DELETED`, senza ricrearlo, clonarlo o investigarlo. Se entrambi sono assenti/RETIRE, completa subito il task come SKIPPED.

# Routing minimo
Per ogni target rimasto leggi una volta: riga matrice visibility, packaging/runtime, test esistenti, `.github/workflows`; niente README/source audit generale. Se CI equivalente esiste, riusala e non duplicare.

# CI
Una sola Python version coerente col runtime; PR + push default branch; path filter docs-only; concurrency cancel-in-progress; permissions minime; nessun secret/rete/account reale. PUBLIC: hosted standard. PRIVATE: solo suite deterministica veloce hosted, niente schedule/job pesanti e nessun nuovo self-hosted runner.

Copertura richiesta solo per repo rimasti:
- `github-autosync`: repo Git temporanei; `no_upstream`, dirty worktree, dedup repository e stato notifiche duplicate.
- `workflowy-import`: fixture JSON -> parser/SQLite, idempotenza e deep-link/date-node; aggiungi al massimo le regressioni mancanti necessarie al comportamento esistente.

# Ciclo
Preflight minimo -> push -> singolo run GitHub canonico. Failure: leggi solo job/test fallito, fix minimo, leaf test e nuovo run; niente retry identici o audit post-PASS.

# Non-goal
Refactor, cleanup, browser, dati reali, nuove feature, backfill o discovery di altri repo.

# Acceptance
Ogni repo rimasto in scope ha CI verde e ripetibile; repo eliminati/RETIRE sono SKIPPED senza essere ricreati.

# Stop
Dopo PASS/SKIPPED:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671`

Output massimo 5 righe: RESULT, github-autosync, workflowy-import, test aggiunti, blocker.