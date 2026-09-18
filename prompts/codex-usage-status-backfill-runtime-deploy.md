PROMPT_ID=274656 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Distribuisci sul Fedora reale il fix già presente su `gernalix/codex-usage-monitor/main` che riconosce report terminali strutturati e verifica che il ciclo storico di `PROMPT_ID=537184` venga ripubblicato come `PASS`. Non rifare l'analisi del bug applicativo di fedora-external-updater.

# Starting point autoritativo
- repo: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- baseline remota minima: `6f56da61f6d5c29fbd221bc8034a3be54a3fa6ea`;
- fix già remoto:
  - `c6ac2eb403091be97a42a4230e628cf4691869e0`: publication semantics v5 per backfill;
  - `4a95aa4a689b036b68a9445dfa14d6b8b5ccb97d`: parser conservativo dei report strutturati;
  - `6f56da61f6d5c29fbd221bc8034a3be54a3fa6ea`: regressione per il formato di 537184;
- runtime installato: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- data repo: `/home/daniele/projects/codex-usage`;
- ciclo target: `PROMPT_ID=537184`, cycle `9d1694bde2a9117328ecd3f8`;
- prima del fix il report era funzionalmente PASS ma pubblicato `status=UNKNOWN`;
- non leggere roadmap/MegaVault/README salvo incoerenza concreta.

# Esecuzione minima
1. Un solo preflight Git: branch/status/fetch; sincronizza `main` in modo non distruttivo e richiedi che la baseline minima sia antenata di HEAD.
2. Esegui solo:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_publishing_status`
   Se fallisce, correggi soltanto lo stesso failure domain e rilancia il leaf necessario.
3. Se hai modificato source/test/config, fai un solo commit/push finale dopo PASS. Se non hai modificato nulla, niente commit.
4. Distribuisci una volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`
5. Esegui una volta il publisher installato:
   `python3 /home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run --wait-lock-seconds 90`
   Gestisci un eventuale overlap col timer in modo bounded; niente retry identico senza stato cambiato.
6. Verifica direttamente nel data repo che `prompts/537184/cycles/9d1694bde2a9117328ecd3f8` riporti `status=PASS` e che la pubblicazione sia committata/pushata. Controlla una sola volta che `codex-usage-publisher.timer` sia enabled/active.
7. Dopo PASS finalizza e stop; niente secondo benchmark, audit o backfill generale manuale.

# Acceptance
PASS solo se:
- test mirato PASS;
- runtime distribuito dalla baseline corretta;
- publisher completa senza errore;
- il ciclo esatto di 537184 è pubblicato come PASS;
- data repo sincronizzato col remoto;
- timer publisher enabled/active.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 274656 --confirm-executed`

BLOCKED/FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 274656 --result BLOCKED --confirm-executed`
oppure `--result FAIL`.

Output massimo 6 righe:
`RESULT=PASS|BLOCKED|FAIL`
`HEAD=<sha>`
`TESTS=<PASS|...>`
`DEPLOY=<PASS|...>`
`BACKFILL_537184=<PASS|...>`
`BLOCKER=<none|testo minimo>`
