# PersonalHub — impedire disinstallazioni/distruzione dati durante test

**Modello consigliato:** GPT-5.5  
**Reasoning:** Medium  
**MegaVault:** FAST, promuovi solo se emerge rischio distruttivo concreto

```text
PROMPT_ID=428619
project_id=49

GOAL: impedire in modo robusto che benchmark, connected tests, profile generation o altri workflow Codex possano disinstallare, fare clear-data o sostituire distruttivamente l'installazione reale di PersonalHub sul Pixel/TCL senza autorizzazione esplicita, preservando comunque la possibilità di testare.

EVIDENZA GIÀ RACCOLTA — non riscoprirla salvo verifica mirata necessaria:
- durante PROMPT_ID=641827 Codex ha eseguito sul Pixel fisico `:benchmark:connectedDebugAndroidTest` / BaselineProfile e successivi tentativi benchmark;
- prima del benchmark PH reale risultava installata e Codex aveva anche fatto `adb ... install -r app-release.apk`;
- dopo quei run `pm list packages` mostrava `com.gernalix.personalhub.test` ma NON `com.gernalix.personalhub`;
- il log Android del test mostra attività di package install/uninstall del framework di test; il report finale di Codex ammette che il run aveva lasciato il Pixel senza `com.gernalix.personalhub`;
- non è stato osservato un `adb uninstall com.gernalix.personalhub` digitato esplicitamente da Codex: quindi verifica la causa precisa nel lifecycle AGP/benchmark/tested-app, senza assumere che il comando fosse manuale;
- la disinstallazione ha messo a rischio il DB privato reale.

Usa MegaVault + AGENTS.md e parti SOLO dai file benchmark/test e dai guardrail device già pertinenti. Non fare repository-wide audit.

1. Riproduci/identifica staticamente la causa precisa del teardown che può rimuovere il package target reale. NON riprodurla sul Pixel/TCL con dati reali.
2. Implementa il minimo guardrail permanente affinché nessun comando/workflow Codex ordinario possa usare il package reale `com.gernalix.personalhub` come tested/benchmark app quando il framework può uninstall/clear-data/reinstallare.
3. Per benchmark/profile/connected test distruttivi usa un target isolato sicuro: emulator o applicationId/package clone dedicato, scegliendo la soluzione minima compatibile con Macrobenchmark/Baseline Profile.
4. Aggiungi preflight fail-closed: se il target è un device fisico con package reale/dati reali e l'operazione può essere distruttiva, il task deve fermarsi prima dell'azione. Blocca almeno uninstall, pm clear, uninstallAll/test teardown equivalente e reinstall incompatibile del package reale salvo opt-in utente esplicito nello stesso prompt.
5. Non affidarti solo a istruzioni testuali se può esistere un controllo eseguibile/script/configurazione più affidabile; mantieni comunque AGENTS/protocollo coerenti se sono il punto canonico.
6. Non disinstallare, clearare, reinstallare o modificare i dati reali di Pixel/TCL durante questo task.
7. Testa il guardrail con test locali/emulator/fixture mirati. Dimostra che un tentativo distruttivo sul package reale viene rifiutato PRIMA dell'esecuzione e che il percorso isolato continua a permettere benchmark/profile.
8. Nessun refactor/cleanup fuori scope. Ferma appena gli acceptance criteria passano.

Acceptance criteria:
- causa esatta documentata con prova;
- PH reale su Pixel/TCL non viene toccata;
- destructive test sul package reale fail-closed;
- benchmark/profile hanno un percorso isolato funzionante;
- test mirati PASS;
- commit + push canonici.

Output finale conciso:
PROMPT_ID=
ROOT_CAUSE=
WHY_REAL_APP_WAS_REMOVED=
GUARDRAIL=
ISOLATED_TEST_TARGET=
TESTS=
REAL_DEVICE_SAFETY=
COMMIT=
PUSH=
```
