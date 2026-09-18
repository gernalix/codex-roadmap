PROMPT_ID=438271 | PARENT_PROMPT_ID=856234 | MERGED_FROM=775412 | project_id=96 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi in un solo pass il follow-up Workflowy: sincronizza il fix remoto già pubblicato, conferma il live smoke reale e attiva il layer locale già implementato (CLI `wf`, bridge localhost, cache-sync timer). Niente redesign.

# Starting point
- repo canonico: `/home/daniele/projects/workflowy-importer`, branch `main`;
- baseline remota minima: `913a76cefa36c190532eb9b37cbd5b7e2631e64b`;
- secret: `~/.config/codex/secrets/workflowy-api-key`; non stamparlo né copiarlo in log/unit/Git;
- i task 856234 e 775412 sono sostituiti da questo task: non eseguirli separatamente.

# Esecuzione minima
1. Un solo preflight Git: branch/origin/status, fetch `origin main`, sincronizzazione non distruttiva; preserva dirty work non correlato. Richiedi la baseline come antenata di HEAD.
2. Riusa `.venv`; esegui `.venv/bin/python -m pip install -q -e .` e una sola suite `.venv/bin/python -m unittest discover -s tests -v`.
3. Valida il secret senza mostrarlo: file regular, non symlink, non vuoto, owner corrente, mode 600; fallback a env `WORKFLOWY_API_KEY` solo se il file manca.
4. Esegui una volta `.venv/bin/workflowy-import-smoke`; richiedi `SMOKE=PASS checks=import,links,todo,noop,replace-guard,replace,cleanup`.
5. Valida i template in `deploy/systemd/` col controllo locale più economico, installa le unità user e fai `systemctl --user daemon-reload`.
6. Abilita/avvia solo `workflowy-bridge.service` e `workflowy-cache-sync.timer`. Installa ma lascia disabled `workflowy-backup.timer` e `workflowy-weekly-review.timer`.
7. Gate runtime: bridge active; `GET http://127.0.0.1:8765/health` ok; una sola `.venv/bin/wf sync` PASS con cache aggiornata; cache timer enabled/active.
8. Su failure diagnostica solo il failure domain, applica il minimo fix, rilancia solo il gate invalidato; se modifichi file tracciati, commit/push `main` una sola volta. Niente retry identici, audit repo-wide o cleanup collaterali.

# Acceptance / stop
PASS solo con suite + smoke + runtime PASS, optional timers installati ma disabled e nessun secret esposto. Poi:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 438271 --confirm-executed`
Per BLOCKED/FAIL usa `roadmap_result.py` con lo stesso PROMPT_ID. Stop immediato.
Output max 6 righe: RESULT, HEAD, TESTS, SMOKE, RUNTIME, BLOCKER.
