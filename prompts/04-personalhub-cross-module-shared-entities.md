PROMPT_ID: 306851

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Phase 1 of cross-module entities: make PersonalHub modules interoperable through shared canonical People/Places relations, without duplicating descriptive facts across module-owned tables. This task establishes the persistence/domain/query foundation only; the user-facing linked-entity UX is a separate phase.

Concrete target: one fact such as “today 16:00–18:00 I walked with Carlo in Piazza Umberto” must be representable as one Timer/activity interval linked to the canonical People entity for Carlo and canonical Places entity for Piazza Umberto, not copied names/addresses in Timer.

## Known current architecture / starting scope
Use MegaVault/`AGENTS.md` first, then inspect in grouped reads only:
- `core/database` Room schema/migrations and current FK/delete conventions;
- People canonical identity (`contacts`, including stable `public_id` if still current);
- Places canonical identity (`places.uuid` if still current);
- Timer authoritative `sessions`/`session_tags` model and its SessionCore boundary;
- Soldi only where its existing canonical Place relation provides a reusable pattern or constraint.

A prior audit found that existing Finance→Places `RESTRICT` FKs exposed a deletion-policy mismatch in Places. Verify the current state before adding new relationships; new links must not recreate uncaught constraint failures.

After verifying the current schema/state and before code changes, increment `version.txt` exactly once by `+1`.

## Work
- Design and implement the minimum reusable relation model linking Timer/activity records to canonical People and Places IDs.
- Reuse stable canonical IDs already owned by each module; do not copy descriptive person/place data into Timer relation rows.
- Preserve ownership: People remains source of truth for people; Places for places; Timer for intervals.
- Prefer explicit junction/link tables and indexed FKs appropriate to actual cardinality.
- Define delete/archive semantics for every new FK: historical activity links must not be silently destroyed by deleting a person/place, and repository/domain flows must fail/archive-preserve coherently.
- Add repository/domain contracts for create/update/remove links and efficient forward/reverse representative queries so phase 2 can build UI without bypassing persistence rules.
- Add a non-destructive Room migration from the actual current schema version and targeted migration tests with pre-existing data.
- Ensure global sync journal, generation/auto-export, DB validation/import/export and Datasette representation remain correct for the new tables. Do not add duplicate per-module transport.

## Explicit phase boundary
Do **not** build the general user-facing person/place selectors, linked chips, reverse activity sections or cross-navigation in this task. Only minimal diagnostic/test UI is allowed if strictly required to prove persistence through an already-existing flow. The next roadmap phase owns the user-visible integration.

## Safety / non-goals
No broad schema rewrite, event-sourcing migration, generic relationship engine, cleanup or conversion of unrelated tables. Preserve existing user data and real-app destructive-test guardrails.

## Resource discipline
This is high-risk because it changes the canonical DB schema, but exploration must remain narrow. Batch schema/repository inspection; do not scan unrelated modules. Test migration/FK/query/sync invariants directly, then stop.

## Acceptance
- example interval can link to canonical person + place with no duplicated descriptive data;
- migration from current production schema preserves existing rows and passes Room validation/foreign-key checks;
- delete/archive behavior is defined and tested for linked canonical entities;
- new rows participate correctly in generation/export/sync semantics;
- repository/domain APIs support efficient forward and reverse cross-module queries needed by phase 2;
- representative create/query survives reopen;
- targeted tests/build PASS; no speculative UI added.

Stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/relationships, cardinality/delete semantics, repository/query contracts, migration safety, sync/export impact, tests, commit SHA.
