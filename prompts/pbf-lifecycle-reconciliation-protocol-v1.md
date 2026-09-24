PROMPT_ID=519810
PROJECT_ID=51
MEGAVAULT=STANDARD
REPO=gernalix/codex-roadmap

# Goal
Rendere i PBF (Prompt Blocked or Failed: qualunque prompt con esito terminale diverso da PASS) impossibili da perdere o dimenticare nella roadmap. Mantieni intatto lo storico degli esiti e aggiungi una riconciliazione canonica che distingua automaticamente ciò che è già risolto, ciò che è coperto da un successore attivo, ciò che è intenzionalmente chiuso e ciò che richiede davvero un nuovo fix.

# Evidenza già verificata
- roadmap.sqlite è la source of truth.
- v_attention oggi considera failed/blocked/unknown ma non rappresenta bene i PBF coperti da successori pending/running e non è ricorsiva.
- Workflowy ha già logica per archiviare una failure con successore attivo/completato tramite fix/replacement/followup/merge.
- Il supporto Workflowy a resolved_by è già stato corretto su main; non rifarlo salvo regressione.
- Gli stub storici privi di obiettivo/repo/materializzazione non sono task recuperabili e non devono generare fix inventati.
- Stato ed execution outcome sono concetti diversi: un BLOCKED storico può essere riconciliato come completed se l'obiettivo è stato provato raggiunto in seguito, senza riscrivere l'outcome storico.

# Implementazione minima
1. Parti da schema/roadmap.sql, tools/roadmap_db.py, renderer e test pertinenti. Niente audit generale del repository.
2. Introduci una vista/contratto canonico PBF che per ogni prompt non-PASS classificabile esponga almeno una disposition:
   - resolved: obiettivo raggiunto/provato in seguito;
   - covered: esiste una catena esplicita fix/replacement/followup/merge/resolved_by verso un successore pending/running/completed;
   - needs_fix: PBF azionabile senza successore;
   - waived: cancellato/superseded intenzionalmente con motivo o sostituzione esplicita;
   - historical_unclassified: stub storico senza dati sufficienti.
3. v_attention/renderer devono mostrare solo i PBF realmente needs_fix. Un PBF covered non deve duplicare il successore in Needs fix; conserva però il backlink/relazione e lo storico.
4. La ricerca del successore deve seguire catene bounded e proteggersi dai cicli. Non trattare automaticamente un generico task non collegato come soluzione.
5. Il flusso terminale non deve creare PROMPT_ID o prompt di fix automaticamente. Dopo FAIL/BLOCKED/UNKNOWN deve però lasciare sempre il PBF visibile come needs_fix finché ChatGPT non registra una disposition/successore. CANCELLED/SUPERSEDED richiedono motivo o replacement per essere waived.
6. Backfill solo dei PBF reali/materializzati già presenti: usa relazioni e risultati già nel DB; non inventare scopi per Historical prompt/Prompt NNNNNN senza metadata. Correggi eventuali stati chiaramente amministrativi solo quando l'obiettivo è già provato raggiunto e preserva execution/status_history.
7. Aggiungi test mirati per: leaf failure, successore pending, running e completed, catena multi-hop, resolved_by, ciclo, cancelled/superseded con e senza motivazione, historical stub e correzione terminale che non altera l'outcome storico.
8. Aggiorna README/SQLITE_ROADMAP con il protocollo PBF in poche righe operative. Nessun refactor estraneo.
9. Verifica che il DB canonico dopo backfill non abbia PBF azionabili orfani non spiegati. Se rimane un caso reale non risolvibile dal solo stato roadmap, lascialo needs_fix con causa concreta: non mascherarlo.

# Acceptance
- ogni PBF azionabile ha una disposition verificabile;
- nessun PBF covered/resolved compare come leaf Needs fix;
- un PBF senza copertura resta visibile e non può sparire in Archive per errore;
- outcome storici non vengono riscritti;
- unknown stub storici non generano task fittizi;
- test PBF e test roadmap direttamente toccati PASS;
- roadmap.sqlite, viste generate e documentazione restano coerenti.

# Stop
Appena gli acceptance criteria sono verificati, finalizza con roadmap_finish.py e termina. Output finale conciso: RESULT, PBF_COUNTS_PER_DISPOSITION, ORPHAN_ACTIONABLE, TESTS, CHANGES, BLOCKER.