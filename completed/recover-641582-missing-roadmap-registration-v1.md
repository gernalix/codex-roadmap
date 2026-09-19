PROMPT_ID=572280 | PARENT_PROMPT_ID=641582 | project_id=51 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Recupera il task 641582, bloccato prima del lavoro reale perché il claim di avvio è stato respinto dal single writer, e correggi il difetto di bootstrap senza rifare lavoro già mergiato.

# Evidenza già verificata
- codex-roadmap Issue #80: [roadmap-mutation] start-641582.
- Actions run 35413429802.
- errore esatto: roadmap_db.RoadmapDBError: prompt_not_found:641582.
- Quindi 641582 non esisteva nel roadmap.sqlite canonico quando roadmap_start.py ha provato pending->running.
- workflowy-importer PR #1 e codex-roadmap PR #75 risultano già mergiati: non reimplementare quelle modifiche.

# Esecuzione
1. Lavora dalla stessa chat Codex di 641582. Sincronizza solo i repo direttamente necessari; niente audit generale.
2. In codex-roadmap, preserva il single-writer. Ricostruisci dal contesto di questa chat l'identità originale di 641582 e registrala una sola volta nel DB canonico come record storico BLOCKED, senza inventare un'esecuzione riuscita e senza riusare l'ID per testo diverso. Collega 572280 a 641582 come fix/recovery secondo lo schema corrente.
3. Correggi roadmap_start.py in modo mirato: prima di creare la Issue start-<id>, preflighta il roadmap.sqlite remoto. Se il PROMPT_ID manca, termina subito con un errore esplicito tipo prompt_not_registered:<id> e NON creare una mutation Issue destinata a essere respinta. Mantieni invariati i claim validi e l'idempotenza.
4. Aggiungi un test di regressione per il caso missing prompt e uno per il normale claim esistente. Tocca solo il codice necessario.
5. Verifica che 572280 sia già registrato e che il suo claim corrente sia valido. Non rilanciare 641582: questo prompt ne è il recovery.
6. Riprendi solo gli acceptance criteria originari di 641582 che risultano ancora realmente mancanti sul codice corrente. Considera già acquisito tutto ciò che è presente su main/PR mergiati; niente reimplementazione.
7. Esegui test mirati, roadmap_db verify e CI pertinente. Se modifichi codex-roadmap, integra su main tramite il workflow previsto e lascia il repo pulito. Stop appena i criteri sono soddisfatti.

# Acceptance
PASS se:
- 641582 è tracciato una sola volta come storico BLOCKED e 572280 è il suo recovery;
- un PROMPT_ID inesistente viene rifiutato localmente da roadmap_start senza creare Issue;
- i claim di prompt registrati continuano a funzionare;
- roadmap DB/renderer/CI pertinenti passano;
- nessun lavoro Workflowy già mergiato viene duplicato;
- gli eventuali residui reali di 641582 sono completati.

Prima riga del report finale: PROMPT_ID=572280
Poi RESULT=PASS|BLOCKED|FAIL e massimo 6 righe totali.
