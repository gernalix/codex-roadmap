# Operational task state — global roadmap recovery

TASK_ID: CHATGPT-20260924-GLOBAL-RECOVERY
Updated: 2026-09-24 12:25 Europe/Copenhagen

## Objective
Apply the global audit findings, repair the prompt/roadmap workflow, complete all relevant PersonalHub work before the final APK, migrate the live PersonalHub DB externally to the final schema, and leave involved repositories tested, operational, clean and without unmanaged PBFs.

## Constraints
- This file is operational memory only; canonical lifecycle remains in roadmap.sqlite.
- Store conclusions/state only, never chain-of-thought, secrets or raw private transcripts.
- Canonical roadmap mutations go only through the codex-roadmap single writer.
- Avoid intermediate PRs unless technically required.
- Model/reasoning live only in roadmap metadata, never in Codex prompt text.
- Ready queue_position is the recommended launch order.
- Prefer direct ChatGPT work; use Codex only for local Fedora/device/runtime work.
- PersonalHub final APK is built only after all relevant PH work/tests/fixes are complete.
- PH DB migrations are external one-shot transformations after schema freeze; do not ship historical Room migrations just to rescue the live DB.
- Device operations must be serial-scoped when multiple Android devices are connected.

## Verified facts
- PersonalHub 920550 and Telegram collector 422308 are currently running in their separate parallel lanes; do not duplicate their work in this global chat.
- 218695 is now guarded by manual-prerequisite:confirm-eboks-scraper-needed; its target public repo exists but is empty, so after 582946 the task must be reevaluated before launch.
- 641903 has been superseded by materialized routing-safe successor 896074; 896074 depends on 302284 and resolves CCS from current repo/metadata instead of hard-coding project_id 96.
- Runaway 788315 is still active as of 2026-09-24 12:17 Europe/Copenhagen: 203 published cycles; latest heartbeat used GPT-6 Sol medium, 112823 total tokens, 1 tool call, and returned only DONT_NOTIFY.
- Phase-1 broad audit is complete; current work is its closure/reconciliation tail.
- Attention/PBF projection currently reports zero unresolved needs_fix items after successor coverage.
- Stale running states were reconciled: 620949 -> blocked + 994029; 254859 -> blocked + 812553; 354882 -> blocked/manual-login + 181259.
- PH detailed P0 ownership is in operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md.
- PH current main uses Room schema 22; 383662 (live DB 20 -> 21) is obsolete and replaced by the final migration path 913264.
- 920550 is running for the residual semantic-photo/owned-items scope; the later PH chain is 857906 -> 707603 -> 840907 -> 788606 -> 913264.
- All infrastructure PRs identified by the audit were resolved: PH #35 closed stale, CCS #24 merged, ActivityWatch #3 merged as b8ef359da6da83be2af64628a004abb27d9b39f1.
- 788315 still has a runaway local automation chatgptexporter-788315-completion; latest observed published cycle started 2026-09-24T10:07:25Z using GPT-6 Sol medium with ~112k input tokens. It is not exposed through ChatGPT task automation controls, so PROMPT_ID 222733 remains required locally.
- A separate ChatGPT automation, "Codex Fix Queue", was active hourly and redundantly scanned B/F/PBF state with a model. It was disabled directly at 2026-09-24T10:15:47Z because the PBF protocol now handles this without model polling.
- Pending non-PH audit:
  - 222733: valid emergency local task; run first.
  - 994029: valid local ActivityWatch/Kuma cutover; independent of 222733.
  - 302284: valid consolidated prompt-infrastructure runtime deploy; depends on 222733.
  - 812553: still valid; prompt-history exists, gernalix/ChatGPTExporter still does not; depends on 222733.
  - 714263: valid bounded sqlite-to-obsidian Kuma recovery; depends on 994029.
  - 181259: semantically valid only after Grindr login, but its declared repo gernalix/grindr-web-exporter does not exist on GitHub. A local checkout may exist, but the current roadmap target cannot use the generic remote single-writer safely until this is reconciled.
  - 556372: gernalix/grindr-export exists and is a distinct local-first selected-conversation exporter; do not treat it as an automatic replacement for the broader grindr-web-exporter lifecycle task. It remains dependent on 181259 to avoid browser contention.
  - 582946: correctly Waiting on manual MitID login.
  - 218695: correctly conditional; launch only if 582946 proves native e-Boks export insufficient, otherwise cancel it.
  - 588376: correctly Waiting on manual revocation of the old PAT.
  - 422308: valid new Telegram-notification history collector; independent but low priority relative to PH/global recovery.
- 641903 is unsafe as written: its explanation/tag correctly says project_id 96 is stale/points to Workflowy, but the executable prompt still hard-codes PROJECT_ID=96 and exact project=96. Its dependency on 302284 does not fix that by itself because 302284 does not reconcile the CCS project ID.
- A canonical replacement allocation request for never-run 641903 is open in MegaVault Issue #100: [prompt-id-command] chatgpt-ccs-641903-project-routing-replacement-20260924-v1. It must resolve current CCS project routing from authoritative metadata/repo identity rather than hard-code 96.

## Decisions
1. Stop 788315 heartbeat before other prompt-infrastructure runtime work.
2. Prioritize PH P0 above unrelated work after the emergency heartbeat stop.
3. Do not run 641903. Replace it with a routing-safe successor after MegaVault allocation Issue #100 completes; successor depends on 302284.
4. Do not launch 181259 merely after login until the missing gernalix/grindr-web-exporter remote/single-writer path is reconciled.
5. Keep 218695 conditional and cancel it if 582946 finishes the e-Boks export adequately.
6. No model-driven waiting/heartbeat/polling. Use bounded readback or non-model event mechanisms.
7. Use empirical prompt_costs after codex-usage attribution/backfill is deployed before making future model-cost recommendations.

## Completed
- 422308 model metadata is now GPT-6 Luna; no prompt-body rewrite was needed.
- 641903 is guarded by manual-prerequisite:resolve-ccs-project-id because verified runtime evidence shows legacy PROJECT_ID=96 resolves workflowy-importer, not chrome-codex-switcher.
- Synthetic SQLite validation confirmed the core regression: a three-cycle goal with a cumulative completion total plus a roadmap mirror counts as one 300-token sample; combined with a second 200-token task the reported average is 250, while a mixed-model task is excluded.
- prompt-history source changes landed on main: cli prompt-level aggregation, model_performance/token_efficiency SQL, v_model_performance view, README contract, and tests/test_model_analytics.py regressions.
- prompt-history model/reasoning analytics now use one sample per canonical PROMPT_ID from codex-usage only, aggregate cycle deltas, ignore roadmap mirror executions, and exclude mixed-model/reasoning tasks from ranking.
- Global Phase-1 audit and stale-state reconciliation.
- PBF disposition protocol landed on codex-roadmap/main and current attention projection has no unresolved needs_fix items.
- Persistent operational checkpoint protocol landed in AGENTS.md and operations/task-state/README.md.
- Token-discipline and metadata-only model/reasoning policies landed.
- Ready queue ordering policy landed.
- Workflowy projection source supports prompt_type and model/reasoning metadata.
- CCS source styling for /goal and model/reasoning landed and PR #24 merged.
- codex-usage source attribution fix landed; runtime deploy/backfill remains in 302284.
- 222733, 994029, 302284, 812553, 714263, 181259, 920550 and 913264 were allocated/materialized as required.
- Pending model audit migrated relevant tasks to GPT-6 metadata.
- Manual prerequisite/conditional tags verified for 181259, 582946, 218695 and 588376.
- Redundant hourly ChatGPT "Codex Fix Queue" automation disabled.

## Remaining
- Complete MegaVault Issue #100 allocation; register/materialize the routing-safe replacement of 641903 and supersede 641903.
- Reconcile 181259's nonexistent remote repo before it can become genuinely launchable.
- Run 222733 locally and verify 788315 no longer produces cycles.
- After 222733 PASS, run 302284 for the consolidated prompt-infrastructure runtime deploy/readback.
- Run 994029, then 714263.
- Keep 812553 behind 222733.
- Complete PH P0 chain and final external DB migration/APK/Pixel gate.
- Then process low-priority/non-PH tasks (including 422308, Grindr/e-Boks/Logseq chains) according to prerequisites and perform the final global gate.

## Blockers
- Local Fedora/device actions require Codex Desktop/local tooling.
- 788315 scheduler is local and not controllable through ChatGPT automations; 222733 must disable it.
- MegaVault allocation Issue #100 is still open at this checkpoint.
- 181259 targets a nonexistent GitHub remote (gernalix/grindr-web-exporter); local state must be reconciled before a safe successor can run.
- Exact current live PH DB identity/schema on Pixel must be read locally before final migration.

## Evidence
- gernalix/codex-roadmap canonical projections, mutation Issues #1012-#1031 and task materializations.
- gernalix/MegaVault allocator Issues #81-#100.
- gernalix/codex-usage published 788315 cycles.
- gernalix/prompt-history exists; gernalix/ChatGPTExporter and gernalix/grindr-web-exporter return GitHub 404; gernalix/grindr-export exists and has its own archive workflow.
- ChatGPT automation readback showing "Codex Fix Queue" disabled.
- PH/CCS/ActivityWatch repository and PR state already recorded above.

## Acceptance criteria
- No runaway/pointless high-cost model automation remains active.
- Roadmap lifecycle/Waiting/PBF state matches authoritative runtime/integration state.
- Every real PBF is resolved, intentionally closed, or linked to an active/completed successor.
- Ready order is the actual recommended execution order.
- No pending prompt embeds model/reasoning execution metadata.
- Workflowy/CCS runtime reflects the new metadata and styling after 302284.
- No pending prompt contains a known-invalid hard-coded project routing value.
- PH relevant work is complete before final build; final PH remote state is main-only.
- Live PH DB has rollback, external final-schema migration, integrity/FK/data-preservation checks.
- Final PH APK is release-validated, installed on Pixel and all relevant modules open with preserved data.
- Involved repositories end tested, operational and clean.

## Next action
Urgent local action: execute 222733 and verify no new 788315 heartbeat is scheduled. In parallel, continue direct remote cleanup: finish prompt-history prompt-level analytics verification/documentation, audit remaining conditional non-PH tasks without duplicating the running PersonalHub/Telegram lanes, and keep 896074 blocked behind 302284. After 222733 PASS, 302284 becomes the next infrastructure runtime gate.
