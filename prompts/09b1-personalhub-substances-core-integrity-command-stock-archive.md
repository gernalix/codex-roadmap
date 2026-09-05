PROMPT_ID: 774638

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Substances v2 — phase 1. Establish a safe canonical data/domain foundation: parent-row integrity, one authoritative command boundary for mutations, mathematically correct stock ledger, and reversible archive/restore. Preserve all real user data.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/capsules/CapsuleContracts.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseGate.kt`

The concrete Substances entities/DAO are referenced from the repository/database files above; follow those declarations directly rather than scanning `feature/sostanze`. If a prior task moved a listed symbol, resolve it with one targeted symbol search only.

## Decisive defects to verify before changing
- parent updates may use replace-like semantics capable of deleting/recreating rows and damaging FK-linked history;
- mutation rules are distributed across entry points instead of one domain command boundary;
- stock adjustments can represent a delta that differs from what was actually applied, including silent clamping/invalid unit assumptions;
- archived substances are not a complete reversible lifecycle;
- personal/demo seed rows must never appear silently in a real database.

After verifying current state, increment `version.txt` exactly once by `+1` before code changes.

## Work
1. Make substance updates true updates; never use delete+insert/`REPLACE` semantics for parent edits. Preserve intake/history, prescriptions, interactions, macro items, stock events and all valid FK children.
2. Add only the DB constraints/uniqueness required for obvious domain invariants and duplicate prevention. Any schema migration must be non-destructive and migration-tested from the actual current production schema.
3. Introduce or consolidate the minimum authoritative command/domain boundary through which Substances persistent mutations pass. UI, macro and future widget/notification actions must be able to reuse the same commands rather than duplicate business rules.
4. Make stock a coherent ledger. Required invariant: `previous stock + actually applied delta = new stock`.
   - insufficient stock must not record a full deduction/intake as though it succeeded;
   - undo restores exactly the amount actually deducted;
   - negative adjustments cannot silently clamp while recording the requested delta;
   - zero adjustment creates no meaningless event;
   - support `Set stock to X` by generating the exact required adjustment;
   - expose/retain adjustment history needed for later UI;
   - do not treat dose and stock units as interchangeable. Unsupported conversions fail clearly.
5. Implement archive + archived query/list contract + restore while preserving all history. Archived substances must be excluded from new active operations where semantically required.
6. Remove/disable automatic personal/demo seeding in real databases.
7. Inspect `CapsuleContracts.kt` only where required by the command boundary. Keep a genuinely used abstraction; remove dead contracts only if consumer-free and directly in scope.

## Non-goals
No scheduling redesign, interaction-rule redesign, macro UI, prescription/notification rebuild, history UI/performance work, import/export rewrite, or broad UI redesign in this phase.

## Tests
Targeted DB/domain tests must prove:
- editing a substance preserves every representative FK child/history row;
- migration preserves pre-existing data and passes Room validation/`foreign_key_check`;
- insufficient stock does not falsify the ledger;
- stock undo and `Set stock to X` are exact;
- invalid/unsupported units fail without mutation;
- archive/restore preserves history and active-operation eligibility changes coherently;
- no personal/demo seed appears on a clean production-style DB;
- representative mutation commands are atomic and use shared generation/auto-export semantics without duplicate export logic.

## Resource discipline
No repo-wide audit. Use only the exact starting files, directly referenced entity/DAO declarations and targeted tests; no identical retries, no unrelated cleanup. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, migration/integrity changes, command boundary, stock invariant, archive behavior, tests, commit SHA.
