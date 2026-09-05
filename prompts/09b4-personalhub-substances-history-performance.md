PROMPT_ID: 467485

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Substances v2 — phase 4. Make History correct, identity-stable and scalable without changing the already-established dosing/domain rules.

## Prerequisite
Use MegaVault/`AGENTS.md`; verify phase-2 canonical intake/scheduling semantics are present. If not, stop `BLOCKED`. Do not recreate earlier phases.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Known defects / work
- History/query joins must identify substances by stable IDs, never by mutable display name when an ID exists.
- Do not eagerly load unbounded intake history or synthesize one missed-dose row per expected dose over years.
- Avoid repeated `O(days × history)` rescans and minute-by-minute recomputation of data that does not depend on the current clock.

Implement a useful canonical History path with:
- readable temporal grouping;
- essential search/filter and substance filter;
- correct timestamp, dose/quantity/unit and missed-dose semantics from the phase-2 domain;
- edit/delete intake actions routed through the authoritative command layer;
- paging/lazy/targeted queries or equivalent bounded loading appropriate to the current architecture;
- aggregate/interval queries for derived missed/due information rather than materializing huge synthetic histories;
- only clock-dependent UI/state updated by a ticker;
- historical timestamps preserved as events, without arbitrary reinterpretation around midnight/timezone changes.

Add indexes only if justified by actual query patterns/plans; do not perform speculative DB tuning.

## Tests
Cover identity after substance rename, filters/search, edit/delete through commands, date/time boundaries, bounded query/loading behavior on a representative large fixture, and no pathological synthetic missed-dose expansion.

## Scope
No notification rebuild, import/export work, archive redesign or broad UI redesign. Modify only History/query/presentation paths plus directly justified indexes/tests.

Stop after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, identity/query changes, performance strategy, history UX changes, tests, commit SHA.
