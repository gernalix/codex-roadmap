PROMPT_ID=914263 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Priorità
P0 bloccante. Eseguire prima degli altri task PersonalHub. La v56 ha regressioni gravi di persistenza/UI: Events del Timer non si salvano/modificano correttamente, Substances può crashare tappando un pulsante e People presenta problemi di salvataggio/modifica. Non assumere che i problemi siano limitati a questi tre moduli.

# Goal
Porta PersonalHub a una garanzia verificabile di persistenza: OGNI tabella app-owned dello schema canonico corrente deve essere coperta da un test di persistenza appropriato e OGNI tipo di entry modificabile dall'utente deve avere almeno un test end-to-end create/save/readback/edit/readback/delete o cleanup attraverso il percorso di produzione. Correggi ogni failure trovato. La suite finale deve passare su tutti e 3 i device disponibili: emulatore Android, TCL e Pixel.

# Scope stretto
Solo persistenza, CRUD/save/edit, wiring UI->domain/repository/DAO, crash direttamente collegati e infrastruttura di test necessaria a rendere la copertura esaustiva e permanente.
Niente redesign UI, refactor estetico, cleanup generale, nuove feature, minificazione, release work non necessario o audit di codice non correlato.
Parti dai file/schema/test direttamente pertinenti e amplia solo seguendo un failure concreto.

# Autorità e baseline
- Repo: ~/projects/PersonalHub
- project_id=49.
- Usa il main corrente ottenuto tramite il workflow single-writer/worktree canonico; non scrivere direttamente sul checkout canonico.
- Usa MegaVault/AGENTS.md/CODE_MAP/personalhubdoc.md come fonti già autorevoli; non riscoprire informazioni già documentate.
- Il DB canonico runtime è personalhub.db.
- Tutti e 3 i device sono disponibili. Ordine QA: emulatore -> TCL -> Pixel.
- Non cancellare, resettare o sovrascrivere i dati reali dei device fisici.

# Strategia di test obbligatoria

## A. Inventario schema completo e gate anti-buchi
1. Ricava programmaticamente l'elenco reale delle tabelle dal DB/schema corrente (Room schema/sqlite_master o fonte canonica equivalente).
2. Distingui solo le tabelle di piattaforma/SQLite/Room realmente non applicative; documenta l'esclusione in codice. Tutte le tabelle app-owned devono comparire ESATTAMENTE UNA VOLTA nel registry/matrice di copertura.
3. Crea un test "schema coverage" che fallisca automaticamente se in futuro viene aggiunta una tabella app-owned senza relativo probe/test. Nessuna allowlist generica che possa nascondere tabelle.
4. Il report finale deve mostrare TABLE_COVERAGE=X/X e l'elenco di eventuali sole esclusioni di sistema.

## B. Persistenza per ogni tabella app-owned
Per ciascuna tabella, usa il percorso di produzione più alto disponibile, non SQL raw salvo verifica readback:
- entità user-editable: create -> save -> readback DB -> edit -> save -> readback -> delete/cleanup;
- tabelle relazione/join: crea prerequisiti minimi, salva la relazione, verifica FK/readback/update se previsto e cleanup;
- tabelle derivate/interne app-owned: attiva il writer di produzione che le alimenta e verifica persistenza/readback; se per design sono immutabili, prova comunque il contratto che le materializza/persiste e classificale esplicitamente;
- config/singleton/history/log app-owned: esercita il relativo write path e verifica il valore persistito.
Nessuna tabella app-owned può restare "untested", "unknown" o silently skipped.

## C. UI/domain E2E per ogni entry editabile
Costruisci/estendi instrumentation test che, per ogni tipo di entry modificabile dall'utente:
- apre il vero flusso UI;
- crea un record con marker sentinella univoco;
- salva;
- riapre e verifica i valori;
- modifica almeno un campo significativo;
- salva e verifica la modifica;
- esegue cleanup sicuro.
Se un'entità non ha UI ma è scritta dal dominio, usa il writer/repository di produzione e documenta il percorso.

Regressioni nominate da coprire obbligatoriamente:
- Timer Events: create + edit + save + reopen + readback;
- Substances: riproduci il crash del pulsante, cattura stack trace, correggi root cause, aggiungi regression test sullo stesso gesto;
- People: create + edit + save + reopen + readback.
Non fermarti dopo aver corretto questi tre casi.

# Sicurezza dati su TCL e Pixel
- Mai clear-data, reset DB, uninstall distruttivo o migrazione irreversibile sui dati reali.
- Usa marker sentinella univoci per PROMPT_ID/device e cleanup verificato.
- Prima delle prove fisiche acquisisci la migliore snapshot/backup non distruttiva disponibile del DB/app state; se il package/signing impedisce una tecnica, usa un'alternativa non distruttiva.
- Dopo il test verifica che i marker siano rimossi e che i dati preesistenti restino presenti.
- Se un test richiede per forza distruzione dati, NON eseguirlo sul device fisico: valida quel caso su emulatore e trova un test equivalente non distruttivo sul device reale.

# Diagnosi/fix
1. Avvia con test/schema già esistenti; niente audit generale.
2. Per ogni failure prendi il primo stack trace/assertion concreto, localizza il failure domain e fai il minimo fix corretto.
3. Vietati retry identici senza nuova evidenza.
4. Dopo ogni fix esegui prima il test mirato che falliva.
5. Quando i leaf test pertinenti sono verdi, esegui una sola suite aggregata schema-persistence su emulatore, poi la stessa suite su TCL, poi Pixel.
6. Cattura logcat/crash per ogni device. Zero crash/ANR ammessi nei percorsi testati.
7. Se emergono problemi collaterali fuori scope, riportali senza investigarli salvo che blocchino la persistenza.

# Test artifact permanente
La copertura non deve essere una verifica una tantum. Lascia nel repo:
- registry/matrice schema->probe;
- test automatico che impedisce tabelle app-owned senza probe;
- test di persistenza per ogni tabella;
- regression UI/domain test per ogni entry user-editable pertinente;
- fixture/helper riusabili minimi, senza duplicare infrastruttura esistente.
Preferisci test generati/data-driven quando riducono duplicazione, ma mantieni failure leggibili per tabella e device.

# Acceptance criteria
PASS solo se TUTTI sono veri:
- schema inventory completo e TABLE_COVERAGE=X/X per tutte le tabelle app-owned;
- 0 tabelle app-owned senza probe;
- 0 entry user-editable senza create/save/readback/edit/readback coverage;
- Timer Events PASS;
- Substances crash riprodotto, root cause corretta e regression PASS;
- People PASS;
- suite completa PASS su emulatore;
- stessa suite completa PASS su TCL;
- stessa suite completa PASS su Pixel;
- zero crash/ANR nei percorsi esercitati;
- cleanup sentinelle verificato su entrambi i device fisici;
- dati preesistenti preservati;
- test automatico anti-regressione resta nel repo;
- build/test/CI pertinenti al diff PASS;
- modifiche integrate via single writer e branch/worktree del task chiusi correttamente.

Non dichiarare PASS con device non testato, tabella non coperta, skip silenzioso o sola prova DAO quando esiste un percorso UI user-editable.

# Efficienza / stop
Riusa build, risultati e inventari già verificati nella sessione. Un solo fetch iniziale quando possibile. Test mirati prima, suite completa solo dopo i fix, poi una sola esecuzione finale per ciascun device. Niente verifiche equivalenti/ridondanti. Dopo tutti gli acceptance criteria verdi, finalizza immediatamente con roadmap_finish.py e stop.

Output finale max 12 righe; prima riga esatta:
PROMPT_ID=914263
Poi: RESULT, HEAD, SCHEMA_TABLES, TABLE_COVERAGE, UI_ENTRY_COVERAGE, FIXES, TIMER, SUBSTANCES, PEOPLE, EMULATOR, TCL, PIXEL, DATA_SAFETY, TESTS/CI, BLOCKER.
