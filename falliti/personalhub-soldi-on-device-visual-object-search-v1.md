PROMPT_ID=963514 | project_id=49 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO la ricerca visiva delle foto transazione di Soldi sopra la base foto già integrata: indicizzazione on-device leggera + “Trova questo oggetto” da fotocamera/galleria + shortlist di transazioni simili. Nessuna API AI a pagamento e nessun modello pesante dentro l’APK.

# Precondizione
Prima di modificare codice verifica che la base di PR #30 (docs/FINANCE_PHOTOS.md, FinancePhotoUi.kt e foto quadrate nel ledger) sia già su PersonalHub/main. Se non lo è, non reimplementarla e non fare cherry-pick creativo: termina BLOCKED indicando solo questa precondizione.

# Scope stretto
Leggi AGENTS.md, .codex/CODE_MAP.tsv, docs/FINANCE_PHOTOS.md e SOLO i file mappati da soldi.photos / soldi.data più test e migrazioni strettamente necessari. Vietati audit repo-wide, refactor, cleanup, modernizzazioni e fix collaterali.

# Implementazione
1. Avvia con roadmap_start.py e usa esclusivamente il worktree task/<PROMPT_ID> restituito.
2. Scegli un image-embedding runtime/modello on-device piccolo con codice+weights licenziati per uso prodotto. Preferisci la soluzione più piccola utile; vietato dipendere dai pesi MobileCLIP research-only. Niente server AI o API a consumo.
3. NON incorporare i pesi nel base APK. Scarica il modello on-demand una sola volta in storage app-private, con model id/version + checksum e comportamento fail-safe se assente/offline.
4. Aggiungi il minimo schema canonico, preferibilmente finance_photo_index keyed da attachmentId con embedding compatto, model id/version, stato, OCR/labels opzionali e timestamp. Le foto restano fuori da SQLite.
5. Indicizza in background dopo l’aggiunta foto e fai backfill idempotente delle foto storiche accessibili. File mancanti/non leggibili non devono rompere la transazione.
6. Implementa “Trova questo oggetto”: camera/galleria -> embedding -> cosine similarity locale -> 5–10 risultati con thumbnail quadrata + metadati essenziali; tap apre la transazione. Non dichiarare automaticamente identità top-1.
7. Il matching deve tollerare normali cambi di posa/sfondo/inquadratura.
8. Estendi la ricerca testuale solo con segnali locali economici (OCR/label) se già disponibili; niente secondo modello grande solo per text-to-image.
9. Mantieni ContentScale.Crop come crop visivo: niente copie quadrate permanenti. Focal point persistito solo se realmente necessario.
10. Non implementare uploader R2/Imgur/S3: provider remoto non scelto; conserva URL provider-agnostic.

# Verifica
- Se tocchi contratti/Room, esegui prima il consumer preflight previsto da AGENTS sui soli target coinvolti; poi test mirati.
- Unit: encoding/decoding embedding, cosine ranking, idempotenza/backfill, lifecycle indice.
- Device prima su emulatore QA: attach foto -> indice -> riapertura -> Trova questo oggetto -> shortlist -> apertura transazione; non modificare dati reali.
- Solo dopo PASS emulatore, smoke fisico minimo secondo protocollo PersonalHub; niente matrici ridondanti.
- Misura APK prima/dopo: i pesi non devono spiegare crescita base APK; riporta separatamente dimensione modello scaricato.
- Con immagini dello stesso oggetto in inquadrature diverse + distractor, il match corretto deve comparire nella shortlist; top-1 perfetto non è richiesto.

# Acceptance
PASS solo se originali restano esterni a SQLite; modello non bundled; inference/similarity locali e offline dopo primo download; licenza product-safe; index/backfill idempotenti; shortlist funziona; test non alterano dati reali; test mirati + architecture boundary PASS. Se un modello piccolo non dà qualità utile, BLOCKED con misure concrete invece di aggiungere un VLM grande.

# Stop
Appena gli acceptance criteria sono verificati, roadmap_result/roadmap_finish e STOP. Niente audit successivi. Output finale max 8 righe: PROMPT_ID, RESULT, MODEL_RUNTIME, MODEL_SIZE, APK_DELTA, TESTS, DEVICE_SMOKE, BLOCKER.