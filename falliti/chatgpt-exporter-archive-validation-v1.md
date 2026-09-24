PROMPT_ID=254859
PARENT_PROMPT_ID=788315
PROJECT_ID=92
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT_MODE=FAST
REPO=gernalix/prompt-history
WORKDIR=/home/daniele/projects/prompt-history

# Goal
Verifica il più recente archivio ChatGPTExporter realmente completato sotto /home/daniele/Documents/ChatGPT e stabilisci con evidenza se i dati esportati sono corretti e completi. Questo task valida l'archivio già prodotto: non riaprire i vecchi blocker Find tab/dashboard e non rilanciare l'export salvo prova concreta di incompletezza.

# Esecuzione minima
1. Avvia con roadmap_start.py per 254859. Usa il worktree restituito se presente.
2. Individua SOLO il più recente ChatGPTExport-* plausibilmente completato. Non scansionare altre directory senza necessità.
3. Leggi archive.json, inventory.json, reports/validation.json|md, indexes/* e runs/* disponibili. Usa l'audit nativo di ChatGPTExporter già implementato al commit pinned se serve rigenerare la validazione; non reinventare un secondo validatore equivalente.
4. Verifica almeno:
   - inventory completa e expectedConversationCount coerente;
   - set inventory = completion markers = conversation.json per le conversazioni attese;
   - nessun JSON richiesto illeggibile/troncato, hash errato, file .part/staging residuo o file zero-byte richiesto;
   - raw graph ↔ normalizzato coerenti;
   - asset dichiarati complete con path/hash/size validi; quantifica separatamente eventuali asset partial/failed;
   - niente conversation ID duplicati/conflicting e indici JSONL parseabili;
   - terminalState dell'audit e findings reali.
5. Completezza esterna: confronta il set esportato con le fonti locali autorevoli già disponibili (precedente conversations.json/export OpenAI e/o stato prompt-history) solo per rilevare buchi reali. Considera date e scope: una fonte più vecchia non può provare che manchino chat nuove. Non aprire ChatGPT/Chrome per un confronto UI salvo che nessuna evidenza locale possa decidere un dubbio materiale.
6. Esegui l'ingest ChatGPTExporter già esistente in prompt-history in modalità sicura/idempotente e verifica che il numero/set di conversazioni importate corrisponda all'indice dell'archivio previsto, senza stampare contenuti privati. Correggi solo bug dell'ingest/adapter se una discrepanza è causata dal codice.
7. Se l'archivio è incompleto per dati realmente mancanti, NON rilanciare automaticamente la capture: identifica esattamente cosa manca, quantità/ID solo se non sensibili, causa più probabile e azione minima successiva.
8. Test mirati soltanto alla validazione/ingest modificata. Niente audit generale, refactor, cleanup o modifiche a Chrome/estensione fuori scope.

# Acceptance
PASS solo se l'audit termina complete (oppure conversations_complete_assets_partial con conversazioni complete e asset mancanti esplicitamente quantificati/accettati), i set conversazioni attesi coincidono, non ci sono errori strutturali/hash irrisolti e prompt-history ingerisce l'intero set previsto senza perdita o duplicazione.

Finalizza con roadmap_finish.py sullo stesso PROMPT_ID. Output massimo 9 righe:
PROMPT_ID, RESULT, ARCHIVE, TERMINAL_STATE, CONVERSATIONS, ASSETS, CROSSCHECK, PROMPT_HISTORY, BLOCKER.