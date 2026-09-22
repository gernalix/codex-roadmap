PROMPT_ID=672304 | PARENT_PROMPT_ID=946821
MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
REPO=gernalix/workflowy-importer

# Goal
Chiudi SOLO il blocker di 946821: nel dashboard live 582946 e 764529 devono risultare Waiting. Non rifare la semantica Needs fix, non creare nuovi successor e non fare audit repo-wide.

# Evidenza già verificata
- 946821 è canonically BLOCKED, senza fix/replacement; fix-packet: `dashboard non riflette la semantica attesa; 582946/764529 non risultano Waiting.`
- roadmap canonica: 582946 è pending con `manual-prerequisite:login-mitid-eboks`; 764529 è pending con `manual-prerequisite:open-codex-desktop`.
- workflowy-importer/main HEAD è `5b742c644cf016d65c7803ab12bc753169ff7645`.
- main legge `manual-prerequisite:%` da `prompt_tags` e `dashboard_group()` restituisce `waiting` per un pending con `manual_prerequisites`.
- Quindi il contratto canonico e la logica sorgente sono già corretti; resta da riallineare il runtime/deploy/readback o, solo se ancora riproducibile, il minimo gap nel flusso dati runtime.

# Esecuzione minima
1. Claim SOLO 672304; non riavviare 946821.
2. Nel checkout canonico workflowy-importer verifica una sola volta HEAD/main e che `roadmap_bridge.py` contenga la logica sopra. Niente history/audit.
3. Esegui `python3 deploy_runtime.py` UNA volta; riavvia solo il servizio/timer Workflowy previsto dal repo se il deploy lo richiede.
4. Verifica che il runtime importi i file appena distribuiti (path + hash/revision, senza dump di config/segreti).
5. Esegui UN `roadmap-sync` live. Rileggi soltanto i nodi 582946, 764529 e 946821: 582946/764529 devono essere Waiting; 946821 non deve essere trattato come leaf senza successor dopo la relazione fix.
6. Se ora PASS, NON modificare codice.
7. Se 582946/764529 restano fuori Waiting, ispeziona SOLO il percorso `fetch_remote_roadmap_db -> read_roadmap_db -> dashboard_group -> sync_roadmap` e il cache state pertinente. Determina il primo punto in cui i due `manual-prerequisite` spariscono; applica il minimo fix + un regression test mirato. Nessun refactor.
8. Ridistribuisci una sola volta dopo eventuale patch e ripeti UN sync/readback. Vietati retry identici senza nuova evidenza.
9. Finalizza 672304 e STOP appena entrambi sono Waiting e Needs fix non contiene 946821 come leaf irrisolto.

# Acceptance
PASS solo se il runtime distribuito corrisponde al sorgente corrente, 582946 e 764529 risultano Waiting nel readback live, 946821 ha un successor fix e non resta un leaf Needs fix, senza modificare altri prompt o pubblicare segreti.

# Report
Massimo 7 righe: RESULT, PARENT_946821, DEPLOYED_REVISION, 582946, 764529, NEEDS_FIX, BLOCKER.