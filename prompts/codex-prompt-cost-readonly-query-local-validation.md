[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=835917 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** il nuovo `codex_prompt_cost_query.py` già pushato su `gernalix/codex-usage-monitor/main`: le lookup di un `PROMPT_ID` devono leggere `task_costs.sqlite` in sola lettura senza riscansionare i rollout né riscrivere DB/CSV. Poi riporta il costo finale completo del prompt precedente `618305`. Correggi solo failure concrete.

# Scope
- Repo `~/projects/codex-usage-monitor`: un solo fetch + pull `--ff-only origin main`; worktree sporco non-task => `BLOCKED`, niente stash/reset.
- Parti solo da `codex_prompt_cost_query.py`, `tests/test_prompt_cost_query.py`; apri `codex_task_costs.py` solo se un test dimostra un'incompatibilità reale.
- Niente monitor Oracle, Telegram, systemd, benchmark generali, PersonalHub o analisi di altre sessioni.
- Non tentare di misurare `835917` stesso: il suo costo finale esisterà solo dopo il suo `task_complete`.

# Gate locale
1. Esegui una volta: `python3 -m unittest tests.test_prompt_cost_query tests.test_task_costs`.
2. Registra `stat` (size + mtime_ns) di `~/.local/share/codex-session-archive/index/task_costs.sqlite`.
3. Esegui una sola query reale read-only:
   `python3 codex_prompt_cost_query.py --prompt-id 706214 --reasoning-effort low --latest --json`
   Deve restituire la riga `task_complete` già nota con `total_tokens=820503`, `uncached_input_tokens=65252`, `tool_call_count=23`; non eseguire `codex_task_costs.py` per questo controllo.
4. Verifica che size + mtime_ns del DB siano identici a prima: la lookup non deve aver scritto nulla.
5. Query `618305` con `--reasoning-effort low --latest --json` e riporta input/cached/uncached/output/reasoning/total, tools, duration e quota_delta. Se e solo se non esiste ancora una riga completa perché l'indice è antecedente al `task_complete`, esegui **una sola** `python3 codex_task_costs.py`, quindi ripeti una volta la query. Nessun altro refresh.
6. Fix minimo + test mirato solo su failure reale; commit/push solo se necessario.

# Stop
PASS appena test + query 706214 immutabile + DB invariato + costo completo 618305 sono verificati. Non misurare il prompt corrente e non aggiungere altre analisi.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 835917 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 835917`

Output ≤6 righe: RESULT; read-only gate; costo 618305; refresh sì/no; fix/SHA; blocker.