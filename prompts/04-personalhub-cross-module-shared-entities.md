PROMPT_ID: 306851

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Make Personal Hub modules genuinely interoperable through shared canonical entities/relations, without duplicating facts across module-owned tables.

Concrete target scenario: one fact such as “today 16:00–18:00 I walked with Carlo in Piazza Umberto” must be representable as one activity/time interval linked to the canonical People entity for Carlo and canonical Places entity for Piazza Umberto, rather than copying person/place data into Timer.

## Work
Inspect only the existing PH database schema/repositories for People, Timer and Places plus their shared database infrastructure. Design and implement the minimum reusable cross-module relation model that fits the current architecture.

- Reuse canonical entity IDs already owned by modules.
- Prefer foreign keys/junction/link tables over copied names/addresses/labels.
- Preserve module ownership: People remains source of truth for people; Places for places; Timer/activity data for intervals.
- Make the shared links queryable from the relevant module paths so future modules (including Soldi) can reference canonical entities instead of duplicating them.
- Add migrations and targeted tests for referential integrity and representative cross-module queries.
- Do not build speculative UI beyond the minimum needed to prove/use the relationship model.

## Safety / non-goals
No broad schema rewrite, event-sourcing migration, cleanup, or conversion of unrelated tables. Preserve existing user data and sync/export semantics.

## Acceptance
The example scenario can be persisted and queried with no duplicated person/place descriptive data; migrations preserve existing data; targeted DB tests pass.

Stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, schema/relationship summary, migration safety, tests, commit SHA.