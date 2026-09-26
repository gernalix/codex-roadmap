PROMPT_ID=992303

# Goal
Rendi C2 capace di registrare e mostrare, per ogni work item/run, l'executor concreto e la conversazione che lo sta eseguendo o lo ha eseguito.

# Requisiti
- Mantieni canonico `roadmap.sqlite`; nessun secondo control plane.
- Per ogni run registra almeno: tipo executor (`chatgpt`, `codex`, `rdc`, `human` o altro tipo già supportato), identificatore stabile dell'executor/worker quando disponibile, tipo di riferimento conversazione e URI/link concreto.
- Supporta almeno:
  - URL della chat ChatGPT web quando disponibile;
  - deep link della chat/thread nell'app desktop/Codex quando disponibile;
  - eventuale altro riferimento nativo già prodotto dai transport C2.
- Distingui il run/executor corrente dallo storico: se un task viene recuperato, riallocato o passa tra ChatGPT/Codex, preserva tutti i precedenti riferimenti con timestamp/stato invece di sovrascriverli.
- La dashboard Workflowy/C2 deve mostrare in modo compatto l'executor corrente e un link apribile alla chat/thread corrente; lo storico deve essere consultabile senza rendere rumorosa la vista principale.
- I transport/supervisor devono popolare questi campi automaticamente al claim/launch/recovery/finalizzazione. Non richiedere inserimento manuale quando il thread/link è già disponibile al runtime.
- Backfill best-effort dei task attivi e dei run recenti usando solo evidenza reale già persistita (worker_ref, thread id, URL/deep link, rollout metadata, ecc.). Non inventare né dedurre link non verificati.
- Se un executor non ha una chat associata (es. processo nativo), registra esplicitamente il tipo di riferimento appropriato o `none`, non un URL falso.
- Mantieni compatibilità con i run esistenti e con il single-writer.
- Aggiungi migrazione/schema, API/helper, proiezione dashboard, test mirati e documentazione necessaria. Nessun refactor fuori scope.

# Acceptance
PASS solo se:
1. un task C2 running espone executor corrente + riferimento apribile alla chat/thread quando disponibile;
2. una riallocazione conserva lo storico executor/chat precedente e imposta correttamente quello nuovo;
3. Workflowy mostra il riferimento corrente senza leggere stato da fonti non canoniche;
4. task senza chat sono rappresentati correttamente senza link inventati;
5. backfill non produce riferimenti non verificati;
6. test di schema/lifecycle/supervisor/proiezione pertinenti PASS;
7. il protocollo C2 documenta che executor e conversation reference sono metadati operativi obbligatori per ogni run.

# Scope
Modifica minima necessaria in codex-roadmap/C2. Non toccare PersonalHub, device Android o task non correlati.