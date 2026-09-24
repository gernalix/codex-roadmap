PROMPT_ID=822595
/goal
MODEL=GPT-5.6 Sol
REASONING=medium
MEGAVAULT=STRICT
PROJECT_ID=49
REPO=gernalix/PersonalHub

# Goal
Promuovi Since When da capsule interna di Timer a capability globale di PersonalHub e implementa integralmente la creazione cross-module discussa nel task precedente 140263. Riusa il codice corrente: niente secondo motore, niente secondo graph, nessuna perdita dati.

# Ownership e navigazione
- Home PH espone una surface globale "Since when".
- La consultazione/creazione/modifica/eliminazione dei counter avviene dalla surface globale.
- Rimuovi Since When dalla navigazione principale di Timer come feature posseduta da Timer.
- Timer può mantenere solo ingressi contestuali "Create Since when" che aprono/creano nel motore globale.
- La surface globale supporta anche counter creati manualmente senza sorgente.
- La provenienza di un counter indica il modulo/record sorgente quando esiste.
- Integra Since When nella ricerca globale PH se lo shared search corrente lo permette senza un engine parallelo.

# Shared Create Since When component
Un solo componente condiviso per i form:
[ ] Create "Since when" counter
- OFF di default.
- Non renderizzare se nessun timestamp compatibile.
- Se un solo timestamp: dopo enable mostra solo "Starts from: <data>".
- Se più timestamp: mostra "Start from" con radio choices, una sola selezione e default dichiarato dal provider.
- Label utente semantiche, mai nomi DB.
- Parent Save gestisce entity + counter; durante save il componente è non interattivo.
- Se entity salvata ma counter fallisce: errore recuperabile e retry SOLO counter, senza duplicare entity.
- Se exact entity+timestamp ha già generato un counter e il prodotto vieta duplicati: mostra "Since when counter already created" + "Open counter".

Per entry esistenti:
- azione "Create Since when counter" nel menu overflow; altrimenti long-press; altrimenti detail action;
- nessuna checkbox permanente per riga;
- con più timestamp apre selector "Start from"; con uno usa il normale create/edit flow.

Label condivise:
Create "Since when" counter
Start from
Starts from
Counter name
Create
Cancel
Open counter

Accessibilità: intera checkbox row tappabile, radio semantics, screen reader annuncia label + data + selected state.

# Provider/timestamp contract
Ogni sorgente espone entityType/entityId/defaultCounterTitle/timestampSources; ogni source espone id/label/timestamp/isDefault.

Semantica:
- Timer Event -> Event date
- Timer Session -> Session started
- Transaction -> Transaction date default; Added to PH alternativa se disponibile
- Place -> Added to PH
- Substance -> Added to PH
- Tag -> First used default se esiste almeno un'assegnazione; Tag created alternativa. Se mai usato, solo Tag created.
- Counter manuale -> timestamp scelto dall'utente, nessuna provenance obbligatoria.

# Persistenza/provenienza
Counter = snapshot. Rappresenta semanticamente:
initial_timestamp
source_entity_type?
source_entity_id?
source_timestamp_field?
created_at
- modificare la sorgente non cambia il counter;
- eliminare la sorgente non elimina il counter;
- se la sorgente esiste, mostra riga tappabile "↳ <Type>: <label>" usando Hub Context/deep-link esistente;
- niente broken-source warning nuovo;
- non creare secondo sistema di relazioni.
- preserva i counter esistenti con migrazione non distruttiva se necessaria.

# Namespace
Since When è dominio PH-level, non concettualmente Timer. Migra/aliasa il namespace tag timer.since_when al namespace globale since_when senza perdita di definizioni, assegnazioni, aliases o backlink e senza contaminare timer.now/timer.events.

# Scope
Fai SOLO questo goal. Parti da AGENTS.md, CODE_MAP, docs/ARCHITECTURE, Timer Since When corrente, Hub Context/tag engine e i consumer direttamente necessari. Nessun audit generale. Nessun cleanup/refactor fuori scope. Riusa i risultati già presenti.

# Verification
Test mirati:
- Home PH apre Since When globale;
- Timer non espone più Since When come tab/drawer principale;
- counter manuale;
- Timer Event -> Event date;
- Timer Session -> Session started;
- Transaction backdated -> Transaction date e Added to PH alternativa;
- Place/Substance -> Added to PH;
- Tag used -> First used default + Tag created;
- Tag unused -> Tag created;
- namespace since_when indipendente;
- checkbox OFF/ON;
- contextual menu create;
- duplicate behavior;
- snapshot invariato dopo edit source;
- source delete preserva counter;
- provenance/deep-link;
- counter ricercabile globalmente se shared search adapter è disponibile;
- migration lossless;
- checkArchitectureBoundaries.

QA Android su emulatore canonico per Home -> Since When, create manuale e almeno un create da sorgente esistente. Niente device fisico salvo blocker concreto.

# Acceptance
PASS solo se la feature è globalmente posseduta da PH, non è più una destination Timer, tutte le sorgenti sopra usano un solo create engine/component, provenance/snapshot e namespace globale funzionano, i dati esistenti sono preservati e i gate pertinenti passano.

Dopo PASS: STOP.