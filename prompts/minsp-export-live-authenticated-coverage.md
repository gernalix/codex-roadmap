PROMPT_ID=682741
/goal

Rendi `gernalix/minsp-export` un exporter COMPLETO, verificato sul Min Sundhedsplatform reale dell'utente, e portalo autonomamente fino al risultato finale. Non fermarti a un'implementazione parziale e non restituire un risultato intermedio solo perché incontri ostacoli tecnici.

# Obiettivo finale
Esportare e preservare localmente TUTTO ciò che l'account autenticato Min Sundhedsplatform rende leggibile all'utente, incluse tutte le categorie effettivamente presenti nel portale: analisi di laboratorio, note/journal, ricoveri/visite/encounters, imaging/referti, diagnosi, farmaci, allergie/CAVE, appuntamenti, messaggi in sola lettura, procedure, questionari, PDF/documenti/allegati, provider, reparti e qualunque altra sezione clinica leggibile scoperta durante l'esecuzione.

Il risultato finale deve comprendere:
- raw HTML/JSON/PDF/allegati preservati;
- manifest/hash per deduplicazione e audit;
- checkpoint/resume affidabile;
- `normalized/health.sqlite`;
- tabelle dominio coerenti con le categorie realmente trovate;
- FTS5/search funzionante;
- `text/complete-medical-record.md`;
- prova reale di completezza rispetto a tutte le sezioni leggibili osservate nel portale.

# Modello e modalità
GPT-5.6 Sol, reasoning medium.
MegaVault FAST.
Repo target unico: `gernalix/minsp-export`.

# Autonomia
Hai piena autonomia OPERATIVA entro questo obiettivo:
- modifica liberamente il codice del repo quando serve;
- aggiungi adapter/selector/seed route/site-specific logic se necessaria;
- installa/usa dipendenze non segrete necessarie secondo la policy Fedora esistente, SENZA venv;
- usa Chrome/Playwright, DevTools/network inspection, DOM/accessibility tree, file locali, SQLite, test e strumenti host disponibili;
- crea directory/stato/checkpoint locali necessari;
- riavvia browser/processi relativi a minsp-export quando serve;
- esegui test mirati e smoke reali;
- correggi autonomamente failure incontrati;
- scegli tu l'approccio tecnico migliore senza chiedere conferma.

Non chiedere all'utente quale fix applicare e non fermarti perché il primo approccio fallisce.

# Confine invalicabile: autenticazione e account
- MitID NON deve essere automatizzato, intercettato, bypassato o emulato.
- Non leggere, stampare, salvare o committare password, credenziali MitID, cookie, Authorization header o secret.
- Quando serve autenticazione, apri/riusa il profilo Chrome persistente e richiedi SOLO che l'utente completi MitID manualmente.
- Dopo che l'utente ha completato il login, prosegui automaticamente dal checkpoint senza richiedere ulteriori conferme.
- Se la sessione scade durante il lavoro, preserva tutto, riapri il login manuale e riprendi esattamente dal checkpoint.
- Non inviare messaggi, non prenotare/cancellare appuntamenti, non richiedere refill, non fare pagamenti, non cambiare preferenze e non eseguire altre mutazioni dell'account.
- La UI può essere usata per letture, apertura dettagli, espansioni, paginazione, lazy-load e download read-only.

# Starting point
Il repo contiene già:
- profilo Chrome persistente;
- crawler same-origin read-only;
- cattura HTML/JSON/PDF/allegati;
- state SQLite;
- SHA-256/deduplicazione/manifest;
- checkpoint/resume;
- ricrawl incrementale;
- normalizzazione;
- FTS5/search;
- Markdown aggregato;
- test mirati;
- `docs/REAL_VALIDATION.md`;
- `SECURITY.md`.

Parti da questi file. NON rifare l'architettura da zero e NON fare audit generale di altri repo.

# Bootstrap obbligatorio
1. Acquisisci il claim roadmap canonico e usa il worktree assegnato dal single writer.
2. Risolvi o registra `minsp-export` nella MegaVault locale e usa il project_id REALE. Non inventare ID e non usare placeholder.
3. Porta il worktree alla baseline canonica richiesta dal coordinamento senza perdere lavoro.
4. Esegui subito i test mirati esistenti. Qualunque failure in-scope va corretto, non usato come motivo per fermarsi.

# Goal loop autonomo
Continua questo ciclo finché gli acceptance criteria non sono tutti soddisfatti:

1. Avvia/riusa Chrome col profilo persistente e ottieni sessione autenticata tramite login MitID manuale se necessario.
2. Inventaria il portale reale:
   - tutte le voci di navigazione;
   - tab e sottosezioni;
   - route raggiunte;
   - link dettagli;
   - paginazione;
   - "vis mere"/load more;
   - lazy loading/infinite scroll;
   - download;
   - XHR/fetch/read-only API;
   - sezioni raggiungibili solo tramite pulsanti senza href;
   - contenuti caricati in modal/pannelli.
3. Confronta ciò che esiste nella UI con ciò che il crawler ha effettivamente catturato.
4. Per ogni gap:
   - determina la causa concreta;
   - applica il minimo fix/adattatore in-scope;
   - aggiungi un test mirato quando utile;
   - rilancia SOLO il gate necessario;
   - riprendi l'export dal checkpoint.
5. Se una response clinica utile non è JSON ma HTML/XML/text/binary, preservala comunque e normalizzala quando ragionevolmente possibile.
6. Se la UI usa POST per una LETTURA, non riprodurre artigianalmente richieste rischiose: lascia che la UI read-only generi la richiesta e cattura la response risultante.
7. Se un download richiede click/read-only flow, automatizza quel flow solo se non produce mutazioni dell'account.
8. Continua fino a esaurimento di ogni pagina/sezione/paginazione osservata.

# Recovery autonomo: gli ostacoli NON sono terminali
I seguenti casi NON autorizzano BLOCKED e devono essere risolti autonomamente:
- selector cambiato/mancante;
- route non scoperta automaticamente;
- pagina JavaScript senza href;
- timeout Playwright;
- browser/context crash;
- download non intercettato;
- response non classificata;
- parser/normalizer incompleto;
- test fallito;
- FTS5/query fallita;
- schema SQLite insufficiente;
- deduplicazione errata;
- resume che ripete/perde dati;
- PDF non estratto;
- sessione Chrome corrotta recuperabile;
- race/timing/lazy load;
- contenuto dietro "vis mere";
- errore di packaging/installazione;
- dipendenza software mancante installabile;
- file permission locale correggibile;
- bug introdotto durante il task.

Per questi casi:
1. raccogli nuova evidenza;
2. correggi;
3. rilancia il leaf gate;
4. continua.

Vietati retry identici senza nuova evidenza.
Vietato fermarsi dopo il primo fix se l'obiettivo globale non è ancora raggiunto.

# Checkpoint/resume obbligatorio
Durante un export reale:
1. interrompi deliberatamente una volta il processo dopo che sono stati acquisiti dati reali;
2. riavvialo;
3. dimostra che riparte dal checkpoint utile;
4. verifica che non perda dati e che la deduplicazione impedisca duplicati logici/artificiali.

# Verifica finale dei dati
Al termine:
- export reale completo fino a coda esaurita;
- nessun errore retryable residuo;
- manifest coerente con gli artefatti;
- `PRAGMA foreign_key_check` vuoto;
- FTS5/search provato su almeno un termine clinico realmente presente;
- tutte le tabelle dominio pertinenti alle categorie trovate controllate;
- Markdown completo generato;
- conteggi raw/normalized riportati;
- almeno un controllo campione raw → normalized → search/Markdown per verificare tracciabilità.

Per categorie non presenti o non rese accessibili dal portale, registra esplicitamente `non esposta/non verificabile`. Non simulare dati mancanti.

# Protezione dati
- NON committare export, screenshot sanitari, DB sanitari, browser profile, cookie o dati personali.
- Prima del commit esegui un controllo mirato che il diff Git non contenga dati sanitari/segreti.
- Il repo deve contenere solo codice/test/documentazione generica.

# Git
Lavora attraverso il worktree/branch assegnato dal single writer della roadmap.
Fai commit delle sole modifiche in-scope.
Lascia al normale integratore del repository la finalizzazione prevista dal coordinamento; non introdurre workflow Git alternativi.

# Criteri di arresto
PASS solo quando TUTTI gli acceptance criteria sotto sono verificati.

BLOCKED è ammesso SOLO per hard blocker esterno non risolvibile dal codice o dall'ambiente sotto il tuo controllo, per esempio:
- MitID non completabile/non disponibile dopo richiesta all'utente;
- account esplicitamente bloccato;
- portale indisponibile lato server in modo persistente;
- rete esterna realmente non disponibile;
- permesso/risorsa esterna indispensabile che l'utente non possiede.

Prima di dichiarare BLOCKED:
- salva ogni dato/checkpoint già acquisito;
- prova le recovery locali ragionevoli;
- non eseguire bypass di autenticazione;
- non ripetere retry identici.

FAIL solo se scopri una contraddizione tecnica che rende impossibili gli acceptance criteria pur avendo accesso normale al portale, e devi riportare evidenza concreta.

# Acceptance criteria
PASS solo se:
1. ogni sezione leggibile osservata nel portale è catturata oppure esplicitamente documentata con motivo preciso di esclusione;
2. tutte le forme di paginazione/lazy-load/read-only detail realmente presenti sono esaurite;
3. checkpoint/resume reale è provato dopo interruzione deliberata;
4. HTML/JSON/PDF/allegati trovati sono preservati con hash/manifest;
5. `health.sqlite`, tabelle dominio, FTS/search e Markdown finale sono costruiti e verificati;
6. raw → normalized → search/Markdown è tracciabile su campioni reali;
7. non restano failure retryable noti;
8. nessuna credenziale o dato sanitario è finito in Git;
9. nessuna azione mutativa dell'account è stata eseguita.

# Efficienza
- Nessun audit generale.
- Nessuna esplorazione di repo non necessaria.
- Riusa sempre ciò che hai già verificato nella stessa sessione.
- Allarga l'indagine solo quando un failure concreto lo richiede.
- Test mirati prima; ampliali solo se il rischio lo richiede.
- Niente refactor/cleanup/modernizzazioni fuori scope.
- Se scopri un problema collaterale non bloccante, annotalo ma NON investigarlo.
- Dopo PASS non fare ulteriori audit.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 682741 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 682741 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 682741 --result FAIL --confirm-executed`

# Report finale
Massimo 10 righe:
PROMPT_ID=682741
RESULT=PASS|BLOCKED|FAIL
PROJECT_ID=<id reale>
COVERAGE=<sezioni coperte + eventuali non esposte>
RAW=<conteggi html/json/pdf/attachments>
NORMALIZED=<record + tabelle principali>
RESUME=<prova>
SEARCH=<prova FTS/search>
TESTS=<gate eseguiti>
BLOCKER=<none|hard blocker esterno preciso>