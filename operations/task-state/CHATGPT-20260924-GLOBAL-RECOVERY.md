# Operational task state — global roadmap recovery

TASK_ID: CHATGPT-20260924-GLOBAL-RECOVERY
Updated: 2026-09-24 15:22 Europe/Copenhagen

## Objective
Apply the global audit findings, repair the prompt/roadmap workflow, complete all relevant PersonalHub work before the final APK, migrate the live PersonalHub DB externally to the final schema, and leave involved repositories tested, operational, clean and without unmanaged PBFs.

## Constraints
- **PersonalHub P0 is the master recovery lane now, and the live-DB migration/cutover is its highest-priority terminal milestone.** No non-PH recovery task may preempt PH while PH is actionable. After 788606 freezes the final commit/schema/artifacts, 913264 must run immediately—before any infrastructure, notification, branch-cleanup, or unrelated recovery work—to take rollback backups, migrate the real DB externally to the exact final schema, install the exact final APK on Pixel, and validate preserved real data. Exception only for a true PH blocker or a data/safety-critical emergency.
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

### Phase 2 — PersonalHub P0 + live DB migration (HIGHEST PRIORITY)
Detailed execution is owned by `CHATGPT-20260924-PERSONALHUB-P0.md`; keep only global gates here.
- [x] Record the obsolete intermediate PH DB task 383662 as superseded by the specialized final cutover path 913264; never launch 383662.
- [x] Implement and host-verify the optional PH ↔ Workflowy integration on `chatgpt/workflowy-integration` without a Room schema/version change; detailed checkpoint: `CHATGPT-20260924-PH-WORKFLOWY.md`.
- [x] Safely park the partially completed 302284 infrastructure task at pushed WIP commit `6f31ceeaa51e5b77b86d2a18620a34079329196a` on `codex-usage-monitor/task/302284`; do not integrate or continue it while PH is actionable.
- [ ] Resume and finish 920550 from its existing pushed checkpoint; Play/minified APK+AAB gate is complete, AVD-only synthetic QA and canonical integration remain.
- [ ] Reconcile and integrate `chatgpt/workflowy-integration` into the then-current PersonalHub main, rerun affected gates, delete the temporary branch, and record the merged commit.
- [ ] Run and integrate 857906 after 920550.
- [ ] Run and integrate 707603 on the resulting schema.
- [ ] Run and integrate 840907, including true offline behavior and artifact-size impact.
- [ ] Run 788606 release preflight; freeze the exact final PersonalHub main commit, Room schema/identity, minified APK/AAB and hashes.
- [ ] **ABSOLUTE NEXT STEP AFTER 788606:** execute 913264 immediately. Read the real Pixel DB identity/schema, take immutable DB/WAL/SHM + installed-APK rollback backup, externally migrate a copy directly to the frozen final schema, and pass SQLite quick_check/integrity/FK/data-preservation checks. Do not insert any unrelated task between 788606 and 913264.
- [ ] Install the exact frozen final APK on the primary Pixel using explicit ADB serial and verify Home + every module against preserved real data before any non-PH lane resumes.
- [ ] Before final cutover, converge every still-relevant PH side branch into `main`: prove patch/semantic uniqueness, merge/cherry-pick/squash only valid unabsorbed work through the canonical writer, then delete all absorbed/obsolete non-main PH branches and close stale PRs. End with clean main-only operational state.
- [ ] Do not resume non-PH recovery lanes until all PH items above are complete, unless PH is truly blocked.

### Phase 3 — Remaining prompt/infrastructure runtime closure (DEFERRED UNTIL PH COMPLETE)
- [x] Stop the runaway 788315 heartbeat/automation with 222733.
- [x] Verify 788315 produces no new model-driven heartbeat cycles after shutdown.
- [ ] Resume 302284 from its parked checkpoint and finish the remaining consolidated roadmap/Workflowy/CCS/codex-usage runtime readback.
- [ ] Run routing-safe CCS successor 896074 only after 302284 PASS.
- [ ] Run 994029 for the ActivityWatch/Kuma local cutover.
- [ ] Run 714263 only after 994029, closing the sqlite-to-obsidian Kuma residual.
- [ ] Run 812553 after 302284, using prompt-history as the canonical primary repo.
- [x] Complete prompt-history source-level model/reasoning analytics and regressions through ff694890.
- [ ] Verify the corresponding live/runtime import/backfill/readback during the infrastructure closure tasks above.

### Phase 4 — Notification and checkpoint infrastructure
- [x] Complete Telegram collector runtime acceptance: account authorization, RUN1=4,244 messages, RUN2=0/no-op, private Git history readable, timer enabled+active; details in `CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md`.
- [x] Deploy the user-requested one-day-auto-delete Telegram archive runtime on Fedora: duplicate-free local SQLite history, revision/tombstone handling, media retention, 5-minute timer, shared Telethon-session lock, and live runtime verification; details in `CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE.md`.
- [ ] Complete the Telegram source/lifecycle closure through canonical successor 966124; never launch 333860. Reconcile both the verified task/422308 baseline and `chatgpt/telegram-autodelete-archive` into fedora-system-monitor main, rerun bounded gates/readback, then delete the temporary branch.
- [ ] After sufficient Telegram history exists, audit noisy producers and apply only producer-specific fixes; verify the post-fix notification stream is quieter and still actionable.
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
PersonalHub P0 is now the sole master lane. Resume 920550 from its existing pushed checkpoint and continue serially through 857906 → 707603 → 840907 → 788606 → 913264. No non-PH task may run while PH is actionable.
Do not launch 994029 or 966124 in parallel from another chat; both remain parked behind the PH P0 cutover.

## Verified facts
- Current PH side-branch inventory is bounded to two real side branches: `task/920550` (2 commits ahead / 0 behind main) and `chatgpt/workflowy-integration` (11 commits ahead / 2 behind main). No other non-main PH branch contains recoverable work. Required order: finish/integrate 920550 → reconcile/integrate Workflowy branch → delete both only after main containment/semantic absorption is proved.
- 920550 Play/minified artifacts were produced successfully from the task worktree with release minification/resource shrinking enabled: `app-play.apk` = 191,469,880 bytes and `app-play.aab` = 87,776,741 bytes. Model weights remain outside the base app. The single Gradle build process exited; no duplicate build was launched.
- A direct user request temporarily preempted the PH-only rule to implement the one-day-auto-delete Telegram archive. That bounded runtime work is complete: fedora-system-monitor branch `chatgpt/telegram-autodelete-archive` is pushed through `2fc6c38`; 14/14 Telegram tests PASS; the live archive preserves Telegram call actions, exposes a no-ID human view with Italian/relative dates and sender names, and retains the earlier 61-message/3-media backfill; both Telegram timers remain enabled+active and concurrent collector startup succeeds under the shared session lock. No model-driven Telegram work remains active, so PersonalHub resumes as master immediately. Authoritative detail: `operations/task-state/CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE.md`.
- 302284 partial prompt-cost work is safely parked and pushed at `codex-usage-monitor/task/302284` commit `6f31ceeaa51e5b77b86d2a18620a34079329196a`; it is intentionally incomplete and must not be merged before PH 913264 PASS.
- Final PH migration source policy: at cutover, inventory the live Pixel DB plus all viable local/export/backup copies and migrate the freshest coherent dataset; do not assume an older backup is authoritative merely because it is easier to access.
- 302284 targeted source gates PASS: codex-roadmap 60 tests; github-autosync 57 tests; workflowy-importer 34 tests; codex-usage-monitor 17 tests; chrome-codex-switcher 3 tests plus Python host compile.
- During 302284, codex-roadmap exposed a real `resolved_by` contract bug: the PBF view understood the relation but the table CHECK rejected it silently. Fixed on main at `f7f67c04371301ab1aae35551234ac566c21d039`; migration-on-open was verified on a copy of the live roadmap DB preserving all 166 existing relations and restoring dependent views.
- github-autosync tests were accidentally invoking real systemd bootstrap on the user's Fedora host. Test isolation fix is integrated on main in `0abda5db71b0ea6518a4818ec2f370619302264b`; runtime behavior itself was not changed.
- PH ↔ Workflowy optional integration is implemented and host-verified on PersonalHub branch `chatgpt/workflowy-integration`; checkpointed remote head is `edd08138702f9ae6cc54c2964f109343a356a149`. It reuses Hub Context resources, adds no Room schema/version change, and has PASS evidence for consumer preflight, targeted Workflowy tests/app compile and architecture boundaries. At 2026-09-24 14:06 the branch is ahead 11 / behind 2 versus current PersonalHub `main` (`57883c2531400efacbefd2c63182bc11833f9537`), so final reconciliation/integration remains intentionally parked. Authoritative detail is `operations/task-state/CHATGPT-20260924-PH-WORKFLOWY.md`.
- 302284 was claimed at 2026-09-24 13:34 local via roadmap issue #1055 and remains canonically `running`, but user priority override now parks it operationally. It is no longer the master lane; PersonalHub P0 is.
- 222733 completed canonically via single-writer commit `0e5b710ac7a783395f70b6af35d69db45dba707f`. The only Codex automation directory is `chatgptexporter-788315-completion`, now `status = "DISABLED"`; bounded scan found zero active recurring automations. Shutdown boundary was 2026-09-24T11:25:10Z; latest published 788315 cycle started 2026-09-24T11:17:26Z, so no cycle exists after shutdown.
- PersonalHub 920550 is safely parked at pushed checkpoints. Roadmap still says `running` only because there is no pause lifecycle state; no active model/process is executing that lane.
- All five current operational checkpoints (global, PersonalHub P0, Telegram notification hygiene, ntfy checkpoints, infrastructure branch cleanup) were read back against `operations/task-state/README.md` at 2026-09-24 13:18; each now contains Objective, Constraints, Plan/checklist, Current step, Verified facts, Decisions, Completed, Remaining, Blockers, Evidence, Acceptance criteria and Next action.
- Handoff checkpoint refreshed for a new ChatGPT chat at 2026-09-24 12:48 Europe/Copenhagen.
- 641903 is no longer actionable: it is superseded by routing-safe successor 896074, which must run only after 302284 and resolves the CCS project from current repo/runtime metadata instead of hard-coding project_id 96.
- MegaVault allocation Issue #100 is no longer a blocker; it is closed. The canonical replacement 896074 already exists in the roadmap.
- 422308 remains terminal BLOCKED historically, but its human authorization prerequisite is now satisfied and the collector runtime is operational: RUN1 archived 4,244 messages, RUN2 was a zero-message no-op, the private history repo is readable via GitHub, and the 15-minute timer is enabled+active. Do not retry 422308; detailed ownership is in operations/task-state/CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md.
- Telegram source closure must use remote-canonical successor 966124. A local allocator fallback incorrectly produced 333860 for the same request_id; roadmap mutation #1056 superseded/replaced 333860, and MegaVault Issue #105 materialized 966124. Never launch 333860.
- prompt-history prompt-level model analytics source work is complete through ff69489074feae82a2838504ff6f2d03875caa2b: CLI aggregation, SQL analytics, v_model_performance, README contract and regressions all use one sample per canonical PROMPT_ID from codex-usage, aggregate cycle deltas, ignore roadmap execution mirrors, and exclude mixed-model/reasoning tasks.
- PersonalHub 920550 is the next active master target after the one-time safe checkpoint of partial 302284 work. Telegram may continue only as a stable non-model timer; no non-PH model lane may run while PH is actionable.
- 218695 is now guarded by manual-prerequisite:confirm-eboks-scraper-needed; its target public repo exists but is empty, so after 582946 the task must be reevaluated before launch.
- 641903 has been superseded by materialized routing-safe successor 896074; 896074 depends on 302284 and resolves CCS from current repo/metadata instead of hard-coding project_id 96.
- Phase-1 broad audit is complete; current work is its closure/reconciliation tail.
- Attention/PBF projection currently reports zero unresolved needs_fix items after successor coverage.
- Stale running states were reconciled: 620949 -> blocked + 994029; 254859 -> blocked + 812553; 354882 -> blocked/manual-login + 181259.
- PH detailed P0 ownership is in operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md.
- PH current main uses Room schema 22; 383662 (live DB 20 -> 21) is obsolete and replaced by the final migration path 913264.
- 920550 is running for the residual semantic-photo/owned-items scope; the later PH chain is 857906 -> 707603 -> 840907 -> 788606 -> 913264.
- All infrastructure PRs identified by the audit were resolved: PH #35 closed stale, CCS #24 merged, ActivityWatch #3 merged as b8ef359da6da83be2af64628a004abb27d9b39f1.
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
  - 422308: historical BLOCKED parent with runtime now validated; do not rerun. Canonical source-closure successor is 966124 and stays parked until Phase 4.
- 641903 is unsafe as written: its explanation/tag correctly says project_id 96 is stale/points to Workflowy, but the executable prompt still hard-codes PROJECT_ID=96 and exact project=96. Its dependency on 302284 does not fix that by itself because 302284 does not reconcile the CCS project ID.
- A canonical replacement allocation request for never-run 641903 is open in MegaVault Issue #100: [prompt-id-command] chatgpt-ccs-641903-project-routing-replacement-20260924-v1. It must resolve current CCS project routing from authoritative metadata/repo identity rather than hard-code 96.

## Decisions
- While PersonalHub P0 is actionable, ready non-PH tasks **994029 and 966124 must remain ready but parked**. Do not execute them from another ChatGPT chat or via Remote Desktop Commander before PH 913264 PASS, unless PersonalHub is truly blocked or a data/safety-critical emergency requires intervention.
- User priority override: PersonalHub + live DB migration now outrank all remaining non-PH recovery work. 302284 is parked after a safe checkpoint and resumes only after PH 913264 PASS, unless PH is truly blocked.
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
- Emergency runaway-Codex closure 222733 completed: heartbeat disabled, zero active recurring Codex automations, no post-shutdown 788315 cycle, canonical terminal state confirmed.
- Checkpoint-protocol compliance audit completed for all current operational checkpoints; missing PH/infra sections corrected in-place without creating competing checkpoint files.
- New-chat handoff prepared from persistent Git state; future continuation must reread this file first.
- 641903 superseded by 896074; no future chat should launch 641903.
- Telegram collector runtime is fully validated: authorization complete, RUN1/RUN2 PASS, timer active, private history repo readable. Source integration/lifecycle closure remains parked under canonical successor 966124; its specialized checkpoint is authoritative.
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
- When the master recovery returns to PersonalHub, reconcile/integrate the verified Workflowy branch, rerun affected gates, delete the temporary branch and update both PH/global checkpoints.
- Run routing-safe CCS successor 896074 only after 302284 PASS; never run superseded 641903.
- Reconcile 181259's nonexistent remote repo before it can become genuinely launchable.
- Resume 302284 only after PH 913264 PASS (or a true PH blocker), using its preserved partial checkpoint; do not redo already-verified work.
- Run 994029, then 714263.
- Keep 812553 behind 222733.
- Complete PH P0 chain and final external DB migration/APK/Pixel gate.
- In Phase 4, run only canonical Telegram successor 966124 to integrate the already-verified source fixes, then perform the history-based producer audit; do not rerun 422308 or launch 333860. Then process remaining conditional/non-PH tasks according to prerequisites and perform the final global gate.

## Blockers
- Local Fedora/device actions are available through the connected Remote Desktop Commander; use Codex only where a Codex agent is actually required.
- MegaVault Issue #100 is closed and no longer relevant; 896074 is the canonical routing-safe CCS successor.
- 181259 targets a nonexistent GitHub remote (gernalix/grindr-web-exporter); local state must be reconciled before a safe successor can run.
- Exact current live PH DB identity/schema on Pixel must be read locally before final migration.
- Telegram runtime and identity repair have no blocker: 966124 is canonical/materialized and parked until Phase 4. This must not interrupt the active Phase-2 master lane.

## Evidence
- gernalix/codex-roadmap canonical projections, mutation Issues #1012-#1031 and task materializations.
- gernalix/MegaVault allocator Issues #81-#100.
- gernalix/codex-usage published 788315 cycles.
- gernalix/prompt-history exists; gernalix/ChatGPTExporter and gernalix/grindr-web-exporter return GitHub 404; gernalix/grindr-export exists and has its own archive workflow.
- ChatGPT automation readback showing "Codex Fix Queue" disabled.
- PH/CCS/ActivityWatch repository and PR state already recorded above.
- Telegram evidence: operations/task-state/CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE.md and operations/task-state/CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE.md; fedora-system-monitor task/422308 through 5d8ed32 plus chatgpt/telegram-autodelete-archive through 2fc6c38; private data commit 99a9952479074f56095586a6ed3fb210111496db; MegaVault Issue #103 allocated 966124; roadmap Issue #1056 replaced 333860 -> 966124; MegaVault Issue #105 materialized 966124.

## Acceptance criteria
- No runaway/pointless high-cost model automation remains active.
- Roadmap lifecycle/Waiting/PBF state matches authoritative runtime/integration state.
- Every real PBF is resolved, intentionally closed, or linked to an active/completed successor.
- Ready order is the actual recommended execution order.
- No pending prompt embeds model/reasoning execution metadata.
- Workflowy/CCS runtime reflects the new metadata and styling after 302284.
- No pending prompt contains a known-invalid hard-coded project routing value.
- PH relevant work, including the checkpointed optional Workflowy integration, is complete before final build; final PH remote state is main-only.
- Live PH DB has rollback, external final-schema migration, integrity/FK/data-preservation checks.
- Final PH APK is release-validated, installed on Pixel and all relevant modules open with preserved data.
- Telegram notification-history runtime is operational, canonical source closure is PASS, and producer-specific notification hygiene has been verified against the real post-fix stream.
- Involved repositories end tested, operational and clean.

## Next action
Hand control immediately to `CHATGPT-20260924-PERSONALHUB-P0.md` and resume 920550 from its existing pushed checkpoint. Continue the PH chain serially to schema freeze. At 913264, select the freshest coherent PH DB available at that moment, preserve immutable rollback, migrate externally to the exact frozen schema, validate integrity/data, install the exact final APK on the Pixel with explicit serial, and complete all-module real-data smoke before returning to any non-PH recovery.
