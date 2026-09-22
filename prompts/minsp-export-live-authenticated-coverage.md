PROMPT_ID=682741

# Obiettivo
Porta ger­nalix/minsp-export da exporter generico già implementato a exporter verificato sul Min Sundhedsplatform reale dell'utente, coprendo ogni sezione sanitaria leggibile dal portale autenticato senza automatizzare MitID né compiere azioni mutative.

# Modello
GPT-5.6 Terra, reasoning medium. MegaVault FAST.

# Scope
Repo target: gernalix/minsp-export.
Parti dai file già presenti su main e da docs/REAL_VALIDATION.md. Non fare esplorazione generale di altri repo. Usa MegaVault solo per risolvere/registrare questo repo e ottenere il project_id canonico; non inventare ID e non usare placeholder. Nessun venv.

# Vincoli di sicurezza
- Il login MitID deve essere completato manualmente dall'utente nella finestra Chrome dedicata.
- Non leggere/salvare password, credenziali MitID, cookie, Authorization header o altri secret.
- Non inviare messaggi, prenotare/cancellare appuntamenti, richiedere refill, fare pagamenti, cambiare preferenze o eseguire qualunque altra mutazione dell'account.
- Sono consentite soltanto navigazione/read-only, apertura di dettagli, paginazione/lazy-load e cattura delle risposte prodotte da tali letture.
- Non committare raw export, browser profile, DB sanitari o altri dati personali.

# Procedura minima
1. Acquisisci il claim roadmap canonico e usa il worktree assegnato dal single writer.
2. Risolvi o registra minsp-export in MegaVault e conserva il project_id reale nel report.
3. Esegui subito i test mirati esistenti. Correggi solo problemi che bloccano questo obiettivo.
4. Avvia il profilo Chrome persistente già previsto dal repo; quando compare MitID lascia che l'utente completi il login manualmente e poi continua senza chiedere ulteriori conferme salvo autenticazione realmente scaduta.
5. Sul portale autenticato inventaria tutte le sezioni/route/read-only control effettivamente disponibili. Copertura attesa, se presenti: analisi di laboratorio, note/journal, ricoveri/visite/encounters, imaging/referti, diagnosi, farmaci, allergie/CAVE, appuntamenti, messaggi in sola lettura, procedure, questionari, PDF/documenti/allegati, provider e reparti.
6. Confronta l'inventario con ciò che crawler e network capture salvano. Aggiungi SOLO gli adapter/selector/seed route minimi necessari per coprire sezioni non raggiunte dagli href normali. Non riscrivere l'architettura già funzionante.
7. Verifica paginazione, "vis mere"/lazy load e download read-only. Non riprodurre manualmente POST mutativi; cattura invece le response generate dalla UI read-only.
8. Esegui un export reale completo fino a esaurimento. Interrompilo deliberatamente una volta e verifica che il resume riparta dal checkpoint senza perdere o duplicare logicamente i dati.
9. Costruisci normalized/health.sqlite e text/complete-medical-record.md. Verifica PRAGMA foreign_key_check vuoto, FTS5/search su almeno un termine realmente presente e popolamento coerente delle tabelle specifiche per le categorie trovate.
10. Per ogni categoria non disponibile nel portale, registra esplicitamente "non esposta/non verificabile" invece di simulare completezza.
11. Esegui i test mirati finali. Quando gli acceptance criteria sono soddisfatti, termina: niente audit, refactor, cleanup o ottimizzazioni extra.

# Acceptance criteria
PASS solo se:
- ogni sezione leggibile osservata nel portale è catturata oppure documentata con motivo preciso di esclusione;
- checkpoint/resume reale è provato;
- HTML/JSON/PDF/allegati trovati sono preservati con hash/manifest;
- health.sqlite, tabelle dominio, FTS/search e Markdown finale sono costruiti e verificati;
- nessuna credenziale/dato sanitario finisce in Git;
- nessuna azione mutativa dell'account è stata eseguita.

Se il solo blocker è la necessità di un nuovo login MitID, mantieni i dati/checkpoint già acquisiti e riporta BLOCKED senza tentare bypass o retry identici.

# Report finale
Massimo 9 righe:
PROMPT_ID=682741
RESULT=PASS|BLOCKED|FAIL
PROJECT_ID=<id reale>
COVERAGE=<sezioni coperte / limitazioni>
RAW=<conteggi html/json/pdf/attachments>
NORMALIZED=<record e tabelle principali>
RESUME=<evidenza>
TESTS=<evidenza>
BLOCKER=<nessuno o blocker preciso>