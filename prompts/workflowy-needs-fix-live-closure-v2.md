PROMPT_ID=946821
PARENT_PROMPT_ID=946527
ROADMAP_PROJECT=Fedora / Workflowy
MODEL=GPT-5.5
REASONING=low
MEGAVAULT=FAST
REPO=gernalix/workflowy-importer

# Goal
Chiudi il deploy live della semantica Needs fix dopo che tutti i failure correnti hanno ora un percorso correttivo esplicito.

# Stato già verificato
- workflowy-importer/main contiene già il filtro: failure storici/anonimi o con successore attivo/completato -> Archive; solo leaf irrisolti -> Needs fix.
- CI del filtro è PASS.
- 738242 e 403496 vengono ora terminalizzati e collegati rispettivamente a 582946 e 764529.
- 946527 viene collegato a questo follow-up, quindi non deve più essere un leaf irrisolto.

# Scope
1. Claim 946821.
2. Aggiorna il checkout canonico workflowy-importer a main senza modifiche distruttive.
3. Esegui solo: python3 deploy_runtime.py
4. Avvia/leggi un singolo roadmap-sync live.
5. Verifica la dashboard:
   - 738242, 403496 e 946527 non sono più in Needs fix;
   - 582946 e 764529 sono Waiting per prerequisito manuale;
   - questo prompt è Running durante la verifica;
   - Needs fix contiene soltanto eventuali nuovi leaf reali o hard blocker di integrazione.
6. Se compare un nuovo elemento reale, riporta esattamente PROMPT_ID/kind; non nasconderlo e non fare audit generale.
7. Se non esistono nuovi leaf/hard blocker, Needs fix deve essere 0.
8. Nessun refactor/cleanup. STOP subito dopo il readback.

# Report
Max 6 righe: PROMPT_ID, RESULT, DEPLOYED_REVISION, SYNC, NEEDS_FIX, BLOCKER.