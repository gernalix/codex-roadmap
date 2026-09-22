PROMPT_ID=788315 | PARENT_PROMPT_ID=736284 | project_id=92 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
REPO=gernalix/prompt-history
WORKDIR=/home/daniele/projects/prompt-history

# Goal
Chiudi il blocker di 736284 e completa il primo archivio ChatGPT Web realmente importabile in prompt-history. Non rilanciare 736284 da zero: riusa tutto il contesto/runtime già verificato e correggi soltanto il percorso live ChatGPTExporter necessario.

# Evidenza già verificata
- 736284 è BLOCKED perché l'automazione non può controllare direttamente pagine chrome-extension://; questo non prova che l'estensione sia inutilizzabile.
- Chrome usa il profilo Daniele/sessione esistente: non cancellare profilo, cookie, login o tab.
- Il runtime prompt-history e gli adapter upstream sono già stati preparati dal lavoro precedente; non riscriverli.

# Scope
1. Esegui il claim canonico e usa il worktree assegnato.
2. Non tentare di automatizzare chrome-extension://. Diagnostica invece il codice/runtime dell'estensione, il service worker/background e il percorso consentito Dashboard/Find tab verso una tab ChatGPT reale.
3. Verifica la build/versione effettivamente caricata e correggi il minimo necessario se la build installata è stale o incompatibile con il ChatGPT corrente. Riusa fix upstream autorevoli quando disponibili invece di reinventarli.
4. Il pulsante Find tab deve trovare una tab ChatGPT reale e il flusso di capture/export deve produrre un archivio valido. Non considerare assenza di un selettore/DOM come richiesta di nuovo login: diagnostica il bridge/DOM.
5. Appena esiste un archivio reale, esegui l'ingestione prompt-history già implementata e verifica che almeno una conversazione venga importata senza stampare contenuti privati.
6. Correggi solo failure in-scope. Niente refactor generale, logout/login forzati, reset del profilo Chrome o riscrittura degli adapter prompt-history.

# Acceptance
PASS solo se la build/estensione effettivamente usata è identificata, Find tab/capture funziona su una tab ChatGPT reale oppure il blocker live residuo è dimostrato esterno e specifico, un archivio reale viene creato e validato, prompt-history lo ingerisce con successo, i test mirati modificati sono PASS e nessun dato/sessione Chrome viene perso.

# Stop
Finalizza con roadmap_finish.py sullo stesso PROMPT_ID. Per un blocker esterno realmente inevitabile usa roadmap_result.py. Dopo PASS: STOP.

Output massimo 10 righe: PROMPT_ID, RESULT, EXTENSION_VERSION, FIND_TAB, CAPTURE, ARCHIVE, INGEST, TESTS, COMMIT, BLOCKER.