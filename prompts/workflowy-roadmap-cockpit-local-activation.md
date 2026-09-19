PROMPT_ID=927641
PROJECT=Workflowy roadmap cockpit
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST

GOAL
Attiva sul Fedora il cockpit Workflowy appena mergiato e verifica end-to-end il contratto PROMPT_ID → roadmap.sqlite → github-autosync → Workflowy → Chrome/Codex. Non fare refactor o audit generali.

BASELINE REMOTO MINIMO GIÀ MERGIATO
- github-autosync: f687e935d0eca98c89fab9016b91f39a392408d6
- chrome-codex-switcher: 61a37678ff8a4f293f0fcf9e1f663b1828d7e65f
- codex-roadmap: 687342dc3e4fdfc2fee9e4290d1309b774134df8
- workflowy-importer: 9e489f10fe40aac39e28346299ca9ffa4c62270d

ACCEPTANCE
1. Esegui per primo:
   python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 927641
2. Porta i checkout locali alle versioni canoniche senza bypassare guard/single writer. Per codex-roadmap usa roadmap_pull.py; per gli altri usa il meccanismo github-autosync/reconcile già installato. Verifica che ciascun HEAD contenga almeno lo SHA sopra.
3. github-autosync: reinstalla/aggiorna i wrapper e le unit user se necessario; repo-integrator.timer deve essere enabled/active. `repo-task status-all --roadmap-only` deve restituire JSON valido con pipeline_state.
4. workflowy-importer: aggiorna l'installazione editable/venv già esistente; aggiorna le unit user dal repo, daemon-reload, abilita/riavvia workflowy-bridge.service e workflowy-roadmap-sync.timer. Il timer deve usare la nuova cadenza e `wf roadmap-sync` deve terminare senza warning/errori.
5. chrome-codex-switcher: esegui l'installer idempotente, riavvia il servizio user e verifica /api/health, /api/prompts e la versione runtime dell'estensione. Il manifest installato deve essere 0.2.0. Attendi in modo bounded un heartbeat runtime 0.2.0; se Chrome mantiene ancora runtime vecchio e non esiste un modo sicuro già disponibile per ricaricare l'estensione senza interrompere dati/sessioni, non chiudere Chrome: riporta una sola azione manuale precisa.
6. Verifica che http://127.0.0.1:8765/roadmap/prompt/927641 restituisca il testo canonico dal DB e che CCS /api/prompt/text?prompt_id=927641 restituisca lo stesso prompt tramite proxy.
7. Esegui un sync reale Workflowy e verifica che il prompt 927641 compaia nella dashboard con gruppo operativo coerente e azioni 🚀 Apri / 📋 Copia. Non impostare manualmente P/R/B/F per simulare uno stato.
8. Verifica che per un task repo-backed già noto a github-autosync la proiezione usi pipeline_state/PR/coda; nessuna vista Markdown deve essere consultata per decidere lo stato.
9. Non modificare codice remoto salvo un difetto direttamente necessario all'attivazione e correggibile con il workflow isolato canonico. Non eseguire test device/Android.
10. Se tutti i gate sono soddisfatti, finalizza con:
    python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 927641 --confirm-executed
    e termina immediatamente.

REPORT
PROMPT_ID=927641
RESULT=PASS|BLOCKED|FAIL
HEADS=<repo=sha...>
AUTOSYNC_CONTRACT=<PASS|...>
WORKFLOWY_COCKPIT=<PASS|...>
CCS_BINDINGS=<PASS|...>
EXTENSION_RUNTIME=<version|manual-action-required>
COPY_PROXY=<PASS|...>
BLOCKER=<none|precise blocker>
