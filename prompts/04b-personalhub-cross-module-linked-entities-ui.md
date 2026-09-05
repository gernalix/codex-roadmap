PROMPT_ID: 934973

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Phase 2 of PersonalHub cross-module entities: make the canonical People ↔ Timer ↔ Places relations created by the preceding architecture task actually usable and visible to the user, without creating a generic entity-browser framework.

## Prerequisite — verify, do not recreate
Use MegaVault/`AGENTS.md`, then verify narrowly that the canonical cross-module link model already exists: Timer/activity records can reference stable People and Places IDs without copied descriptive data, with repository/query contracts and safe FK/delete semantics.

If that foundation is absent or materially incomplete, stop `BLOCKED` and report the missing prerequisite. Do not reimplement the phase-1 schema task here.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## User-visible work
Implement the minimum coherent UX around the existing relation model:

- In the relevant Timer session/activity create/edit flow, allow selecting the canonical People and Place entities supported by the phase-1 cardinality. Reuse existing searchable/selectable UI patterns where available.
- Do not copy names, addresses or other descriptive fields into Timer. Persist only canonical relation IDs.
- In Timer history/detail, show linked people/place using their current human-readable canonical labels; tapping a linked entity should open its existing detail flow when one exists.
- In People detail, expose a compact linked-activities section/list showing Timer intervals related to that person, with navigation to the Timer record.
- In Place detail, expose the equivalent linked Timer activities for that canonical place.
- A rename/edit in People or Places must automatically be reflected wherever the relation is displayed; no manual synchronization or duplicated label cache as source of truth.
- Preserve phase-1 archive/delete semantics. A UI action must not bypass relation integrity.

If the current architecture naturally supports multiple people and one place, reflect that. If cardinality differs, follow the implemented canonical model rather than inventing a second relation representation.

## Performance / state
- Use the repository/query contracts introduced by phase 1; avoid per-row N+1 lookups in history lists.
- Preserve selections and in-progress editor state across normal Activity/configuration recreation using current PH patterns.
- Linked records must survive close/reopen and normal process recreation through persisted IDs.

## Scope / non-goals
No schema redesign unless a tiny compatibility correction is strictly required by the already-implemented phase-1 contract. No generic graph UI, global search, recommendation engine, automatic inference of people/places, broad People/Timer/Places redesign, or Soldi redesign.

## Resource discipline
Start only from the phase-1 relation repositories/DAOs plus the concrete Timer editor/history, People detail and Place detail surfaces. Batch inspection and targeted tests. Do not scan unrelated modules. Stop immediately after acceptance passes.

## Acceptance
- create/edit one Timer interval with canonical person + place links through UI;
- reopen and confirm links persist;
- Timer, People and Places surfaces all show the same linked activity without copied descriptive data;
- rename a disposable/test canonical entity and verify linked displays resolve the new label automatically;
- navigation between linked surfaces works where supported;
- targeted tests/build PASS and one focused safe device/emulator flow proves create/view/reopen/navigation.

Final output only: `PROMPT_ID`, `RESULT`, user flows added, relation queries reused, persistence/navigation checks, tests/device check, commit SHA.
