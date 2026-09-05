PROMPT_ID: 465850

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 2. Build correct therapy scheduling and make intake, interaction rules and macros converge on the phase-1 authoritative command/domain boundary.

## Prerequisite — verify narrowly
Use MegaVault/`AGENTS.md`, then verify that Substances has the safe command boundary, parent-row integrity, stock ledger and archive lifecycle from phase 1. If absent materially, stop `BLOCKED`; do not recreate phase 1.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Known defects / required behavior
The current logic has historically conflated frequency with `24/frequency`, mishandled start/end/forever/PRN, reset state around midnight, generated future/phantom missed doses, allowed some interaction BLOCK paths to be bypassed, and let macro/intake entry points diverge.

## Work
### Scheduling
Represent and evaluate real therapy schedules sufficient for:
- one or more explicit dose times;
- specific days when applicable;
- start date/time and end date/time;
- continuous/forever therapy;
- PRN;
- frequency only where it has a precise supported meaning.

Do not reinterpret historical periods using only the current regimen. Historical due/taken/missed calculations must use the regimen valid for that period.

Correct semantic states including due/`LATER`/`BLOCKED`/`TAKEN` and missed-dose generation. Never create future missed doses or fake midnight timestamps. Completion must respect dose quantities, not only row counts.

### Record intake command
All intake paths must call the same authoritative command and validate atomically:
- substance active/not archived;
- therapy active at requested timestamp;
- schedule timing;
- interaction BLOCK/WARN outcome;
- quantity/unit validity;
- stock availability where applicable;
- idempotency/duplicate protection.

Return explicit domain results such as success, warning, blocked, early dose, insufficient stock and duplicate. An early dose requiring user confirmation must not be indistinguishable from a normally due dose.

Support manual date/time and quantity, plus edit/delete with safe inverse stock/history behavior. Do not implement final UI redesign here; expose only the minimum UI needed to exercise the domain flow if current screens cannot.

### Interactions
- PRN and macro execution cannot bypass BLOCK;
- WARN remains distinct from BLOCK;
- reject self-target and invalid zero-duration rules;
- prevent semantic duplicates;
- when several BLOCK rules apply, use/report the actually most restrictive active block;
- support specific target and all-other-substances semantics where already intended.

### Macros
Macro items must execute through the same RecordIntake command. Return per-item outcomes and never report blanket success for unexplained partial execution. Prevent duplicate/retry/double-tap execution from recording the same intended action twice. Preserve archived-substance rules.

If an additional schema migration is genuinely required for explicit schedules, keep it minimal, non-destructive and migration-tested; do not redesign unrelated tables.

## Tests
Cover at minimum:
- start/end/forever and explicit schedule boundaries;
- dose around midnight/timezone-safe timestamp semantics;
- no future/phantom missed dose;
- quantity-aware taken/completion logic;
- double tap/retry idempotency;
- PRN and macro respect BLOCK;
- simultaneous BLOCK rules choose/report the correct active restriction;
- WARN does not block;
- early-dose result/confirmation contract;
- manual historical intake/edit/delete preserves ledger/history invariants;
- macro produces correct per-item outcomes and cannot silently partially succeed.

## Scope / resource discipline
No prescription/notification rebuild, history performance project, import/export cleanup or broad Substances UI redesign. Start from phase-1 commands plus scheduling/interaction/macro paths only. Targeted tests and hard stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, schedule model/semantics, intake command outcomes, interactions/macros behavior, migration if any, tests, commit SHA.
