PROMPT_ID: 306851

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Make PersonalHub modules genuinely interoperable through shared canonical entities/relations, without duplicating person/place facts across module-owned tables.

Concrete target: one fact such as “today 16:00–18:00 I walked with Carlo in Piazza Umberto” must be representable as one Timer/activity interval linked to the canonical People entity for Carlo and canonical Places entity for Piazza Umberto, not copied names/addresses in Timer.

## Known current architecture / starting scope
Use MegaVault/AGENTS first, then inspect in grouped reads only:
- `core/database` Room schema/migrations and current FK/delete conventions;
- People canonical identity (`contacts`, including stable `public_id` if still current);
- Places canonical identity (`places.uuid` if still current);
- Timer authoritative `sessions`/`session_tags` model and its SessionCore boundary;
- Soldi only where its existing canonical Place relation provides a reusable pattern or constraint.

A prior audit found that existing Finance→Places `RESTRICT` FKs exposed a deletion-policy mismatch in Places. Verify the current state before adding new relationships; new links must not recreate uncaught constraint failures.

## Work
- Design and implement the minimum reusable relation model linking Timer/activity records to canonical People and Places IDs.
- Reuse stable canonical IDs already owned by each module; do not copy descriptive person/place data into Timer relation rows.
- Preserve ownership: People remains source of truth for people; Places for places; Timer for intervals.
- Prefer explicit junction/link tables and indexed FKs appropriate to cardinality.
- Define delete/archive semantics for every new FK: historical activity links must not be silently destroyed by deleting a person/place, and UI/domain flows must fail/archival-preserve coherently.
- Make representative cross-module queries possible from the relevant repository/domain boundaries.
- Add a non-destructive Room migration from the actual current schema version and targeted migration tests with pre-existing data.
- Ensure global sync journal, generation/auto-export, DB validation/import/export and Datasette representation remain correct for the new tables. Do not add duplicate per-module transport.
- Minimal UI only if needed to create/view the linked record through an existing flow; no speculative entity browser or generic graph UI.

## Safety / non-goals
No broad schema rewrite, event-sourcing migration, generic relationship engine, cleanup or conversion of unrelated tables. Preserve existing user data and real-app destructive-test guardrails.

## Resource discipline
This is high-risk because it changes the canonical DB schema, but exploration must remain narrow. Batch schema/repository inspection; do not scan unrelated modules. Test migration/FK/query/sync invariants directly, then stop.

## Acceptance
- example interval can link to canonical person + place with no duplicated descriptive data;
- migration from current production schema preserves existing rows and passes Room validation/foreign_key_check;
- delete/archive behavior is defined and tested for linked canonical entities;
- new rows participate correctly in generation/export/sync journal semantics;
- representative create/query survives reopen;
- targeted tests/build PASS; device check only if user-visible flow changed.

Stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/relationships, delete semantics, migration safety, sync/export impact, tests/device check, commit SHA.
