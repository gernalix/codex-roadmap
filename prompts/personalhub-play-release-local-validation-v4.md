PROMPT_ID=788606 | PARENT_PROMPT_ID=334679 | project_id=49 | MegaVault=FAST

# Goal
Esegui il preflight locale finale della build PersonalHub destinata a Google Play. Non aggiungere feature.

# Starting point
- repo: /home/daniele/projects/PersonalHub, main finale dopo 840907;
- release ha già isMinifyEnabled=true, isShrinkResources=true e proguard-android-optimize: non creare un task separato di minificazione;
- usa signing secret canonico e i gate Play già nel repo.

# Esecuzione
1. Richiedi main pulito/sincronizzato; non modificare codice salvo blocker concreto del preflight.
2. Esegui i gate Play/release mantenuti, signed AAB/APK con config locale, bundletool validation e smoke AVD minimo.
3. Verifica che R8/resource shrink siano attivi e misura/report size finale APK/AAB; non disabilitare shrink per far passare build.
4. Controlla signing, manifest/version, policy tecniche e compatibilità solo tramite gate già presenti. Se un gate fallisce, correggi il minimo e riesegui quel gate.

# Acceptance
PASS con bundle firmato/validato, shrink attivo, size riportata, smoke AVD e preflight esistente PASS. Nessun upload Play Store. Stop immediato.
