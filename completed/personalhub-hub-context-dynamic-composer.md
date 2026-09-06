PROMPT_ID: 895243

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STRICT

# Goal
Make HubContext combinations and Context templates configurable directly from the Android UI so the user can create a new relationship idea while away from a computer, without changing code.

After this task, code may still be required once when a **new module/entity kind** joins HubContext, but creating a **new combination of already registered entity kinds** must be possible entirely from the app UI.

Examples that must require no code change once Person/Place/Session are registered:
- Person + Place;
- Person + Session;
- Place + Session;
- Person + Place + Session;
- multiple People + Place + Session;
- future combinations of any other already registered entity kinds.

## Prerequisite
The People/Timer/Places HubContext vertical slice must already exist and its focused tests/architecture guardrails must pass. Verify that state through the known HubContext adapter/Context flow only. Do not reopen the foundation or vertical-slice architecture unless an acceptance failure proves a defect.

Increment `version.txt` exactly once by `+1` for this goal.

## Starting points
Start from the current HubContext engine/repository, adapter registry, Context-type persistence and Person/Place/Session adapters created by the prerequisite tasks. Locate those exact known symbols with one targeted search if their final paths differ.

For host/detail integration, inspect only the existing detail/navigation entrypoints already used by the People/Timer/Places vertical slice and the app composition root if required.

## Required UI
### Ad-hoc Context Composer
From any HubContext-enabled entity detail, provide an action equivalent to `+ Collega` / `+ Registra attività` that opens a shared Composer.

The launching entity is preselected. Example from Giovanni:
- Person: Giovanni ✓
- `+ Aggiungi`

`+ Aggiungi` must list the entity kinds currently registered in the adapter registry, not a hardcoded list of People/Places/Timer combinations.

For an added entity kind, the Composer must use adapter capabilities to:
- search/select an existing canonical entity;
- optionally launch canonical creation if the adapter supports create;
- add/remove members;
- show current resolved labels;
- avoid duplicate accidental membership.

A Context created ad hoc must not require any Context Type/template.

### Edit existing Context
An existing Context must be reopenable and support:
- add member;
- remove member;
- replace member;
- preserve unrelated members;
- respect Context Type/cardinality rules when a type is assigned.

Do not recreate the Context as duplicated pairwise links.

### Context Type / template editor
Provide an in-app flow to create and edit user-defined Context Types. The UI must persist the existing Context-type model from the foundation rather than introducing Kotlin enums/combinations.

At minimum the user can configure:
- name;
- ordered fields;
- accepted registered entity kind/capability;
- field label;
- optional role;
- minimum/required cardinality;
- maximum cardinality or unbounded;
- field order.

Example user-defined template:

`Uscita`
- `Quando` → Timer Session, exactly 1
- `Con chi` → Person, 0..N
- `Dove` → Place, 0..1

### Save combination as template
After saving an ad-hoc Context, offer a flow equivalent to `Salva questa combinazione come template`.

It must create a new editable Context Type based on the participating entity kinds/roles without retroactively changing the already saved Context or copying its concrete members into the template.

### Entry-point prefill
Opening the Composer from:
- Giovanni preselects Giovanni;
- Piazza Savona preselects Piazza Savona;
- a Timer Session preselects that Session.

Design the API so a later recursive explorer can open the same Composer with an entire multi-entity scope prefilled.

### UX constraints
Cross-module linking is optional. The normal primary actions of a module must stay optimized for their original job: e.g. simple Timer Start/Stop must not gain mandatory linking steps.

Keep the common ad-hoc flow short: compact chips/cards, immediate search and sensible recent/frequent suggestions only if they can be derived cheaply from existing data without a new recommendation subsystem.

## Semantics
Separate these concepts explicitly:
- **registered adapter/entity kind** = technically available to HubContext;
- **Context Type field** = shown in that user-defined template;
- **default related section visibility** = a later explorer/UI preference, not permission to link.

Do not implement an allowlist/blacklist of pairwise module combinations.

## Non-goals
- no recursive/faceted explorer yet;
- no Soldi/Substances/WordPulse adapters yet;
- no generic Resource entity yet;
- no graph canvas;
- no global search;
- no redesign of unrelated module screens.

## Acceptance
PASS only if focused tests and one representative Android flow prove:
1. From Giovanni, create an ad-hoc `Giovanni + Piazza Savona` Context without a template.
2. Reopen it and add a Timer Session without recreating/duplicating existing relationships.
3. Remove/replace one member without losing unrelated members.
4. Create `Uscita` entirely from the UI with Timer/Person/Place fields and configured cardinalities/order.
5. Create a Context from that template and enforce required/max cardinalities clearly.
6. Change template label/order/cardinality without mutating already saved Context facts.
7. `Person 0..N` supports multiple people.
8. `Salva questa combinazione come template` creates an editable reusable type without copying concrete members.
9. Activity recreation preserves the Composer draft.
10. Adding a registered entity kind to the registry would make it appear through the generic Composer/Context Type mechanisms without pair-specific UI code.
11. Existing Timer/People/Places behavior and architecture guardrails remain intact.

Stop after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, ad-hoc Composer behavior, Context Type editor/cardinality, prefill/save-as-template behavior, proof of no-code combinations, tests/device check, commit SHA, blocker.