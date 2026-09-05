PROMPT_ID: 934973

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Phase 2 of PersonalHub cross-module entities: make the canonical People ↔ Timer ↔ Places relations created by the preceding architecture task actually usable and visible to the user, including inline creation of missing canonical entities, without creating a generic entity-browser framework.

## Prerequisite — verify, do not recreate
Use MegaVault/`AGENTS.md`, then verify narrowly that the canonical cross-module link model already exists: Timer/activity records can reference stable People and Places IDs without copied descriptive data, with repository/query contracts, safe FK/delete semantics, and a Timer-linked Place interval can be exposed as one canonical Places visit/history fact without an independently authoritative duplicate.

If that foundation is absent or materially incomplete, stop `BLOCKED` and report the missing prerequisite. Do not reimplement the phase-1 schema task here.

## Exact starting files — verified on PersonalHub/main
After prerequisite verification, start with one grouped read of:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/sessions/controller/SessionOwnerCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/timeline/ui/TimelineScreen.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactsRepository.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/ui/contacts/ContactDetailCapsule.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/ui/app/SuperContactsApp.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceEditorDialog.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryScreen.kt`

Phase 1 will have introduced relation repository/DAO classes whose filenames do not yet exist at roadmap-authoring time. Locate those **once** by searching for the exact new relation table/API names recorded in `PersonalHubDatabase.kt`/phase-1 code, then use only those resolved files. Do not scan modules. If an existing listed file was renamed by an earlier task, one targeted symbol search is allowed.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## User-visible work
Implement the minimum coherent UX around the existing relation model.

### Timer entity selectors
In the relevant Timer session/activity create/edit flow, expose searchable canonical selectors equivalent to:

```text
Persona
[ Giovanni ]
[ + Nuova persona ]

Luogo
[ Cafe Oscar ]
[ + Nuovo luogo ]
```

Adapt labels/layout to existing PH UI conventions; the semantics above are mandatory.

- Existing Person/Place selection must use canonical entities and persist only stable IDs.
- `+ Nuova persona` must open/reuse the existing People creation flow (or the narrowest reusable equivalent), create the canonical People entity once, return its ID to the Timer editor and leave it selected.
- `+ Nuovo luogo` must open/reuse the existing Places creation flow (including current address/location validation where required), create the canonical Place once, return its ID to the Timer editor and leave it selected.
- A Place created from this Timer inline flow must default automatically to **radius = 75 m**. Persist the normal canonical Place radius field; do not create a Timer-only radius. The user may edit the Place later through normal Places UI.
- Do not create a second People/Places record if the user cancels creation or an equivalent canonical entity was not actually saved.
- Preserve editor state when temporarily navigating into inline creation and returning.

If phase 1 supports multiple people, the selector may be multi-select; the inline `+ Nuova persona` flow must still append/select the newly created canonical person. Follow the implemented canonical cardinality rather than inventing a second relation representation.

### Linked displays and navigation
- In Timer history/detail, show linked people/place using their current human-readable canonical labels; tapping a linked entity opens its existing detail flow when one exists.
- In People detail, expose a compact linked-activities section/list showing Timer intervals related to that person, with navigation to the Timer record.
- In Place detail, expose the equivalent linked Timer activities for that canonical place.
- A rename/edit in People or Places must automatically be reflected wherever the relation is displayed; no manual synchronization or duplicated label cache as source of truth.
- Preserve phase-1 archive/delete semantics. A UI action must not bypass relation integrity.

### Timer interval as Places visit — user-visible behavior
When the user saves a Timer interval linked to a Place, that same interval must also appear in normal Places visit/history/statistics paths according to the phase-1 single-source semantics.

Example: saving `16:00–18:00 + Giovanni + Cafe Oscar` must result in:
- one Timer interval;
- one People-linked activity visible from Giovanni;
- one Place-linked activity/visit visible from Cafe Oscar;
- **no second independently editable 16:00–18:00 visit copy**.

Editing the Timer start/end or changing the linked Place must update what Places shows automatically. Unlink/delete must not leave a stale Places visit. Total time and number-of-visits metrics must count the Timer-backed visit exactly once.

## Performance / state
- Use the repository/query contracts introduced by phase 1; avoid per-row N+1 lookups in history lists.
- Preserve selections and in-progress editor state across normal Activity/configuration recreation using current PH patterns.
- Linked records must survive close/reopen and normal process recreation through persisted IDs.

## Scope / non-goals
No schema redesign unless a tiny compatibility correction is strictly required by the already-implemented phase-1 contract. No generic graph UI, global search, recommendation engine, automatic inference of people/places, broad People/Timer/Places redesign, or Soldi redesign.

Do not add Places list sorting or redesign the Places map here; those are handled by a later dedicated Places UX task.

## Resource discipline
Use only the exact starting files, the phase-1 relation files resolved by the one targeted search, and directly failing tests. Batch inspection/test commands. Stop immediately after acceptance passes.

## Acceptance
- create/edit one Timer interval with canonical person + place links through UI;
- from the Timer selector create a new disposable Person and confirm it is canonical, selected and visible in People;
- from the Timer selector create a new disposable Place and confirm it is canonical, selected, visible in Places and has radius exactly/defaulted to 75 m;
- reopen and confirm links persist;
- Timer, People and Places surfaces all resolve the same linked activity without copied descriptive data;
- Timer-backed Place visit appears once in Places history/stats and is not independently duplicated; edit/unlink behavior stays coherent;
- rename a disposable/test canonical entity and verify linked displays resolve the new label automatically;
- navigation between linked surfaces works where supported;
- targeted tests/build PASS and one focused safe device/emulator flow proves create-inline/select/save/view/reopen/navigation.

Final output only: `PROMPT_ID`, `RESULT`, selector/inline-create flows, 75m Place default, Timer-backed visit behavior, relation queries reused, persistence/navigation checks, tests/device check, commit SHA.
