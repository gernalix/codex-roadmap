PROMPT_ID=601566 | PARENT_PROMPT_ID=285894 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
WORKDIR=/home/daniele/projects/grindr-web-exporter

# Goal
Chiudi SOLO il blocker runtime di 285894: elimina la dipendenza obbligatoria da CDP `127.0.0.1:9222` sul profilo Chrome predefinito e rendi `grindr-web-exporter` capace di gestire autonomamente un profilo Chrome persistente dedicato per Grindr. Poi valida `export-all --discovery-only` e, se autenticato, una chat lunga top→bottom. Non rifare recovery/T7/architettura già completati.

# Evidenza già verificata
- 285894: implementazione completata; commit locale `e875ae9`; nessun remote; 5 test mirati PASS.
- Restic/T7 già chiusi: nessuna copia storica trovata. NON rimontare il T7 e NON ripetere recovery/search.
- L'unico blocker è: sessione Grindr autenticata presente nel Chrome normale, ma il CLI richiede CDP su `127.0.0.1:9222`.
- Da Chrome 136, `--remote-debugging-port` / `--remote-debugging-pipe` non sono rispettati sul data-dir Chrome predefinito; serve un `--user-data-dir` non standard. Non tentare workaround sul profilo predefinito.
- Python globale; venv/virtualenv/poetry/uv vietati.

# Implementazione minima
1. Esegui `roadmap_start` per 601566. Parti dal commit `e875ae9`; leggi solo i file browser/CLI/test direttamente pertinenti.
2. Sostituisci il requisito `127.0.0.1:9222` con un browser manager persistente:
   - data dir dedicato fuori dal repo, default `~/.local/share/grindr-web-exporter/chrome-profile`;
   - permessi locali restrittivi;
   - avvio del Chrome stabile installato tramite Playwright persistent context (preferito) o equivalente supportato, usando quel data dir non standard;
   - il profilo deve sopravvivere tra esecuzioni e mantenere la sessione Grindr dopo login.
3. Aggiungi/adegua un comando minimale tipo `setup-browser` / `login` che:
   - apre `https://web.grindr.com/` nel profilo dedicato;
   - rileva automaticamente se la sessione è già autenticata;
   - se non lo è, lascia il browser aperto per il login manuale e conclude con una sola istruzione precisa; al run successivo non deve richiedere login di nuovo se la sessione persiste.
4. `scan-chats`, `export-one`, `export-all` e `resume` devono usare per default il profilo dedicato senza richiedere una porta CDP esterna. Mantieni un endpoint CDP esplicito solo come override opzionale, se utile; non deve essere il percorso normale.
5. NON copiare/migrare dal profilo Chrome predefinito `Cookies`, `Login Data`, Local Storage, token o altri segreti. Non tentare di aggirare la protezione Chrome 136. L'eventuale login nel profilo dedicato deve avvenire tramite normale UI Grindr.
6. Aggiungi test mirati solo per il nuovo browser/session lifecycle: scelta data-dir, persistenza config, assenza requisito 9222, detection authenticated/unauthenticated mockata e override CDP se mantenuto. Riusa i 5 test precedenti senza riscriverli.
7. Gate runtime:
   - avvia il profilo dedicato;
   - se è già autenticato, esegui `export-all --discovery-only` e poi smoke top→bottom su una chat lunga;
   - se NON è autenticato, non dichiarare FAIL: implementazione+test devono essere completi e il solo esito ammesso è BLOCKED con una singola azione manuale: fare login Grindr nella finestra del profilo dedicato e rilanciare il comando indicato.
8. Dopo login disponibile, il task deve riprendere senza modifiche codice e verificare discovery + chat lunga. Nessun contenuto reale Grindr in Git/log/report.
9. Commit locale del fix nel repo. Nessun remote nuovo. Aggiorna README solo per il nuovo flusso browser/login; niente refactor o feature collaterali.

# Acceptance
PASS solo se `export-all --discovery-only` non dipende più da `:9222`, usa autonomamente un profilo persistente non-default e la validazione reale discovery + top→bottom passa con una sessione autenticata. Se manca esclusivamente il login iniziale nel nuovo profilo, BLOCKED è corretto e deve richiedere una sola azione manuale, senza altri blocker.

# Stop
Niente T7, niente nuova recovery, niente nuova architettura scraping, niente audit generale, niente dashboard, niente servizio systemd. Dopo acceptance STOP.

# Report
Massimo 7 righe: RESULT, COMMIT, BROWSER_MODE, PROFILE_DIR, TESTS, REAL_VALIDATION, BLOCKER.