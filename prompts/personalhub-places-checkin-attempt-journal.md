[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=893806 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=3/4 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Aggiungere a Luoghi un journal diagnostico persistente di OGNI tentativo **utente** di check-in basato sul riconoscimento della posizione, inclusi falliti/ambigui/annullati/interrotti, senza contaminare le visite reali. Nella stessa sessione emulator chiudi una sola volta il debito QA UI della fase 1 Hub/episodi, senza riaprire la fase Timer già completata.

# Starting point autoritativo
- repo canonico: `/home/daniele/projects/PersonalHub`;
- fase 1 `PROMPT_ID=838979`: implementazione Hub/episodi in `3cfd170cc8a2b2155f8f531ce6efcb0fc116247f`;
- fase 2 `PROMPT_ID=314719`: Timer Now completato in `82d56960d4e7d83dcca34a230efcd7cdb87a6a4e`;
- audit successivo ha ripristinato i guard dei vecchi androidTest fisici Hub: NON modificarli per farli girare su emulator;
- la fase 1 non ha ancora una prova androidTest emulator-safe focalizzata su Home/Search/Episodi/fatigue; questa è l'unica verifica ereditata da chiudere qui;
- prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault salvo blocker concreto.

# Lease + sync + emulator helper
1. Esegui direttamente `python3 tools/personalhub_task_lock.py acquire --prompt-id 893806`; se non acquisisce, `RESULT=BLOCKED` senza attesa.
2. Subito dopo: richiedi worktree pulito, `git fetch --prune origin && git pull --ff-only origin main`, quindi registra lo SHA di `origin/main` come base remota. Se il fast-forward non è possibile, BLOCKED: niente rebase/merge.
3. Per la QA emulator usa solo `python3 tools/android_emulator_control.py status|start|wait|stop`; riusa il `target.serial` restituito. Non aprire `AGENTS.md` soltanto per lease/emulator e non fare discovery ADB/AVD parallela salvo blocker concreto.
4. Prima del commit/push finale: UNA `git fetch origin`; se `origin/main` è avanzato rispetto alla base registrata, `RESULT=BLOCKED` e STOP senza rebase/merge/rerun dei gate. Non assorbire lavoro PersonalHub concorrente nella stessa sessione.
5. Dopo PASS/BLOCKED/FAIL rilascia sempre `python3 tools/personalhub_task_lock.py release --prompt-id 893806`.

# Routing — scope stretto
Usa `.codex/CODE_MAP.tsv` solo per `places.checkin`, `places.data`, `database.schema`. Parti da `LuoghiHomeViewModel.checkInAtCurrentLocation()`, `CheckInCapsule`, `CheckInPolicy`, repository/DAO/schema già mappati. Niente audit Luoghi/core.
Facts già verificati:
- oggi permission denied/location unavailable/unknown/ambiguous/cancel/failure non hanno un journal persistente;
- `PlaceEvent` rappresenta visite effettive e NON va riusato per failure diagnostici;
- matching dispone già di distanza/raggio/accuracy utili alla diagnosi.

# Modello dati minimo
Nel `personalhub.db`, con migrazione canonica:
- attempt: id stabile, `startedAt`, `finishedAt`, source, stage/outcome, location disponibile (solo campi realmente forniti), selected/matched place id, error code + messaggio sanificato;
- candidate: attempt id, place id, distanza, soglia/raggio effettivo, ranking/esito minimo necessario.
Colonne normali + FK/index essenziali; niente JSON opaco se lo schema è stabile.

# Lifecycle obbligatorio
1. Persisti l'attempt prima del primo abort possibile.
2. Stati terminali almeno equivalenti a `SUCCESS`, `PERMISSION_DENIED`, `LOCATION_UNAVAILABLE`, `NO_MATCH`, `AMBIGUOUS`, `USER_CANCELLED`, `PERSISTENCE_FAILED`, `INTERRUPTED`.
3. Non usare `getOrNull()` perdendo la causa: registra categoria/messaggio sanificato, UI invariata/user-friendly.
4. Unknown -> form nuovo luogo: conserva lo stesso attempt fino a create/cancel.
5. `IN_PROGRESS` lasciato da process death -> `INTERRUPTED` al recovery, idempotente.
6. Scope funzionale = flow di check-in user-triggered dalla posizione corrente e sue continuazioni. **Geofence/automatic check-in sono fuori scope** salvo riuso naturale dello stesso journal senza nuova esplorazione o codice dedicato. Check-in retroattivi verso luogo già noto restano esclusi.
7. Nessun failure attempt deve creare visita o rumore nel Registro globale.

# UI diagnostica minima
Una voce discreta `Diagnostica check-in`: recenti newest-first, filtro outcome/place, riga comprensibile + dettaglio con timestamp/accuracy/candidate-distanze-raggi/error; copia report testuale singolo. Nessuna telemetria/coordinate esterne.

# Verifica a costo controllato
1. Prima: migration/unit test mirati per schema, lifecycle, candidate e recovery. Failure => leaf fix basato sull'errore, poi solo il test fallito; non rilanciare identico l'intero set dopo ogni ipotesi.
2. Esegui `./gradlew --quiet --console=plain checkArchitectureBoundaries` una volta perché cambia persistence ownership/schema.
3. Prima di avviare emulator, prepara SOLO se ancora assente un singolo androidTest **emulator-safe** focalizzato sul debito fase 1. Deve verificare direttamente: Home espone le spiegazioni Context/Search/Activity; Search mostra `Episodi salvati`; un episodio titolato creato nella fixture QA è visibile e riapribile come lo stesso Context; il wording fatigue è quello previsto. Non riusare né modificare `HubContextComposerDeviceTest`, `HubContextExplorerDeviceTest`, `HubContextAllModulesDeviceTest` o altri test dichiaratamente fisici per aggirare i loro guard.
4. Solo dopo host PASS, avvia UNA sessione Pixel_8a emulator con `android_emulator_control.py start` + `wait` e riusa quel serial fino allo stop.
5. Esegui i nuovi test check-in nella più piccola invocazione androidTest pertinente con `--quiet --console=plain`, filtrata a permission denied + unknown/ambiguous + success. Verifica: failure non produce `PlaceEvent`; success produce attempt SUCCESS + visita normale; migration preserva dati fixture.
6. Nella STESSA sessione emulator esegui una sola volta anche il test app della fase 1 con il task canonico noto: `ANDROID_SERIAL=<serial> ./gradlew :app:connectedAndroidTest -Ppersonalhub.testBuildType=qa -Pandroid.testInstrumentationRunnerArguments.class=<classe_fase1> --quiet --console=plain`. Nessuna suite Hub fisica, nessuna navigazione manuale ADB, nessun secondo screenshot se il test è già probante.
7. Le invocazioni androidTest compilano gli APK necessari: niente `assembleDebug` separato. Stop emulator una volta. Nessun Pixel/TCL/release in questa fase.

# Non-goal
Niente tuning raggio 75 m, geofence redesign/instrumentazione, mappa, sync cloud, cleanup storico, telemetria remota, riapertura del lavoro Timer Now o bug collaterali non bloccanti.

# Campagna
Fase intermedia: niente bump `version.txt`, Pixel reale, APK/Telegram. Push una volta dopo PASS. La fase 4 NON dovrà ripetere migration/UI test di questa fase se i relativi file restano invariati.

# Acceptance
PASS se ogni tentativo user-triggered è ricostruibile, failure non crea visite, migrazione preserva dati, recovery è idempotente, diagnostica è leggibile, i gate Luoghi mirati PASS e il singolo test emulator-safe chiude davvero Home/Search/Episodi/fatigue della fase 1.

# Stop
Solo dopo acceptance PASS e base remota invariata: commit/push PersonalHub una volta, quindi
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806`.
Se `roadmap_guard` rifiuta il completamento, `RESULT=BLOCKED` anche con codice PASS; non manipolare manualmente la roadmap. Rilascia il lease. Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe.
