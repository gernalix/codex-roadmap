[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=472913 | project_id=8 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Rendere Fedora l'unico runtime reale di `codex-usage-monitor`, preservare eventuale storico unico Oracle, dismettere solo il vecchio monitor sulla VM e lasciare il repo con CI GitHub minima e ripetibile. Kuma/Datasette restano sulla VM.

# Starting point autoritativo
- Fedora repo: `/home/daniele/projects/codex-usage-monitor`; dati: `/home/daniele/projects/codex-usage`.
- Runtime: `~/.local/lib/codex-usage-monitor`; sessioni: `~/.codex/sessions`; DB: `~/.local/share/codex-usage-monitor/codex_usage_monitor.db`.
- `origin/main` contiene almeno `6c3441393a6894883f7815ecb36cebd9fb43900c`.
- Connessione/path VM: solo MegaVault, niente inventory generale.

# Esecuzione minima
1. **Fedora gate:** una sola fotografia Git; se dirty/conflitti => BLOCKED. `fetch` + `pull --ff-only`; esegui insieme:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_chat_dump_publisher tests.test_uptime_kuma_push tests.test_quota_notification_policy -v`
   - `python3 -m py_compile codex_usage_monitor.py codex_usage_publisher.py codex_chat_dump_publisher.py codex_session_archive.py deploy_runtime.py uptime_kuma_push.py`
   Failure: solo leaf test/fix pertinente, poi una conferma finale; niente full audit.
2. **Deploy Fedora:** `python3 deploy_runtime.py` una volta; usa solo le unit canoniche monitor/archive/publisher già nel repo, `systemctl --user daemon-reload`, enable/start dei tre timer se necessario. Rimuovi eventuale duplicato Fedora solo se dimostrato equivalente.
3. **Smoke Fedora:** avvia una volta ciascun service monitor → archive → publisher. Verifica timer enabled/active, runtime `current`, `codex-usage` clean/synced, manifest/chunk recenti e un dump strutturato/redatto. Un solo heartbeat Kuma `--strict` se configurato.
4. **Storico Oracle:** solo dopo PASS Fedora, individua esclusivamente il vecchio runtime monitor. Confronta metadati DB (schema rilevante, count, primo/ultimo timestamp). Se esiste storia unica, copia il DB su Fedora in `~/.local/share/codex-usage-monitor/legacy-oracle/` con timestamp, SHA256 e permessi privati. Non fare merge SQLite.
5. **Dismissione VM:** ferma/disabilita solo unit monitor verificate. Prima di rimuovere clone/runtime, controlla origin, clean worktree e assenza di commit locali non pushati; qualsiasi dubbio => BLOCKED e non cancellare. Non toccare Kuma, Datasette, Codex CLI, secret o altri servizi.
6. **CI dello stesso repo:** non rimandarla a un task successivo. Se manca CI equivalente, aggiungi un solo workflow GitHub Actions con suite deterministica esistente (parser/archive/publisher/quota/Kuma mockati), PR+push `main`, Python singola versione, permissions read-only, concurrency e nessun secret/runtime reale. Se il repo resta PRIVATE usa solo test veloci; se PUBLIC dopo futuri cambi visibility il workflow deve continuare a funzionare invariato. Push una volta e osserva il singolo run; su failure leggi solo il job fallito e fai il fix minimo.
7. **MegaVault:** aggiorna solo `project_id=8`: host canonico Fedora, nessun monitor Oracle, path reali e archivio storico se creato.

# Non-goal
Niente nuova architettura/timer, full scan sessioni, merge DB storico, migrazione Kuma/Datasette, audit VM, reinstall Codex, refactor/cleanup, retry identici o controlli post-PASS.

# Acceptance
Fedora unico runtime monitor; tre service/timer PASS; publish/chat dump PASS; eventuale storia Oracle preservata; vecchio monitor VM inactive/disabled e clone rimosso solo con gate sicuri; CI repo verde; MegaVault aggiornato; altri servizi VM intatti.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, Fedora SHA/deploy, service/timer, publish, storico Oracle, VM retired, CI+MegaVault/blocker.