PROMPT_ID=499100
PROJECT_ID=101

# Goal

Bring `gernalix/minsp-export` to a complete, real, local export of every read-only category visible to the authenticated user's Min Sundhedsplatform account. Work only in the single-writer-assigned worktree. Do not treat setup, a partial crawler pass, or test success alone as completion.

## Safety

- MitID must only be completed manually by the user. Never automate, bypass, intercept, print, persist, or commit credentials, cookies, Authorization headers, or secrets.
- Use Chrome/Playwright only for read-only navigation, detail opening, expansion, pagination, lazy load, and read-only downloads. Never send messages, alter appointments, refill prescriptions, make payments, or change account preferences.
- Do not commit raw exports, health data, screenshots, profiles, cookies, or any personal data.

## Required work

1. Run the existing focused tests immediately and fix every in-scope failure.
2. Reuse/start the persistent Chrome profile; if login is needed, request only manual MitID completion, then continue automatically from the saved checkpoint.
3. Inventory all actual portal navigation, tabs, routes, detail links, button-only views, modals, pagination, `vis mere`, infinite/lazy loads, downloads, and read-only XHR/fetch APIs. Exhaust them.
4. Compare this inventory with crawler capture. Fix each demonstrated gap with the smallest site-specific adapter/selector/seed logic and a focused test where useful. Do not retry unchanged failures.
5. Preserve all useful HTML, JSON, PDF, XML/text, binaries and attachments with SHA-256 manifest/deduplication. For UI-triggered read-only POST or download flows, let the UI trigger the request and capture its response.
6. Demonstrate an intentional interruption after real data, restart from checkpoint, and prove no lost or artificial duplicate records.
7. Build and validate `normalized/health.sqlite`, coherent domain tables for the categories actually found, FTS5/search, and `text/complete-medical-record.md`.

## Acceptance evidence

PASS only with real evidence that: every observed readable section is captured or explicitly documented as unavailable with a precise reason; all observed pagination/lazy-load/details are exhausted; checkpoint/resume was demonstrated; raw artifacts and manifest hashes agree; `PRAGMA foreign_key_check` is empty; FTS search succeeds for a clinically present term; relevant normalized tables are checked; a real raw-to-normalized-to-search/Markdown sample is traceable; no retryable failure remains; Git contains no health data/secrets; and no account mutation occurred. Record categories absent/not accessible as `non esposta/non verificabile`, never fabricate data.

## Recovery and completion

Selectors, routes, browser crashes, timeouts, downloads, formats, parsers, schema, resume, FTS, packaging, permissions, and test failures are recoverable: collect evidence, apply the minimal repair, run the leaf gate, and continue. A hard external blocker is limited to unavailable manual MitID, account block, persistent portal outage, unavailable network, or an indispensable external permission/resource. Preserve checkpoint data before reporting it.

Final PASS: `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 499100 --confirm-executed`

Final BLOCKED: `python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 499100 --result BLOCKED --confirm-executed`

Final report, max 10 lines: PROMPT_ID, RESULT, PROJECT_ID, COVERAGE, RAW, NORMALIZED, RESUME, SEARCH, TESTS, BLOCKER.
