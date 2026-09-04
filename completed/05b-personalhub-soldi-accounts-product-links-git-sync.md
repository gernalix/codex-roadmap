PROMPT_ID: 684213

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Correct and complete the newly migrated Soldi module before cross-module architecture work: make products truly canonical in transactions, add account-based balances/reconciliation, bring the main Soldi UX close to the supplied My Budget Book Pro reference screenshots, and add an OPTIONAL safe Git-backed exchange path so ChatGPT can add receipt-derived transactions externally.

Known state to reuse, not rediscover broadly:
- Soldi is already a native PH module from commit `a20e9171a2a48775980d673f2e418ca847b0121c` with normalized finance tables and isolated QA testing.
- `finance_transactions` already has `productId`, but the current UI product picker passes the product name into `title` instead of persisting the selected canonical `productId`. Fix this local defect.
- PH already has unified DB, sync/export infrastructure and guardrails protecting the real installed app/data. Preserve them.
- No old Soldi data needs importing for this task.

Use project_id 49/MegaVault/AGENTS first. Inspect only current Soldi finance capsule/UI/schema, PH DB/sync/export primitives directly needed here, and any existing authoritative Git integration pattern available in project context. Do not broadly explore unrelated modules.

## 1. Canonical products
- Selecting/purchasing an existing catalog product MUST persist its `productId` FK in `finance_transactions`; do not represent product identity only by copied title/name text.
- Keep `titleId` only for transaction description semantics where useful; product identity comes from `productId`.
- Editing/reopening a transaction must preserve and resolve the same product ID.

## 2. Accounts and balances
Add a canonical `finance_accounts` table (or equivalent consistent with existing naming) and make every transaction reference exactly one `accountId` FK.

- Account examples: Contanti, Danske Bank, Lunar, Revolut, Rejsekort.
- A transaction's signed amount changes the referenced account balance: positive increases it, negative decreases it.
- Do NOT maintain an independently mutable duplicated current-balance field if the balance can be derived reliably from an opening/baseline balance plus transactions. Choose one canonical accounting model and enforce it consistently.
- Support account opening/baseline balance and the minimum metadata needed for correct balance computation; avoid speculative banking features.
- Existing finance rows created before this migration must be migrated safely to a deterministic default account rather than left invalid.

## 3. Soldi home/account UX — reference screenshots
Use the supplied My Budget Book Pro screenshots as visual/interaction reference, not as a requirement to clone branding/assets pixel-for-pixel.

- Main transaction screen should prioritize transaction list/navigation and show ALWAYS at the bottom the total money currently owned across the accounts selected for inclusion.
- Add an Accounts screen/list broadly following screenshot 2: account name + useful balance information and a selectable inclusion control.
- User can choose which accounts contribute to the bottom total (e.g. include Revolut + Lunar, exclude Danske Bank). Persist this preference.
- Provide account create/edit only to the minimum extent needed to use the model.
- Keep Material/PH conventions where they conflict with copying the reference app literally; no unrelated visual redesign.

## 4. Reconcile/update an account balance
From an account, allow “update/reconcile balance” broadly following screenshot 3:

- user selects date/time and desired resulting account balance;
- compute `difference = desiredBalance - computedBalanceAtThatInstant`;
- on save create ONE normal compensation/reconciliation transaction on that same `accountId` for exactly the signed difference;
- resulting computed balance at that instant must equal the requested amount;
- allow a sensible default title/category/notes/provenance for the compensation transaction and keep it editable/deletable like other transactions;
- zero difference must not create a meaningless transaction unless there is a compelling existing domain reason.

## 5. Optional Git exchange for ChatGPT receipt ingestion
Add a Soldi Settings button on the module home. In Soldi settings expose an OPTIONAL configuration where the user can paste the Git repository URL to connect.

Purpose: ChatGPT may OCR a receipt externally and commit transaction data to that repository; PH can then pull/import those transactions. PH may also push its finance data/changes so the Git copy can stay usable as an exchange source.

Implement the safest/minimal architecture consistent with PH guidelines:
- Do NOT put credentials/tokens inside the repository URL, DB, exported JSON, logs, commits, or source code.
- A plain repository URL is configuration, not authentication. If private-repo authentication is required, use an existing secure credential mechanism available in PH/project guidance; if none exists, support public/auth-free operation first and leave authenticated private Git explicitly unsupported rather than invent insecure token storage.
- Prefer a small deterministic, versioned interchange representation for finance data/transactions (e.g. canonical JSON) over treating Git as concurrent replication of the live SQLite file, unless existing project guidance proves whole-DB Git transport is safe and preferable.
- Import by stable IDs/UUIDs with idempotent upsert/deduplication: pulling the same Git state twice must not duplicate transactions.
- Define conflict behavior explicitly and conservatively; never silently overwrite newer local data.
- Validate imported records, FK references/account/product mappings and amounts before committing them to the live DB; fail atomically on invalid input.
- Git import/export must go through normal PH database mutation paths so existing sync journal, generation tracking and SAF auto-export remain correct.
- Never run Git operations on the UI thread. Show concise sync status/error and explicit Pull / Push actions; do not add continuous background polling in this task.
- If pushing the full PH DB would expose unrelated modules or private data, DO NOT do it. Export only the minimum finance interchange data needed for Soldi/ChatGPT receipt ingestion.
- Do not implement OCR in PH.

## Safety / scope
Minimal coherent diff for these requirements. No broad PH refactor, generic Git-sync framework, generic accounting engine, ML/OCR, bank API integration, or unrelated UI work. Preserve existing PH real-app destructive-test guardrails. Do not uninstall/wipe/reset the real package or user data during QA/testing.

## Acceptance
Targeted DB/domain tests prove:
- transaction -> required account FK and signed balance effect;
- selected account subset -> correct aggregate total;
- product picker/purchase persists canonical `productId` and survives edit/reopen;
- reconciliation creates exactly the required signed compensation transaction and reaches the requested balance;
- migration preserves existing finance rows with valid account references;
- Git interchange round-trip is deterministic; repeated pull is idempotent; malformed/conflicting input cannot partially corrupt live data; no credentials leak into persisted interchange/logging.

Build must pass. On the isolated/project-approved QA device/emulator, verify: Soldi opens; create accounts/transactions and observe account + bottom aggregate totals; include/exclude accounts and see total update/persist; choose a catalog product and reopen the transaction with the same product identity; reconcile an account and verify the generated transaction/balance; close/reopen and verify persistence; configure a safe test Git repo/fixture and exercise explicit Push then Pull without duplicate transactions. Verify Soldi writes still participate in existing PH auto-export/sync paths.

## Final deployment — mandatory after PASS
Only AFTER all QA/tests above PASS, build the normal/main PersonalHub app artifact and install/update that MAIN package on BOTH the physical Pixel and the physical TCL resolved from the project's authoritative device context. This is final deployment, not destructive testing:
- preserve each device's existing PH app data and configuration; perform an in-place update only;
- do not uninstall, clear data, reset storage, substitute the `.qa` package, or run destructive instrumentation/benchmark lifecycle against the main package;
- verify the installed main PH version/build is the newly produced one on both Pixel and TCL and that PH launches successfully on both;
- if safe in-place installation cannot be completed on either device, RESULT must be `BLOCKED`, not PASS.

Stop immediately after all acceptance criteria and both final installations PASS; no further audit.

Final output only: `PROMPT_ID`, `RESULT=PASS|BLOCKED`, account model/balance semantics, canonical product fix, reconciliation behavior, Git interchange/auth/conflict design, targeted tests, QA device checks, Pixel main-app install/version, TCL main-app install/version, commit SHA.

## Execution record

RESULT: PASS — 2026-09-04. PersonalHub commit `8a6f3dc` (main, pushed).
Application 14 built after QA and installed in place on both physical main packages: Pixel 12→14, TCL 8→14. Both cold launches and Room 5 migration verified; all 54 preexisting domain tables preserved on each device. No original Soldi or synthetic QA data imported into main.
Targeted JVM gates, isolated TCL/Pixel instrumentation, real local Git Push/repeated Pull/external transaction ingestion, SAF readback and final Pixel UI checks passed. User refinements included readable localized timestamps, currency-separated account groups/totals, contextual screen titles and local field suggestions. Receipt content remains external; PH retains only the boolean provenance flag. Full design and evidence summary: target repository `docs/FINANCE_EXCHANGE.md`.
Only this prompt executed; no later prompt investigated or started.
