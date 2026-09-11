[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=592604 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Dopo i task che possono cambiare lo schema, rendere fail-safe gli upgrade del `personalhub.db` sullo SCHEMA FINALE: un'unica migration registry produzione/test, gate al primo avvio dopo update, nessun fallback distruttivo e test da ogni snapshot storico alla versione corrente.

# Starting point
Non assumere più `SCHEMA_VERSION=10`: leggi una volta la versione corrente e gli snapshot esportati. Riusa `PersonalHubDatabase`, `DatabaseVault` validation/snapshot/rollback e `PersonalHubApplication` recovery; non riscrivere migration/import/backup già funzionanti.

Primo pass solo su `PersonalHubDatabase.kt`, `DatabaseVault.kt`, `PersonalHubApplication.kt`, `GlobalDatabaseInstrumentedTest.kt` e Gradle migration-test support. Apri una migration/schema specifica solo su failure concreta; non leggere manualmente tutti i JSON.

# Design
- Esporre la lista esatta delle production migrations in un registry riusato da Room opening, temporary/import opening, path check e test.
- `canMigrateFrom(v)` deve verificare un path reale nel grafo fino al current, non un range numerico.
- Nessun `fallbackToDestructiveMigration`/delete-recreate.
- Startup/update gate prima delle feature writes:
  - fresh/current: open+validate;
  - older con path: snapshot recoverable → Room migrate → validate → abilita app;
  - older senza path, newer DB, migration/validation failure: non sostituire né abilitare writes; conserva/ripristina DB recuperabile e mostra stato utente conciso.
- Mantieni ordering del recovery import e memorizza successo per app-version/schema, evitando gate costoso a ogni Activity.

# Tests
Guidati automaticamente dagli snapshot esistenti: ogni historical version deve avere path completo e Room deve accettare lo schema finale. Usa representative data survival per core + tabelle introdotte dalle principali feature, non ogni colonna/tabella. Copri current→current, fresh, newer reject, missing/failing path no data replacement, destructive fallback absent. Una sola upgrade QA su DB disposable, mai downgrade del DB reale.

PASS solo se produzione e test condividono lo stesso grafo, tutti gli snapshot storici raggiungono current, startup è fail-safe e recovery esistente resta integro. Un solo bump/build/install/delivery se richiesto dal bootstrap; commit/push, roadmap, STOP.

Output: `PROMPT_ID`, `RESULT`, current schema, migration graph/versions tested, startup gate/failure behavior, Android check, version/APK/delivery, SHA, blocker.
