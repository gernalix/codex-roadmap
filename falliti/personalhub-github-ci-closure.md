PROMPT_ID=962109
PROJECT_ID=49
MODEL=GPT-5.6 Terra
reasoning=medium
MegaVault=FAST

# PersonalHub — chiudi definitivamente la CI GitHub

Workdir canonico: /home/daniele/projects/PersonalHub
Repo: gernalix/PersonalHub
Branch finale: main

## Goal
Porta tutti i workflow GitHub Actions mantenuti di PersonalHub a PASS sull'ultimo main, chiudendo solo i failure reali emersi dalla campagna CI 483921. Lavora in autonomia sui fix necessari in-scope; termina appena i gate sono verdi.

## Starting point verificato
Parti da origin/main aggiornato. Al momento dell'handoff HEAD remoto era:
396c960ea5c7ae08859c85c8d2c2bb42d7263700

Failure già verificati su quel commit:
1. Android unit CI — run 35405328654:
   :feature:soldi:testDebugUnitTest
   FinanceCapsuleTest.versionThreeUpgradeKeepsExistingRowsAndCreatesOnlyEmptyFinanceTables
   failure a FinanceCapsuleTest.kt:92.
2. Play Store preflight — run 35405328705:
   :app:lintPlay
   MissingTranslation per app/src/main/res/values/strings.xml:
   module_salute
   module_salute_subtitle
   mancanti in values-it.
3. Android instrumentation CI — run 35405328675 era ancora in esecuzione all'handoff. Usa il run più recente non superseded come autorità. Il workflow usa l'opt-in CI debug personalhub.allowCiEmulatorDebug: non introdurre keystore/signing reali in GitHub.

## Scope stretto
- Correggi i failure sopra con il minimo cambiamento necessario.
- Se il run instrumentation più recente fallisce, apri solo quel job/log e correggi quel failure domain; non fare audit Android generale.
- Puoi modificare codice, test, risorse, build logic o workflow direttamente collegati ai failure.
- Non disabilitare test, non aggiungere lint baseline/soppressioni generiche solo per ottenere verde.
- Non fare refactor, cleanup, upgrade dipendenze o modifiche funzionali non necessarie.
- Non usare Pixel/TCL o altri device fisici. Per riprodurre instrumentation localmente usa solo un emulatore e selezionalo esplicitamente.
- Mantieni fail-closed signing per release/Play/device reali; il bypass unsigned deve restare limitato all'emulatore CI debug già previsto.

## Esecuzione token-efficient
1. git fetch origin && git switch main && git pull --ff-only.
2. Verifica subito i workflow/run più recenti; se uno dei failure sopra è già stato risolto da commit successivi, non reinvestigarlo.
3. Parti dai file/test indicati. Espandi solo se l'evidenza lo richiede.
4. Test mirati prima dei gate completi. Nessun retry identico senza nuova evidenza.
5. Push una volta per batch coerente; usa i nuovi run GitHub come acceptance finale.
6. Se serve una branch per policy GitHub, mergiala appena verde e cancellala; stato finale: solo main per questo lavoro.

Test locali suggeriti solo quando pertinenti:
- ./gradlew --no-daemon --console=plain :feature:soldi:testDebugUnitTest --tests '*FinanceCapsuleTest.versionThreeUpgradeKeepsExistingRowsAndCreatesOnlyEmptyFinanceTables'
- ./gradlew --no-daemon --console=plain :app:lintPlay
- Per instrumentation locale solo se necessaria: imposta ANDROID_SERIAL all'emulatore e usa CI=true ./gradlew --no-daemon --console=plain connectedDebugAndroidTest -Ppersonalhub.allowCiEmulatorDebug=true

## Acceptance
PASS solo quando, sul commit finale di main:
- Android unit CI = success;
- Android instrumentation CI = success;
- Play Store preflight = success;
- Architecture boundaries = success;
- Salute module = success;
- nessun workflow duplicato introdotto;
- git status locale pulito e main sincronizzato con origin/main.

Se un gate fallisce, correggi autonomamente il failure concreto e continua. BLOCKED solo per un requisito esterno realmente non risolvibile senza intervento umano. Output finale conciso: commit finale, run verificati e PASS/BLOCKED.
