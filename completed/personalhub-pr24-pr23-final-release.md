PROMPT_ID=514458 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Integra nel main canonico di gernalix/PersonalHub, solo tramite single-writer, il lavoro utile delle PR GitHub #24 e #23 e genera una sola release APK finale dal main risultante.

# Starting point
- repository: /home/daniele/projects/PersonalHub;
- #24: [single-writer] 825147, cleanup zombie aggiornato;
- #23: fix Android 17 Restricted Settings / overlay;
- #20 è superseded e non va mergiata;
- chatgpt/autoexport-single-db-618338 è già contenuto in main e non va mergiato.

# Execution
1. Esegui un solo fetch iniziale e verifica SHA main, stati/check di #24/#23 e ahead/behind rispetto a main.
2. Per #24, se merged verifica che il merge sia antenato di main. Se aperta usa solo il worktree/task branch 825147 e correggi esclusivamente failure CI concrete; push del minimo fix e lascia merge/cleanup al single-writer. Se resta CI pending, non attendere.
3. Per #23 non mergiare il vecchio branch. Confrontalo con main dopo #24 e porta nel task worktree single-writer basato sul main corrente soltanto il delta valido per Android 16/17: rilevamento sideload/local-file, guida App info/menu/Allow restricted settings, poi normale permesso Display over other apps, mantenendo comportamento store/pre-Android precedenti e test mirati. Escludi version bump, codice obsoleto, duplicati e differenze non correlate. Esegui solo compile leaf, CallOverlayRequestGateTest (o equivalenti) ed eventuale compile app necessaria; poi push e handoff writer.
4. Quando entrambi i delta sono nel main remoto, reconcile canonico e verifica checkout main pulito e allineato a origin/main; assicurati bounded che non resti codice unico necessario in branch storici.
5. Solo dal main finale esegui ./gradlew --no-daemon --no-configuration-cache :app:assembleRelease senza clean. Verifica APK prodotto, size, SHA-256, firma valida, package com.gernalix.personalhub e versionCode/versionName.
6. Se Pixel è disponibile, identifica il device, installa con adb install -r senza perdita dati, avvia una volta e verifica il processo. Se non disponibile, riportalo senza bloccare l'APK.
7. Per ogni distribuzione APK finale segui il preflight e la consegna Telegram canonici, senza esporre segreti.

# Constraints
- main è canonico; non scrivere direttamente su main e non fare merge manuali.
- Preserva canonical DB export e tutti i fix esistenti.
- Nessun refactor/cleanup fuori scope, nessun merge cieco, nessuna matrice test completa se CI equivalente esiste, nessun polling CI prolungato.
- Se la sola CI remota è pending, termina con RESULT=PENDING_INTEGRATION e non produrre APK.

# Acceptance
PASS solo se #24 e #23 utili sono in main, main è pulito/sincronizzato, assembleRelease dal main finale passa, APK firmato/minificato/resource-shrunk è verificato, e Pixel è aggiornato in-place se disponibile. Nessuna perdita dati.

# Output
Massimo 10 righe: PROMPT_ID, RESULT, PR24, PR23, MAIN, BUILD, APK, APK_SIZE, SHA256, PIXEL_INSTALL, BLOCKER.
