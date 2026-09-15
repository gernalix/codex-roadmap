[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=286671 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Portare a CI GitHub Actions i repository Python/automation già identificati:
- `gernalix/codex-usage-monitor`
- `gernalix/github-autosync`
- `gernalix/workflowy-import`
- `gernalix/MegaVault`
- `gernalix/codex-roadmap`

Obiettivo: far eseguire a GitHub i test deterministici che oggi consumano round-trip Codex locali, senza inventare nuove architetture.

# Starting point già verificato
- `codex-usage-monitor` ha già una suite `tests/` ampia e `scripts/secret_scan.sh`.
- `github-autosync` ha `tests/test_github_autosync.py` e regressioni.
- `workflowy-import` ha `test_workflowy_days.py`.
- MegaVault ha già `.github/workflows/validate.yml` che esegue `megavault.py validate`, unittest e clean-tree check: non duplicarlo.
- `codex-roadmap` ha test per `roadmap_guard`/workflow locali: usa quelli esistenti.

# Procedura per repo
Risolvi una volta il `project_id` reale di ciascun repo con MegaVault. Poi, per ciascuno:
1. leggi solo packaging (`pyproject`, requirements se presenti), test runner esistente e `.github/workflows`;
2. se esiste già CI equivalente, non crearne una seconda;
3. usa la versione Python canonica del repo; se non dichiarata, una sola versione stabile coerente col runtime reale, niente matrix;
4. workflow su PR + push default branch, concurrency cancel-in-progress;
5. niente credenziali reali: GitHub API, Telegram, Uptime Kuma, filesystem Codex e rete esterna vanno mockati/fixture quando i test lo consentono;
6. carica output solo su failure.

Specifiche:
- **codex-usage-monitor:** esegui il runner/test suite canonico e secret scan; includi quota notification policy, parsing/archive/publisher già coperti.
- **github-autosync:** usa repository Git temporanei e fixture; copri `no_upstream`, dirty worktree, dedup e notification state senza toccare repo reali.
- **workflowy-import:** testa fixture JSON -> parser/SQLite, idempotenza e deep-link/date-node; se questi ultimi non sono ancora coperti, aggiungi solo test mirati usando fixture sintetiche.
- **MegaVault:** estendi `validate.yml` solo se trovi un gap reale rispetto a validate + unittest + clean-tree; altrimenti lascialo invariato e conta il workflow esistente come PASS.
- **codex-roadmap:** esegui unittest e un check read-only di coerenza roadmap/spiegazioni/prompts; non chiamare `complete` né mutare la roadmap durante CI.

# Ciclo remoto
Per ogni repo modificato:
- gate locale mirato una volta;
- push;
- osserva il singolo run con `gh`;
- failure -> solo log del job fallito -> fix minimo -> retry;
- niente retry identici senza nuova evidenza;
- PASS -> repo chiuso.

# Non-goal
- niente refactor dei parser/monitor;
- niente backfill di dati reali;
- niente accesso a `~/.codex/sessions` in GitHub cloud;
- niente dipendenze CI nuove se stdlib/runner esistente basta;
- niente browser;
- niente modifiche a MegaVault fuori dal necessario per CI/test.

# Acceptance
Tutti i repo attivi hanno CI verde o, per MegaVault, il workflow esistente è verificato sufficiente. I test non richiedono secret di produzione e sono ripetibili.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 286671`

Output massimo 8 righe: RESULT + stato dei cinque repo + eventuale test aggiunto + blocker.
