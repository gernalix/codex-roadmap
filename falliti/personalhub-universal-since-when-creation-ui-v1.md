PROMPT_ID=140263
/goal
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=STRICT
PROJECT_ID=49
REPO=gernalix/PersonalHub

# Goal

Estendi "Create Since When counter" da feature locale della history Events di Timer a capability condivisa cross-module per entità con timestamp semanticamente utile, riusando l'attuale motore Since When e Hub Context. Non creare implementazioni parallele per modulo.

# Starting point

Leggi prima AGENTS.md, .codex/CODE_MAP.tsv, docs/ARCHITECTURE.md e il codice corrente di Timer Since When. Usa current main come verità: se parte della capability esiste già, estendila invece di rifarla.

Il motore Tags/Facets/Backlinks condiviso del PROMPT_ID 522084 è già completato: riusalo e non creare un secondo graph/tag engine.
Questo task parte dopo 773323 per evitare modifiche concorrenti alle primitive UI condivise.

# Capability condivisa

Definisci un unico contratto/engine per convertire una entità timestamped in un Since When counter. Ogni provider espone solo:
- identità/tipo sorgente;
- timestamp disponibili;
- label semantica del timestamp;
- titolo predefinito del counter;
- deep-link/backlink alla sorgente quando ancora esiste.

Non hardcodare cinque flussi indipendenti.

Timestamp richiesti:
- Timer Event history: preserva il comportamento esistente sulla data/ora dell'evento, migrandolo al percorso condiviso se necessario;
- Timer session: timestamp di inizio sessione;
- Transaction: data/ora semantica della transazione come default; se esiste anche created_at, esponilo solo come alternativa "Added to PH";
- Place: created_at / "Added to PH";
- Substance button/entity: created_at / "Added to PH";
- Tag di qualunque modulo supportato dal motore condiviso: "First used" come default quando calcolabile affidabilmente dalle associazioni, e "Tag created" come alternativa.

Per i tag NON mostrare l'opzione ogni volta che un tag viene assegnato a un record: la checkbox appartiene alla creazione del tag; per tag esistenti usa l'azione contestuale/dettaglio.

# UI — componente condiviso di creazione

Crea una singola primitive/composable condivisa, con naming coerente al progetto, equivalente a:

[ ] Create "Since when" counter

Regole:
- presente nei form/dialog di creazione solo per entità che dichiarano almeno un timestamp compatibile;
- OFF di default;
- con un solo timestamp: nessun controllo aggiuntivo;
- con più timestamp: quando viene attivata mostra un piccolo selector "Start from" con le sorgenti disponibili;
- precompila un titolo sensato del counter e consenti di modificarlo solo se il flusso Since When corrente già supporta il naming/editing senza introdurre un nuovo editor parallelo;
- il salvataggio dell'entità e la creazione opzionale del counter devono usare un unico percorso applicativo condiviso e non lasciare stati parziali evitabili.

Non trasformare core:ui in un mega design system: centralizza soltanto questa primitive e la logica realmente condivisa.

# UI — entry esistenti e history

Per ogni entry/entity supportata già esistente, esponi "Create \"Since when\" counter" come azione contestuale:
- menu overflow ⋮ della riga quando presente;
- oppure long-press se quello è il pattern canonico della lista;
- pagina/detail action quando esiste una schermata dettaglio.

NON mettere checkbox permanenti su ogni riga di history/lista.

Il concetto non deve dipendere dal fatto che una schermata si chiami "History": qualunque entity view compatibile può esporre l'azione.

Se la sorgente offre più timestamp, l'azione apre la scelta "Start from"; con una sola sorgente crea direttamente secondo il normale confirmation/edit flow già usato da Since When.

# Persistenza e provenienza

Rappresenta il counter come snapshot della data iniziale, non come formula che si ricalcola continuamente dalla sorgente.

Riusa campi/relazioni esistenti quando equivalenti; aggiungi schema solo se necessario. Il modello deve poter rappresentare semanticamente l'equivalente di:
- initial_timestamp;
- source_entity_type;
- source_entity_id;
- source_timestamp_field;
- created_at.

Regole:
- modificare successivamente la data della Transaction/Place/Tag/sessione non cambia silenziosamente il counter già creato;
- eliminare la sorgente non elimina né invalida il counter;
- se la sorgente esiste ancora, il counter mostra provenienza/navigazione compatta, es. "↳ Transaction: …";
- usa Hub Context/backlink esistente; niente secondo sistema di relazioni;
- preserva counter e dati esistenti.

Se serve migrazione Room: esplicita, non distruttiva, con schema export e test; nessun reset DB.

# Semantica tag

Per "First used":
- deriva la prima associazione reale del tag nel namespace corretto;
- rispetta l'isolamento namespace implementato da 522084;
- non confondere creazione del tag con prima assegnazione;
- se non esiste alcuna assegnazione, usa "Tag created" come unica sorgente valida invece di inventare una first-use.

# Scope e disciplina

Fai SOLO questa feature.
Niente refactor, cleanup, modernizzazione o redesign fuori scope.
Parti dai file indicati da CODE_MAP/architettura e dai consumer Since When; non fare audit generale del repository.
Riusa codice e test esistenti.
Dopo il primo failure, correggi in base all'evidenza senza ripetere comandi equivalenti.
Problemi collaterali non bloccanti: segnala, non investigare.

# Verifica minima obbligatoria

Test mirati per:
- Event history: comportamento preesistente invariato;
- Timer session -> start timestamp;
- Transaction backdated: counter parte dalla transaction date, non dal momento di inserimento;
- Transaction: selezione alternativa Added to PH se disponibile;
- Place -> created_at;
- Substance -> created_at;
- Tag con usi -> First used default + Tag created selezionabile;
- Tag senza usi -> Tag created;
- namespace tag indipendenti;
- checkbox OFF -> nessun counter;
- checkbox ON -> entity + counter corretti;
- menu/long-press/detail di entry esistente -> counter corretto;
- modifica della sorgente dopo la creazione -> snapshot invariato;
- eliminazione sorgente -> counter preservato;
- backlink/deep-link alla sorgente quando disponibile;
- architecture guard: nessuna implementazione duplicata per modulo.

Esegui compile/unit/architecture gate direttamente pertinenti. QA Android mirato su emulatore canonico; non usare device fisici salvo necessità concreta. Amplia test solo se rischio o failure lo richiede.

# Acceptance

PASS solo se:
- un solo engine/contratto cross-module gestisce Create Since When;
- il componente di creazione condiviso è usato dai form compatibili;
- le entry esistenti usano azione contestuale, non checkbox per-riga;
- Timer Events mantiene il comportamento attuale;
- Timer sessions, Tags, Places, Substances e Transactions funzionano con le semantiche sopra;
- tag usa First used vs Tag created correttamente;
- provenance + snapshot sono persistenti e non dipendono dalla vita futura della sorgente;
- nessuna perdita dati/migrazione distruttiva;
- test mirati + architecture gate + QA pertinente PASS.

# Roadmap

Prima azione:
python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 140263
Procedi solo se lo stato diventa running e usa il worktree restituito come autoritativo.

Al PASS:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 140263 --confirm-executed

Per BLOCKED/FAIL usa roadmap_result.py con lo stesso PROMPT_ID.
Dopo PASS: STOP immediato.

Output finale max 12 righe:
PROMPT_ID
RESULT
SHARED_ENGINE
CREATE_UI
ENTRY_MENU
TIMESTAMPS
TAG_SEMANTICS
PROVENANCE
MIGRATION
TESTS
ANDROID_QA
BLOCKER