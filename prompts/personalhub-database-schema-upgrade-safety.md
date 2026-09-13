[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 3/3, unica release
Rendi fail-safe gli upgrade `personalhub.db` sullo schema finale dopo le fasi `381527` e `742913`, poi fai **1 bump + 1 build finale + 1 install Pixel + 1 delivery** dell'esatto stesso APK.

# Starting point/sicurezza
Usa `origin/main` corrente; rileva schema/versione una volta, non hardcodare. Riusa `DatabaseVault`, rollback/recovery e test DB disposable. Nessun fallback distruttivo. `tools/deliver_personalhub_apk.py`: ≤50 MiB Telegram cloud; >50 MiB prerelease GitHub `personalhub-dev-apk` + link Telegram. `tools/smoke_large_apk_delivery.py`: smoke isolato `personalhub-dev-apk-smoke`. Vietati Local Bot API/TDLib, R8/ABI split/post-processing/re-sign per aggirare size.
Acquisisci lock PH; occupato => `BLOCKED`, no polling. Se `origin/main` avanza con commit PH estranei dopo inizio QA => `BLOCKED`, non incorporarli.

Niente progress narration: tra tool call non scrivere aggiornamenti di stato salvo nuovo failure/blocker che cambia il piano. Raggruppa operazioni indipendenti.

# Schema safety
Primo pass solo `PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` + supporto Gradle migration-test; apri migration/schema specifiche solo su failure.
- registry unico production migrations riusato da Room open, temporary/import open, path check e test;
- `canMigrateFrom(v)` dal grafo reale fino a `SCHEMA_VERSION`, non range;
- vietati destructive migration/delete-recreate;
- startup/update gate prima di feature writes: current/fresh validate; older con path => snapshot recuperabile→migrate→validate; older senza path/newer/failure => preserva DB, niente replace/writes, stato utente conciso;
- `recoverInterruptedImport` prima del gate; successo memoizzato per app-version/schema;
- test automatico da tutti gli snapshot Room storici disponibili→current con representative data survival; niente audit colonna-per-colonna.
- Per la prova migration Android disposable, se presente usa `tools/android_room_fixture.py --launch-and-verify` con `--target-version`, `--expect-table` e una query di preservazione. Una sola invocazione per fixture+launch+verifica; il JSON dell'helper deve attestare anche `migration.integrity="ok"` e `migration.foreign_keys="ok"`. Non ripetere questi PRAGMA manualmente. Vietati loop equivalenti `adb shell sqlite3`/quoting/push/cp/.read salvo failure concreta dell'helper.

# Disciplina verifica prima della release
Durante l'implementazione schema esegui soltanto compile/test migration mirati. Se un test/lint fallisce, leggi l'intero report del leaf task, correggi in batch e rilancia **solo quel leaf task**. Non usare il gate campagna/finale come inner loop e non rilanciare un full `check` dopo ogni fix.

# Gate/release una volta sola
1. Quando schema + leaf test sono verdi, esegui un unico gate campagna pre-bump con i test mirati delle fasi `381527`+`742913`, `HubActivityRegisterTest` e architecture gate; non ripetere casi già coperti. Se questo gate trova un nuovo failure, risolvi con il solo leaf task coinvolto e poi ripeti il gate campagna **una sola volta**.
2. Incrementa `version.txt` una volta dal remoto corrente.
3. Build canonica signed debug `<version>.apk` una volta; verifica firma/versione/hash una volta. Se la build fallisce, correggi il leaf compile/package task e poi rifai questa build una sola volta: nessun ciclo full gate.
4. QA Pixel reale, compatta/non distruttiva: Home/versione; Random timer controllato; Cerca→sezioni→Salva subset; root moduli senza versioni legacy + Soldi theme; startup DB current. Test schema distruttivi solo QA/disposable.
5. Installa sul Pixel l'esatto APK verificato.
6. Delivery senza rebuild/modifica byte: se ≤50 MiB, una sola `deliver_personalhub_apk.py`; se >50 MiB, una sola `smoke_large_apk_delivery.py` sul vero APK e poi `deliver_personalhub_apk.py` sullo stesso file. Non creare APK finto/padded.
7. Failure transport/auth: fix minimo solo se evidente, altrimenti BLOCKED. Commit/push PH + evento MegaVault richiesto; release lock.

PASS = migration graph/storici/startup fail-safe + regressioni campagna + unico bump + stesso hash APK verificato/installato/consegnato. Stop immediato dopo completion; niente audit/ottimizzazione post-PASS.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604`

Dopo il secondo comando, **STOP immediato**: niente `git status`, `pull`, `log`, `rev-parse` o verifiche aggiuntive della roadmap.

Output ≤9 righe: RESULT, schema/grafo, historical/startup, campaign gates, version/APK/hash, Pixel, delivery/smoke, SHA, blocker.
