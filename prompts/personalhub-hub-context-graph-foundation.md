PROMPT_ID: 726594

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Implement the neutral, scalable **Hub Context Graph** foundation for PersonalHub.

Canonical entities must continue to belong to their owning modules, while multiple entities can participate in one N-ary Context. Future combinations such as `Person + Place + Timer Session + Transaction + Resource` must not require pairwise integrations such as People↔Places, People↔Timer, Places↔Timer, etc.

The architecture must scale by adding one adapter/binding for a new module/entity kind, not by adding code for every pair of modules.

## Prerequisite
`personalhub-complete-module-capsulization` must already be implemented and its architecture guardrail must pass. Verify that prerequisite with the narrow existing guardrail/build check only; do not repeat the encapsulation audit. If the prerequisite is missing or failing for reasons unrelated to this task, stop `BLOCKED`.

Capture the current PersonalHub version once and increment `version.txt` exactly once by `+1` for this goal.

## Starting points
Start from the current equivalents of these verified boundaries:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/build.gradle.kts`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/sync/SyncJournal.kt`
- `app/build.gradle.kts`
- `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`
- the public module/database contracts produced by the encapsulation task.

If encapsulation moved a known symbol, locate that exact symbol with one targeted search rather than scanning modules.

## Required model
### Hub entity identity
Introduce a neutral `HubEntity` identity/registry suitable for cross-module references.

A HubEntity is only a stable graph identity. It must **not** replace or duplicate the canonical domain entity:
- People still owns people;
- Places still owns places;
- Timer still owns sessions;
- Soldi still owns financial entities;
- other modules keep their own canonical data.

The Hub layer may store the minimum stable module/entity-kind identity and lifecycle metadata needed for graph integrity, but current labels/descriptions must remain resolved from the owning module rather than copied as a second source of truth.

Do not make a universal `from_module/from_id/to_module/to_id` pairwise edge table the primary relationship model. Use an explicit module-owned/typed binding seam so integrated entity kinds can retain real canonical identity/integrity without feature implementation dependencies.

### N-ary contexts
Implement the minimum normalized persistence for:
- `hub_contexts`;
- `hub_context_members`;
- the HubEntity registry/bindings needed by the chosen boundary design.

A Context must support:
- two or more participating entities;
- three/four/N-way facts without decomposing them into pairwise copies;
- multiple entities of the same kind where allowed;
- no mandatory parent/child hierarchy.

Prevent accidental duplicate membership of the same entity in the same role/context while allowing semantically distinct roles if the model explicitly supports them.

### User-defined Context types
Prepare the persistence layer for future Context templates created from the UI. Context types must be **data**, not Kotlin enums or hardcoded combination lists.

Persist enough information to define at least:
- Context type name/identity;
- ordered fields;
- module/entity kind or capability accepted by each field;
- user-facing label;
- optional role;
- minimum cardinality;
- maximum cardinality or unbounded;
- required state derivable from cardinality.

Ad-hoc Contexts must remain valid without any Context type/template.

### Public adapter/registry contract
Define a narrow public contract that an owning module can implement for one or more entity kinds. It must be sufficient for later tasks to provide, where applicable:
- stable identity/binding;
- existence/lifecycle resolution;
- current display summary;
- search/select capability;
- navigation/open capability;
- optional canonical create flow.

The Hub engine must not import feature implementation classes. Adapter registration/composition belongs at the app composition root or another boundary allowed by the encapsulation architecture.

### Query engine
Provide indexed repository/query contracts for at least:
- Contexts containing one HubEntity;
- Contexts containing **all** HubEntities in a supplied scope;
- distinct entities related to an entire scope;
- grouping/faceting by module/entity kind;
- reverse traversal and distinct counts.

Design the normal list/facet paths to avoid N+1 lookup patterns and loading the entire graph into memory.

### Delete/archive/history semantics
Define and test explicit behavior for:
- deleting a Context;
- removing one member;
- canonical entity archive/delete;
- preventing silent orphan references;
- preserving historical readability when the owning domain requires it.

Do not silently cascade away historical associations merely because an owning record changes lifecycle state.

## Migration / shared infrastructure
Add only the non-destructive Room migration required by this foundation. Preserve the canonical single `personalhub.db`, generation/auto-export, import/export, sync journal and Datasette behavior.

## Non-goals
- no full user-facing Composer yet;
- no real People/Timer/Places adapters yet;
- no Soldi/Substances/WordPulse adapters yet;
- no recursive explorer UI;
- no graph-canvas visualization;
- no global search;
- no pairwise module relationship framework;
- no unrelated domain/schema cleanup.

## Acceptance
PASS only if all of the following are true:
1. PersonalHub has one generic N-ary Context foundation rather than pairwise module links.
2. A future new **combination** of already registered entity kinds requires no schema/code change.
3. A future new **entity kind/module** can integrate through the defined adapter/binding seam without feature→feature implementation dependencies.
4. Context types/templates are persisted as user-configurable data, while ad-hoc Contexts need no template.
5. Forward, reverse and all-members scope queries are indexed and tested.
6. Delete/archive/orphan behavior is explicit and safe.
7. Room migration preserves existing data and shared import/export/sync/auto-export behavior.
8. Focused migration/FK/index/query tests and the existing architecture guardrail pass.

Use fake/test adapters to prove the contract without prematurely integrating real feature modules. Stop after the task-specific acceptance checks pass.

Final output only: `PROMPT_ID`, `RESULT`, schema, Context semantics, adapter/binding contract, delete/archive semantics, query API, migration/shared-infrastructure checks, tests, commit SHA, blocker.