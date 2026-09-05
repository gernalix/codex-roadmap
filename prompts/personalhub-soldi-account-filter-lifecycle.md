PROMPT_ID: 348615

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Fix the localized Soldi lifecycle regression so in-progress editor and navigation/filter state survives normal Activity/configuration recreation.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceAccountsInstrumentedTest.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceInstrumentedTest.kt`

Open a directly referenced Soldi state/model file only if required by the selected save-state mechanism. If an earlier task renamed a listed symbol/file, use one targeted search only; no repository sweep.

## Known evidence
`SoldiScreen` keeps transaction/account/reconcile/product draft, tab, search and month in plain `remember` state. Configuration/Activity recreation drops unsaved user input and navigation state.

## Work
- Preserve in-progress transaction/account/reconcile/product editor state and relevant tab/search/month state across `ActivityScenario.recreate()` / configuration recreation using the minimum robust mechanism (`rememberSaveable` with explicit Saver for simple state, or ViewModel/SavedStateHandle where required).
- Do not persist transient `busy/error` state in a way that can replay or duplicate a write after recreation.
- Preserve existing accounting, account inclusion, totals and transaction-history behavior unchanged.
- No Soldi redesign, accounting refactor, Git-sync work or unrelated cleanup.

## Tests
- recreate during transaction/account/reconcile/product editor preserves entered fields and selected screen;
- tab/search/month state survives recreation where user-visible;
- no save/write is duplicated by recreation.

Use only the focused emulator/instrumentation check needed to prove recreation behavior. Stop after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, lifecycle mechanism, preserved state, tests, commit SHA.
