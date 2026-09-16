[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=893806 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=3/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STRICT`

# Goal
Aggiungere a Luoghi un journal diagnostico persistente di OGNI tentativo **utente** di check-in basato sul riconoscimento della posizione, inclusi falliti/ambigui/annullati/interrotti, senza contaminare le visite reali. Nella stessa unica sessione emulator chiudi una sola volta il debito QA UI della fase 1 Hub/episodi, senza riaprire la fase Timer già completata.

# Starting point autoritativo
- repo/workdir canonico: `/home/daniele/projects/PersonalHub`;
- fase 1 Hub/episodi: `3cfd170cc8a2b2155f8f531ce6efcb0fc116247f` + follow-up Timer Hub `99bcf743965d9d9508d33ad50ad97946285d08c8`;
- fase 2 Timer Now: `82d56960d4e7d83dcca34a230efcd7cdb87a6a4e`;
- i vecchi `HubContextComposerDeviceTest`, `HubContextExplorerDeviceTest`, `HubContextAllModulesDeviceTest` sono test fisici: NON modificarli né indebolirne i guard per farli girare su emulator;
- manca ancora una prova androidTest emulator-safe focalizzata su Home/Search/Episodi/fatigue;
- prompt autosufficiente: NON leggere README/roadmap/spiegazioni/MEMORY/MegaVault salvo blocker concreto.

# Lease + sync
1. Dal workdir canonico esegui `python3 tools/personalhub_task_lock.py acquire --prompt-id 893806`; failure => `RESULT=BLOCKED`, nessuna attesa.
2. Richiedi worktree pulito, poi `git fetch --prune origin && git pull --ff-only origin main`; registra SHA di `origin/main`. Se non è fast-forwardabile, BLOCKED: niente rebase/merge.
3. Prima del commit/push finale fai UNA `git fetch origin`; se `origin/main` è avanzato rispetto alla base, BLOCKED senza rebase/merge/rerun gate.
4. Rilascia sempre il lease a PASS/BLOCKED/FAIL.

# Routing — niente audit
Usa `.codex/CODE_MAP.tsv` solo per `places.checkin`, `places.data`, `database.schema`. Parti da `LuoghiHomeViewModel.checkInAtCurrentLocation()`, `CheckInCapsule`, `CheckInPolicy`, repository/DAO/schema mappati. Niente inventario Luoghi/core.

Facts già verificati:
- permission denied/location unavailable/unknown/ambiguous/cancel/failure non hanno oggi un journal persistente;
- `PlaceEvent` rappresenta visite reali e NON va riusato per failure diagnostici;
- matching dispone già di distanza/raggio/accuracy.

# Modello dati minimo
Nel solo `personalhub.db`, con migrazione canonica:
- attempt: id stabile, `startedAt`, `finishedAt`, source, stage/outcome, coordinate/accuracy solo se realmente disponibili, selected/matched place id, error code + messaggio sanificato;
- candidate: attempt id, place id, distanza, soglia/raggio effettivo, ranking/esito minimo necessario.
Usa colonne normali + FK/index essenziali; niente JSON opaco per schema stabile.

# Lifecycle
1. Crea l'attempt prima del primo abort possibile.
2. Stati terminali almeno equivalenti a `SUCCESS`, `PERMISSION_DENIED`, `LOCATION_UNAVAILABLE`, `NO_MATCH`, `AMBIGUOUS`, `USER_CANCELLED`, `PERSISTENCE_FAILED`, `INTERRUPTED`.
3. Non perdere la causa con `getOrNull()`: registra categoria/messaggio sanificato, mantenendo UI user-friendly.
4. Unknown → form nuovo luogo: conserva lo stesso attempt fino a create/cancel.
5. `IN_PROGRESS` lasciato da process death → `INTERRUPTED` al recovery, idempotente.
6. Scope = check-in user-triggered dalla posizione corrente + continuazioni. Geofence/automatic e check-in retroattivi restano fuori scope.
7. Nessun failure attempt crea `PlaceEvent` o rumore nel Registro globale.

# UI diagnostica minima
Una voce discreta `Diagnostica check-in`: recenti newest-first, filtro outcome/place, riga leggibile + dettaglio timestamp/accuracy/candidate-distanze-raggi/error, copia singolo report testuale. Nessuna telemetria/coordinate esterne.

# Verifica host prima del device
1. Migration/unit test mirati per schema, lifecycle, candidate e recovery. Su FAIL leggi il solo report pertinente, correggi il leaf e rilancia solo il test fallito; riconferma il set mirato una volta alla fine.
2. `./gradlew --quiet --console=plain checkArchitectureBoundaries` una sola volta.
3. Prepara, SOLO se assente, esattamente `app/src/androidTest/java/com/gernalix/personalhub/HubDiscoverabilityEpisodesEmulatorTest.kt`. Deve essere emulator-safe e verificare direttamente: Home espone spiegazioni Context/Search/Activity; Search mostra `Episodi salvati`; una fixture con context titolato è visibile e riapribile come lo stesso Context; wording fatigue corretto. Non riusare i test fisici.

# UNA sessione emulator
1. Avvia una volta con `python3 tools/android_emulator_control.py start` + `wait`; riusa il `target.serial`; niente `adb devices` o discovery AVD parallela.
2. Check-in: usa il task canonico `:feature:luoghi:connectedDebugAndroidTest` con `ANDROID_SERIAL=<serial>`, `--quiet --console=plain` e filtro alla sola nuova classe/test suite che copre permission denied + unknown/ambiguous + success. Failure non deve produrre `PlaceEvent`; success produce attempt `SUCCESS` + visita normale; migration preserva fixture.
3. Debito fase 1: UNA sola invocazione
   `ANDROID_SERIAL=<serial> ./gradlew :app:connectedAndroidTest -Ppersonalhub.testBuildType=qa -Pandroid.testInstrumentationRunnerArguments.class=com.gernalix.personalhub.HubDiscoverabilityEpisodesEmulatorTest --quiet --console=plain`.
4. Le invocazioni androidTest compilano gli APK necessari: niente `assembleDebug`, install manuale, navigation ADB o screenshot se le assertion sono probanti.
5. Stop emulator una volta con `android_emulator_control.py stop`. Per comandi lunghi usa una sola attesa bloccante o controlli radi, non polling ogni 30 s.

# Non-goal
Niente tuning raggio 75 m, geofence redesign/instrumentazione, mappa, sync cloud, cleanup storico, telemetria remota, riapertura Timer Now o bug collaterali non bloccanti.

# Campagna
Fase intermedia: niente bump `version.txt`, Pixel reale, APK/Telegram. Push una volta dopo PASS. La fase 4 non ripete migration/check-in/Hub QA se i file coperti restano invariati.

# Acceptance
PASS se ogni tentativo user-triggered è ricostruibile, failure non crea visite, migration preserva dati, recovery è idempotente, diagnostica è leggibile, gate Luoghi mirati PASS e `HubDiscoverabilityEpisodesEmulatorTest` PASS.

# Stop
Dopo acceptance PASS e base remota invariata: commit/push PersonalHub una volta. Prova `roadmap_guard complete --prompt-id 893806 --dry-run`; se ready esegui complete. Solo su `prompt_identity_mismatch` dovuto a task indipendente precedente usa `reconcile --prompt-id 893806 --result PASS` dry-run + `--confirm-executed`. Altri errori guard => BLOCKED. Rilascia il lease.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe.
