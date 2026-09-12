[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=527814 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | type=Prompt`

# Goal
Elimina SOLO i `ResourceWarning` per connessioni SQLite non chiuse in `gernalix/codex-usage-monitor`, preservando esattamente commit/rollback, WAL, notifiche e comportamento runtime. Verifica localmente il fix senza Telegram reale.

# Starting point autoritativo
`main` parte dal fix quota `9e6160d55d84f4b4e3bb7cb03a10763132220b18`. Nei test mirati del prompt 184639 sono comparsi `ResourceWarning` su connessioni SQLite. In `codex_usage_monitor.py`, `connect_db(cfg)` restituisce una `sqlite3.Connection` raw e vari caller usano `with connect_db(cfg) as con:`; il context manager standard di `sqlite3.Connection` gestisce commit/rollback ma NON chiude la connessione all'uscita. Questo è il solo problema da trattare.

NON leggere `~/.codex/memories/MEMORY.md`, README, MegaVault, roadmap/spiegazioni o altri documenti: questo prompt è autosufficiente. Niente progress narration. Raggruppa controlli indipendenti; target indicativo ≤10 tool-call salvo failure concreta.

# Esegui
1. Nel checkout `/home/daniele/projects/codex-usage-monitor`, in UNA call: verifica worktree/branch, fai `git pull --ff-only origin main` solo se pulito, poi `rg -n "connect_db\\(" codex_usage_monitor.py tests`. Se modifiche locali incompatibili => BLOCKED; niente stash/reset/force.
2. Verifica solo i callsite restituiti e applica il fix minimo che garantisca la chiusura reale delle connessioni usate come context manager SENZA perdere le semantiche transaction commit/rollback. Preferisci una soluzione centralizzata compatibile con l'API esistente (es. `sqlite3.Connection` subclass/factory che chiude in `__exit__`) se i callsite confermano che nessuno usa la connessione dopo l'uscita dal `with`. Nessun refactor DB generale.
3. Aggiungi UN test mirato che dimostri che, dopo il blocco `with`, la connessione non è più utilizzabile perché chiusa e che un'eccezione nel blocco conserva il rollback previsto. Riusa helper esistenti; niente duplicazioni dei test quota.
4. Esegui una sola volta il gate mirato con warning visibili: `python -W always::ResourceWarning -m unittest tests.test_quota_notification_policy tests.test_parsing` più l'eventuale modulo del nuovo test solo se separato. PASS richiede test verdi e nessun `ResourceWarning` SQLite. Non usare/provare pytest.
5. Commit/push solo il fix + test. Poi, in UNA call finale, verifica che la user unit/timer Fedora `codex-usage-monitor` continui a puntare al checkout/runtime previsto e fai al massimo una `once --dry-run-notifications` se serve a provare il percorso DB. Nessun Telegram reale, nessuna VM Oracle, nessuna attesa di polling.

# Stop
PASS = connessioni context-managed realmente chiuse + commit/rollback preservati + test mirati PASS senza ResourceWarning SQLite + push + runtime Fedora sano. Side issue non bloccanti: segnala senza investigare. Nessun broad suite/audit/refactor/cleanup.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 527814 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 527814`
Poi STOP.

Output ≤6 righe: RESULT, SHA, lifecycle fix, test/warnings, runtime/timer, blocker.
