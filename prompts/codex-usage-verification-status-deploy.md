PROMPT_ID=468205 | model=GPT-5.5 | reasoning=low

# Goal
Distribuisci SOLO il fix già presente su GitHub che fa riconoscere al publisher Codex i final report con `VERIFICA: PASS/FAIL`, quindi forza una sola ripubblicazione e verifica che PROMPT_ID=742591 non risulti più `UNKNOWN`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`;
- HEAD remoto verificato: `e92680284b216e3a61fed6aa53180dd6a0aae8ba`;
- il fix è già remoto: `status.py` riconosce `VERIFICA|VERIFICATION|ESITO`, i test coprono il caso reale, e `PUBLICATION_SEMANTICS_VERSION=3` forza il backfill;
- ciclo da correggere nel repo privato `/home/daniele/projects/codex-usage`: `prompts/742591/cycles/220a18d0f267fc8be909e449/metrics.json`;
- stato attuale pubblicato: `UNKNOWN`; final response reale contiene `VERIFICA: PASS`;
- runtime canonico Fedora: `/home/daniele/.local/lib/codex-usage-monitor`;
- nessuna modifica ulteriore al codice è richiesta.

# Esecuzione minima
1. In UNA sola shell call nel repo monitor:
   - verifica branch `main` e worktree pulito;
   - `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`;
   - verifica `HEAD=e92680284b216e3a61fed6aa53180dd6a0aae8ba`;
   - esegui SOLO:
     `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_publishing_status tests.test_publication_semantic_backfill -v`;
   - se PASS, usa il deployment canonico già presente `deploy_runtime.py` per distribuire quel checkout nel runtime immutabile. Non esplorare altri script.
2. Se test o deploy falliscono: `BLOCKED` e stop. Non patchare codice.
3. Avvia UNA sola volta il servizio publisher user canonico `codex-usage-publisher.service` e attendine il completamento normale. Nessun polling ravvicinato e nessun secondo run.
4. Nel checkout privato `/home/daniele/projects/codex-usage`, fai al massimo un `git pull --ff-only` e leggi SOLO il metrics JSON del ciclo indicato. Deve risultare `status=PASS`.
5. Non analizzare altri prompt, non ricostruire tutto l'archivio, non eseguire suite complete, non modificare MegaVault, non fare audit generali.

# Acceptance
PASS solo se:
- checkout locale monitor è esattamente all'HEAD remoto indicato;
- i due test mirati PASS;
- deploy runtime PASS;
- un solo ciclo publisher completa senza errore;
- il metrics JSON di PROMPT_ID=742591/ciclo indicato riporta `status=PASS`.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 468205 --confirm-executed`

Niente dry-run o verifiche post-PASS. Output massimo 5 righe: `RESULT`, `TESTS`, `DEPLOY`, `PUBLISH`, `STATUS_742591`.
