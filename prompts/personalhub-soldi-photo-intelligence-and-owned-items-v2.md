PROMPT_ID=624831 | REPLACES=963514 | project_id=49 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa TUTTE le parti ancora non implementate del sistema foto-transazioni di Soldi sopra la base già integrata da PR #30 e PR #31: indicizzazione visiva locale, ricerca semantica testo↔foto e foto↔foto, “Trova questo oggetto”, layer opzionale di oggetti posseduti/durevoli, focal point non distruttivo per thumbnail e QA prestazionale/device. Non rifare ricerca globale, photos-only gallery o thumbnail già presenti.

# Precondizione
Prima di modificare codice verifica che PersonalHub/main contenga:
- PR #30: docs/FINANCE_PHOTOS.md + FinancePhotoUi.kt + thumbnail quadrate;
- PR #31: 🔍 global live search + 📷 photos-only gallery + tap foto→transazione.
Se una manca, BLOCKED con la sola precondizione mancante. Non cherry-pickare o reimplementare la base.

# Scope
Leggi AGENTS.md, .codex/CODE_MAP.tsv e i soli target soldi.photos / soldi.search / soldi.data + test/migrazioni necessari. Vietati audit repo-wide, refactor, cleanup e fix collaterali.

# 1. Modello e runtime on-device
- Scegli un modello/runtime piccolo con codice E pesi licenziati per uso prodotto/commerciale.
- Vietato fare affidamento sui pesi MobileCLIP research-only.
- Preferisci un modello con spazio embedding congiunto testo↔immagine se la qualità/size lo consentono; altrimenti usa il minimo stack locale che supporta bene entrambe le query senza introdurre un VLM grande.
- Nessuna API AI a pagamento, nessun server inference, nessun upload delle foto per inferenza.
- NON bundle i pesi nel base APK: download on-demand una sola volta in app-private storage, con model id/version, checksum e fail-safe offline. Niente retry identici senza nuova evidenza.

# 2. Indice foto canonico
Aggiungi il minimo schema Room, preferibilmente finance_photo_index keyed da attachmentId, con:
- embedding compatto;
- model id/version;
- stato indicizzazione/error code;
- OCR locale e label/categorie locali quando economicamente disponibili;
- timestamp;
- eventuale hash della sorgente per invalidazione/idempotenza.
Le immagini originali restano sempre fuori da SQLite.

Quando si allega una foto:
- salva transazione senza attendere l'inferenza;
- indicizza in background;
- backfill idempotente delle foto storiche accessibili;
- file mancante/non leggibile non deve rompere la transazione.

# 3. Ricerca semantica integrata nella UX esistente
La 🔍 Search già presente resta l'unica ricerca utente.
- Continua a fare la ricerca live testuale attuale su tutti i campi.
- Integra OCR/labels e, se il modello congiunto lo supporta, semantic text→image ranking: “giubbotto” deve poter trovare foto/transazioni visivamente pertinenti anche quando quel termine non era stato scritto manualmente.
- Mantieni risultati spiegabili: normale metadato testuale prima, semantic score come segnale aggiuntivo, senza fingere certezza.
- Non scaricare/re-encodare tutte le foto a ogni query: usa l'indice persistito.

# 4. “Trova questo oggetto”
Dentro Search aggiungi un'azione dedicata distinta da 📷 photos-only:
- camera O gallery input;
- embedding locale;
- cosine similarity contro gli indici;
- shortlist di 5–10 candidati con thumbnail + metadati essenziali;
- tap→transazione;
- mai affermare automaticamente che top-1 è “lo stesso oggetto”.
Il matching deve tollerare normale cambio di posa, sfondo, luce e inquadratura: l'utente non deve ricordare come aveva disposto l'oggetto nella foto originale.

# 5. Oggetti posseduti / acquisti durevoli
Aggiungi un layer opzionale persistente separato dalla transazione per gli oggetti che ha senso ritrovare nel tempo (vestiti, elettronica, mobili, scarpe, utensili...), senza trasformare automaticamente consumabili ricorrenti come alimentari in asset.
Preferenza schema:
- finance_owned_items con UUID, sourceTransactionId FK, productId opzionale, displayName, primaryAttachmentId opzionale, createdAt/updatedAt, archived/disposedAt opzionale;
- una transazione può avere zero o più owned items.
UX minima:
- dall'editor transazione/foto consentire “Traccia come oggetto” / rimuovi tracking;
- il photos-only/semantic retrieval deve poter aprire transazione e, se presente, l'oggetto associato;
- non duplicare dati finanziari: prezzo/data/esercente restano autorevoli nella transazione.

# 6. Thumbnail/focal point
ContentScale.Crop resta non distruttivo e l'originale non viene mai risalvato quadrato.
Se il center-crop produce anteprime chiaramente sbagliate, aggiungi “Regola anteprima”:
- drag del focal point dentro preview quadrata;
- persisti solo coordinate normalizzate/alignment metadata;
- nessuna seconda copia permanente croppata.
Se center-crop è già adeguato nei test, non aggiungere UI inutile: documenta NOT_NEEDED con evidenza.

# 7. Storage
- Conserva supporto SAF content:// e URL remoto provider-agnostic.
- NON scegliere/implementare unilateralmente Imgur, R2, S3, B2, Supabase ecc.: il provider remoto non è stato scelto.
- Cache/thumbnail locali devono essere eliminabili e rigenerabili.
- Nessun BLOB immagine finance nel DB.

# Verifica minima
Prima di Gradle usa i consumer preflight prescritti da AGENTS se cambi API/Room.
Unit:
- embedding encode/decode + version invalidation;
- cosine/text-image ranking;
- search con OCR/labels;
- idempotenza/backfill;
- owned-item lifecycle/FK;
- focal point math se implementato.
Emulatore QA:
- attach foto → transazione salva immediatamente → indice successivo;
- riapertura;
- 🔍 query metadati;
- 🔍 query semantica “giubbotto”;
- 📷 photos-only invariata;
- “Trova questo oggetto” con stessa cosa da angolo/sfondo differente + distractor;
- tap risultato/foto→transazione;
- owned-item create/open/remove.
Poi smoke fisico minimo secondo protocollo PersonalHub; niente matrice ridondante.

Misura:
- APK prima/dopo;
- peso modello scaricato separato;
- tempo indicizzazione foto;
- latenza query su almeno un dataset sintetico di migliaia di embeddings;
- memoria/scorrimento gallery.
I pesi non devono spiegare crescita del base APK.

# Acceptance
PASS solo se:
- originali fuori SQLite;
- model weights non bundled;
- licenza product-safe verificata;
- inference/search locali e offline dopo primo download;
- indice/backfill idempotenti;
- search testo↔foto e foto↔foto funzionano;
- same-object test con pose diverse porta il target nella shortlist;
- photos-only gallery e ricerca globale PR #31 restano intatte;
- owned-item layer è opzionale e non trasforma consumabili in asset;
- test non alterano dati reali;
- targeted tests + architecture boundaries PASS.

Se un modello piccolo non raggiunge qualità utile, BLOCKED con misure concrete; non sostituirlo automaticamente con un VLM grande.

# Stop
Al PASS roadmap_result/roadmap_finish e STOP. Niente audit dopo PASS.
Output finale max 10 righe: PROMPT_ID, RESULT, MODEL_RUNTIME, LICENSE, MODEL_SIZE, APK_DELTA, INDEX_PERF, SEARCH_QA, OWNED_ITEMS, BLOCKER.
