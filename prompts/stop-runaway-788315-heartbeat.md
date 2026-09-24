PROMPT_ID=222733

# Goal
Disabilita definitivamente l'automazione Codex locale `chatgptexporter-788315-completion` che continua PROMPT_ID=788315 circa ogni 10 minuti senza progresso, e verifica che non possa più generare nuove continuazioni model-driven.

# Evidenza già verificata
- `gernalix/codex-usage` contiene 190 cicli di 788315.
- Gli ultimi cicli hanno prompt `<heartbeat>` con `automation_id=chatgptexporter-788315-completion`, GPT-6 Sol medium, ~100k token di contesto e output DONT_NOTIFY/attesa.
- L'export ChatGPTExporter richiede un'azione manuale dell'utente; tenere un modello attivo in polling è vietato dal protocollo corrente.
- Non serve modificare ChatGPTExporter, prompt-history o l'archivio per questo task.

# Scope
1. Esegui il claim canonico e usa solo gli strumenti locali necessari a individuare l'entry scheduler/automation esatta.
2. Disabilita o elimina SOLO `chatgptexporter-788315-completion` usando l'API/CLI/storage canonico del runtime che la possiede; non modificare DB o file a mano se esiste un comando supportato.
3. Verifica in readback che l'automazione non sia più enabled/schedulata e che non abbia un prossimo run attivo.
4. Fai una sola ricerca bounded delle automazioni Codex/model ricorrenti attive. Se ne trovi altre il cui unico comportamento è polling senza progresso (`DONT_NOTIFY`, `still waiting`, attesa di click/login/CI/merge/export), riportale nel risultato ma NON avviare analisi estese né modificarle senza evidenza equivalente.
5. Non toccare Chrome, exporter, archivio, roadmap lifecycle di 788315, file privati o altri task.
6. Nessun heartbeat di verifica model-driven: il readback dello scheduler è sufficiente. Dopo PASS, finalizza e STOP.

# Acceptance
PASS solo se `chatgptexporter-788315-completion` non è più attiva/schedulata, il readback è esplicito e nessun nuovo polling modello viene creato per verificarla.

# Report
Massimo 6 righe: RESULT, AUTOMATION_ID, PREVIOUS_STATE, NEW_STATE, OTHER_WASTEFUL_AUTOMATIONS, BLOCKER.