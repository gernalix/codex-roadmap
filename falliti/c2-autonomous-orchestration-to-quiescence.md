PROMPT_ID=660629

# Goal
Porta C2 a quiescenza reale come **orchestratore**, non come executor monolitico.

Mantieni questa sessione leggera: triage, riconciliazione, prioritizzazione, assegnazione e supervisione. Ogni leaf sostanziale va eseguito in una **sessione Codex fresca e dedicata**, con solo il contesto necessario.

# Loop canonico
Ripeti fino a quiescenza:

1. Rileggi lo stato C2 canonico.
2. Recupera/reconcilia run stale, terminali non recepiti, integration già concluse e worker orfani.
3. **Svuota completamente la Inbox**:
   - processa anche issue arrivati durante il Goal;
   - per ogni pending: match, promote o discard canonico;
   - deduplica quando supportato;
   - niente ricerca extra solo per arricchire metadata.
4. Dopo `issue_inbox pending=0`, riconcilia tutti i work item non terminali, vecchi + appena creati.
5. Ricalcola l’ordine globale:
   - priorità/tag espliciti;
   - blocker che sbloccano lavoro prioritario;
   - dipendenze;
   - execution override;
   - resource/repo locks;
   - `sort_order` canonico come tie-break.
6. Seleziona il **leaf più prioritario realmente eseguibile**.
7. Assegna al leaf il modello/reasoning appropriato nei **metadata C2**, mai nel testo del prompt:
   - semplice, meccanico, deploy/readback/fix evidente → GPT-6 Luna `low`;
   - coding/debugging ordinario o task focalizzato con giudizio → GPT-6 Luna `medium`;
   - architettura, multi-repo, debugging ambiguo, recovery complesso o rischio dati elevato → GPT-6 Sol `medium`;
   - modello/reasoning superiore solo con necessità concreta documentabile.
   Se metadata canonici validi esistono già, preservali salvo evidenza che vadano corretti prima del run.
8. Prepara il leaf secondo protocollo C2 e avvialo in una **nuova sessione Codex dedicata**:
   - un leaf per sessione, salvo task strettamente accoppiati che condividono realmente worktree/acceptance;
   - `executor_started` canonico;
   - worktree/resource locks canonici;
   - nessun executor duplicato.
9. Non incorporare nella sessione 660629 codice, log o history dettagliata del leaf. C2/Git sono la memoria; passa al leaf solo objective, acceptance, starting point ed evidenza necessaria.
10. Supervisiona il leaf tramite stato/receipts/eventi C2:
    - correggi/recover solo quando serve;
    - niente model polling;
    - niente attesa modello per CI/timer/merge/eventi esterni;
    - un run recuperabile conserva identità/checkpoint quando previsto.
11. Quando il leaf termina:
    - verifica risultato e acceptance;
    - riconcilia integration/run/work item;
    - libera risorse;
    - considera concluso il contesto della sessione leaf.
12. Torna al punto 1. Nuovi issue Inbox hanno precedenza sul successivo ciclo di scheduling.

# Recovery
Un problema locale recuperabile non giustifica abbandono del Goal. Recupera in-scope:
- merge/rebase semanticamente risolvibile;
- repo/worktree sporco recuperabile;
- lifecycle C2 stale;
- lease/run orfano;
- helper/control-plane difettoso;
- integration già avvenuta ma non riconciliata;
- turn terminale rimasto `running`;
- PR/task record recuperabile.

Cattura immediatamente in C2 Inbox ogni nuovo bug/blocker/inefficienza/material improvement incontrato; poi continua. Il nuovo issue sarà processato nel ciclo Inbox successivo.

# Regole di efficienza
- Questa sessione non deve diventare un mega-executor multi-repo.
- Nessuna esplorazione repo-wide salvo necessità concreta.
- Riusa evidenza verificata; non ripetere test/acceptance già validi.
- Test leaf-first; amplia solo per failure/evidenza.
- Operazioni meccaniche/event-driven devono restare native e senza modello.
- Dopo un leaf terminale non conservarne nel context più dettagli del necessario: rientra sempre nello stato C2 canonico.
- Non produrre prompt leaf prolissi: materializza solo contesto necessario e acceptance.
- Non cambiare PROMPT_ID di un leaf per una semplice variazione model/reasoning pre-run.

# Starting point
- PROMPT_ID 328371, 158995, 682297, 718501 risultano completati: non rifarli.
- PROMPT_ID 812553 è failed: riconcilia eventuale lavoro residuo tramite Inbox/work item correnti.
- PROMPT_ID 340495 è blocked dal gap di integrazione codex-roadmap: risolvi il problema sistemico canonico prima di riprendere il leaf.
- PROMPT_ID 891963 aveva PR #6 già integrata: se C2 è ancora stale, riconcilia; non reimplementare.
- Sono presenti issue Inbox non ancora processati: una snapshot fresca prevale sempre sui numeri qui riportati.
- Il runtime C2 event-driven, fencing, scheduler, receipts e locks esistono già: riusali; non creare un secondo scheduler.

# Quiescenza
QUIESCENT=YES solo dopo una snapshot fresca che verifichi contemporaneamente:
- `issue_inbox pending = 0`;
- nessun run `claimed/running/recovering` senza executor/recovery valido;
- nessun work item configurato e realmente schedulabile;
- nessun blocker locale recuperabile;
- nessuna integration/mutation terminale da riconciliare;
- nessun executor terminale che trattiene lock/lane;
- un ulteriore ciclo completo Inbox → reconcile → priority non produce nuovo lavoro.

Hard blocker realmente esterni possono restare `blocked` se C2 non possiede alcuna azione utile corrente.

# Persistenza
Aggiorna il checkpoint canonico di 660629 dopo ogni cambiamento materiale:
- Inbox svuotata;
- leaf lanciato;
- leaf terminale;
- priorità ricalcolata;
- blocker/recovery significativo;
- quiescenza.

Il checkpoint deve permettere a un successore di riprendere direttamente dalla `Next action` senza transcript precedente.

# Stop
Continua autonomamente finché:
- `QUIESCENT=YES`, oppure
- un blocker del control plane impedisce materialmente di determinare o proseguire lo stato C2.

Finalizza PROMPT_ID=660629 secondo protocollo C2.

Report finale massimo:
PROMPT_ID=660629
RESULT=PASS|BLOCKED|FAIL
INBOX_PENDING=<n>
LEAVES_COMPLETED=<n>
EXTERNAL_BLOCKED=<n>
ACTIVE_RUNS=<n>
RUNNABLE=<n>
QUIESCENT=YES|NO