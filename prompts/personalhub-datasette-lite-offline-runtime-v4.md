PROMPT_ID=840907 | PARENT_PROMPT_ID=811925 | project_id=49 | MegaVault=STANDARD

# Goal
Completa il Data Explorer offline di PersonalHub con Datasette Lite vendorizzato, mantenendo la semantica relazionale del server e funzionando senza rete.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- esistono DataExplorerActivity, DataExplorerContract, DataExplorerSnapshots e docs/DATA_EXPLORER.md;
- oggi non risultano vendorizzati gli asset app/src/main/assets/datasette-lite richiesti dal contratto;
- esegui dopo 707603 e 489818 per usare schema/history e projection server finali.

# Esecuzione
1. Implementa solo i gap indicati da docs/DATA_EXPLORER.md: runtime Datasette Lite/Pyodide/wheels vendorizzato e bootstrap offline.
2. Servi esclusivamente DataExplorerSnapshots detached/validated; mai live DB/WAL.
3. Costruisci la presentation DB read-only necessaria per PK/FK, label e backlink equivalenti al server, incluso Health e Hub relations; riusa i contratti esistenti.
4. Mantieni filtri/facets/pagination/SQL read-only e mobile presentation senza reimplementare Datasette in Compose.
5. Test host mirati; AVD con rete disabilitata e navigazione FK/backlink; verifica che nessun asset runtime venga scaricato a esecuzione.
6. Valuta size release dopo il vendoring; shrink/R8 esistenti vanno mantenuti, non disabilitati.

# Acceptance
PASS con Explorer realmente offline, snapshot-safe, read-only, relazioni equivalenti al server e AVD offline PASS. Stop dopo PASS.
