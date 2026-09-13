[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=463218 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | campaign_id=PH_SOLDI_V2_POSTQA_20260913 | type=Prompt`

# Goal
Valida **solo** i due fix remoti aggiunti dopo il PASS di `917364` sul branch `feature/soldi-ui-v2`: (A) materializzazione ricorrenze nello stesso giorno di apertura conto; (B) modalità one-shot di `tools/android_room_fixture.py`. Correggi soltanto failure concrete. Niente review generale, merge o release.

# Starting point verificato
Il branch remoto contiene già il fix dominio e relativo test (`FinanceCapsule.kt`, `FinanceAccountsTest.kt`) e l'helper Room esteso. Tutti i gate preesistenti di Soldi v2 erano già PASS prima di questi tre file; non ripeterli salvo dipendenza diretta da un fix che fai tu.

# Scope / sicurezza
- Acquisisci `python3 tools/personalhub_task_lock.py acquire --prompt-id 463218`; lock occupato => `BLOCKED`, nessun polling.
- `~/projects/PersonalHub`, fetch una volta, usa `feature/soldi-ui-v2`; sporco non-task => `BLOCKED`, niente stash/reset.
- Nessun main/merge, bump versione, release, Telegram, package reale o DB personale.
- Niente discovery generale. Parti esclusivamente dai 3 file sopra; amplia solo se un errore concreto lo richiede.

# Gate A — regressione ricorrenza
Esegui una sola volta il test mirato:
`./gradlew --no-daemon :feature:soldi:testDebugUnitTest --tests 'com.gernalix.personalhub.core.database.capsules.soldi.FinanceAccountsTest.sameDayRecurrenceMaterializesAtAccountOpeningInstant'`

Il test deve provare che un'occorrenza nello stesso giorno dell'apertura non viene retrodatata a mezzanotte: usa l'istante di apertura e resta valida rispetto al vincolo del conto. Se fallisce, correggi solo `FinanceCapsule.kt`/quel test e rilancia solo questo test.

# Gate B — helper Room one-shot Android
1. `python3 -m py_compile tools/android_room_fixture.py` una volta.
2. Avvia/attendi il `Pixel_8a` canonico. Usa solo `com.gernalix.personalhub.qa` e l'APK QA già esistente; costruisci `:app:assembleQa --no-configuration-cache` solo se manca.
3. Prepara seed v11 minimo + query di preservazione in file temporanei.
4. Esegui **una sola invocazione** dell'helper con `--launch-and-verify --target-version 12 --expect-table finance_recurrences --verify-sql ... --expect-line ...`.
5. PASS se la stessa invocazione crea la fixture v11, avvia Room, arriva a v12, conserva il record seed e trova `finance_recurrences`.
6. Se fallisce, correggi solo l'helper dalla failure concreta e ripeti Gate B. Vietati workaround manuali equivalenti `adb shell sqlite3`, `push/cp/.read`, pipe/quoting sperimentali senza nuova evidenza.

# Stop
PASS appena A+B sono verdi. Non eseguire suite complete, smoke UI, audit o ulteriori test dopo PASS. Commit/push solo eventuali fix locali necessari; se non modifichi nulla, limita la verifica a divergenza `0/0`. Ferma emulatore e rilascia lock.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 463218 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 463218`

Output ≤5 righe: RESULT, gate A, gate B, fix/push, blocker.
