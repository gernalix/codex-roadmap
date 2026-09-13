[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=731608 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** il nuovo refresh mirato di `codex_prompt_cost_query.py` già pushato su `gernalix/codex-usage-monitor/main`: una lookup normale deve restare read-only; quando un prompt appena concluso manca dall'indice, `--refresh-prompt --latest` deve trovare e ricalcolare soltanto il rollout più recente che contiene davvero quel `PROMPT_ID`, senza eseguire il rebuild globale. Poi riporta il costo finale completo del precedente `835917`.

# Scope
- Repo `~/projects/codex-usage-monitor`: un solo fetch + pull `--ff-only origin main`; worktree sporco non-task => `BLOCKED`, niente stash/reset.
- Parti solo da `codex_prompt_cost_query.py` e `tests/test_prompt_cost_query.py`; apri `codex_task_costs.py` solo su incompatibilità concreta.
- Vietato eseguire `python3 codex_task_costs.py` in questo gate: il punto è provare che non serve più per un singolo prompt appena concluso.
- Niente monitor Oracle, Telegram, systemd, benchmark generali, PersonalHub o altre sessioni.
- Non tentare di misurare `731608` stesso: il suo costo finale esisterà solo dopo il suo `task_complete`.

# Gate locale
1. Esegui una volta: `python3 -m unittest tests.test_prompt_cost_query`.
2. Sul DB reale registra: `session_costs` count, size/mtime di `task_costs.sqlite`, e mtime di `task_costs.csv`.
3. Query read-only di controllo:
   `python3 codex_prompt_cost_query.py --prompt-id 618305 --reasoning-effort low --latest --json`
   Deve restituire `task_complete total_tokens=604502 uncached_input_tokens=39194 tool_call_count=12`; size/mtime DB invariati.
4. Prova `835917` normalmente con `--reasoning-effort low --latest --json`. Se è già completo, riporta il costo e NON fare refresh. Se manca, esegui **una sola volta**:
   `python3 codex_prompt_cost_query.py --prompt-id 835917 --reasoning-effort low --latest --refresh-prompt --json`
   Il refresh deve dichiarare `rollouts=1`; non deve invocare il builder globale.
5. Dopo eventuale refresh, verifica che `session_costs` count e `task_costs.csv` mtime siano invariati; `prompt_costs`/`prompt_costs.csv` possono cambiare. La riga `835917` deve essere `task_complete` e completa.
6. Fix minimo + test mirato solo su failure reale; commit/push solo se necessario.

# Stop
PASS appena test + lookup read-only + eventuale refresh mirato + costo completo `835917` sono verificati. Nessun broad suite, nessun rebuild globale e nessun ulteriore audit.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 731608 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 731608`

Output ≤6 righe: RESULT; read-only gate; targeted refresh sì/no; costo 835917; fix/SHA; blocker.