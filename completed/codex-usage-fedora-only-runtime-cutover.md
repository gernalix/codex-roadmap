[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=472913 | project_id=8 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Rendere Fedora l'unico runtime reale di `codex-usage-monitor`, preservare eventuale storico unico Oracle, dismettere solo il vecchio monitor sulla VM e lasciare il repo con CI GitHub minima e ripetibile. Kuma/Datasette restano sulla VM.

# Starting point autoritativo
- Fedora repo: `/home/daniele/projects/codex-usage-monitor`; dati: `/home/daniele/projects/codex-usage`.
- Runtime: `~/.local/lib/codex-usage-monitor`; sessioni: `~/.codex/sessions`; DB: `~/.local/share/codex-usage-monitor/codex_usage_monitor.db`.
- `origin/main` contiene almeno `31e687e120f588e66e05e29cf4f0bb9bbd057f45`.
- PR #3 `chatgpt/telemetry-efficiency-current-main` contiene il hardening telemetria/efficienza già implementato in chat; non rifarlo.
- Connessione/path VM: solo MegaVault, niente inventory generale.

# Esecuzione minima
0. **PR #3, solo verifica locale + integrazione:** una fotografia Git, fetch del branch PR #3 e nessun audit. Sul branch esegui una sola volta:
   - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_prompt_efficiency tests.test_publisher_path_metrics tests.test_chat_dump_publisher tests.test_uptime_kuma_push tests.test_quota_notification_policy`
   - `python3 -m py_compile codex_usage_publisher.py scripts/analyze_prompt_efficiency.py scripts/verify_repo.py`
   - esegui `scripts/analyze_prompt_efficiency.py` sui file locali `~/projects/codex-usage/prompts/734581/metrics.json` + transcript: deve distinguere correttamente sessione cache-heavy/tool-heavy e rilevare l'install ADB non serializzata + churn trace-processor; niente scansione di altre sessioni.
   - una sola parse mirata del rollout nativo di `734581`: verifica che i `repo_paths` derivati siano unici e che la write `apply_patch` venga attribuita a `/home/daniele/projects/PersonalHub`; non richiedere che i vecchi artifact già pubblicati vengano retro-riscritti.
   Se PASS, integra PR #3 su `main` con fast-forward se ancora possibile e pusha una volta. Failure: leaf fix pertinente e una sola riconferma.
1. **Fedora gate:** sul `main` integrato esegui insieme:
   - `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_chat_dump_publisher tests.test_uptime_kuma_push tests.test_quota_notification_policy`
   - `python3 -m py_compile codex_usage_monitor.py codex_usage_publisher.py codex_chat_dump_publisher.py codex_session_archive.py deploy_runtime.py uptime_kuma_push.py`
   Non usare pytest/uv/venv: `scripts/verify_repo.py` è il runner canonico. Failure: solo leaf test/fix pertinente, poi una conferma finale; niente full audit.
2. **Deploy Fedora:** `python3 deploy_runtime.py` una volta; usa solo le unit canoniche monitor/archive/publisher già nel repo, `systemctl --user daemon-reload`, enable/start dei tre timer se necessario. Rimuovi eventuale duplicato Fedora solo se dimostrato equivalente.
3. **Smoke Fedora:** avvia una volta ciascun service monitor → archive → publisher. Verifica timer enabled/active, runtime `current`, `codex-usage` clean/synced, manifest/chunk recenti e un dump strutturato/redatto. Un solo heartbeat Kuma `--strict` se configurato.
4. **Storico Oracle:** solo dopo PASS Fedora, individua esclusivamente il vecchio runtime monitor. Confronta metadati DB (schema rilevante, count, primo/ultimo timestamp). Se esiste storia unica, copia il DB su Fedora in `~/.local/share/codex-usage-monitor/legacy-oracle/` con timestamp, SHA256 e permessi privati. Non fare merge SQLite.
5. **Dismissione VM:** ferma/disabilita solo unit monitor verificate. Prima di rimuovere clone/runtime, controlla origin, clean worktree e assenza di commit locali non pushati; qualsiasi dubbio => BLOCKED e non cancellare. Non toccare Kuma, Datasette, Codex CLI, secret o altri servizi.
6. **CI dello stesso repo:** non rimandarla a un task successivo. Se manca CI equivalente, aggiungi un solo workflow GitHub Actions con suite deterministica esistente (parser/archive/publisher/quota/Kuma mockati), PR+push `main`, Python singola versione, permissions read-only, concurrency e nessun secret/runtime reale. Se il repo resta PRIVATE usa solo test veloci; se PUBLIC dopo futuri cambi visibility il workflow deve continuare a funzionare invariato. Push una volta e osserva il singolo run; su failure leggi solo il job fallito e fai il fix minimo.
7. **MegaVault:** aggiorna solo `project_id=8`: host canonico Fedora, nessun monitor Oracle, path reali e archivio storico se creato.

# Non-goal
Niente nuova architettura/timer, full scan sessioni, backfill generale dei vecchi metrics, merge DB storico, migrazione Kuma/Datasette, audit VM, reinstall Codex, refactor/cleanup, retry identici o controlli post-PASS.

# Acceptance
PR #3 validato e integrato; analyzer `734581` coerente con i dati reali; Fedora unico runtime monitor; tre service/timer PASS; publish/chat dump PASS; eventuale storia Oracle preservata; vecchio monitor VM inactive/disabled e clone rimosso solo con gate sicuri; CI repo verde; MegaVault aggiornato; altri servizi VM intatti.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, Fedora SHA/deploy, service/timer, publish+telemetry, storico Oracle, VM retired, CI+MegaVault/blocker.
