PROMPT_ID=334679 | PARENT_PROMPT_ID=243871 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Esegui solo la validazione locale finale Google Play del `main` PersonalHub già completato da 811925: crea una volta l'AAB firmato, ispezionalo e fai uno smoke bounded dell'APK set derivato sull'AVD `Pixel_8a`. Nessun upload Play e nessuna modifica repo.

# Precondizioni
- esegui dopo 811925 PASS;
- repo `/home/daniele/projects/PersonalHub`, canonical main, worktree pulito;
- usa la versione corrente di `version.txt`: non hardcodare un numero futuro e non fare bump;
- signing `~/.config/codex/secrets/android_signing.env`, Maps/Routes `~/.config/codex/secrets/map.env`; mai stampare secret.

# Esecuzione minima
1. Lease PH. Un solo fetch/ff main; fissa RUN_HEAD e verifica asset Datasette Lite presenti.
2. Gate secret/keystore bounded senza mostrare valori.
3. Costruisci esattamente una volta `./gradlew --no-configuration-cache :app:bundlePlay`.
4. Sul solo AAB: `tools/check_play_bundle.py`, firma/integrità, SHA-256/fingerprint pubblico, package/version/min/target SDK (target>=36), manifest senza permessi/componenti vietati già codificati dal checker. Scarica bundletool ufficiale in /tmp solo se manca.
5. Avvia/riusa solo `Pixel_8a` tramite facade; genera un solo APK set dallo stesso AAB, verifica 16-KiB alignment e installa quello stesso set. Nessuna ricompilazione.
6. Smoke: avvio/Home/Settings Privacy/People/Places e una superficie Maps; nessun crash né richiesta di permessi vietati. Cleanup temp e AVD; rilascia lease.

# Acceptance / stop
PASS con AAB firmato/verificato, policy/SDK/alignment PASS e smoke dello stesso artifact PASS. Nessun commit/bump/upload. Finalizza PROMPT_ID 334679. Output max 7 righe.
