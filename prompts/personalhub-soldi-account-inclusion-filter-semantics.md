PROMPT_ID: 313314

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal

Fix the remaining Soldi account-inclusion semantics bug: `FinanceAccount.included` must control only whether an account contributes to the displayed owned-money total. It must never hide that account's transactions from transaction history/search/month views.

Use `MegaVault/ai/personalhubdoc.md` as the PH bootstrap. No repository-wide exploration.

## Exact starting files — verified on current PersonalHub/main

Read once:
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceCapsule.kt`
- `core/database/src/test/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceAccountsTest.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/FinanceAccountsInstrumentedTest.kt`
- `version.txt`

Open one additional directly referenced Soldi test/file only if a targeted test requires it.

Capture `version.txt` once and increment it exactly by +1 once for this goal.

## Required behavior

- Transaction list/history must include transactions from both included and excluded accounts, subject only to the existing month/search filters.
- `included=false` must continue to exclude that account from `FinanceCapsule.totals(...)` and from the list of account names shown under each total.
- Toggling inclusion must not modify, delete or reassign any transaction.
- Preserve account balance math, reconcile semantics, currencies, editor state persistence and all other Soldi behavior.
- Make the smallest UI/query change; no Finance refactor or cleanup.

## Verification

Add/adjust focused tests proving: excluded account transaction remains visible; excluded account does not contribute to total; re-including it restores only the total contribution; transaction data is unchanged. Run the smallest relevant unit/instrumented tests, then build only if required by the PH bootstrap.

Stop after targeted PASS and required terminal operations.

Final output only: `PROMPT_ID`, `RESULT`, transaction visibility semantics, total semantics, tests, version, commit SHA.