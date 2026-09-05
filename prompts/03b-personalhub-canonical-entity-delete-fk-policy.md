PROMPT_ID: 761284

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Fix the concrete Places↔Soldi referential-integrity regression and establish the minimum safe deletion policy that future canonical cross-module FKs can reuse.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceEntities.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceDao.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/places/PlacesCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/LuoghiHomeViewModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceInstrumentedTest.kt`

Open `FinanceAccountsInstrumentedTest.kt` or another directly relevant DAO/test only if the grouped inspection or a failing targeted test requires it. If an earlier roadmap task renamed a listed file, resolve that exact symbol with one targeted search; no repo scan.

## Known evidence
`finance_stores.placeId` and `finance_transactions.placeId` reference `places.uuid` with `ForeignKey.RESTRICT`. Places still exposes hard delete and its UI does not preflight/translate the resulting constraint failure. Once a place is used by Finance, deleting it can therefore fail at the DB boundary instead of producing a coherent user behavior.

## Work
- Define and implement the smallest canonical policy for a Place that is still referenced by another module.
- Preferred semantics: preserve historical references. Use archive when appropriate, or fail closed with a clear user-facing explanation; never cascade-delete Finance history merely to make Place deletion succeed.
- Make the repository/domain boundary return a meaningful result instead of leaking an uncaught SQLite constraint exception to UI.
- Keep ordinary hard-delete behavior only where it is demonstrably safe and intended.
- Add a reusable preflight/helper only if it materially reduces duplication for the immediately upcoming shared-entity work; do not build a generic entity framework.
- Preserve sync journal, generation/auto-export and existing Place history semantics.

## Tests
Targeted tests must cover at least:
1. unreferenced Place delete/archive path;
2. Place referenced by `finance_transactions`;
3. Place referenced by `finance_stores`;
4. user-facing/domain result on blocked/reference-preserving deletion;
5. Finance rows remain intact.

## Resource discipline
No general Places or Soldi audit. Use only the exact starting files plus a directly implicated test/helper, batch checks and stop after PASS.

## Acceptance
No normal Places delete action can surface an uncaught FK constraint for the known Finance relationships, and linked financial history can never be silently destroyed.

Final output only: `PROMPT_ID`, `RESULT`, deletion policy, affected paths, tests, commit SHA.
