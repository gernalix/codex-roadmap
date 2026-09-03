PROMPT_ID: 470318

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Add a Places feature “Dov'ero?” that answers where the user was at an arbitrary date/time using existing recorded place visits.

## UX / behavior
- Provide a date+time selector.
- If the selected instant falls inside a recorded visit, show that Place.
- If no Place covers that instant, find the immediately preceding recorded Place and immediately following recorded Place and report that the user was traveling/going from the former to the latter.
- Handle boundaries and missing previous/next data explicitly; never fabricate a location or route.

## Implementation
Reuse the canonical Places visit/history model, including manual visits if present. Query efficiently with targeted indexed lookups; add an index only if justified by the actual query plan/schema.

## Scope
No route reconstruction, GPS timeline inference, Maps API calls or unrelated Places redesign.

## Acceptance
Tests cover inside-visit, exact boundaries, between two visits, only previous, only next, and no data. Focused UI check confirms selector/result behavior.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, query semantics, tests, commit SHA.