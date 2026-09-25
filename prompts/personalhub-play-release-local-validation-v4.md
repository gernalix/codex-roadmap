PROMPT_ID=788606 | PARENT_PROMPT_ID=334679 | project_id=49 | MegaVault=FAST

# Goal
Congela una sola revisione finale PersonalHub e produci UNA VOLTA gli artefatti firmati/minificati che 913264 installerà sul Pixel.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- parte solo dopo 840907 PASS e integrazione su main;
- release ha già minify/resource shrink/proguard optimize attivi.

# Esecuzione ottimizzata
1. Verifica che main sia pulito/sincronizzato e contenga 707603+840907; nessun altro lavoro PH sorgente rilevante deve essere pendente.
2. Congela FINAL_HEAD, schema Room/identity, package/version e signing config. Non aggiungere feature.
3. Riusa l'evidenza dei gate già PASS; riesegui solo i gate release che coprono rischi non già verificati o codice cambiato dopo quei gate.
4. Costruisci UNA SOLA VOLTA signed minified APK + AAB dal FINAL_HEAD con shrink attivo. Registra path, SHA-256 e size.
5. Esegui bundletool/manifest/signing validation e un solo smoke AVD minimo sull'APK esatto prodotto.
6. Salva un release manifest locale verificabile con FINAL_HEAD, schema/identity, package/version, artifact path/hash/size e shrink state. Questi artefatti sono immutabili input di 913264.
7. Se un gate fallisce, correggi solo il blocker concreto, congela il nuovo FINAL_HEAD e ricostruisci una volta; niente audit extra dopo PASS.

# Acceptance
PASS con main finale congelato, shrink attivo, APK/AAB firmati e validati, hash/size/schema/identity registrati e smoke AVD PASS. Nessun upload Play Store. 913264 deve poter riusare gli stessi byte senza rebuild.
