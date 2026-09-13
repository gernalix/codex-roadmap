[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=706214 | project_id=51 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** il nuovo supporto per costi Codex per `PROMPT_ID` già pushato su `gernalix/codex-usage-monitor/main`, poi usa i rollout nativi locali per riportare il costo esatto dei prompt `917364`, `463218` e `284731`. Correggi solo failure concrete. Non modificare PersonalHub.

# Perché il dump ChatGPT non aveva i token
Il transcript UI/Markdown copiato da Codex non contiene gli eventi nativi `event_msg/type=token_count`. I contatori esatti sono invece nei rollout `~/.codex/sessions/*.jsonl`. Il vecchio `codex_task_costs.py` usava solo l'ultimo contatore cumulativo dell'intera sessione; quindi più `PROMPT_ID` nella stessa chat non erano separabili correttamente. Il nuovo codice deriva delta per ogni vero `event_msg/user_message` con `PROMPT_ID` e ignora ID solo ecoati da tool/file/output.

# Scope
- Repo `~/projects/codex-usage-monitor`: un solo fetch + pull `--ff-only` di `main`; worktree sporco non-task => `BLOCKED`, niente stash/reset.
- Parti solo da `codex_task_costs.py`, `tests/test_task_costs.py` e, su failure concreta, dai test archive correlati.
- Niente refactor generale, monitor Oracle, notifiche Telegram, systemd o modifiche PH/roadmap oltre al completion guard finale.

# Gate locale
1. Esegui una volta: `python3 -m pytest -q tests/test_task_costs.py tests/test_session_archive.py::SessionArchiveTests::test_diagnostic_bundle_includes_redacted_diagnostic_sources`.
2. Esegui **una sola ricostruzione** reale: `python3 codex_task_costs.py`.
3. Interroga `~/.local/share/codex-session-archive/index/task_costs.sqlite` in read-only e verifica:
   - tabella `prompt_costs` presente;
   - `917364`, `463218`, `284731` presenti come prompt distinti;
   - per ciascuno riporta: `model`, `reasoning_effort`, `duration_seconds`, `tool_call_count`, `input_tokens`, `cached_input_tokens`, `uncached_input_tokens`, `output_tokens`, `reasoning_output_tokens`, `total_tokens`, `quota_delta_points`;
   - nessuna riga spuriosa creata soltanto perché un `PROMPT_ID` compare in output/tool/file.
4. Se uno dei tre ID manca, cerca **solo** il rollout che contiene letteralmente quell'ID e diagnostica l'ordine `user_message`/`token_count`; correggi il parser soltanto se il formato nativo reale dimostra che serve. Nessuna scansione esplorativa ulteriore.
5. Se fai un fix, rilancia soltanto i test mirati e una ricostruzione. Commit/push solo fix necessari.

# Stop
PASS appena test + DB reale + tre costi esatti sono verificati. Non fare benchmark aggiuntivi, confronti tra modelli o altre sessioni.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 706214 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 706214`

Output ≤7 righe: RESULT; causa token mancanti; costo 917364; costo 463218; costo 284731; fix/SHA; blocker.