[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=835204 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Verificare localmente, correggere solo eventuali failure concrete e rilasciare l'implementazione **già presente** del Registro attività globale di PersonalHub. Non riprogettare e non reimplementare la feature.

# Starting point già verificato
Repository: `gernalix/PersonalHub`, branch remoto già creato `feature/global-activity-register`.

L'implementazione contiene già:
- `HubActivityLog.kt`: journal globale Room + DAO/paging;
- `HubActivityCapture.kt`: bridge semantici People/Timer/Places e cattura selettiva degli altri write root, con soppressione di duplicati/derived writes;
- `HubActivityUndo.kt`: undo compensativo fail-closed con conflict detection;
- `HubActivityRegisterScreen.kt`: UI leggibile, filtri, navigazione tramite adapter e pulsante Undo solo quando sicuro;
- integrazione Home;
- DB Room portato a schema 11 con migrazione 10→11;
- test sorgente `HubActivityRegisterTest` e aspettative migration aggiornate;
- `version.txt=42` sul branch.

Semantica da preservare:
- Registro = modifiche effettuate nel tempo; append-only dal punto di vista della cronologia, con compensating event per undo;
- Cerca temporale = eventi/entità appartenenti realmente all'intervallo; **non** deve essere riscritta per leggere il Registro;
- Composer = relazioni persistenti fra entità; **non** deve diventare un alias del Registro;
- niente raw ID/UUID nella UI normale;
- payload impostazioni sensibili non devono finire nel journal.

# Scope consentito
Parti SOLO dai file già modificati sul branch e dagli errori prodotti da build/test:
- `core/database/.../HubActivityLog.kt`
- `core/database/.../HubActivityCapture.kt`
- `core/database/.../HubActivityUndo.kt`
- `core/database/.../PersonalHubDatabase.kt`
- `core/database/.../capsules/sync/SyncJournal.kt`
- `app/.../HubActivityRegisterScreen.kt`
- `app/.../MainActivity.kt`
- `app/src/main/res/values*/strings.xml`
- `core/database/src/test/.../HubActivityRegisterTest.kt`
- `core/database/src/test/.../HubContextMigrationTest.kt`
- schema Room 11 generato
- `.codex/CODE_MAP.tsv` solo se serve ad aggiungere l'entry della nuova feature.

Apri altri file soltanto se una failure concreta punta direttamente lì. Nessun audit generale del repository.

# Procedura minima
1. Consulta il bootstrap PersonalHub/MegaVault remoto previsto dalle regole già caricate. Esegui il preflight Telegram finale solo se richiesto dal bootstrap e non esiste già una readiness proof valida.
2. `git fetch` mirato di `origin/main` e `origin/feature/global-activity-register`. Non perdere modifiche locali: se il checkout PersonalHub non è pulito, usa un worktree isolato invece di stash/reset.
3. Verifica che il branch contenga l'attuale `origin/main`. Se `main` è avanzato, integra solo le nuove modifiche necessarie senza force/reset. Mantieni la versione monotona: `42` se resta valida; se `origin/main` ha già versione >=42, imposta una sola volta `version.txt = versione_main + 1` e non incrementare ancora per retry/build/test.
4. Esegui subito i controlli mirati, senza inventory:
   - compilazione Kotlin di `:core:database` e `:app` sufficiente a far girare KSP/Room;
   - test `HubActivityRegisterTest` e `HubContextMigrationTest`;
   - `tools/check_architecture_boundaries.py`.
5. Assicurati che KSP generi `core/database/schemas/com.gernalix.personalhub.core.database.PersonalHubDatabase/11.json`; verifica migrazione 10→11 e compatibilità con gli upgrade precedenti. Correggi solo incongruenze concrete tra entity, migration e schema.
6. Se build/test falliscono, applica il minimo fix nei file direttamente coinvolti e ripeti soltanto il controllo fallito + dipendenze necessarie. Niente refactor/cleanup/ottimizzazioni fuori scope e niente retry identici senza nuova evidenza.
7. QA Android con il workflow `test-android-apps`, usando prima emulatore/QA package per i flussi che modificano dati. Verifica almeno:
   - Home → Registro;
   - una modifica People produce una voce leggibile e il tap apre la persona pertinente;
   - una modifica Places o conto reversibile mostra Undo; Undo ripristina il dato, marca l'originale come annullato e aggiunge l'azione compensativa;
   - un caso stale/dipendente non viene annullato;
   - filtri/paging non mostrano raw ID/UUID;
   - Cerca continua a mostrare dati per il loro tempo di dominio e non per `occurred_at` del Registro;
   - Composer continua a usare relazioni persistenti e non viene alterato.
8. Solo dopo PASS: integra il branch in `main` senza force e senza perdere commit remoti, esegui il minimo smoke post-merge se il merge ha introdotto differenze, commit/push PersonalHub.
9. Crea il final main APK della versione risultante, senza rebuild successivi; installa **quello stesso artefatto** sul Pixel fisico secondo il bootstrap PersonalHub e invia **quello stesso APK** via Telegram col filename `<versione>.apk`, senza caption/testo extra.
10. Registra l'evento MegaVault richiesto dalle regole PersonalHub. Poi finalizza questo prompt nella roadmap con il comando canonico sotto e fermati.

# Non-goal
- Non ampliare la copertura undo oltre i casi già dichiarati sicuri solo per “avere Undo ovunque”.
- Non trasformare il Registro in event sourcing generale.
- Non cambiare il significato di Cerca o Composer.
- Non catturare tabelle operative/sync/cache né segreti.
- Non rifare design, inventory dei write path o benchmark generali.
- Non fare test distruttivi sul package reale prima del final install autorizzato.

# Acceptance / stop
PASS solo se: compile + test mirati + schema 11/migrazione + QA Android sopra passano; nessuna regressione semantica Cerca/Composer; branch integrato e `main` pushato; final APK installato sul Pixel e consegnato via Telegram; evento MegaVault registrato.

Se un blocker esterno impedisce build/device/Telegram/push, riporta `BLOCKED` con la sola evidenza utile e fermati. Dopo PASS non fare audit o verifiche aggiuntive.

Su PASS finalizza la roadmap:
```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 835204 --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 835204
```

Output finale conciso in italiano: risultato, eventuali fix locali necessari, test/QA, versione/APK, Pixel, Telegram, commit/push, eventuali colli di bottiglia realmente incontrati.
