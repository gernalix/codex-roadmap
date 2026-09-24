PROMPT_ID=105883
/goal
PROJECT_ID=49
REPO=gernalix/PersonalHub
PREIMPLEMENTATION_BRANCH=chatgpt/105883-since-when

# Goal
Promuovi Since When da capsule interna di Timer a capability globale di PersonalHub e completa la creazione cross-module già definita. ChatGPT prepara il codice sul branch PREIMPLEMENTATION_BRANCH; Codex deve riusarlo, non rifare discovery o implementazione equivalenti.

# Ownership e navigazione
- Home PH espone una surface globale "Since when".
- Consultazione, creazione manuale, modifica ed eliminazione dei counter avvengono dalla surface globale.
- Rimuovi Since When dalla navigazione principale di Timer.
- Timer resta una sorgente di counter, non il proprietario della feature.
- La surface globale supporta anche counter manuali senza sorgente.
- Integra i counter nella ricerca globale PH tramite l'engine esistente.

# Shared Create Since When
Un solo componente condiviso per i form:
[ ] Create "Since when" counter
- OFF di default.
- Non renderizzare senza timestamp compatibili.
- Una sorgente: "Starts from: <data>".
- Più sorgenti: "Start from" + radio selector con default semantico.
- Label semantiche, mai nomi DB.
- Salvataggio entity + counter senza duplicare entity in caso di retry.
- Exact duplicate: "Since when counter already created" + "Open counter".

Per entità già esistenti:
- azione "Create Since when counter" in overflow; fallback long-press/detail action;
- nessuna checkbox permanente nelle righe;
- stesso engine sottostante dei form.

Label condivise:
Create "Since when" counter
Start from
Starts from
Counter name
Create
Cancel
Open counter

# Provider contract
Ogni sorgente espone entityType/entityId/defaultCounterTitle/timestampSources.
Ogni timestamp source espone id/label/timestamp/isDefault.

Semantica:
- Timer Event -> Event date
- Timer Session -> Session started
- Transaction -> Transaction date default; Added to PH alternativa
- Place -> Added to PH
- Substance -> Added to PH
- Tag -> First used default se esiste un uso; Tag created alternativa. Se mai usato: solo Tag created.
- Counter manuale -> timestamp scelto dall'utente.

# Persistenza e provenienza
Counter snapshot con equivalente semantico di:
initial_timestamp
source_entity_type?
source_entity_id?
source_timestamp_field?
created_at
- edit sorgente non muta il counter;
- delete sorgente non elimina il counter;
- se la sorgente esiste, mostra provenienza tappabile tramite Hub Context/deep-link;
- nessun secondo graph.
- preserva dati esistenti.

# Namespace
Since When è dominio PH-level. Porta il namespace concettuale da timer.since_when a since_when senza perdita o contaminazione di timer.now/timer.events.

# Scope
Fai SOLO questo task. Parti dal branch PREIMPLEMENTATION_BRANCH e dal diff rispetto a main. Non rifare l'implementazione già presente. Ispeziona altri file solo se un compile/test failure lo richiede. Niente refactor/cleanup fuori scope.

# Codex finishing
1. Avvia il lifecycle canonico con roadmap_start per 105883 e usa il worktree restituito.
2. Porta nel worktree i commit del PREIMPLEMENTATION_BRANCH senza riscriverli inutilmente.
3. Esegui consumer-preflight solo per API pubbliche realmente cambiate.
4. Esegui compile/test mirati, checkArchitectureBoundaries e QA emulatore richiesti.
5. Correggi solo failure concreti.
6. Appena acceptance è verificata, finalizza e STOP.

# Verification
- Home -> Since When globale.
- Timer non mostra Since When come destination primaria.
- Counter manuale.
- Timer Event, Timer Session, Transaction, Place, Substance, Tag con timestamp corretti.
- Checkbox OFF/ON e contextual action.
- snapshot/provenance/delete-source.
- namespace since_when.
- ricerca globale.
- persistence/migration lossless.
- checkArchitectureBoundaries.
- QA emulatore: Home -> Since When, creazione manuale, almeno una creazione da sorgente.

# Acceptance
PASS solo se Since When è globalmente posseduto da PH, tutte le sorgenti usano un solo engine/component, i counter esistenti sono preservati e i gate pertinenti passano.