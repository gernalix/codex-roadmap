[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Dopo i task che possono cambiare lo schema, rendere fail-safe gli upgrade del `personalhub.db` sullo SCHEMA FINALE: un'unica migration registry produzione/test, gate al primo avvio dopo update, nessun fallback distruttivo e test da ogni snapshot storico alla versione corrente.

# Starting point già verificato
Non fare discovery generale. Al momento della preparazione remota:
- `PersonalHubDatabase` dichiara schema `10`, ma al momento dell'esecuzione usa sempre la versione finale corrente, senza hardcodare 10;
- le production migrations sono ancora concatenate inline con ripetuti `.addMigrations(...)` dentro `PersonalHubDatabase.build()`;
- `canMigrateFrom(version)` è ancora `version in 1..SCHEMA_VERSION`: **questo è un difetto reale** perché non verifica il grafo;
- non è presente `fallbackToDestructiveMigration` nel file verificato: preserva questa proprietà e non perdere tempo a cercare un fallback inesistente salvo failure/test;
- `DatabaseVault` possiede già validation, snapshot, import rollback e interrupted-import recovery: riusali, non riscriverli;
- `PersonalHubApplication.onCreate()` oggi esegue `DatabaseVault.recoverInterruptedImport(this)` prima di `super.onCreate()` e inizializza poi gli adapter; **non esiste ancora il migration/startup gate richiesto**;
- `GlobalDatabaseInstrumentedTest` ha già recovery/import/export safety e database disposable: estendilo, non creare una seconda harness.

Primo pass **solo** su:
`PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` e Gradle migration-test support. Apri una migration/schema specifica soltanto quando un test guidato da snapshot fallisce.

# Design
- Esporre la lista esatta delle production migrations in un registry riusato da Room opening, temporary/import opening, path check e test.
- `canMigrateFrom(v)` deve verificare un path reale nel grafo fino al current, non un range numerico.
- Nessun `fallbackToDestructiveMigration`/delete-recreate.
- Startup/update gate prima delle feature writes:
  - fresh/current: open+validate;
  - older con path: snapshot recoverable → Room migrate → validate → abilita app;
  - older senza path, newer DB, migration/validation failure: non sostituire né abilitare writes; conserva/ripristina DB recuperabile e mostra stato utente conciso.
- Mantieni `recoverInterruptedImport` prima del gate e memorizza successo per app-version/schema, evitando il gate costoso a ogni Activity.
- Non cambiare import/export o schema feature salvo necessità dimostrata da failure.

# Tests
Guidati automaticamente dagli snapshot Room esistenti: enumera versioni/file una sola volta, poi ogni historical version deve avere path completo e Room deve accettare lo schema finale. Usa representative data survival per core + tabelle introdotte dalle principali feature, non ogni colonna/tabella.

Copri: current→current, fresh, newer reject, missing/failing path no data replacement, destructive fallback absent, recovery ordering. Una sola upgrade QA su DB disposable, mai downgrade/mutazione del DB reale.

# Discipline
Questo è il task schema-safety finale: STRICT è giustificato. Non allargare però a refactor database, backup redesign o audit di tutte le entity. Parti dai cinque file sopra, esegui test mirati, amplia solo su failure concreta. Nessun retry equivalente. Stop immediato al PASS.

PASS solo se produzione e test condividono lo stesso grafo, tutti gli snapshot storici raggiungono current, startup è fail-safe e recovery esistente resta integro. Un solo bump/build/install/delivery se richiesto dal bootstrap; commit/push.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 592604`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, current schema, migration graph/versions tested, `canMigrateFrom`, startup gate/failure behavior, recovery ordering, Android check, version/APK/delivery, SHA, blocker.
