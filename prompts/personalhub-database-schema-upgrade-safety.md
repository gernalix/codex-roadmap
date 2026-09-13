[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 3/3, unica release
Porta nel WordPulse incorporato in PersonalHub il boundary Alertness/Fatigue v4 appena verificato dal task `483217`, collega il **fatigue score canonico** alla Cerca temporale già implementata, poi rendi fail-safe gli upgrade `personalhub.db` sullo schema finale e fai **1 bump + 1 build finale + 1 install Pixel + 1 delivery** dell'esatto stesso APK.

# Prerequisito WordPulse verificato
`483217` deve risultare già completato in roadmap. Usa come riferimento il `origin/main` corrente di `/home/daniele/projects/wordpulse`, che deve corrispondere al commit verificato/pushato dal task immediatamente precedente; se è avanzato in modo non spiegabile dopo quel PASS => `BLOCKED`, non integrare codice non verificato.

Leggi dal repo standalone **solo** il boundary v4 necessario, partendo da: `domain/Alertness.kt`, `domain/TypingPerformance.kt`, `data/PvtResultEntity.kt`, `data/WordPulseDatabase.kt`, `data/WordRepository.kt`, `ui/WordPulseViewModel.kt`, `ui/AlertnessOverlay.kt` e migration/schema/test v4 direttamente correlati. Non fare audit generale WordPulse e non copiare wholesale il suo `WordPulseDatabase`: PH usa il proprio DB Room condiviso.

# Handoff WordPulse → PH
Nel checkout PH, porta solo le differenze necessarie nei corrispondenti `feature/wordpulse` e `contracts/database` + schema/migration di `PersonalHubDatabase`:
- preserva il comportamento PH esistente e il package/shared DB;
- fatigue `0..100`, alertness complementare, baseline insufficiente => valore non disponibile, PVT/calibrazione e fallback typing-only devono mantenere le semantiche del commit standalone verificato;
- storage/migration aggiuntivi v4 devono entrare nel grafo migration **PH**, senza DB WordPulse separato e senza destructive fallback;
- `WordSessionHubAdapter.queryTemporal()` deve esporre in `HubTemporalRecord.attributes["fatigueScore"]` soltanto un valore canonico realmente derivato/persistito dalla feature verificata, mai un placeholder/synthetic score;
- se il modello standalone non persiste direttamente un singolo score per sessione, usa una mappatura deterministica al grain canonico disponibile (campioni/evaluation appartenenti alla sessione) e documentala nel test; non inventare un valore in assenza di dati comparabili;
- aggiungi un test **end-to-end sul vero storage/provider PH** che inserisca/produca dati WordPulse canonici e dimostri che la query temporale restituisce `fatigueScore` valido quando disponibile e nessun attributo quando il baseline è insufficiente. Il solo `HubTemporalSearchScreenTest` con record sintetici NON basta.

# Starting point/sicurezza PH
Usa `origin/main` corrente; rileva schema/versione una volta, non hardcodare. Riusa `DatabaseVault`, rollback/recovery e test DB disposable. Nessun fallback distruttivo. Le correzioni remote post-742913 su `HubTemporalSearchScreen` (solo ref canonici selezionabili + lookup People incrementali) sono già su `main`: preservale e coprile col normale test, senza un gate separato.

`tools/deliver_personalhub_apk.py`: ≤50 MiB Telegram cloud; >50 MiB prerelease GitHub `personalhub-dev-apk` + link Telegram. `tools/smoke_large_apk_delivery.py`: smoke isolato `personalhub-dev-apk-smoke`. Vietati Local Bot API/TDLib, R8/ABI split/post-processing/re-sign per aggirare size.
Acquisisci lock PH; occupato => `BLOCKED`, no polling. Se `origin/main` avanza con commit PH estranei dopo inizio QA => `BLOCKED`, non incorporarli.

Niente progress narration: tra tool call non scrivere aggiornamenti di stato salvo nuovo failure/blocker che cambia il piano. Raggruppa operazioni indipendenti.

# Schema safety
Dopo il port WordPulse, concentra il pass schema su `PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` + supporto Gradle migration-test; apri migration/schema specifiche solo su failure.
- registry unico production migrations riusato da Room open, temporary/import open, path check e test;
- `canMigrateFrom(v)` dal grafo reale fino a `SCHEMA_VERSION`, non range;
- vietati destructive migration/delete-recreate;
- startup/update gate prima di feature writes: current/fresh validate; older con path => snapshot recuperabile→migrate→validate; older senza path/newer/failure => preserva DB, niente replace/writes, stato utente conciso;
- `recoverInterruptedImport` prima del gate; successo memoizzato per app-version/schema;
- test automatico da tutti gli snapshot Room storici disponibili→current con representative data survival, compresi i nuovi dati WordPulse v4; niente audit colonna-per-colonna;
- per la prova migration Android disposable, se presente usa `tools/android_room_fixture.py --launch-and-verify` con `--target-version`, `--expect-table` e una query di preservazione. Una sola invocazione per fixture+launch+verifica; il JSON dell'helper deve attestare anche `migration.integrity="ok"` e `migration.foreign_keys="ok"`. Non ripetere questi PRAGMA manualmente. Vietati loop equivalenti `adb shell sqlite3`/quoting/push/cp/.read salvo failure concreta dell'helper.

# Disciplina verifica prima della release
Durante porting/schema esegui soltanto compile/test mirati. Se un test/lint fallisce, leggi l'intero report del leaf task, correggi in batch e rilancia **solo quel leaf task**. Non usare il gate campagna/finale come inner loop e non rilanciare un full `check` dopo ogni fix.

# Gate/release una volta sola
1. Quando port WordPulse + schema + leaf test sono verdi, esegui un unico gate campagna pre-bump con: test temporal search/provider WordPulse real-storage, regressioni mirate delle fasi `381527`+`742913`, `CheckInAccuracyPolicyTest`, `HubActivityRegisterTest` e architecture gate. Se trova un nuovo failure, risolvi col solo leaf task e ripeti il gate campagna **una sola volta**.
2. Incrementa `version.txt` una volta dal remoto corrente.
3. Build canonica signed debug `<version>.apk` una volta; verifica firma/versione/hash una volta. Se fallisce, correggi il leaf compile/package task e rifai questa build una sola volta: nessun ciclo full gate.
4. QA Pixel reale, compatta/non distruttiva: Home/versione; Random timer controllato; Cerca→sezioni→WordPulse fatigue reale/non disponibile secondo dati→Salva subset; root moduli senza versioni legacy + Soldi theme; startup DB current. Test schema distruttivi solo QA/disposable.
5. Installa sul Pixel l'esatto APK verificato.
6. Delivery senza rebuild/modifica byte: se ≤50 MiB, una sola `deliver_personalhub_apk.py`; se >50 MiB, una sola `smoke_large_apk_delivery.py` sul vero APK e poi `deliver_personalhub_apk.py` sullo stesso file. Non creare APK finto/padded.
7. Failure transport/auth: fix minimo solo se evidente, altrimenti BLOCKED. Commit/push PH + evento MegaVault richiesto; release lock.

PASS = WordPulse v4 integrato nel shared DB PH + fatigue temporal provider provato su storage reale + migration graph/storici/startup fail-safe + regressioni campagna + unico bump + stesso hash APK verificato/installato/consegnato. Stop immediato dopo completion; niente audit/ottimizzazione post-PASS.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604`

Dopo il secondo comando, **STOP immediato**: niente `git status`, `pull`, `log`, `rev-parse` o verifiche aggiuntive della roadmap.

Output ≤9 righe: RESULT, WordPulse SHA/parity+fatigue provider, schema/grafo, historical/startup, campaign gates, version/APK/hash, Pixel+delivery, SHA PH, blocker.
