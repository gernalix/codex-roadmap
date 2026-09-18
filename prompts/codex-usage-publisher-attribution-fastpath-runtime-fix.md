PROMPT_ID=371237 | PARENT_PROMPT_ID=538642 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Distribuisci sul Fedora reale il fix già presente su `gernalix/codex-usage-monitor/main` e completa SOLO le verifiche runtime rimaste incompiute dopo il BLOCKED di 538642: attribuzione corretta di PROMPT_ID=918274 e fast-path `noop_unchanged_sources`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`;
- baseline minima obbligatoria: `464fc49bced4499669758bcbb9ad78a6ebb057f7`;
- 538642 si è fermato prima del deploy perché `test_native_user_message_accepts_markdown_escaped_prompt_id` falliva;
- la root cause è già corretta nel remoto: il parser costi normalizza un singolo `\_` Markdown-escaped;
- runtime canonico: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- evidenza da riconciliare: sessione `01a0b571-34c1-77a0-873b-79aab0d23acf`, cycle `00a0f021a74b7246cbec3109`, PROMPT_ID=918274;
- repo dati locale: `/home/daniele/projects/codex-usage`.

# Esecuzione minima
1. In una sola shell call fail-fast:
   - richiedi `main`;
   - `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`;
   - richiedi `HEAD=origin/main` e baseline `464fc49bced4499669758bcbb9ad78a6ebb057f7` antenata;
   - esegui SOLO:
     `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher tests.test_publication_semantic_backfill tests.test_usage_publisher_regressions tests.test_task_costs`.
2. Se il checkout/runtime locale è la causa di un failure, correggi solo quella causa locale e rilancia il leaf gate. Non modificare source Python: un failure source ancora presente sulla baseline richiesta è terminale per questo task e va registrato come FAIL con evidenza compatta.
3. Dopo PASS dei test:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
4. In una sola shell call:
   - misura un primo run di `/home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`;
   - verifica in `/home/daniele/projects/codex-usage` che il cycle `00a0f021a74b7246cbec3109` risulti sotto PROMPT_ID=918274 e che `prompts/918274/metrics.json` riporti la stessa sessione/cycle;
   - misura subito un secondo run consecutivo: deve restituire `status=noop_unchanged_sources`.
5. Verifica una sola volta che `codex-usage-publisher.timer` sia enabled e che l'ultimo risultato della service non sia failed.
6. PASS:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 371237 --confirm-executed`.
   Per un terminale BLOCKED/FAIL usa una sola volta `roadmap_result.py` con lo stesso PROMPT_ID e l'esito reale.

# Acceptance
PASS solo se:
- test mirati PASS;
- deploy runtime PASS sulla baseline richiesta o successiva;
- cycle reale 918274 pubblicato/indexato col PROMPT_ID corretto;
- secondo run = `noop_unchanged_sources`;
- wall time dei due run riportato;
- timer enabled e service non failed.

# Scope / stop
Niente audit generale, suite completa, modifiche source, scansione di tutti i rollout, cleanup dello storico `unassigned`, benchmark extra o verifiche post-PASS. Nessun retry equivalente senza nuova evidenza.

Output massimo 7 righe: `RESULT`, `TESTS`, `DEPLOY`, `BACKFILL_918274`, `RUN1`, `RUN2`, `TIMER`.
