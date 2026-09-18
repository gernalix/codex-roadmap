PROMPT_ID=294731 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Esegui SOLO la validazione locale finale della release Google Play di PersonalHub già verificata da remoto: crea una sola volta l'AAB firmato con i segreti canonici locali, ispezionalo e fai uno smoke bounded sull'AVD `Pixel_8a`. Nessun upload su Play Console.

# Gate già chiuso fuori da Codex
- repo: `/home/daniele/projects/PersonalHub`, branch `main`, project_id `49`;
- HEAD remoto atteso e già verificato: `7cf69218b5956c13e70194fe1801804c4143e4fc`;
- il Play Store preflight di questo HEAD è PASS, inclusi build/minify, manifest policy e verifica 16 KiB delle librerie native 64-bit;
- NON interrogare/rilanciare GitHub Actions e NON diagnosticare/fixare CI remoto;
- se dopo un solo `git fetch origin main` `origin/main` non è esattamente l'HEAD atteso, `BLOCKED` e stop: serve una nuova verifica remota prima di consumare lavoro locale.

# Vincoli
- Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault e niente audit repo-wide.
- Nessuna modifica al codice/repo in questo task. Un difetto prodotto rilevato => `BLOCKED`, riportalo senza investigazione estesa.
- applicationId: `com.gernalix.personalhub`.
- AAB: esegui esattamente una volta `./gradlew --no-configuration-cache :app:bundlePlay`.
- signing: `/home/daniele/.config/codex/secrets/android_signing.env`; Maps/Routes: `/home/daniele/.config/codex/secrets/map.env`. Non stampare secret (`cat`, `env`, `set -x` vietati).
- usa solo l'AVD canonico `Pixel_8a`; mai Pixel/TCL fisici. Helper canonico: `python3 tools/android_target_preflight.py start`.

# Esecuzione minima
1. In un unico preflight shell: verifica worktree pulito, fai un solo `git fetch origin main`, richiedi `origin/main == 7cf69218b5956c13e70194fe1801804c4143e4fc`, quindi `git merge --ff-only origin/main`. Dirty/divergenza/mismatch => `BLOCKED`, nessun retry/stash/rebase.
2. In un unico controllo bounded verifica, senza mostrare valori: file dei segreti leggibili; tutti gli `ANDROID_SHARED_*` richiesti presenti/non vuoti; keystore referenziato leggibile e mode `0600`; una chiave Maps/Routes accettata dal build presente.
3. Costruisci UNA sola volta l'AAB firmato col comando sopra. Nessun bump versione e nessuna seconda build Gradle.
4. Sul solo AAB prodotto, riusa il tooling già nel repo/SDK/cache:
   - `python3 tools/check_play_bundle.py` deve PASS; non considerare la semplice presenza di `.so` un errore: lo script valida AGP e allineamento ELF 16 KiB delle librerie native 64-bit;
   - verifica integrità/firma e registra SHA-256 + fingerprint pubblico del certificato;
   - estrai package, versionCode/versionName, min/target SDK (`targetSdk >= 36`);
   - dal manifest effettivo conferma assenza di `ACCESS_BACKGROUND_LOCATION`, `READ_CALL_LOG`, `READ_PHONE_STATE`, `SYSTEM_ALERT_WINDOW`, `USE_FULL_SCREEN_INTENT`, `com.supercontacts.app.CallStateReceiver`, `com.supercontacts.app.CallOverlayDebugReceiver`, `com.gernalix.luoghi.capsules.geofence.PlaceGeofenceReceiver`.
   Se manca soltanto bundletool e non esiste nel toolchain/cache, scarica una sola release ufficiale stabile in `/tmp`; niente installazione globale.
5. Avvia/riusa `Pixel_8a` con l'helper canonico. Da QUELL'AAB genera un solo APK set con bundletool per il seriale dell'emulatore. Prima dell'installazione esegui sul set/APK pertinente la verifica di zip-alignment 16 KiB con lo `zipalign` già nell'Android SDK (`-c -P 16 -v 4`); poi installa lo stesso set sull'emulatore. Nessuna ricompilazione e nessun device fisico.
6. Smoke bounded, senza dati personali/sync produzione: avvio senza crash; Home; Settings con `Privacy policy`; apri People e Places una volta; nessuna richiesta call-log/phone/overlay/full-screen/background-location; apri una sola superficie Places che inizializza Maps/Places e verifica assenza di crash di configurazione.
7. Conserva l'AAB nel normale output Gradle; elimina solo APK set/temp bundletool in `/tmp`. PASS => stop immediato, senza benchmark, audit dipendenze, altri moduli o test aggiuntivi.

# Acceptance
PASS solo se AAB firmato e verificato, policy/SDK corretti, verifica native/16 KiB PASS, APK set derivato dallo stesso AAB con zip-alignment 16 KiB PASS e installato su `Pixel_8a`, smoke sopra PASS e output finale contiene path AAB + SHA-256 + fingerprint pubblico senza secret.

# Finish/output
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 294731 --confirm-executed`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `HEAD`, `AAB`, `SHA256`, `SIGNING_CERT`, `MANIFEST`, `EMULATOR_SMOKE`, `BLOCKER`.
