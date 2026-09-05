PROMPT_ID: 571846

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Implement canonical People ↔ Timer ↔ Places linking end-to-end in one task: persistence/schema/query contracts plus the user-facing selectors, inline creation, linked displays/navigation, and Timer-backed Places visit semantics. Do not create duplicated descriptive facts or a generic relationship framework.

Concrete target: one Timer interval such as `16:00–18:00 + Giovanni + Cafe Oscar` links to canonical People/Places IDs and is the same temporal fact consumed by Places history/stats, with no second independently authoritative visit row and no double counting.

## Exact starting files — verified on PersonalHub/main
Start with grouped reads of the relevant schema/repository/UI boundaries only:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/TimerEntities.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/sync/SyncJournal.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactsRepository.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactModels.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/ui/contacts/ContactDetailCapsule.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/SessionCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/timeline/ui/TimelineScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitMapper.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceEditorDialog.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryScreen.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/GlobalDatabaseInstrumentedTest.kt`

Follow only directly referenced DAO/entity/navigation collaborators. One targeted symbol search is allowed for renamed files; no module scans. Increment `version.txt` exactly once by +1.

## Persistence/domain
- Reuse stable canonical IDs; People owns people, Places owns places, Timer owns intervals.
- Implement the minimum indexed FK/junction relation model and explicit safe delete/archive semantics; historical links must not silently disappear.
- Provide efficient forward/reverse repository queries without N+1 list lookups.
- A Timer interval linked to a Place must project into normal Places history/stats as the same fact. Editing time/place updates the projection; unlink/delete leaves no stale visit; count/time metrics count it once. Existing manual/automatic non-Timer visits remain supported.
- Add the minimum non-destructive Room migration and migration/FK tests. Preserve generation, auto-export, sync journal, import/export and Datasette correctness.

## User-facing integration
- Timer create/edit exposes canonical Person and Place selectors.
- Provide `+ Nuova persona` and `+ Nuovo luogo` inline creation using existing canonical flows; return/select the newly saved ID. A Place created here defaults to radius exactly 75 m. Cancellation creates nothing.
- Preserve editor state while navigating to inline creation and across normal recreation.
- Timer history/detail resolves current canonical labels; linked entities navigate to their existing detail flows.
- People detail and Place detail expose compact linked Timer activities with reverse navigation where supported.
- Renames resolve automatically from canonical data; never persist copied labels as source of truth.

## Tests / acceptance
Migration preserves existing data and passes Room/FK validation. Create/edit/reopen an interval with canonical person+place; inline-create a Person and 75m Place; verify reverse queries/navigation; rename resolves everywhere; Timer-backed Place visit appears exactly once and updates/unlinks coherently; representative rows survive reopen and participate in export/sync semantics. Run one focused safe emulator/device end-to-end flow after targeted tests.

No generic graph UI, global search, Places sorting/map redesign, broad schema rewrite or unrelated cleanup. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, schema/relationships, delete semantics, selectors/inline-create, 75m default, Timer→Places single-source behavior, migration/sync/export checks, tests/device check, commit SHA.
