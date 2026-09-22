PROMPT_ID=329968
PROJECT_ID=96
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT_MODE=FAST
REPO=gernalix/workflowy-importer

# Goal
Distribuisci e verifica sul Fedora reale la nuova mini-dashboard dell'integratore Workflowy già implementata su workflowy-importer/main. Non progettare nuove feature e non rifare il lavoro sorgente se il runtime funziona.

# Starting point
- main contiene almeno d673c669284648cd4d203444b05fbb92e6858fa0.
- La dashboard usa il contratto reale di github-autosync: repo-task status-all --roadmap-only.
- Le barre mappano soltanto fasi reali: queued=20%, checks=40%, rebasing=60%, merge-wait/integrating=80%, merged=100%.
- Integration deve avere una nota-riepilogo con conteggi, task, PR/coda e motivo; ogni task con pipeline attiva mostra la propria barra.
- Non è una stima del tempo residuo.

# Esecuzione minima
1. Claim 329968. Nel checkout workflowy-importer fai un solo sync/fast-forward sicuro a origin/main; niente stash/reset/cleanup.
2. Esegui SOLO i test mirati:
   python3 -m unittest tests.test_roadmap_bridge.RoadmapBridgeTests.test_integrator_progress_uses_real_pipeline_phases tests.test_roadmap_bridge.RoadmapBridgeTests.test_running_repo_task_moves_to_integration_group
3. Se PASS, esegui python3 deploy_runtime.py una sola volta.
4. Verifica repo-task status-all --roadmap-only una sola volta e salva i campi pipeline_state/integration_state/PR/coda dei task attivi.
5. Esegui un solo wf roadmap-sync.
6. Rileggi il nodo Integration e i soli prompt con pipeline attiva. Verifica che riepilogo e barre corrispondano ai dati di repo-task. Se 522084 è ancora attivo, la sua riga deve riflettere lo stato reale corrente; non forzare un valore specifico.
7. Se non ci sono integrazioni attive, è valido il testo "nessuna integrazione attiva", ma i test delle fasi devono essere PASS.
8. Correggi codice solo se questa verifica trova un bug direttamente introdotto dalla feature; test mirato, un solo deploy aggiuntivo e un solo sync/readback.
9. Stop immediato dopo PASS.

# Acceptance
PASS se runtime distribuito = main corrente, test mirati PASS, Workflowy mostra la mini-dashboard Integrator e le barre reali senza percentuali temporali inventate, e nessun altro nodo/stato roadmap viene alterato.

# Roadmap
Su PASS roadmap_finish.py per 329968; su blocker reale roadmap_result.py. Poi STOP.

Output max 8 righe: PROMPT_ID, RESULT, REVISION, TESTS, INTEGRATOR_SOURCE, WORKFLOWY_SUMMARY, ACTIVE_BARS, BLOCKER.