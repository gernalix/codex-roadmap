PROMPT_ID=294731 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Esegui SOLO la validazione locale finale Google Play del `main` PersonalHub già completato dal task `861305`: crea una sola volta l'AAB firmato, ispezionalo e fai uno smoke bounded dell'APK set derivato dall'AAB su `Pixel_8a`. Nessun upload su Play Console.

# Starting point e precondizioni
- repo: `/home/daniele/projects/PersonalHub`, project_id `49`, unico branch remoto `main`;
- questo prompt va lanciato solo dopo `861305` PASS/finalizzato;
- baseline minima che deve essere antenata del RUN_HEAD: `c457eee4880d0f58ed271d5069d78ecdd500059e`;
- `version.txt` deve essere `51` e `app/src/main/assets/datasette-lite/` deve essere presente/non vuoto;
- il RUN_HEAD esatto viene fissato una sola volta all'inizio perché `861305` crea necessariamente il commit finale; non interrogare/rilanciare GitHub Actions;
- nessuna modifica al codice/repo è ammessa in questo task.

# Vincoli
- Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault e niente audit repo-wide.
- applicationId: `com.gernalix.personalhub`.
- AAB: esegui esattamente una volta `./gradlew --no-configuration-cache :app:bundlePlay`.
- signing: `/home/daniele/.config/codex/secrets/android_signing.env`; Maps/Routes: `/home/daniele/.config/codex/secrets/map.env`. Non stampare secret.
- usa solo l'AVD canonico `Pixel_8a`; mai Pixel/TCL fisici.

# Esecuzione minima
1. Acquisisci `python3 tools/personalhub_task_lock.py acquire --prompt-id 294731`. In un unico preflight: richiedi worktree pulito e branch `main`; fai un solo fetch + `git merge --ff-only origin/main`; fissa `RUN_HEAD=origin/main=HEAD`; verifica che la baseline sopra sia antenata, `version.txt=51` e gli asset Datasette Lite siano presenti. Se no => `BLOCKED`. Nessun altro discovery Git.
2. In un unico controllo bounded verifica, senza mostrare valori, file dei segreti leggibili, `ANDROID_SHARED_*` richiesti presenti/non vuoti, keystore leggibile mode `0600` e una chiave Maps/Routes valida per il build.
3. Costruisci UNA sola volta l'AAB firmato. Nessun bump versione e nessuna seconda build Gradle.
4. Sul solo AAB prodotto: esegui `python3 tools/check_play_bundle.py`; verifica integrità/firma e registra SHA-256 + fingerprint pubblico; estrai package/version/min/target SDK con `targetSdk >= 36`; dal manifest effettivo conferma assenza di `ACCESS_BACKGROUND_LOCATION`, `READ_CALL_LOG`, `READ_PHONE_STATE`, `SYSTEM_ALERT_WINDOW`, `USE_FULL_SCREEN_INTENT`, `com.supercontacts.app.CallStateReceiver`, `com.supercontacts.app.CallOverlayDebugReceiver`, `com.gernalix.luoghi.capsules.geofence.PlaceGeofenceReceiver`. Se manca soltanto bundletool, scarica una sola release ufficiale stabile in `/tmp`.
5. Avvia/riusa `Pixel_8a` solo tramite `python3 tools/android_emulator_control.py start` + `wait`. Da QUELL'AAB genera un solo APK set per il seriale dell'emulatore; verifica zip-alignment 16 KiB con lo `zipalign` SDK (`-c -P 16 -v 4`) e installa lo stesso set. Nessuna ricompilazione.
6. Smoke bounded senza dati personali/sync produzione: avvio senza crash; Home; Settings con Privacy policy; People; Places; nessuna richiesta call-log/phone/overlay/full-screen/background-location; apri una sola superficie Places che inizializza Maps/Places e verifica assenza di crash di configurazione.
7. Conserva l'AAB nel normale output Gradle; elimina solo temp APK set/bundletool; ferma l'emulatore tramite facade se avviato dal task. Rilascia il task lock in ogni esito. PASS => stop immediato.

# Acceptance
PASS solo se AAB firmato/verificato, policy/SDK corretti, native/16 KiB PASS, APK set derivato dallo stesso AAB con zip-alignment PASS e installato su `Pixel_8a`, smoke PASS e output contiene path AAB + SHA-256 + fingerprint pubblico senza secret.

# Finish/output
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 294731 --confirm-executed`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `HEAD`, `AAB`, `SHA256`, `SIGNING_CERT`, `MANIFEST`, `EMULATOR_SMOKE`, `BLOCKER`.
