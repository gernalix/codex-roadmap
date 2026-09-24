PROMPT_ID=302284

# Goal
Distribuisci sul Fedora reale in UN SOLO passaggio bounded gli ultimi fix già presenti sui main remoti della prompt infrastructure: lifecycle roadmap consolidato, Workflowy aggiornato, publisher Codex con attribuzione goal corretta e styling Workflowy/CCS. Nessun redesign e nessun audit generale.

# Precondizione
- Esegui solo dopo 222733 PASS: il heartbeat runaway di 788315 deve essere spento prima di toccare il runtime ChatGPTExporter/prompt infrastructure.

# Baseline remote minime già verificate
- codex-roadmap: contiene il lifecycle single-writer/PBF corrente e operations/task-state; usa il main corrente.
- github-autosync >= b47f7bd16c94afb17214a49d49637dd20dfd858b.
- workflowy-importer >= 38df310862c3256f57391c72f781e12a09ec8d2f.
- codex-usage-monitor >= 547e92b0c0f60b02e515cb8293d5c6d84ea35f8b.
- chrome-codex-switcher >= 00963e3f31939d936b614c36db1fde57a872e4c7.
- Il vecchio 729874 è sostituito da questo task perché non deployava il nuovo codex-usage-monitor e non verificava le nuove projection/style Workflowy.
- Non rileggere storico/MegaVault/roadmap oltre ai mismatch concreti: questo starting point è sufficiente.

# Esecuzione
1. Claim 302284.
2. In un solo batch per repo, porta in fast-forward sicuro i checkout canonici di codex-roadmap, github-autosync, workflowy-importer, codex-usage-monitor e chrome-codex-switcher. Niente stash/reset/cleanup di dirty non correlato.
3. Gate mirati soltanto:
   - codex-roadmap: test PBF/lifecycle/single-writer direttamente pertinenti;
   - github-autosync: test_repo_single_writer + test_github_autosync;
   - workflowy-importer: tests.test_roadmap_bridge;
   - codex-usage-monitor: tests.test_usage_publisher_regressions + tests.test_task_costs;
   - chrome-codex-switcher: tests.test_late_bind_contract + py_compile host.
   Se un leaf fallisce, correggi solo quel failure domain e rilancia il leaf; niente suite complete salvo impatto condiviso dimostrato.
4. Deploy una volta usando gli entrypoint già versionati:
   - codex-roadmap: install_live_status_systemd.py e runtime sync già esistente;
   - github-autosync: install_systemd.py;
   - workflowy-importer: deploy_runtime.py;
   - codex-usage-monitor: deploy_runtime.py --skip-fetch;
   - chrome-codex-switcher: ./install.sh; non creare una seconda estensione/profilo.
5. Readback lifecycle:
   - roadmap live-status/sync, github-autosync/repo-integrator/watchdog, workflowy bridge/sync e codex-usage publisher timer/service devono essere enabled/active o non-failed secondo il loro tipo;
   - una sola esecuzione roadmap sync deve terminare 0;
   - repo_integrator.py --json una sola volta: nessun writer concorrente o falsa finalizzazione.
6. Readback Workflowy/CCS:
   - esegui un solo sync Workflowy;
   - verifica su un nodo Goal e uno Prompt che la projection contenga riga /goal solo per Goal e riga dedicata model/reasoning;
   - l'estensione installata deve contenere ct-roadmap-model viola+bold+underline e ct-roadmap-goal ciano; se una normale tab Workflowy è già disponibile, fai un solo readback live del class assignment. Non aprire chrome-extension:// e non creare polling.
7. Readback codex-usage:
   - esegui una sola run publisher bounded;
   - verifica la sessione 01a0ca04-1001-7650-8c7a-f8e74aecf3d4: i cicli del goal successore devono risultare attribuiti a 613102 quando roadmap_start ha dichiarato prompt_id=613102, e non restare duplicati sotto prompts/624831/cycles;
   - esegui/rigenera task_costs e usa prompt_costs/delta per il costo per PROMPT_ID; non sommare ingenuamente total_tokens cumulativi di goal;
   - una seconda publisher run è ammessa SOLO come fast-path noop_unchanged_sources, non come polling.
8. Verifica che codex-usage resti telemetria passiva e Workflowy lifecycle read-only.
9. Dopo PASS finalizza e STOP. Non attendere CI/merge in modello e non creare follow-up cosmetici.

# Acceptance
PASS solo se i cinque runtime corrispondono ai main minimi, test mirati PASS, lifecycle single-writer è sano, Workflowy mostra i nuovi metadata/style, il publisher ha corretto/backfillato l'attribuzione 613102/624831 e prompt_costs è la base del confronto costi.

# Report
Massimo 9 righe: RESULT, ROADMAP_AUTOSYNC, WORKFLOWY, CCS_STYLE, CODEX_USAGE_ATTRIBUTION, PROMPT_COSTS, SYSTEMD, COMMITS_IF_ANY, BLOCKER.