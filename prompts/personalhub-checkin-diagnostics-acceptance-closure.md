[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=529184 | project_id=49 | campaign_id=personalhub-20260916-checkin-diagnostics-closure | phase=1/1 | model=GPT-5.5 | reasoning=medium | MegaVault=STRICT`

# Goal
Chiudi SOLO i requisiti rimasti incompleti dopo `PROMPT_ID=893806` nel journal diagnostico del check-in Luoghi, preservando davvero la diagnostica nel tempo e provandola con toolchain Android/Room locale.

# Starting point autoritativo — niente discovery generale
Repo/workdir canonico: `/home/daniele/projects/PersonalHub`.

Base remota verificata al momento della preparazione: `a71d52e0b856df6c2d337839cfcb7ea4f954a1da` (`Add Luoghi check-in attempt diagnostics`). Prima di editare sincronizza solo con `git fetch --prune origin && git pull --ff-only origin main` se il worktree è pulito e registra lo SHA base effettivo. Nessun rebase/merge.

L'audit post-run ha verificato tre lacune concrete nel codice corrente:

1. `HomeScreen.CheckInDiagnosticsPanel` mostra solo `attempts.take(5)` e NON implementa i filtri richiesti per outcome e luogo.
2. `diagnosticDetail` / `diagnosticReport` non mostrano i candidate del tentativo (distanza, threshold/raggio, rank/result), benché `check_in_attempt_candidates` esista e il DAO abbia già `checkInAttemptCandidates(attemptId)`.
3. `CheckInAttemptCandidateEntity` ha oggi una FK `place_id -> places.uuid` con `onDelete = CASCADE`: cancellare realmente un luogo può quindi cancellare evidenza diagnostica storica dei candidate. Per un journal persistente questo è un difetto da correggere; la diagnostica deve sopravvivere alla cancellazione del luogo.

Non rileggere README/roadmap/spiegazioni/MEMORY/MegaVault. Usa solo i file/simboli seguenti e amplia soltanto per una failure concreta:
- `contracts/database/.../PlaceEntities.kt`
- `contracts/database/.../PlaceDao.kt`
- `feature/luoghi/.../data/PlaceRepository.kt`
- `feature/luoghi/.../LuoghiHomeViewModel.kt`
- `feature/luoghi/.../ui/home/HomeScreen.kt`
- `core/database/.../PersonalHubDatabase.kt`
- `feature/luoghi/src/test/.../PlacesHistoryMapGeofencingTest.kt`
- `core/database/src/test/.../DatabaseMigrationSafetyTest.kt`
- `feature/luoghi/src/androidTest/.../CheckInAttemptJournalInstrumentedTest.kt`

Se devi localizzare una costruzione `CheckInAttemptCandidateEntity`, fai un solo `rg -n 'CheckInAttemptCandidateEntity\\('` nei path già indicati. Niente dump di `.codex/CODE_MAP.tsv` o inventory del modulo.

# Lease e Git
1. `python3 tools/personalhub_task_lock.py acquire --prompt-id 529184`; failure => `BLOCKED`, niente attesa.
2. Mantieni il diff non committato fino a tutti i gate tecnici PASS.
3. Prima del commit finale fai UNA `git fetch origin`; se `origin/main` è avanzato rispetto alla base effettiva, `BLOCKED`, niente rebase/merge/rerun.
4. Rilascia sempre il lease a PASS/BLOCKED/FAIL.

# Implementazione minima

## A. Persistenza candidate
- Mantieni la FK `attempt_id -> check_in_attempts.id` con cascade.
- Rimuovi la dipendenza distruttiva `place_id -> places.uuid` dai candidate diagnostici: la cancellazione di un luogo non deve eliminare righe candidate storiche.
- Conserva nel candidate anche un nome leggibile snapshot del luogo al momento del tentativo (`place_name_snapshot` o equivalente nullable), così report/filtri restano utili dopo delete/rename.
- Popola lo snapshot quando registri i candidate; per i dati già esistenti della DB v14, la migration deve copiarli e valorizzare lo snapshot dal luogo corrente quando disponibile.
- Questo richiede una migration Room stretta `14 -> 15`, senza toccare altre tabelle o semantiche `PlaceEvent`. Aggiorna lo schema esportato Room e il test migration safety. Nessuna destructive migration.

## B. Diagnostica UI completa
- In “Diagnostica check-in” aggiungi filtri locali, semplici e stabili per **outcome** e **luogo**. Non creare una nuova schermata o navigazione.
- Ogni row/detail deve poter mostrare in modo leggibile i candidate del tentativo: luogo/snapshot, distanza, threshold/raggio usato, rank e result.
- Il report copiato per singolo tentativo deve contenere gli stessi dati candidate oltre a timestamp, location/accuracy, stage/outcome ed errore già presenti.
- Il filtro luogo deve poter trovare anche un luogo presente solo tra i candidate, non soltanto selected/matched.
- Mantieni newest-first e il pannello discreto; nessun redesign.

Scegli la rappresentazione dati minima compatibile con Room esistente: projection/query dedicata o relazione già supportata. Niente nuove astrazioni generiche.

# Test host — massimo due invocazioni Gradle
1. Prima invocazione mirata: test Luoghi + migration nello stesso comando. Aggiungi/asserta direttamente:
   - filter outcome;
   - filter luogo anche via candidate;
   - report/detail contiene distance + threshold/radius + rank/result;
   - candidate sopravvive alla cancellazione del luogo e conserva snapshot leggibile;
   - migration 14→15 preserva attempt/candidate fixture e non crea `PlaceEvent`.
2. Solo se la prima FAIL: leggi il JUnit XML mirato sotto `build/test-results/...`, correggi il leaf e rilancia una volta il set mirato.
3. Dopo l'ultima modifica a Kotlin/resources esegui UNA sola conferma finale del set mirato se necessaria. Non fare suite generale.
4. `checkArchitectureBoundaries` solo se i file toccati attraversano un boundary rilevante; altrimenti non ripeterlo perché era già PASS in `893806`.

# UNA sessione emulator
Solo dopo host PASS:
1. `python3 tools/android_emulator_control.py start && python3 tools/android_emulator_control.py wait`; riusa il serial restituito.
2. Esegui SOLO la suite `CheckInAttemptJournalInstrumentedTest` aggiornata con `ANDROID_SERIAL=<serial> :feature:luoghi:connectedDebugAndroidTest ... --quiet --console=plain`.
3. La suite deve provare sul DB/device almeno: attempt/candidate persistono; delete del luogo non elimina il candidate; report/filter data path è disponibile con snapshot. Se le assertion host/UI pure coprono i filtri, non fare navigation ADB né screenshot.
4. Stop emulator una volta.

# Acceptance audit obbligatorio
Prima di PASS verifica esplicitamente requisito→evidenza per tutti questi punti: filtro outcome, filtro luogo, candidate distance/threshold/rank/result in dettaglio, stessi candidate nel report copiabile, persistenza candidate dopo delete luogo, migration 14→15, nessun `PlaceEvent` per failure, test emulator PASS. Un generico “test verde” senza assertion su un punto NON vale come prova.

# Non-goal
Niente tuning del raggio check-in, geofence, mappa, sync cloud, redesign Luoghi, cleanup storico, refactor repository/DAO, nuove feature Hub, bump/release APK, test Pixel/TCL o modifiche fuori dai requisiti sopra.

# Stop
Dopo PASS tecnico e solo allora commit/push una volta. Poi:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 529184 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 529184`

Se il guard richiede `--result PASS` perché il task risulta già tentato, aggiungilo sia al dry-run sia al complete; non usare `reconcile` salvo mismatch causato da modifica concorrente della roadmap che non puoi risolvere senza violare la policy Git.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `SCHEMA`, `FILTERS`, `CANDIDATES`, `PERSISTENCE`, `HOST_TEST`, `EMULATOR`, `COMMIT/GUARD`.