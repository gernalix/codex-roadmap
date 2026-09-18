PROMPT_ID=468205 | model=GPT-5.6 Luna | reasoning=low

# Goal
Distribuisci SOLO il fix già presente su GitHub che fa riconoscere al publisher Codex i final report con `VERIFICA: PASS/FAIL`, quindi forza una sola ripubblicazione e verifica che PROMPT_ID=742591 non risulti più `UNKNOWN`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`; unico branch remoto persistente: `main`;
- HEAD remoto verificato: `1d1072e8bebef042c50040808c7a58ee8b94d9c0`; CI su questo HEAD PASS;
- baseline funzionale: `e92680284b216e3a61fed6aa53180dd6a0aae8ba`; i commit successivi hanno soltanto aggiunto/rimosso il workflow one-shot usato per eliminare branch obsoleti, senza modifiche runtime;
- il fix è già remoto: `status.py` riconosce `VERIFICA|VERIFICATION|ESITO`, i test coprono il caso reale e `PUBLICATION_SEMANTICS_VERSION=3` forza il backfill;
- ciclo da correggere nel repo privato `/home/daniele/projects/codex-usage`: `prompts/742591/cycles/220a18d0f267fc8be909e449/metrics.json`;
- stato attuale pubblicato: `UNKNOWN`; final response reale contiene `VERIFICA: PASS`;
- runtime canonico Fedora: `/home/daniele/.local/lib/codex-usage-monitor`;
- nessuna modifica al codice è richiesta.

# Esecuzione minima
1. In UNA sola shell call nel repo monitor: verifica branch `main` e worktree pulito; `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`; richiedi `HEAD=origin/main=1d1072e8bebef042c50040808c7a58ee8b94d9c0`; esegui SOLO `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_publishing_status tests.test_publication_semantic_backfill -v`; se PASS usa direttamente `deploy_runtime.py` per distribuire quel checkout nel runtime immutabile. Non esplorare altri script.
2. Se test o deploy falliscono: `BLOCKED` e stop. Non patchare codice.
3. Avvia UNA sola volta `codex-usage-publisher.service` e attendine il completamento normale; niente polling ravvicinato e nessun secondo run.
4. Nel checkout privato `/home/daniele/projects/codex-usage` fai al massimo un `git pull --ff-only` e leggi SOLO il metrics JSON del ciclo indicato: deve risultare `status=PASS`.
5. Non analizzare altri prompt, non ricostruire l'archivio, non eseguire suite complete, non modificare MegaVault e non fare audit post-PASS.

# Acceptance
PASS solo se i due test mirati PASS, deploy runtime PASS, un solo ciclo publisher completa senza errore e il metrics JSON indicato riporta `status=PASS`.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 468205 --confirm-executed`

Niente dry-run o verifiche post-PASS. Output massimo 5 righe: `RESULT`, `TESTS`, `DEPLOY`, `PUBLISH`, `STATUS_742591`.
