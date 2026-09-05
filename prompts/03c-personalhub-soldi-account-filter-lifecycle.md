PROMPT_ID: 348615

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Fix two localized regressions in the current Soldi module: account inclusion must affect only aggregate owned-money totals, and in-progress editor/navigation state must survive Activity recreation.

## Known evidence
Start from `feature/soldi/.../SoldiActivity.kt` and the Soldi capsule/tests only.

1. The transaction list currently filters rows with `accounts.any { it.id == row.value.accountId && it.included }`. This makes an account excluded from the bottom total disappear from transaction history too. The intended 05b semantics are: `included` selects which account balances contribute to the aggregate total; it does not hide transactions.
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
