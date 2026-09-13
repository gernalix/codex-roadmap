[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 3/3, unica release
Porta nel WordPulse incorporato in PersonalHub il boundary Alertness/Fatigue v4 **già verificato** al commit standalone `ca238d26de189e75b341ed63066f0bb7ed532b16`, collega il fatigue score canonico alla Cerca temporale già implementata, poi rendi fail-safe gli upgrade `personalhub.db` sullo schema finale e fai **1 bump + 1 build finale + 1 install Pixel + 1 delivery** dell'esatto stesso APK.

# Prerequisito WordPulse verificato — nessuna discovery
`483217` è già PASS. Fonte autoritativa WordPulse = `gernalix/wordpulse@ca238d26de189e75b341ed63066f0bb7ed532b16`. Nel checkout `/home/daniele/projects/wordpulse` fai al massimo un solo `git rev-parse HEAD`: se non è quello SHA, usa `git show <SHA>:<path>`/il commit esplicito come fonte senza pull/merge e senza investigare MegaVault, roadmap, memoria o cronologia Git. **Non usare un `origin/main` successivo** come sorgente del port.

Leggi dal commit standalone solo il boundary necessario, partendo da questi path esatti:
- `app/src/main/java/com/wordpulse/app/domain/Alertness.kt`
- `app/src/main/java/com/wordpulse/app/domain/TypingPerformance.kt`
- `app/src/main/java/com/wordpulse/app/data/PvtResultEntity.kt`
- `app/src/main/java/com/wordpulse/app/data/WordPulseDatabase.kt` (solo migration/registrazione v4 pertinente; non copiare il DB wholesale)
- `app/src/main/java/com/wordpulse/app/data/WordRepository.kt` (solo persistence/query fatigue/PVT pertinente)
- `app/src/main/java/com/wordpulse/app/ui/WordPulseViewModel.kt`
- `app/src/main/java/com/wordpulse/app/ui/AlertnessOverlay.kt`
- test/migration v4 direttamente collegati.
Non aprire `4.json` standalone salvo confronto schema puntuale: è generato e già verificato. Non fare audit generale WordPulse.

Semantiche verificate da preservare: fatigue `0..100`; alertness=`100-fatigue`; baseline insufficiente ⇒ score assente; PVT/calibrazione opzionali; fallback typing-only; pesi fatigue attuali `speed 0.35`, `rhythm 0.30`, `sessionDrift 0.15`, `sleepContext 0.12`, `control 0.08`. Non reinterpretare o ricalibrare questi pesi durante il port.

# Handoff WordPulse → PH
Nel checkout PH, porta solo le differenze necessarie nei corrispondenti `feature/wordpulse` e `contracts/database` + schema/migration di `PersonalHubDatabase`:
- preserva il comportamento PH esistente e il package/shared DB;
- storage/migration v4 devono entrare nel grafo migration **PH**, senza DB WordPulse separato e senza destructive fallback;
- `WordSessionHubAdapter.queryTemporal()` espone `HubTemporalRecord.attributes["fatigueScore"]` solo da valore canonico realmente derivato/persistito; mai placeholder/synthetic score;
- se lo standalone non persiste un singolo score per sessione, usa una mappatura deterministica al grain canonico disponibile appartenente alla sessione e documentala nel test; assenza di dati comparabili ⇒ attributo assente;
- test end-to-end sul vero storage/provider PH: caso con fatigue valido + caso baseline insufficiente. Il solo `HubTemporalSearchScreenTest` sintetico NON basta.

# Starting point/sicurezza PH
Acquisisci lock PH. Nel checkout `/home/daniele/projects/PersonalHub` fai un solo fetch/pull fast-forward se pulito; stato incompatibile ⇒ `BLOCKED`, niente stash/reset/force. Rileva schema/versione PH una volta, non hardcodare. Riusa `DatabaseVault`, rollback/recovery e test DB disposable. Nessun fallback distruttivo.

Le correzioni post-742913 già su `main` sono authoritative e vanno preservate: solo ref canonici sono selezionabili negli episodi; paging People fa lookup solo sui record nuovi. Coprile nel normale test temporal, senza gate separato.

È già presente anche il fix export introdotto da ChatGPT in `DatabaseVault` (`4f23be0629a1becc2c2526351ca03efa7af32d27`) con test `DatabaseVaultLegacyTableValidationTest` (`fbf583b5962ffa046947e57833dc12d019b2ff0b`). Motivo: il DB reale del Pixel mostrava `Export failed: Unexpected database table`; il validator ora valida integralmente tutte le tabelle Room possedute da PH ma tollera tabelle extra/legacy inerti, mentre **tutti i trigger restano obbligatoriamente validati**. Preserva questa policy: non ripristinare il controllo di uguaglianza esatta delle tabelle e non allentare la validazione trigger.

`tools/deliver_personalhub_apk.py`: ≤50 MiB Telegram cloud; >50 MiB prerelease GitHub `personalhub-dev-apk` + link Telegram. `tools/smoke_large_apk_delivery.py`: smoke isolato `personalhub-dev-apk-smoke`. Vietati Local Bot API/TDLib, R8/ABI split/post-processing/re-sign per aggirare size.

Niente progress narration tra tool call salvo nuovo failure/blocker che cambia il piano. Raggruppa operazioni indipendenti. Non fare inventory generale né lookup MegaVault iniziali: questo prompt contiene già identità, SHA e boundary; usa MegaVault solo per l'evento finale esplicitamente richiesto dalla campagna.

# Schema safety
Dopo il port WordPulse, concentra il pass schema su `PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` + supporto migration-test; apri migration/schema specifiche solo su failure.
- registry unico production migrations riusato da Room open, temporary/import open, path check e test;
- `canMigrateFrom(v)` dal grafo reale fino a `SCHEMA_VERSION`, non range;
- vietati destructive migration/delete-recreate;
- startup/update gate prima di feature writes: current/fresh validate; older con path ⇒ snapshot recuperabile→migrate→validate; older senza path/newer/failure ⇒ preserva DB, niente replace/writes, stato utente conciso;
- `recoverInterruptedImport` prima del gate; successo memoizzato per app-version/schema;
- test automatico da tutti gli snapshot Room storici disponibili→current con representative data survival, compresi i nuovi dati WordPulse v4; niente audit colonna-per-colonna;
- esegui anche `DatabaseVaultLegacyTableValidationTest`: una tabella extra inerte deve essere accettata; un trigger non riconosciuto sulla stessa tabella deve essere rifiutato;
- prova migration Android disposable: se presente usa **una sola volta** `tools/android_room_fixture.py --launch-and-verify` con `--target-version`, `--expect-table` e query preservazione; JSON deve attestare `migration.integrity="ok"` e `migration.foreign_keys="ok"`. Niente loop equivalenti `adb shell sqlite3` salvo failure concreta dell'helper.

# Disciplina verifica
Durante porting/schema esegui solo compile/test leaf mirati. Al primo failure leggi l'intero report del leaf, correggi in batch e rilancia solo quel leaf. Non usare full `check` come inner loop.

# Gate/release una volta sola
1. Quando port + schema + leaf test sono verdi, unico gate campagna pre-bump: temporal/provider WordPulse real-storage, `DatabaseVaultLegacyTableValidationTest`, regressioni mirate `381527`+`742913`, `CheckInAccuracyPolicyTest`, `HubActivityRegisterTest`, architecture gate. Se emerge un nuovo failure, leaf fix e **una sola** ripetizione del gate.
2. Incrementa `version.txt` una volta dal remoto corrente.
3. Build canonica signed debug `<version>.apk` una volta; firma/versione/hash una volta. Su failure: leaf compile/package fix, poi una sola nuova build.
4. QA Pixel reale compatta/non distruttiva: Home/versione; Random timer controllato; Cerca→sezioni→WordPulse fatigue reale/non disponibile secondo dati→Salva subset; root moduli senza versioni legacy + Soldi theme; startup DB current; **apri Sostanze/Export sul DB reale attuale e verifica che l'export completi senza il banner `Unexpected database table`**. Non cancellare né modificare la tabella extra/legacy per far passare il test. Test schema distruttivi solo QA/disposable.
5. Installa sul Pixel l'esatto APK verificato.
6. Delivery senza rebuild/modifica byte: ≤50 MiB una `deliver_personalhub_apk.py`; >50 MiB una `smoke_large_apk_delivery.py` sul vero APK e poi `deliver_personalhub_apk.py` sullo stesso file.
7. Failure transport/auth: fix minimo solo se evidente, altrimenti `BLOCKED`. Commit/push PH + evento MegaVault richiesto; release lock.

# Stop
PASS = parity semantica con `wordpulse@ca238d26` + fatigue temporal provider provato su storage reale + export del DB reale Pixel senza falso `Unexpected database table` + migration graph/storici/startup fail-safe + regressioni campagna + unico bump + stesso hash APK verificato/installato/consegnato.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604`

Dopo il secondo comando, **STOP immediato**: niente `git status`, `pull`, `log`, `rev-parse` o verifiche aggiuntive della roadmap.

Output ≤9 righe: RESULT, WordPulse parity+fatigue provider, schema/grafo+export regression, historical/startup, campaign gates, version/APK/hash, Pixel+delivery, SHA PH, blocker.
