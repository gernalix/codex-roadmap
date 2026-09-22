PROMPT_ID=738242 | PARENT_PROMPT_ID=413258 | project_id=23 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Scarica LOCALMENTE l'intera posta e-Boks dell'utente tramite la UI ufficiale già autenticata in Chrome RPM, includendo TUTTI i messaggi di:
1. Posta pubblica
2. Posta dalle aziende
fino a esaurimento reale delle rispettive liste. Non fermarti ai badge/contatori visibili: possono essere unread count e non il totale.

# Starting point verificato
- Chrome RPM Browser Use funziona direttamente: DOM/click/scroll/navigation disponibili.
- NON usare alcuna probe o estensione temporanea.
- 413258 ha verificato: select-all = 15 righe attualmente caricate; "Mostra altro" pagina/carica altri messaggi; nessun select-all inbox-wide.
- Flusso batch verificato: seleziona righe -> "Di più" -> "Salva una copia locale" -> dialog con PDF separati -> "Salva tutto".
- Test 2 messaggi PASS.
- e-Boks rimane funzionante senza probe.
- Sessione e-Boks è già autenticata nella stessa chat/browser.

# Output locale
Crea:
`~/Documents/e-Boks/full-export-2026-09-22/`
con:
- `posta-pubblica/batch-0001/`, `batch-0002/`, ...
- `posta-aziende/batch-0001/`, `batch-0002/`, ...
- `progress.json` con stato resumable: sezione, signature dei messaggi processati, batch, file scaricati.

Non cambiare la cartella Download di Chrome globalmente. Dopo ogni batch, individua solo i nuovi download rispetto allo snapshot pre-batch, attendi che non esistano più `.crdownload`, poi sposta i nuovi file nella cartella batch dedicata. Non toccare file preesistenti in ~/Downloads.

# Regole di completezza/idempotenza
- Prima di ogni batch raccogli una signature stabile per ogni riga visibile usando solo dati UI già presenti (es. href/id DOM se disponibile; altrimenti sender+subject+date+section).
- Mantieni un set persistente di signature già processate in progress.json.
- Processa al massimo 15 messaggi per batch.
- Se "Mostra altro" APPENDE messaggi mantenendo quelli precedenti, seleziona individualmente SOLO le righe non processate; non usare select-all se selezionerebbe anche vecchi messaggi.
- Se "Mostra altro" sostituisce la pagina, puoi usare select-all solo quando tutte le righe correnti sono non processate.
- Dopo ogni download riuscito, aggiorna progress.json atomicamente.
- In caso di restart/session interruption, riparti da progress.json e NON riscaricare batch già confermati.
- Non assumere corrispondenza 1 messaggio = 1 PDF: salva tutti i file prodotti da "Salva tutto".

# Esecuzione
1. Claim:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 738242`
2. Riusa ESCLUSIVAMENTE il Browser Use diretto del Chrome RPM già autenticato. Nessuna probe, content script custom, CDP manuale o nuova estensione.
3. Crea la directory output e progress.json se assente.
4. Completa prima "Posta pubblica":
   a. vai alla sezione;
   b. identifica tutte le righe correnti non processate;
   c. seleziona un batch <=15;
   d. usa SOLO la UI ufficiale "Di più" -> "Salva una copia locale" -> "Salva tutto";
   e. attendi download completi e sposta solo i nuovi file nella batch dir;
   f. registra signature + file;
   g. continua con le altre righe; usa "Mostra altro" finché necessario;
   h. se non ci sono nuove righe e "Mostra altro" non esiste/più non aggiunge nuovi messaggi, la sezione è completa.
5. Ripeti integralmente per "Posta dalle aziende".
6. Non aprire il contenuto dei PDF e non estrarne testo in questo task.
7. Non cliccare mai Elimina, Sposta, Inoltra, logout o altri comandi non richiesti.
8. Se compare CAPTCHA, 429/throttling, login scaduto o controllo anti-bot: STOP fail-closed e conserva progress.json; nessun bypass e nessun retry identico.
9. Verifica finale:
   - entrambe le sezioni percorse fino all'assenza di righe non processate e di ulteriore paginazione utile;
   - zero `.crdownload`;
   - tutte le batch directory registrate esistono;
   - nessun file preesistente in Downloads è stato spostato;
   - riporta numero di messaggi processati e file salvati per sezione.
10. Finalizza e STOP.

# Acceptance
PASS solo se:
- Posta pubblica COMPLETA;
- Posta dalle aziende COMPLETA;
- nessun messaggio incontrato resta non processato;
- paginazione "Mostra altro" esaurita in entrambe;
- tutti i download confermati e archiviati localmente;
- progress.json coerente e resumable;
- nessun uso di probe/API private/session data;
- nessuna azione distruttiva su e-Boks.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 738242 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 738242 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 738242 --result FAIL --confirm-executed`

# Report
Massimo 8 righe:
PROMPT_ID
RESULT
OUTPUT_DIR
POSTA_PUBBLICA=<messages>/<files>
POSTA_AZIENDE=<messages>/<files>
BATCHES
PAGINATION
BLOCKER
