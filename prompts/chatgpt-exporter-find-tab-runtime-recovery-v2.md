PROMPT_ID=515185
PARENT_PROMPT_ID=788315
PROJECT_ID=92
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT_MODE=FAST
REPO=gernalix/prompt-history

# Goal
Chiudi solo il blocker runtime rimasto di ChatGPTExporter: nel pannello già funzionante, "Find ChatGPT tab" deve trovare una tab chatgpt.com reale e il flusso deve arrivare a un primo archivio valido e ingeribile da prompt-history.

# Starting point verificato
- Non rieseguire 736284 o 788315 da zero.
- L'estensione si apre e il pannello parte dopo azione manuale dell'utente.
- Il blocco corrente avviene su "Find ChatGPT tab".
- Le pagine chrome-extension:// non sono controllabili dall'automazione: non tentare bypass, CDP o percorsi indiretti vietati.
- Preserva profilo Chrome, login, tab e dati esistenti.

# Scope minimo
1. Claim canonico di 515185 e riusa il contesto/runtime della stessa chat di 788315.
2. Parti dal codice dell'estensione/bridge direttamente coinvolto in Find tab. Niente audit generale di prompt-history o Chrome.
3. Verifica una sola volta build/versione effettivamente caricata, service worker/background, permessi/host matching e criterio con cui viene selezionata una tab chatgpt.com.
4. Riproduci il failure sulla tab ChatGPT già aperta. Correggi il minimo difetto concreto; riusa API/approccio upstream già presenti.
5. Non richiedere login, reload massivi o apertura casuale di molte tab. Se serve un'azione UI non automatizzabile, limita l'handoff a una sola azione manuale precisa e continua subito dopo.
6. Dopo Find tab PASS, esegui capture/export una sola volta. Valida struttura e file dell'archivio senza stampare contenuti privati.
7. Esegui l'ingest prompt-history già esistente e verifica almeno una conversazione importata.
8. Test solo mirati alle modifiche; amplia soltanto se un failure nuovo lo richiede. Vietati retry equivalenti senza nuova evidenza.
9. Stop immediato quando acceptance è verificata.

# Acceptance
PASS solo se Find ChatGPT tab identifica la tab reale, capture/export crea un archivio valido, prompt-history lo ingerisce, test mirati sono PASS e nessuna sessione/dato Chrome viene perso. Un limite chrome-extension:// già noto non è da solo un nuovo BLOCKED se il flusso consentito può procedere.

# Roadmap
Avvia con roadmap_start.py per 515185. Su PASS roadmap_finish.py; su blocker esterno inevitabile roadmap_result.py. Dopo terminalizzazione: STOP.

Output max 9 righe: PROMPT_ID, RESULT, EXTENSION_VERSION, FIND_TAB, CAPTURE, ARCHIVE, INGEST, TESTS, BLOCKER.