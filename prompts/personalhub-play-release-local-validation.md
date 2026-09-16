PROMPT_ID=294731 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal
Valida sul Fedora reale la variante Google Play di PersonalHub già preparata e impacchettata sul remoto, produci UNA volta l'Android App Bundle firmato con il keystore canonico, ispeziona bundle/manifest/firma e installa l'artefatto derivato dall'AAB sull'emulatore Pixel_8a per uno smoke test bounded. Non caricare nulla su Play Console.

# Starting point autoritativo
- repo canonico: `/home/daniele/projects/PersonalHub`, branch `main`, project_id `49`;
- applicationId Play: `com.gernalix.personalhub`;
- build type Play già definito: `play`, derivato da `release`, minified/shrunk e non debuggable;
- commit remoto minimo con packaging Play CI: `36b4b7a3ef1692b9172b24f9f4667b323a3ad630` o successivo;
- comando bundle canonico firmato locale: `./gradlew --no-configuration-cache :app:bundlePlay`;
- signing locale canonico: `/home/daniele/.config/codex/secrets/android_signing.env`; non stampare mai password, secret o private-key material;
- il Play preflight remoto costruisce già un AAB minified/shrunk **senza signing secret** con un opt-in ristretto alla sola task-set CI, oltre a `lintPlay`, merged-manifest policy check e `tools/check_play_bundle.py`;
- `tools/check_play_bundle.py` fallisce se l'AAB manca/non è leggibile, supera il ceiling preflight o introduce librerie native `.so` senza una verifica esplicita di compatibilità 16 KiB;
- la build Play remota rimuove background location, `READ_CALL_LOG`, `READ_PHONE_STATE`, `SYSTEM_ALERT_WINDOW`, `USE_FULL_SCREEN_INTENT`, receiver call-overlay e geofence receiver; non reintrodurli;
- privacy policy e release guide sono già nel repo e il link Privacy è già esposto nelle Settings;
- i test deterministici/sandboxabili globali vengono completati dal task roadmap `483921` prima di questo gate: NON duplicare suite host già verdi;
- usa l'AVD canonico `Pixel_8a`; non installare la variante Play sul Pixel fisico e non rischiare il database reale.

Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault, non fare audit repo-wide e non modificare codice salvo blocker locale che impedisca di validare l'artefatto già preparato.

# Esecuzione minima
1. Fotografia Git del solo checkout PersonalHub. Se pulito: UNA sync bounded `git fetch origin main && git merge --ff-only origin/main`; dirty non pertinente, fetch/merge fallisce o diverge => `BLOCKED`, stop. Niente stash/rebase/retry.
2. Verifica che HEAD includa `36b4b7a...` e che il **Play Store preflight** pertinente all'ultimo commit code-bearing sia verde. Se HEAD è più recente solo per documentazione/non-code, riusa quel PASS. Non rilanciare GitHub Actions e non rifare `lintPlay`, `processPlayMainManifest` o il bundle unsigned localmente.
3. Verifica senza stampare valori che il signing env esista, sia leggibile e contenga tutti gli `ANDROID_SHARED_*` richiesti; verifica che il keystore referenziato sia file leggibile mode 0600. Nessun output di secret.
4. Costruisci UNA sola volta l'AAB firmato: `./gradlew --no-configuration-cache :app:bundlePlay`. Non fare bump di `version.txt` in questo task: usa il versionCode/versionName già presenti nell'HEAD remoto.
5. Sul bundle prodotto, usando tooling Android/JDK già disponibile e preferendo il bundletool già presente nell'installazione/cache locale:
   - verifica integrità/firma dell'AAB;
   - registra solo fingerprint pubblico del certificato, SHA-256 del file, package, versionCode/versionName, min/target SDK;
   - conferma dal manifest effettivo del bundle che NON compaiano `ACCESS_BACKGROUND_LOCATION`, `READ_CALL_LOG`, `READ_PHONE_STATE`, `SYSTEM_ALERT_WINDOW`, `USE_FULL_SCREEN_INTENT`, `com.supercontacts.app.CallStateReceiver`, `com.supercontacts.app.CallOverlayDebugReceiver`, `com.gernalix.luoghi.capsules.geofence.PlaceGeofenceReceiver`;
   - conferma che `targetSdk >= 36`;
   - se l'AAB contiene librerie native `.so`, `BLOCKED`: il preflight remoto dovrebbe averlo impedito e serve prima chiudere la compatibilità 16 KiB nel repo, non improvvisare qui.
   Se manca soltanto bundletool e non esiste una copia ufficiale già presente nel toolchain/cache, scarica UNA versione ufficiale stabile in `/tmp` con checksum/source verificabile; non installarla globalmente.
6. Avvia/riusa solo l'AVD `Pixel_8a`. Genera da QUELL'AAB un APK set per il device con bundletool, installalo sull'emulatore e non sul Pixel/TCL fisici. Nessuna seconda build Gradle.
7. Smoke bounded sull'emulatore:
   - package avvia senza crash;
   - Home visibile;
   - Settings si apre e mostra `Privacy policy`;
   - apri People e Places una volta ciascuno e verifica che la variante Play non presenti richiesta call-log/phone/overlay/full-screen/background-location né crash da capability rimossa;
   - non inserire dati personali reali e non testare sync contro endpoint di produzione.
8. Conserva l'AAB verificato nel normale output Gradle e riporta path + SHA-256. Elimina solo APK set/temp bundletool creati in `/tmp`. Non caricare artifact su GitHub/Telegram/Play Console.
9. PASS => stop immediato; niente benchmark, Pixel reale, audit dipendenze, test di altri moduli o build APK aggiuntive.

# Acceptance
PASS solo se:
- checkout sincronizzato con `origin/main`, include il commit minimo e Play preflight remoto pertinente verde;
- AAB `bundlePlay` costruito una sola volta con signing canonico e verificato;
- package/version/SDK coerenti e policy surface proibita assente dal bundle effettivo;
- nessuna libreria nativa non validata è presente;
- AAB-derived APK set installato sull'emulatore Pixel_8a senza ricompilazione;
- Home/Settings/People/Places smoke PASS e nessuna capability esclusa viene richiesta;
- path AAB + SHA-256 + fingerprint pubblico del certificato sono riportati senza secret.

# Non-goal
Niente upload Play Console, store listing/Data safety/content rating, cambio Play App Signing, bump versione, nuove feature, refactor, lint/suite/bundle unsigned duplicati, Pixel/TCL fisici, APK Telegram o modifica MegaVault.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 294731 --confirm-executed`

Il finalizzatore è race-safe per push non-fast-forward concorrenti; niente dry-run separato né controlli Git equivalenti dopo `status=completed|already_completed`.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `HEAD/CI`, `AAB`, `SHA256`, `SIGNING_CERT`, `MANIFEST`, `EMULATOR_SMOKE`, `BLOCKER`.
