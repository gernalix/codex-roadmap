PROMPT_ID=729874
/goal

# Goal
Distribuisci e verifica sul Fedora reale SOLO il consolidamento lifecycle già implementato e verde nei repo remoti. Nessun redesign.

# Starting point autoritativo
- La dipendenza canonica 570349 deve essere già PASS; non rieseguirla.
- codex-roadmap/main >= 0e4d888d46fb64fca8acf203d179d84bd34d8271.
- github-autosync/main >= bad15eb9b2293b691a504e8bac11ff73babfeb1c.
- workflowy-importer/main >= b9d0f7f3c8ff9cd5318d0504bbfba994ca81ed83.
- codex-usage-monitor/main >= afa92654a5515d9353c5ae6df2a07148e153f9a3.
- CI remota pertinente dei quattro repo è PASS prima di questo task.
- Il loop 879838 è stato corretto alla sorgente in github-autosync; l'ultima falsa terminal Issue osservata prima del fix è #903.
- usage Issue #922 ha già provato che la telemetria di 822595 viene registrata senza modificare il suo stato canonicale.
- Non rileggere README, MegaVault, roadmap o storico salvo mismatch concreto: questo starting point è sufficiente.

# Esecuzione
1. Claim con roadmap_start.py per 729874. Procedi solo se conferma running.
2. Per codex-roadmap, github-autosync, workflowy-importer e codex-usage-monitor: un solo fetch + fast-forward sicuro del branch canonico; niente stash/reset/cleanup. Richiedi le baseline sopra.
3. Esegui solo gate mirati:
   - codex-roadmap: test_roadmap_finish, test_usage_execution_single_writer, test_roadmap_pull, test_live_running_lifecycle + py_compile degli helper modificati;
   - github-autosync: test_repo_single_writer e test_github_autosync;
   - workflowy-importer: test_roadmap_bridge.
   Non eseguire suite complete salvo failure che dimostri impatto condiviso.
4. Deploy locale:
   - python3 ~/projects/codex-roadmap/tools/install_live_status_systemd.py --repo ~/projects/codex-roadmap
   - python3 ~/projects/github-autosync/install_systemd.py
   - cd ~/projects/workflowy-importer && python3 deploy_runtime.py
   Il deploy codex-usage-monitor appartiene a 570349: qui fai solo readback, non duplicarlo.
5. Verifica una sola volta:
   - codex-roadmap-live-status e codex-roadmap-sync timer enabled+active, ultimo service non failed;
   - github-autosync, repo-integrator e watchdog timer enabled+active;
   - workflowy-bridge e workflowy-roadmap-sync timer enabled+active; un sync roadmap termina 0;
   - python3 ~/projects/github-autosync/repo_integrator.py --json una sola volta: nessuna finalizzazione roadmap da task privi di roadmap_prompt_id e nessun 879838;
   - readback GitHub una sola volta: nessuna terminal-879838 successiva a #903;
   - 822595 resta running dopo usage #922, oppure se nel frattempo è stato finalizzato deve esistere una terminal_request autorevole; la telemetria da sola non vale;
   - Workflowy non interpreta R/P/B/F come comandi lifecycle: stato canonicale e pipeline sono proiezioni read-only.
6. Non creare mutazioni sintetiche su prompt reali per lo smoke. Nessuna modifica fuori da questo failure domain.
7. Appena tutti i gate sono PASS, finalizza una sola volta con roadmap_finish.py --result PASS --confirm-executed e STOP.

# Acceptance
- un solo percorso lifecycle operativo;
- nessun nuovo loop terminal-879838;
- codex-usage passivo rispetto allo stato roadmap;
- repo-integrator unico owner dell'integrazione Git;
- Workflowy read-only per il lifecycle;
- runtime systemd aggiornato e sano;
- test mirati PASS.

# Output
Massimo 8 righe: RESULT, ROADMAP, AUTOSYNC_INTEGRATOR, WORKFLOWY, USAGE_PASSIVE, LOOP_879838, SYSTEMD, BLOCKER.