PROMPT_ID=840907 | PARENT_PROMPT_ID=811925 | project_id=49 | MegaVault=STANDARD

# Goal
Completa il Data Explorer offline di PersonalHub con Datasette Lite vendorizzato, snapshot-safe e realmente utilizzabile senza rete.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- parti dal main risultante da 707603 PASS;
- DataExplorerActivity, DataExplorerContract, DataExplorerSnapshots e docs/DATA_EXPLORER.md esistono già;
- manca il runtime offline vendorizzato richiesto dal contratto.

# Esecuzione ottimizzata
1. Ispeziona solo Data Explorer, asset/runtime e contratti già esistenti; niente audit repo-wide.
2. Vendoriza il runtime minimo Datasette Lite/Pyodide/wheels con versioni/checksum deterministici; nessun download a runtime.
3. Servi esclusivamente DataExplorerSnapshots detached e validate; mai live DB/WAL.
4. Completa la presentation DB read-only per PK/FK, label e backlink equivalenti al server, incluso Health e Hub relations; riusa i contratti esistenti.
5. Mantieni filtri/facets/pagination/SQL read-only e mobile presentation senza reimplementare Datasette in Compose.
6. Esegui test host mirati e UN solo gate AVD end-to-end con rete disabilitata, inclusa navigazione FK/backlink e prova che nessun asset venga scaricato.
7. Misura solo il peso degli asset vendorizzati e il delta stimato; NON fare una signed release build qui. Il build/size/shrink finale appartiene esclusivamente a 788606.
8. Correggi solo failure osservati, integra su main e STOP dopo PASS.

# Acceptance
PASS con Explorer realmente offline, snapshot-safe, read-only, relazioni equivalenti al server, zero download runtime e AVD offline PASS. Nessuna release build duplicata.
