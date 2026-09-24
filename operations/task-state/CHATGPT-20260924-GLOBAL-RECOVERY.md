# Operational task state — global roadmap recovery

TASK_ID: CHATGPT-20260924-GLOBAL-RECOVERY
Updated: 2026-09-24 13:21 Europe/Copenhagen

## Objective
Apply the global audit findings, repair the prompt/roadmap workflow, complete all relevant PersonalHub work before the final APK, migrate the live PersonalHub DB externally to the final schema, and leave involved repositories tested, operational, clean and without unmanaged PBFs.

## Constraints
- **Single active recovery lane until global recovery is complete:** run only one model-driven recovery task/corsia at a time. Do not launch another phase/task until the current one is terminal and checkpointed. Manual-prerequisite/Waiting tasks may remain parked; stable non-model background services may continue only if they do not mutate overlapping repos/state.
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

## Plan / checklist
### Phase 0 — Recovery framework and protocol
- [x] Adopt single-active-recovery-lane execution until the final global gate; parallel model-driven recovery prompts are suspended/avoided.
- [x] Establish the persistent operational-checkpoint protocol in `operations/task-state/README.md`.
- [x] Establish single-writer-only canonical roadmap mutations.
- [x] Establish model/reasoning as roadmap metadata only, never prompt-body text.
- [x] Establish Ready ordering as the actual recommended launch order.
- [x] Establish direct-ChatGPT-first execution and bounded Codex/local-runtime delegation.
- [x] Establish mandatory PBF disposition/successor handling so failed/blocked prompts cannot disappear silently.
- [x] Verify all current operational checkpoints against `operations/task-state/README.md`; PH and infrastructure-cleanup section gaps were corrected and all five current checkpoints now contain every required section.

### Phase 1 — Broad audit and stale-state reconciliation
- [x] Complete the broad Phase-1 audit across roadmap/runtime/infrastructure and PersonalHub.
- [x] Reconcile stale running states and allocate/materialize required successors.
- [x] Resolve infrastructure PR residue identified by the audit (PH #35, CCS #24, ActivityWatch #3).
- [x] Verify current Attention/PBF projection has no unresolved `needs_fix` item lacking disposition/successor coverage.
- [x] Supersede unsafe CCS prompt 641903 with routing-safe successor 896074; never launch 641903.
- [x] Guard conditional/manual tasks 181259, 582946, 218695 and 588376 with explicit prerequisites.

### Phase 2 — Emergency and prompt-infrastructure runtime closure
- [ ] Stop the runaway 788315 heartbeat/automation with 222733.
- [ ] Verify 788315 produces no new model-driven heartbeat cycles after shutdown.
- [ ] Run 302284 and verify the consolidated roadmap/Workflowy/CCS/codex-usage runtime deployment and readback.
- [ ] Run routing-safe CCS successor 896074 only after 302284 PASS.
- [ ] Run 994029 for the ActivityWatch/Kuma local cutover.
- [ ] Run 714263 only after 994029, closing the sqlite-to-obsidian Kuma residual.
- [ ] Run 812553 after 222733, using prompt-history as the canonical primary repo.
- [x] Complete prompt-history source-level model/reasoning analytics and regressions through ff694890.
- [ ] Verify the corresponding live/runtime import/backfill/readback during the infrastructure closure tasks above.

### Phase 3 — PersonalHub P0
Detailed execution is owned by `CHATGPT-20260924-PERSONALHUB-P0.md`; keep only global gates here.
- [x] Record the obsolete intermediate PH DB task 383662 as superseded by the specialized final cutover path 913264; never launch 383662.
- [ ] Complete and integrate all still-relevant PH implementation/validation work through the release-preflight gate.
- [ ] Freeze the final PH commit/schema/artifacts and complete external live-DB backup+migration+Pixel cutover via the specialized PH lane.
- [ ] Finish PH-specific branch/PR cleanup only after absorption is proved; end with clean main-only operational state.

### Phase 4 — Notification and checkpoint infrastructure
- [ ] Complete the Telegram notification-history collector lane after one-time human Telegram authorization; details in `CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md`.
- [ ] After sufficient Telegram history exists, audit noisy producers and apply only producer-specific fixes.
- [ ] Complete the ntfy checkpoint-notification lane and prove accepted Git checkpoint pushes produce one remote notification; details in `CHATGPT-20260924-NTFY-CHECKPOINTS.md`.

### Phase 5 — Conditional/manual project lanes
- [ ] Reconcile 181259's missing `gernalix/grindr-web-exporter` remote/single-writer path without guessing.
- [ ] After the real Grindr-login prerequisite and repo-routing fix, complete 181259.
- [ ] Run 556372 only after 181259 to avoid browser/session contention.
- [ ] Resume 582946 only after the user completes MitID login.
- [ ] Reevaluate 218695 after 582946: cancel it explicitly if native e-Boks export is sufficient; otherwise run it.
- [ ] Resume 588376 only after the old GitHub PAT is manually revoked.

### Phase 6 — Infrastructure branch cleanup
Detailed branch evidence is owned by `CHATGPT-20260924-INFRA-BRANCH-CLEANUP.md`.
- [ ] After active/integration tasks are terminal, perform the bounded patch-equivalence review and delete only proven-safe infrastructure branches.
- [ ] Re-read every affected remote and retain only canonical branches plus explicitly justified active/seed branches.

### Phase 7 — Final global gate
- [ ] Re-run roadmap Attention/PBF reconciliation and verify every real PBF is completed, intentionally closed, or linked to an active/completed successor.
- [ ] Verify no runaway/model-driven waiting, heartbeat or polling automation remains active.
- [ ] Verify Waiting/manual/conditional tasks still match their real prerequisites and no obsolete prompt is launchable.
- [ ] Verify no pending prompt contains model/reasoning execution metadata in its body or a known-invalid hard-coded project route.
- [ ] Verify Workflowy/CCS/codex-usage runtime reflects the consolidated metadata/lifecycle behavior.
- [ ] Verify PersonalHub final release/data migration/device acceptance is complete.
- [ ] Verify involved repositories are tested, pushed, clean, and branch cleanup is complete.
- [ ] Mark global recovery complete only when every acceptance criterion below is satisfied.

## Current step
Phase 2, first actionable item: stop the runaway 788315 heartbeat with existing task 222733, then prove no new model-driven cycles are produced before moving to 302284.

## Verified facts
- All five current operational checkpoints (global, PersonalHub P0, Telegram notification hygiene, ntfy checkpoints, infrastructure branch cleanup) were read back against `operations/task-state/README.md` at 2026-09-24 13:18; each now contains Objective, Constraints, Plan/checklist, Current step, Verified facts, Decisions, Completed, Remaining, Blockers, Evidence, Acceptance criteria and Next action.
- Handoff checkpoint refreshed for a new ChatGPT chat at 2026-09-24 12:48 Europe/Copenhagen.
- 641903 is no longer actionable: it is superseded by routing-safe successor 896074, which must run only after 302284 and resolves the CCS project from current repo/runtime metadata instead of hard-coding project_id 96.
- MegaVault allocation Issue #100 is no longer a blocker; it is closed. The canonical replacement 896074 already exists in the roadmap.
- 422308 is now canonically BLOCKED after implementation commit f577f66fb4cc9e354df032ee1b5dea527006ea9e; its only blocker is one-time Telegram account authorization (API ID/hash + Telethon session). Detailed ownership is delegated to operations/task-state/CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md. Do not retry it before new human auth evidence.
- Attention currently contains only 422308; treat it as a known manual-prerequisite leaf owned by the Telegram lane, not as an invitation to create another Codex retry.
- prompt-history prompt-level model analytics source work is complete through ff69489074feae82a2838504ff6f2d03875caa2b: CLI aggregation, SQL analytics, v_model_performance, README contract and regressions all use one sample per canonical PROMPT_ID from codex-usage, aggregate cycle deltas, ignore roadmap execution mirrors, and exclude mixed-model/reasoning tasks.
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
- Until the final global gate, recovery work is serialized: one model-driven lane at a time. Existing active tasks are first brought to a safe checkpoint/parked state before the master lane advances; no new parallel recovery prompt is launched.
- Do not duplicate the PersonalHub or Telegram lanes from the global recovery chat. PersonalHub detail belongs to CHATGPT-20260924-PERSONALHUB-P0.md; Telegram detail belongs to CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md.
1. Stop 788315 heartbeat before other prompt-infrastructure runtime work.
2. Prioritize PH P0 above unrelated work after the emergency heartbeat stop.
3. Do not run 641903. Replace it with a routing-safe successor after MegaVault allocation Issue #100 completes; successor depends on 302284.
4. Do not launch 181259 merely after login until the missing gernalix/grindr-web-exporter remote/single-writer path is reconciled.
5. Keep 218695 conditional and cancel it if 582946 finishes the e-Boks export adequately.
6. No model-driven waiting/heartbeat/polling. Use bounded readback or non-model event mechanisms.
7. Use empirical prompt_costs after codex-usage attribution/backfill is deployed before making future model-cost recommendations.

## Completed
- Checkpoint-protocol compliance audit completed for all current operational checkpoints; missing PH/infra sections corrected in-place without creating competing checkpoint files.
- New-chat handoff prepared from persistent Git state; future continuation must reread this file first.
- 641903 superseded by 896074; no future chat should launch 641903.
- Telegram lane 422308 implemented code/runtime preparation and is now blocked only on one-time Telegram authorization; its own checkpoint is authoritative for that lane.
- prompt-history analytics correction completed through ff694890 with prompt-level sampling/regressions; runtime import verification remains part of later local infrastructure work.
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
- Run routing-safe CCS successor 896074 only after 302284 PASS; never run superseded 641903.
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
- MegaVault Issue #100 is closed and no longer relevant; 896074 is the canonical routing-safe CCS successor.
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
Execute the existing 222733 closure locally now: disable the `chatgptexporter-788315-completion` scheduler/heartbeat, verify the scheduler is no longer active and that no new 788315 cycle appears after the shutdown boundary, then checkpoint this file. Do not duplicate PersonalHub 920550, Telegram 422308, ntfy, or branch-cleanup work owned by their specialized lanes.
