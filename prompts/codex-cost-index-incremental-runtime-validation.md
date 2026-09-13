[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=482631 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

# Goal
Valida **solo** la nuova pipeline incrementale già implementata e pushata su `gernalix/codex-usage-monitor/main`: il timer archivio non deve più (A) copiare+SHA256-hashare tutti i rollout invariati né (B) riparsarli tutti per i costi. Verifica test, bootstrap costi una tantum e user unit Fedora aggiornata. Correggi solo failure concrete.

# Scope
- Repo `~/projects/codex-usage-monitor`: worktree pulito, un solo fetch + `pull --ff-only origin main`; sporco non-task => `BLOCKED`, niente stash/reset.
- Parti solo da `codex_session_archive_incremental.py`, `tests/test_session_archive_incremental.py`, `codex_task_costs_incremental.py`, `tests/test_task_costs_incremental.py`, `codex_prompt_cost_query.py`, `tests/test_prompt_cost_query.py`, `tests/test_prompt_cost_state_sync.py` e `systemd/codex-session-archive.service`.
- Nessun monitor Oracle, Telegram, PersonalHub, benchmark generale o scansione manuale dei rollout.
- Non chiamare manualmente né `codex_session_archive.py import` né `codex_task_costs.py`: restano full/fallback. Il primo `codex_task_costs_incremental.py` può fare internamente il bootstrap una tantum se `cost_source_state` non esiste.

# Gate locale
1. Esegui una sola volta: `python3 -m unittest tests.test_session_archive_incremental tests.test_task_costs_incremental tests.test_prompt_cost_query tests.test_prompt_cost_state_sync`.
2. Registra count `session_costs`/`prompt_costs` e i valori noti di `835917` (`total=704885`, `uncached=19471`, `tools=11`).
3. Esegui `python3 codex_task_costs_incremental.py` una prima volta. Se lo stato incrementale non esiste ancora è ammesso `mode=bootstrap`; dopo il bootstrap `cost_source_state` deve essere popolata e `835917` deve restare invariato. Senza modificare `archive.sqlite`, una seconda esecuzione immediata deve essere `mode=incremental sources_parsed=0 sources_removed=0` e non modificare `task_costs.sqlite`, `task_costs.csv`, `prompt_costs.csv`.
4. Aggiorna la **user unit locale** copiando esclusivamente il file tracciato `systemd/codex-session-archive.service` in `~/.config/systemd/user/`, poi `systemctl --user daemon-reload`. Verifica con `systemctl --user cat`:
   - primo `ExecStart` = `codex_session_archive_incremental.py`;
   - secondo `ExecStart` = `codex_task_costs_incremental.py`;
   - nessun full `codex_session_archive.py ... import` e nessun `codex_task_costs.py`.
   Non reinstallare tramite `codex_session_archive.py install-user-systemd` in questo gate.
5. Avvia una sola volta `systemctl --user start codex-session-archive.service`; controlla solo stato/journal di quella esecuzione. Poiché il rollout del prompt corrente cresce mentre lavori, è normale che l'archive step trovi 1/poche `sessions_candidates`; PASS richiede che siano **molto meno di `sessions_seen`** e che il cost step riporti `mode=incremental` con un numero piccolo/coerente di `sources_parsed`, non bootstrap/full rebuild.
6. Se `731608` è ora disponibile con una normale query read-only, riporta il suo costo completo; se non lo è, segnala `not indexed yet`: non fare refresh/manual rebuild solo per misurarlo.
7. Fix minimo + test mirato soltanto su failure concreta; commit/push solo se necessario.

# Stop
PASS appena test + bootstrap/no-op costi + unit/runtime a due stadi incrementali sono verificati. Non misurare `482631` stesso e non aprire altri task.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 482631 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 482631`

Output ≤7 righe: RESULT; test; bootstrap/no-op costi; unit/runtime archive+cost; costo 731608 se già disponibile; fix/SHA; blocker.