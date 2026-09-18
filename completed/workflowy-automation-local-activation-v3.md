PROMPT_ID=231789 | PARENT_PROMPT_ID=775412 | project_id=96 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Attiva sul Fedora reale il layer locale Workflowy già implementato: CLI `wf`, bridge localhost e refresh periodico cache. Il live smoke 856234 è appena PASS: NON ripeterlo e non rifare audit/test già chiusi.

# Starting point
- repo: `/home/daniele/projects/workflowy-importer`, branch `main`;
- 856234 deve risultare completed/PASS nella roadmap;
- baseline remota minima: `913a76cefa36c190532eb9b37cbd5b7e2631e64b`;
- secret canonico: `~/.config/codex/secrets/workflowy-api-key`; mai stamparlo o copiarlo in unit/log/Git.

# Esecuzione minima
1. Un solo preflight Git: branch/origin/status + fetch/ff non distruttivo; preserva dirty work non correlato. Richiedi baseline minima antenata di HEAD.
2. Riusa `.venv` e fai solo `.venv/bin/python -m pip install -q -e .`; NON rieseguire suite o live smoke già PASS.
3. Verifica i template `deploy/systemd/` col checker più economico disponibile; correggi solo errori concreti.
4. Installa/copia le unit user in `~/.config/systemd/user/`; `systemctl --user daemon-reload`.
5. Abilita/avvia SOLO `workflowy-bridge.service` e `workflowy-cache-sync.timer`. Installa ma lascia disabled `workflowy-backup.timer` e `workflowy-weekly-review.timer`.
6. Secret gate senza valore in output; quindi verifica: bridge active, `GET http://127.0.0.1:8765/health` ok, una sola `.venv/bin/wf sync` PASS con cache aggiornata, cache timer enabled/active.
7. Su failure: minimo failure domain, minimo fix, rilancia solo il gate invalidato. Se modifichi codice/template tracciato, commit/push main una sola volta. Niente retry identici, audit, refactor o smoke duplicati.

# Acceptance / stop
PASS con runtime attivo, sync/cache PASS, optional timer presenti ma disabled e nessun secret esposto. Finalizza:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 231789 --confirm-executed`
BLOCKED/FAIL via roadmap_result. Output max 6 righe: RESULT, HEAD, BRIDGE, CACHE_SYNC, OPTIONAL_TIMERS, BLOCKER.
