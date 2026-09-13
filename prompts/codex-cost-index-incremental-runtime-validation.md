[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=482631 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** l'indicizzazione incrementale dei costi Codex già implementata e pushata su `gernalix/codex-usage-monitor/main`: il timer archivio non deve più riparsare tutti i rollout a ogni minuto. Verifica il bootstrap iniziale, il no-op successivo e la user unit Fedora aggiornata. Correggi solo failure concrete.

# Scope
- Repo `~/projects/codex-usage-monitor`: worktree pulito, un solo fetch + `pull --ff-only origin main`; sporco non-task => `BLOCKED`, niente stash/reset.
- Parti solo da `codex_task_costs_incremental.py`, `tests/test_task_costs_incremental.py`, `codex_prompt_cost_query.py`, relativo test e `systemd/codex-session-archive.service`.
- Nessun monitor Oracle, Telegram, PersonalHub, benchmark generale o scansione manuale dei rollout.
- Non chiamare `codex_task_costs.py` manualmente: il primo `codex_task_costs_incremental.py` può fare internamente il bootstrap una tantum se `cost_source_state` non esiste.

# Gate locale
1. Esegui una sola volta: `python3 -m unittest tests.test_task_costs_incremental tests.test_prompt_cost_query`.
2. Registra count `session_costs`/`prompt_costs` e i valori noti di `835917` (`total=704885`, `uncached=19471`, `tools=11`).
3. Esegui `python3 codex_task_costs_incremental.py` una prima volta. Se lo stato incrementale non esiste ancora è ammesso `mode=bootstrap`; dopo il bootstrap `cost_source_state` deve essere popolata e `835917` deve restare invariato.
4. Registra size+mtime_ns di `task_costs.sqlite`, `task_costs.csv`, `prompt_costs.csv`, quindi esegui immediatamente una seconda volta `python3 codex_task_costs_incremental.py`. PASS richiede `mode=incremental sources_parsed=0 sources_removed=0` e nessuno dei tre file modificato.
5. Aggiorna la **user unit locale** copiando esclusivamente il file tracciato `systemd/codex-session-archive.service` in `~/.config/systemd/user/`, poi `systemctl --user daemon-reload`. Verifica con `systemctl --user cat` che il secondo `ExecStart` sia `codex_task_costs_incremental.py` e che non compaia `codex_task_costs.py` full builder. Non reinstallare tramite `codex_session_archive.py install-user-systemd` in questo gate.
6. Avvia una sola volta `systemctl --user start codex-session-archive.service`; controlla lo stato/journal della sola esecuzione. Il cost step deve riportare `mode=incremental` e un numero piccolo di `sources_parsed` coerente con i rollout effettivamente cambiati dopo il passo 4, non un bootstrap/full rebuild.
7. Se `731608` è ora disponibile con una normale query read-only, riporta il suo costo completo; se non lo è, segnala soltanto `not indexed yet`: **non fare refresh/manual rebuild solo per misurarlo**.
8. Fix minimo + test mirato soltanto su failure concreta; commit/push solo se necessario.

# Stop
PASS appena test + bootstrap/no-op + unit runtime incrementale sono verificati. Non misurare `482631` stesso e non aprire altri task.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 482631 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 482631`

Output ≤7 righe: RESULT; bootstrap; no-op; unit/runtime; costo 731608 se già disponibile; fix/SHA; blocker.