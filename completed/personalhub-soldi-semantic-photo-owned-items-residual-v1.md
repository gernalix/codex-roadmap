PROMPT_ID=920550
/goal
PROJECT_ID=49
REPO=gernalix/PersonalHub
MEGAVAULT=STANDARD

# Goal
Completa SOLO il residuo funzionale realmente mancante del vecchio 624831 sopra PersonalHub main corrente, senza rifare il lavoro già PASS di 613102: indicizzazione foto locale di Soldi, ricerca semantica testo↔foto e foto↔foto, “Trova questo oggetto”, layer opzionale degli oggetti posseduti e gli eventuali metadati focal-point ancora necessari.

# Starting point già verificato
- 613102 è PASS e main contiene il motore foto globale condiviso People/Places/Soldi, la rimozione della pipeline People legacy, Places photo_uri, preview/cache comuni e Soldi Search/photos-only.
- NON modificare People/Places salvo un consumer minimo strettamente necessario della primitive condivisa; niente nuova AI fuori da Soldi.
- Main non contiene oggi finance_photo_index, finance_owned_items, embedding/OCR/cosine retrieval o “Trova questo oggetto”.
- Primo candidato modello, per evitare discovery generale: wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M, model card MIT; safetensors 93.8 MB, SHA-256 9339ee3d736344d0ddcaa6c03edc9f89688f08caaea5401220885233da726fcc. Verifica comunque licenza dell'artefatto esatto prima di adottarlo. Non cercare altri modelli finché questo candidato non fallisce un gate concreto di conversione, size, qualità o runtime Android.
- I pesi non devono essere nel base APK: download on-demand in app-private storage, model id/version/checksum, fail-closed e uso offline dopo il primo download.
- PersonalHub non deve accumulare migration Room storiche nell'APK solo per il DB reale dell'utente; il live DB verrà portato allo schema finale dal task 913264.

# Scope
1. Claim 920550 e usa il worktree assegnato. Leggi AGENTS.md, CODE_MAP e soltanto Soldi photo/search/data + core photo/database consumer necessari.
2. Riusa il motore foto globale corrente. Nessun secondo media store, gallery o search surface.
3. Aggiungi il minimo indice persistente keyed per attachment: embedding compatto, model id/version, source hash, status/error, OCR/label locale solo se implementabile offline con footprint ragionevole, timestamps. Mai BLOB originali nel DB.
4. Salvataggio transazione mai bloccato dall'inferenza. Indicizzazione/backfill in background, ripetibile senza duplicati; file mancanti => errore locale dell'indice, non della transazione.
5. L'unica Search Soldi esistente integra metadati + OCR/label + semantic text→image ranking. Mantieni risultati spiegabili.
6. Aggiungi “Trova questo oggetto”: camera/gallery QA input -> embedding locale -> cosine similarity -> 5–10 candidati, mai auto-affermare same-object top-1.
7. Aggiungi layer opzionale finance_owned_items: UUID, source transaction FK, nome, primary attachment opzionale, created/updated, archived/disposed opzionale; una transazione 0..N items; “Traccia come oggetto”/remove tracking. Prezzo/data/esercente restano autorevoli nella transazione.
8. Focal point: aggiungi coordinate normalizzate/preview control SOLO se una prova mirata dimostra che il crop condiviso corrente produce anteprime chiaramente sbagliate. Mai seconda copia croppata.
9. Se serve schema nuovo, fai un solo bump coerente dello schema corrente + export/test; NON aggiungere una catena di migration Room storiche per il Pixel reale. 913264 farà la migrazione esterna finale.
10. Test mirati prima di device: encode/decode/version invalidation, cosine ranking, text↔image, image↔image, index/backfill, owned-item lifecycle/FK, focal math se presente, architecture boundaries.
11. QA solo AVD/clone QA con immagini sintetiche: attach→save immediato→index, query semantica, photos-only invariata, same-object da posa/sfondo diverso + distractor, owned item create/open/remove, reopen/persistence. Nessun dato reale e nessun Pixel principale.
12. Misura modello scaricato, APK delta, indicizzazione, latenza query su migliaia di embeddings e memoria. Se il primo modello fallisce un gate concreto, prova al massimo UNA alternativa product-safe mirata; niente model-zoo audit.
13. Al PASS usa roadmap_finish e STOP. Non aspettare CI/merge asincrono con turni modello.

# Acceptance
PASS solo se semantic text↔image e image↔image sono realmente locali/offline dopo il primo download, same-object entra nella shortlist del test, indice/backfill sono robusti ai retry, owned-items è opzionale e persistente, photos-only/search esistenti non regrediscono, originali restano fuori SQLite, pesi fuori base APK, licenza artefatto verificata, gate mirati + AVD + architecture PASS.

# Report
Massimo 10 righe: RESULT, HEAD, MODEL_ARTIFACT, LICENSE_CHECK, MODEL_SIZE/APK_DELTA, INDEX, TEXT_IMAGE, IMAGE_IMAGE, OWNED_ITEMS, BLOCKER.