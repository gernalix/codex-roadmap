PROMPT_ID=521404 | PARENT_PROMPT_ID=380812 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Chiudi il lavoro già prodotto da 380812 partendo dalla PR PersonalHub #15 pronta. Non rifare implementazione, migrazioni o gate host già validati: completa solo CI/QA/integration closure, merge e cleanup.

# Stato verificato
- repo: `/home/daniele/projects/PersonalHub`;
- PR #15 `Integrate shared Places alerts and profile runtime restore` è OPEN e mergeable;
- candidate: `feature/shared-alerts-place-tags`, head verificato `9f66636d1efaf4c75caf276473ea2090ef449825`;
- base verificata: `main=c8fe8b75072ba03b8e307b95f74a54b6c5ac3510`;
- candidate è 89 commit avanti e 0 indietro rispetto a main al momento della verifica;
- la PR contiene già il runtime restore di `chatgpt/918274-runtime-restore`, schema Room v16, shared alerts/Places tags e `version.txt=52`;
- PR body: migration/FK, alerts, Places, Timer e app compile già validati;
- CI remoto già PASS: Architecture boundaries. Gli altri workflow erano ancora in progress al momento della verifica;
- non fare un altro bump versione.

# Esecuzione minima
1. Esegui roadmap_start per 521404. Un solo fetch mirato di `main` e del candidate/PR #15. Se il PR head è avanzato, usa il nuovo head; non tornare a commit vecchi.
2. Non ripetere i gate host già PASS. Controlla una volta lo stato CI della PR #15:
   - se un job è ancora pending/in-progress, non rilanciare localmente test equivalenti; prosegui con la QA locale mancante e ricontrolla CI una sola volta prima del merge;
   - se un job fallisce, apri solo log/step del job fallito, correggi esclusivamente una regressione causata dal candidate e rilancia solo il gate locale direttamente pertinente. Nessun audit generale.
3. Acquisisci il lease PH una sola volta prima di AVD/integration. Se il tool segnala un lock:
   - usa esclusivamente le sue funzioni di status/TTL/recovery;
   - recupera solo lock scaduto secondo il tool;
   - non cancellare manualmente un lock vivo. Se appartiene davvero a un task ancora attivo, termina BLOCKED indicando prompt/owner.
4. QA AVD su `Pixel_8a` via facade canonica. Riusa artifact candidato già valido se disponibile; altrimenti esegui una sola build debug necessaria. Verifica solo lo scope di questa PR: avvio app, switch profilo senza runtime perso, Places tags, apertura/uso alert Places, Timer alert regression minima, link-only `http|https|workflowy` diretto e mixed/unsafe non auto-open. Non usare Pixel fisico.
5. Se QA trova un failure, modifica solo il candidate, esegui il minimo test/compile invalidato, push una volta e aggiorna PR #15. Non riaprire discovery o migrazioni già PASS.
6. Prima del merge fai un solo refresh di main e semantic review del delta PR corrente. Se main è avanzato, integra solo il necessario sul candidate e rivalida esclusivamente l'area toccata.
7. Richiedi i check PR necessari verdi. Merge PR #15 in main. Verifica che il PR head sia contenuto in origin/main.
8. Elimina `feature/shared-alerts-place-tags` e `chatgpt/918274-runtime-restore` locale/remoto solo dopo containment in main. Rilascia lease in ogni esito.

# Non-goal
Nessun redesign alert, refactor, cleanup collaterale, nuovo schema, secondo bump versione, release, delivery APK o test repo-wide.

# Acceptance / stop
PASS solo se PR #15 è merged, QA AVD scope PASS, check necessari PASS, main contiene il candidate, i due branch sono eliminati e lease rilasciato.
Finalizza 521404 con roadmap_finish; BLOCKED/FAIL via roadmap_result.
Prima riga output: `PROMPT_ID=521404`. Poi max 7 righe: RESULT, PR, HEAD, CI, AVD, BRANCH_CLEANUP, BLOCKER.
