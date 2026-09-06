PROMPT_ID: 467318

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Implement recursive associative navigation over the Hub Context Graph so any HubContext-enabled entity can be the starting point for progressively narrowing the current scope.

Required example:

`Giovanni → Luoghi → Piazza Savona → Sessioni → 12/02/2026 13:30–14:53`

The same underlying facts must also be discoverable starting from Piazza Savona or from the Timer Session. Do not persist this UI path as a parent/child hierarchy or duplicated backlinks; it is a query/view over Context membership.

## Prerequisite
The dynamic HubContext Composer and the People/Timer/Places adapters must already exist and their focused tests/architecture guardrails must pass. Verify that state narrowly. Do not reopen earlier architecture unless an acceptance check proves a defect.

Increment `version.txt` exactly once by `+1` for this goal.

## Starting points
Start from the current HubContext scope/query repository, adapter registry, Composer entrypoint and People/Place/Session detail integrations created by the prerequisite tasks. Locate those exact known symbols with a targeted symbol search if paths differ; do not scan feature trees.

## Required scope semantics
Represent an ordered current scope of selected HubEntities.

Example:
- `[Giovanni]`
- `[Giovanni, Piazza Savona]`
- `[Giovanni, Piazza Savona, Session #123]`

At each step, candidate data must be derived from Contexts compatible with **the entire current scope**, not from independent pairwise links that can introduce false associations.

Provide efficient query results for at least:
- available related entity kinds/facets;
- candidate entities within each facet;
- distinct compatible Context count for each candidate;
- the current resolved entity summary.

Do not repeatedly offer an entity already in the scope unless a distinct semantic role explicitly requires it.

## Recursive explorer UI
Do not implement indefinitely nested accordions that progressively squeeze the mobile screen.

Use a breadcrumb/scope UX equivalent to:

`Giovanni › Piazza Savona › Session 12/02`

followed by related sections/facets such as:
- Persone;
- Luoghi;
- Sessioni;
- any future registered entity kind.

Required navigation:
- tap candidate → extend/restrict scope;
- tap breadcrumb level → return to that scope;
- Android back → previous scope;
- clear/restart;
- arbitrary practical depth without recursive UI nesting.

Provide a distinct action to open the owning module's entity detail where appropriate, while normal candidate selection continues the explorer. Do not force extra navigation hops just to inspect an entity.

## Detail-screen related sections
HubContext-enabled entity details must be able to show compact related sections generated from the same query engine.

Example from Giovanni:

`Luoghi`
- Piazza Savona — 2
- Oscar Cafe — 1

Selecting Piazza Savona creates scope `[Giovanni, Piazza Savona]`, after which the Session facet must show only Sessions compatible with both.

Counts must be deterministic and deduplicated. Default definition: number of distinct compatible Contexts for `current scope + candidate`, unless an adapter explicitly exposes a better domain metric without changing graph truth.

## Reverse symmetry
The same underlying Context membership must support:
- Giovanni → Piazza Savona;
- Piazza Savona → Giovanni;
- either of those scopes → their compatible Sessions;
- Session → its linked People/Places.

Do not persist separate reverse links.

## User-configurable related sections
From the app UI, persist per entity kind/module preferences for:
- which related sections are shown by default;
- section order;
- show/hide.

This controls presentation only. Hiding a section must **not** disable linking in the Composer or remove existing Context membership.

## Composer integration
From any current scope, `+ Aggiungi` / `+ Registra` must open the existing shared Composer with the entire current scope preselected, so the user never has to reselect already traversed entities.

## Performance/safety
Normal explorer paths must:
- use indexed Context/scope queries;
- avoid N+1 entity loading where batch resolution is available;
- avoid loading the whole graph into memory;
- paginate/lazy-load potentially large facets;
- be cycle-safe;
- avoid double counts caused by join multiplication.

Add a realistic synthetic query test sufficient to catch gross scaling regressions without building an unrelated benchmark framework.

## Required test fixture
Create test data equivalent to:

Context A:
- Giovanni
- Piazza Savona
- Session 12/02

Context B:
- Giovanni
- Piazza Savona
- Session 17/05

Context C:
- Giovanni
- Oscar Cafe
- Session X

Verify:
- scope `[Giovanni]` → Places: Piazza Savona = 2, Oscar Cafe = 1;
- scope `[Giovanni, Piazza Savona]` → Sessions: exactly 12/02 and 17/05;
- starting from Piazza Savona → People → Giovanni → the same two compatible Sessions;
- no duplicates or false Session X in the Piazza Savona scope.

Also verify breadcrumb/back, section visibility/order persistence, Activity recreation and Composer prefill from a multi-entity scope.

## Non-goals
- no new adapters for other modules yet;
- no generic Resource entity yet;
- no visual node/edge graph canvas;
- no global full-text search;
- no pairwise materialized backlinks;
- no unrelated module redesign.

## Acceptance
PASS only if:
1. any of Person, Place or Session can be the starting point;
2. each selection narrows against the entire current scope correctly;
3. the required recursive path and its reverse routes work without duplicated stored backlinks;
4. related sections/counts are deterministic and user-configurable;
5. breadcrumb/back/clear support deep navigation cleanly on mobile;
6. the Composer inherits the current scope;
7. query paths are indexed, deduplicated and avoid obvious N+1/full-graph loading;
8. focused tests plus one representative Android end-to-end flow pass;
9. architecture guardrails remain green.

Stop after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, scope semantics, facet query/count semantics, reverse traversal, breadcrumb/related-section configuration, performance checks, Composer prefill, tests/device check, commit SHA, blocker.