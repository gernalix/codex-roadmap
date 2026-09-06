PROMPT_ID: 314872

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STRICT

# Goal
Integrate People, Timer and Places as the first real vertical slice of the Hub Context Graph.

Concrete target: a fact such as `12:00–14:00 + Giovanni + Piazza Savona` must be represented by one Context containing canonical module-owned entities:
- Timer-owned Session;
- People-owned Person;
- Places-owned Place.

The same fact must be discoverable from Timer, Giovanni and Piazza Savona without copied labels, duplicated relationship facts or direct feature→feature implementation dependencies.

## Prerequisite
The Hub Context Graph foundation must already exist and its focused schema/query/architecture tests must pass. Verify that state narrowly through the known HubContext symbols/tests; do not redesign the foundation unless a failing acceptance check proves it necessary. If the prerequisite is absent, stop `BLOCKED`.

Increment `version.txt` exactly once by `+1` for this goal.

## Starting points
Start from the HubContext public contract/repository/registry introduced by the prerequisite plus these verified current feature boundaries (or their exact-symbol successors if an earlier task moved them):
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

Follow only directly referenced DAO/navigation collaborators. If a listed symbol moved, use one targeted symbol search; do not scan whole feature trees.

## Required integration
### Real adapters/bindings
Implement real HubContext adapters/bindings for:
- Person;
- Timer Session;
- Place.

Reuse canonical stable IDs. Current names/titles must resolve from the owning module; never persist copied labels as the authoritative Context value.

### Timer create/edit
Timer Session create/edit must allow optional Context membership with canonical Person and Place selection.

A normal Timer Session with no cross-module Context must remain fully supported and must not gain mandatory extra steps.

Support more than one Person if the foundation's cardinality model allows it without special-case pairwise code; Place may remain single-valued in this initial UX where semantically appropriate.

### Inline canonical creation
From the Timer selection flow provide:
- `+ Nuova persona` using the existing canonical People creation flow;
- `+ Nuovo luogo` using the existing canonical Places creation flow.

Return/select the newly saved canonical ID. A Place created from this flow must default to radius exactly **75 m**. Cancel creates nothing. Preserve the editor draft across navigation and normal Activity recreation.

### Timer-backed Places visit semantics
A Timer Session linked to a Place must be the same temporal fact consumed by Places history/stats. Do not create a second independently authoritative visit row for the same interval.

Required behavior:
- it appears exactly once in normal Places visit/history projections;
- duration comes from the canonical Timer Session;
- editing Session time updates the projected visit;
- changing Place moves the projection;
- unlink/delete/archive leaves no stale projected visit;
- count/time metrics do not double-count it;
- existing manual/automatic non-Timer visits remain supported.

### Reverse views/navigation
- Timer history/detail resolves the current Person/Place labels and can open their owner detail flows.
- People detail exposes compact linked Timer activities and can navigate to the relevant Session/Place where appropriate.
- Place detail exposes the relevant Timer activities/People and can navigate back.

These are views over the same Context membership; do not persist duplicated backlink rows.

### Rename behavior
Renaming Giovanni or Piazza Savona must automatically update every linked display because labels resolve from canonical data, with no Context rewrite.

## Migration/shared behavior
Add only migrations/binding tables required by these real adapters. Preserve one `personalhub.db`, import/export, auto-export generation, sync journal and Datasette behavior.

## Non-goals
- no fully dynamic Composer or Context Type editor yet;
- no recursive/faceted explorer yet;
- no Soldi/Substances/WordPulse adapters;
- no generic Resource entity;
- no Places sorting/map/geofence redesign;
- no global graph/search UI;
- no pairwise relationship framework.

## Acceptance
PASS only if a focused end-to-end flow proves all of the following:
1. Create/reopen a Timer Session linked to canonical Person + Place IDs.
2. The same Context is visible/navigable from Timer, Person and Place.
3. Renames resolve everywhere without duplicated descriptive facts.
4. A Timer-linked Place contributes exactly one visit/time fact and updates correctly on time/place edit, unlink and delete/archive.
5. Inline Person creation and 75 m Place creation work and cancellation is side-effect free.
6. Draft state survives the required navigation/recreation flow.
7. Representative links survive DB reopen and retain export/sync semantics.
8. Architecture guardrails still prove no feature implementation depends on another feature implementation.
9. Focused tests plus one safe representative Android end-to-end check pass.

Stop after these acceptance checks pass.

Final output only: `PROMPT_ID`, `RESULT`, adapters/bindings, Context flow, Timer→Places single-source behavior, inline creation/75m default, reverse navigation, migration/shared-infrastructure checks, tests/device check, commit SHA, blocker.