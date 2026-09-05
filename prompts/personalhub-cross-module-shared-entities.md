PROMPT_ID: 306851

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Phase 1 of cross-module entities: make PersonalHub modules interoperable through shared canonical People/Places relations, without duplicating descriptive facts across module-owned tables. Establish the persistence/domain/query foundation only; the user-facing linked-entity UX is a separate phase.

Concrete target: one fact such as “today 16:00–18:00 I walked with Carlo in Piazza Umberto” must be representable as one Timer/activity interval linked to the canonical People entity for Carlo and canonical Places entity for Piazza Umberto, not copied names/addresses in Timer.

A Timer interval linked to a Place must also be capable of representing the same temporal visit fact consumed by normal Places history/statistics without creating a second independently authoritative visit row that can drift or be double-counted.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/TimerEntities.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/sync/SyncJournal.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceEntities.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceDao.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactsRepository.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitMapper.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/SessionCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`

Do not scan module directories. Open a DAO/entity declaration directly referenced by these files only when needed to implement the FK/migration. If an earlier roadmap task renamed a listed symbol, resolve that exact symbol with one targeted search. After phase-1 implementation creates new relation files, use those directly for tests; do not discover adjacent architecture.

## Known current architecture
- People canonical identity is owned by SuperContacts/People.
- Places canonical identity is owned by Places (`places.uuid` in the current schema).
- Timer authoritative intervals are the canonical Timer session tables exposed through `SessionCore`/`SessionRepository`.
- Existing Finance→Places `RESTRICT` FKs provide a concrete deletion-policy precedent; the preceding roadmap task should have made that UI/domain behavior safe. Verify the current policy from the files above rather than rediscovering it.

After verifying the current schema/state and before code changes, increment `version.txt` exactly once by `+1`.

## Work
- Design and implement the minimum reusable relation model linking Timer/activity records to canonical People and Places IDs.
- Reuse stable canonical IDs already owned by each module; do not copy descriptive person/place data into Timer relation rows.
- Preserve ownership: People remains source of truth for people; Places for places; Timer for intervals.
- Prefer explicit junction/link tables and indexed FKs appropriate to actual cardinality.
- Define delete/archive semantics for every new FK: historical activity links must not be silently destroyed by deleting a person/place, and repository/domain flows must fail/archive-preserve coherently.
- Add repository/domain contracts for create/update/remove links and efficient forward/reverse representative queries so phase 2 can build UI without bypassing persistence rules.
- Define one authoritative representation for a Timer interval linked to a Place so Places history/stats can consume that same interval without a duplicate independently editable visit record. Manual/automatic Places visits that are not Timer-backed remain supported by the existing history model.
- Editing Timer start/end or changing/unlinking the Place must change the Places projection automatically; delete/unlink must not leave stale visits; total time and visit count must count a Timer-backed visit exactly once.
- Add a non-destructive Room migration from the actual current schema version and targeted migration tests with pre-existing data.
- Ensure global sync journal, generation/auto-export, DB validation/import/export and Datasette representation remain correct for the new tables. Do not add duplicate per-module transport.

## Explicit phase boundary
Do **not** build the general user-facing person/place selectors, inline creation, linked chips, reverse activity sections or cross-navigation in this task. Only minimal diagnostic/test wiring is allowed if strictly required to prove persistence. The next roadmap phase owns the user-visible integration.

## Safety / non-goals
No broad schema rewrite, event-sourcing migration, generic relationship engine, cleanup or conversion of unrelated tables. Preserve existing user data and real-app destructive-test guardrails.

## Resource discipline
This is high-risk because it changes the canonical DB schema, but exploration must remain narrow. Use the exact starting set, batch schema/repository inspection, test migration/FK/query/projection/sync invariants directly, then stop.

## Acceptance
- example interval can link to canonical person + place with no duplicated descriptive data;
- Timer-backed Place interval appears through the canonical Places history/stats query path without a second authoritative duplicate and without double counting;
- edit/change/unlink/delete semantics keep that projection coherent;
- migration from current production schema preserves existing rows and passes Room validation/foreign-key checks;
- delete/archive behavior is defined and tested for linked canonical entities;
- new rows participate correctly in generation/export/sync semantics;
- repository/domain APIs support efficient forward and reverse queries needed by phase 2;
- representative create/query survives reopen;
- targeted tests/build PASS; no speculative UI added.

Stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/relationships, Timer→Places single-source semantics, cardinality/delete semantics, repository/query contracts, migration safety, sync/export impact, tests, commit SHA.
