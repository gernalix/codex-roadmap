[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=618305 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** gli ultimi fix già pushati su `gernalix/codex-usage-monitor/main` per le metriche per-`PROMPT_ID`: confine a `task_complete`, stato `completion_state`, esclusione dei prompt ancora `eof_incomplete` dalle query esatte e filtri `--model/--reasoning-effort/--latest`. Poi ricostruisci una volta i dati reali e riporta il costo finale di `706214`. Correggi solo failure concrete.

# Baseline già verificata — NON ripetere analisi rollout
Il gate `706214` ha già provato il parsing nativo e questi token, che **non devono cambiare** per effetto del nuovo confine temporale:
- `917364` latest low: input=2298676 cached=2204160 uncached=94516 output=8781 reasoning=1246 total=2307457 tools=42; la vecchia duration 1246.751 s includeva idle.
- `463218` low: input=616639 cached=550528 uncached=66111 output=1935 reasoning=131 total=618574 tools=11; la vecchia duration 608.35 s includeva idle.
- `284731` low: input=475256 cached=456576 uncached=18680 output=1438 reasoning=34 total=476694 tools=8; vecchia duration 59.95 s.
`706214` non poteva conoscere il proprio costo finale mentre era ancora in esecuzione: ora il rollout è concluso e deve risultare `task_complete`.

# Scope
- Repo `~/projects/codex-usage-monitor`: un solo fetch/pull `--ff-only` di `main`; worktree sporco non-task => BLOCKED, niente stash/reset.
- Parti solo da `codex_task_costs.py`, `tests/test_task_costs.py`; niente monitor Oracle, Telegram, systemd, altri repo o audit.
- Non aprire rollout manualmente salvo failure concreta del parser.

# Gate locale
1. Esegui una volta `python3 -m unittest tests.test_task_costs`.
2. Esegui una sola ricostruzione reale: `python3 codex_task_costs.py`.
3. Interroga `task_costs.sqlite` in read-only, senza rilanciare il parser, e verifica:
   - latest `917364` con `reasoning_effort='low'`, `463218` e `284731` hanno `completion_state='task_complete'` e gli stessi token/tools della baseline sopra;
   - `duration_seconds` di `917364 low` è <1246.751 e quella di `463218` è <608.35, perché l'idle post-completion non è più contato;
   - eventuali righe `eof_incomplete` esistono solo come diagnostica e non vengono scelte da `select_prompt_rows` senza opt-in;
   - `706214` latest completed è presente: riporta model, reasoning, duration, tools, input, cached, uncached, output, reasoning tokens, total e quota delta osservata.
4. Se fallisce, fix minimo solo nei due file indicati; rilancia solo unittest + una ricostruzione. Commit/push solo fix necessari.

# Stop
PASS appena test + ricostruzione + invarianti token + costo finale `706214` sono verdi. Niente benchmark, altri prompt o confronti.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 618305 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 618305`

Output ≤6 righe: RESULT; duration corrette; token invarianti; costo 706214; fix/SHA; blocker.