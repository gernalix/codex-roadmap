PROMPT_ID=672304 | PARENT_PROMPT_ID=946821
MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
REPO=gernalix/workflowy-importer

# Goal
Chiudi SOLO il blocker di 946821: nel dashboard live i prompt con prerequisito manuale attualmente canonici, 582946 e 284653, devono risultare Waiting. Non rifare la semantica Needs fix, non creare nuovi successor e non fare audit repo-wide.

# Evidenza già verificata
- 946821 è ormai superseded e ha successor 672304; il suo blocker storico era che la dashboard non rifletteva la semantica Waiting.
- roadmap canonica attuale:
  - 582946 è pending con manual-prerequisite login MitID e-Boks;
  - 284653 è pending con manual-prerequisite open Codex Desktop;
  - 764529 e 784216 sono superseded dal combinato 284653 e NON devono più comparire in Waiting.
- workflowy-importer/main contiene già la logica pending + manual_prerequisites -> waiting.
- Quindi il contratto sorgente è già corretto; resta deploy/runtime/readback o, solo se ancora riproducibile, il minimo gap nel flusso dati runtime.

# Esecuzione minima
1. Claim SOLO 672304; non riavviare 946821.
2. Nel checkout canonico workflowy-importer verifica una sola volta HEAD/main e la logica Waiting in roadmap_bridge.py. Niente history/audit.
3. Esegui python3 deploy_runtime.py UNA volta; riavvia solo il servizio/timer Workflowy previsto dal repo se necessario.
4. Verifica che il runtime importi i file distribuiti (path + hash/revision, senza segreti).
5. Esegui UN roadmap-sync live. Rileggi soltanto:
   - 582946 => Waiting;
   - 284653 => Waiting;
   - 764529 e 784216 => Archive/assenti dalle code attive perché superseded;
   - 946821 => non deve essere un leaf Needs fix.
6. Se PASS, NON modificare codice.
7. Se 582946/284653 restano fuori Waiting, ispeziona SOLO fetch_remote_roadmap_db -> read_roadmap_db -> dashboard_group -> sync_roadmap e il cache state pertinente; trova il primo punto in cui i manual-prerequisite spariscono, applica il minimo fix + un regression test mirato.
8. Ridistribuisci una sola volta dopo eventuale patch e ripeti UN sync/readback. Vietati retry identici senza nuova evidenza.
9. Finalizza 672304 e STOP appena il readback è coerente.

# Acceptance
PASS solo se il runtime distribuito corrisponde al sorgente corrente, 582946 e 284653 risultano Waiting, 764529/784216 non risultano Waiting, 946821 non resta Needs fix, senza modificare altri prompt o pubblicare segreti.

# Report
Massimo 8 righe: RESULT, PARENT_946821, DEPLOYED_REVISION, 582946, 284653, SUPERSEDED_DESKTOP_TASKS, NEEDS_FIX, BLOCKER.