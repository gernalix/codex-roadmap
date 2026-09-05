PROMPT_ID: 348615

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Fix two localized regressions in the current Soldi module: account inclusion must affect only aggregate owned-money totals, and in-progress editor/navigation state must survive Activity recreation.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceCapsule.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceDao.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceEntities.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceAccountsInstrumentedTest.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceInstrumentedTest.kt`

Do not explore other finance/Git-exchange files unless a targeted test proves the bug reaches them. If an earlier task renamed a listed symbol/file, use one targeted search for it; no repository sweep.

## Known evidence
1. `SoldiActivity.kt` currently filters transaction rows through account `included`, causing an account excluded from the bottom total to disappear from transaction history too. Intended semantics: `included` selects which account balances contribute to the aggregate total; it does not hide transactions.
2. `SoldiScreen` keeps transaction/account/reconcile/product draft, tab, search and month in plain `remember` state. Configuration/Activity recreation drops unsaved user input and navigation state.

## Work
- Remove `included` from transaction-history visibility. Preserve normal month/search filters.
- Keep `FinanceCapsule.totals()` inclusion semantics unchanged unless a concrete bug is found.
- Preserve in-progress editor state and relevant navigation/filter state across `ActivityScenario.recreate()` / configuration recreation using the minimum robust mechanism (`rememberSaveable` with explicit Saver for simple state, or ViewModel/SavedStateHandle where required).
- Do not persist transient `busy/error` state in a way that can replay a write after recreation.
- No Soldi redesign, accounting refactor, Git-sync work or unrelated cleanup.

## Tests
- excluded account remains absent from aggregate total but all its transactions remain visible/searchable;
- inclusion preference still persists;
- recreate during transaction/account/reconcile editor preserves entered fields and selected screen;
- no save/write is duplicated by recreation.

Focused emulator/instrumentation check only if needed to prove recreation behavior.

Stop after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, filter fix, lifecycle mechanism, tests, commit SHA.
