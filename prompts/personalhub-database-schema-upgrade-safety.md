[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT | campaign_id=PH_FINAL_20260912`

> Esecuzione diretta. Non usare `select` e non rileggere roadmap/README/spiegazioni. Fase 4/4 e **unica fase di release** della campagna PersonalHub.

# Goal
Rendere fail-safe gli upgrade del `personalhub.db` sullo schema finale della campagna e poi eseguire **un solo bump versione, una sola build finale, una sola installazione Pixel e una sola delivery di produzione** per tutte le fasi PersonalHub precedenti.

# Starting point
Usa il `main` remoto corrente dopo le tre fasi della stessa campagna. Non hardcodare schema/versione: rilevali una volta. Sono già esistenti `DatabaseVault`, recovery/import rollback e test database disposable; riusali. Nessun fallback distruttivo.

La delivery è già implementata in `tools/deliver_personalhub_apk.py`: APK `<=50 MiB` via Telegram cloud, APK `>50 MiB` via prerelease stabile GitHub `personalhub-dev-apk` + link Telegram. `tools/smoke_large_apk_delivery.py` prova end-to-end il ramo `>50 MiB` su una prerelease isolata `personalhub-dev-apk-smoke`, accetta solo un vero APK ZIP con `AndroidManifest.xml` e verifica l'asset dopo l'upload. **Non usare Local Bot API/TDLib e non reinventare questa logica.**

Acquisisci il lock PersonalHub introdotto dal task infrastrutturale. Se un altro task PH è attivo, `BLOCKED`; non aspettare/pollare. Se `origin/main` avanza con commit PH estranei dopo l'acquire/inizio QA, fermati come concurrency blocker invece di assorbirli e rifare la QA.

# Schema safety
Primo pass solo su `PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` e supporto Gradle migration test. Apri migration/schema specifiche solo su failure.

Implementa/chiudi:
- registry unico delle production migrations riusato da Room open, temporary/import open, path check e test;
- `canMigrateFrom(v)` basato sul grafo reale fino a `SCHEMA_VERSION`, non su range numerico;
- nessun `fallbackToDestructiveMigration`/delete-recreate;
- startup/update gate prima delle feature writes: current/fresh validate; older con path => snapshot recuperabile→migrate→validate; older senza path/newer/failure => niente replace e niente writes, DB recuperabile preservato + stato utente conciso;
- `recoverInterruptedImport` resta prima del gate;
- successo memoizzato per app-version/schema, non gate costoso a ogni Activity.

Test automaticamente da tutti gli snapshot Room storici disponibili verso current, con representative data survival; niente audit di ogni colonna.

# Gate finali campagna
Prima del bump esegui i test mirati delle tre fasi precedenti e `HubActivityRegisterTest`, più architecture gate. Non rifare manualmente casi già provati da unit/integration test.

Poi:
1. incrementa `version.txt` **una sola volta** rispetto al valore corrente remoto; nessuna fase precedente della campagna deve averlo cambiato;
2. build canonica signed debug `<version>.apk` una sola volta dopo tutti i gate;
3. verifica firma/versione/hash una volta;
4. QA finale Pixel compatta e non distruttiva sul package reale: Home/versione, un Random timer controllato, Cerca→sezioni→Salva episodio subset, root moduli senza versioni legacy, startup DB current. Usa package QA/disposable per qualunque prova schema distruttiva;
5. installa sul Pixel l'esatto APK finale già verificato;
6. delivery senza ricostruire/modificare l'APK:
   - se `<=50 MiB`, usa una sola volta `tools/deliver_personalhub_apk.py` e verifica successo Telegram cloud;
   - se `>50 MiB`, esegui **una sola volta** `tools/smoke_large_apk_delivery.py` sullo stesso APK reale per provare GitHub autenticato + upload su `personalhub-dev-apk-smoke` + notifica Telegram + verifica asset; dopo PASS usa `tools/deliver_personalhub_apk.py` sullo stesso file per la delivery di produzione `personalhub-dev-apk` + link Telegram;
   - non creare/paddare un falso APK per forzare il ramo `>50 MiB`: se l'APK reale è `<=50 MiB`, il smoke grande è semplicemente non applicabile;
7. qualunque failure di transport/auth => fix minimo solo se evidente; altrimenti `BLOCKED`. **Vietato** Local Bot API/TDLib, rebuild release, R8, ABI split, post-processing o re-signing per ridurre dimensione;
8. commit/push PersonalHub + evento MegaVault richiesto; release lock; completa roadmap e stop.

# Acceptance
PASS solo se migration graph/storici/startup fail-safe passano, regressioni campagna passano, un solo bump è avvenuto, l'esatto APK verificato è installato sul Pixel e la delivery di produzione usa quegli stessi byte: documento Telegram cloud se `<=50 MiB`, oppure asset GitHub stabile + link Telegram se `>50 MiB`. Per un APK reale `>50 MiB`, anche lo smoke isolato deve essere PASS. Nessun lavoro concorrente deve essere incorporato durante QA.

Su PASS completa solo `PROMPT_ID=592604`; `push_verified=git_push_exit_0` è terminale, niente follow-up Git sulla roadmap.

Output ≤9 righe: RESULT, schema/grafo, historical versions, startup gate, campaign tests, version/APK/hash, Pixel, delivery/smoke, SHA/blocker.
