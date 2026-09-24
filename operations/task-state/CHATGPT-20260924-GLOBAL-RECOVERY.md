# Operational task state — global roadmap recovery

TASK_ID: CHATGPT-20260924-GLOBAL-RECOVERY
Updated: 2026-09-24 12:10 Europe/Copenhagen

## Objective
Apply the findings from the global audit, repair the prompt/roadmap workflow, complete all relevant PersonalHub work before producing the final APK, migrate the live PersonalHub database externally to the final schema, and leave involved repositories tested, operational, clean and without unmanaged PBFs.

## Constraints
- This file is operational memory only; it is not canonical roadmap lifecycle state.
- Do not store chain-of-thought. Store only verified facts, decisions, evidence, completed/restant work, blockers and next action.
- Canonical roadmap mutations must continue through the codex-roadmap single writer.
- Avoid intermediate PRs unless technically required.
- For Codex prompts, model/reasoning belong only in roadmap metadata, never in prompt body.
- Ready must be ordered in the recommended launch order.
- Prefer direct ChatGPT work where possible; use Codex only for work requiring local Fedora/device/runtime access.
- PersonalHub final APK must be generated only after all relevant PH tasks/fixes/tests/optimizations are complete.
- PersonalHub DB migrations must be external/one-shot; do not add permanent historical Room migrations to the APK.
- No generic ADB install command when multiple devices are connected; device operations must be serial-scoped.

## Verified facts
- Attention/PBF projection is now down to one unresolved leaf: 354882 (manual Grindr login, no fix successor yet).
- PROMPT_ID 994029 is allocated, registered and materialized for the final local Kuma/ActivityWatch runtime cutover.
- ActivityWatch PR #3 was manually audited and merged as b8ef359da6da83be2af64628a004abb27d9b39f1 after GitHub Actions failed before test execution due the external billing gate.
- Stale roadmap Running states have been reconciled: 620949 is now blocked with successor 994029; 254859 is blocked and covered by follow-up 812553; 354882 is blocked/manual-login rather than falsely running.
- Phase 1 audit completed read-only.
- codex-usage publishes redacted native Codex session dumps to the private gernalix/codex-usage repository.
- Roadmap snapshot found 3 running, 13 pending, 25 blocked, 4 failed and 77 unknown records; 26 PBFs lacked an explicit fix relation.
- Running is inconsistent: 620949 already has terminal BLOCKED evidence; 354882 is stale/manual-wait; 254859 is marked running without a launch timestamp.
- PersonalHub main currently uses Room schema 22 and version.txt 60.
- Schema 21 -> 22 adds only since_when_counters and since_when_migration_state; existing schema-21 entities are unchanged.
- Prompt 383662 is obsolete as written because it targets live DB 20 -> 21 while current PH main requires 22.
- 624831 remains partially unresolved: successor 613102 fixed the shared photo engine/People legacy pipeline, but semantic photo indexing/search, image-to-image retrieval and owned-items functionality are not present on current main.
- PersonalHub remote branches observed: main and chatgpt/105883-since-when; the latter is 0 commits ahead and 30 behind main.
- Open PRs observed: PersonalHub #35 (stale head), activity-watch-uploader #3 (real residue of 620949), chrome-codex-switcher #24 (real fix, CI green, not on main).
- 788315 has a runaway automation heartbeat (automation_id chatgptexporter-788315-completion) invoking GPT-6 Sol medium approximately every 10 minutes with ~100k-token context and DONT_NOTIFY output. 190 cycles were published.
- Some codex-usage cycles for successor 613102 are misattributed to prompt_id 624831, so prompt-level cost/outcome attribution needs repair before automated model recommendation is trusted.
- Large PH goals 522084 and 822595 were inefficient mainly because of hundreds/thousands of model-tool round trips, not just model choice.
- Workflowy currently preserves queue_position but does not guarantee that Ready queue_position is the recommended launch order.
- Existing Workflowy CSS treats "Modello:" as muted metadata; requested model+reasoning purple/bold/underlined and distinct /goal styling are not implemented.
- Many pending prompt bodies still contain MODEL=/REASONING= despite the new metadata-only rule.

## Decisions
- PersonalHub detailed P0 state is delegated to `operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md`. Keep only cross-project dependencies and concise PH progress in this global file.
1. Emergency action before all other Phase-2 work: stop the runaway 788315 heartbeat.
2. Then prioritize PersonalHub P0 above unrelated project work.
3. PH P0 must complete all relevant PH functional work, PBF fixes, tests, merge/reconciliation, final schema freeze, release preflight, external live-DB migration, final APK build, and Pixel installation/smoke.
4. Do not migrate the live PH DB to an intermediate schema. Back up/inspect early; perform final transformation only after PH schema is frozen.
5. 383662 must be replaced/revised for live-schema -> final-schema migration rather than launched as-is.
6. 624831 should not be redone wholesale; create the smallest successor for the remaining semantic-photo/owned-items scope not already completed by 613102.
7. Stop using GPT-6 Sol for repetitive monitoring/polling. Luna-low or non-model condition checks should be preferred for bounded monitoring.
8. Model/reasoning decisions should use empirical usage after attribution/cumulative-goal accounting is corrected.

## Completed
- Pending model audit is GPT-6-clean after updating legacy 641903 and 422308 metadata; Sol remains only where complexity/data risk justifies it.
- All current pending canonical prompt bodies pass the metadata-only rule: zero MODEL=/REASONING= execution metadata embedded in the first 20 lines.
- Current HEADs of the eight infrastructure repositories have no attached GitHub Actions runs requiring repair; required verification is consolidated into local task 302284.
- Open Issue audit across codex-roadmap, MegaVault, codex-usage-monitor, workflowy-importer, github-autosync, chrome-codex-switcher, activity-watch-uploader and prompt-history found no real open issues after transport mutations drain.
- All infrastructure PRs identified in Phase 1 are resolved; org-wide open PR search currently returns none.
- Attention/PBF dashboard now reports zero unresolved items.
- PROMPT_ID 181259 is the waiting manual-login successor for the stale browser-export task; downstream dependency forwarding is active.
- PROMPT_ID 302284 replaces 729874 as the consolidated Fedora runtime activation for lifecycle, Workflowy/CCS and codex-usage fixes.
- 729874 is superseded.
- codex-usage-monitor attribution fix implemented on main: goal continuations can override stale inherited PROMPT_ID from authoritative roadmap_start output; reassigned cycle directories are removed; semantic publication version bumped to 7; regression tests added.
- PersonalHub P0 successors now exist: 920550 for residual photo/owned-items and 913264 for final live DB migration/APK/Pixel.
- PBF protocol implementation for 519810 already landed directly on codex-roadmap/main: recursive cycle-safe v_pbf_dispositions, v_attention needs_fix-only, tests/docs.
- chrome-codex-switcher PR #24 merged to main.
- PersonalHub PR #35 closed as stale/non-mergeable residue.
- Workflowy projection now exposes prompt_type (/goal) and model/reasoning as dedicated metadata; chrome-codex-switcher main contains cyan /goal styling and purple/bold/underlined model styling with regression coverage.
- PROMPT_ID 222733 allocated/materialized as the emergency local task to disable chatgptexporter-788315-completion; it is present in the canonical registry as pending.
- Persistent operational-memory protocol added to codex-roadmap AGENTS.md and operations/task-state/README.md.
- Token-discipline protocol added: no model-driven waiting heartbeats, no polling CI/merge/manual actions, stop after queued integration.
- Model/reasoning metadata-only rule added to protocol; GPT-6 Luna-first/Sol-for-complex-work policy documented.
- Ready queue_position documented as recommended launch order invariant.
- workflowy-importer changed to expose prompt_type /goal and model+reasoning as dedicated Workflowy metadata lines; targeted test added.
- chrome-codex-switcher main now contains dedicated ct-roadmap-model and ct-roadmap-goal styling plus regression coverage; PR #24 has been merged into main.
- Global Phase-1 audit.
- Persistent operational-memory protocol added to AGENTS.md and operations/task-state/README.md.
- Token-discipline protocol added: no model-driven waiting/heartbeats, no identical retries without new evidence, stop after asynchronous integration queue.
- Prompt metadata policy added: model/reasoning only in structured roadmap metadata; GPT-6 Luna-first/Sol-for-complexity policy documented.
- Ready ordering policy documented: queue_position must represent recommended launch order.
- Workflowy projection updated to expose prompt_type /goal and model+reasoning as dedicated metadata.
- chrome-codex-switcher updated to style model/reasoning purple+bold+underlined and /goal bright cyan; extension bumped to 0.3.9.
- PROMPT_ID 222733 allocated for the local runtime-only task that disables chatgptexporter-788315-completion.
- First 222733 mutation attempt rejected because relation was incorrectly embedded in register; corrected v2 mutation uses separate relation op and is queued.

- Identification of the last ten previously unaudited Codex tasks and review of outcomes/costs/artifacts.
- Branch/PR audit for PersonalHub and global open PR shortlist.
- Verification of current PH schema 22 and the 21->22 delta.
- Identification of 624831 residual work.
- Identification of runaway 788315 heartbeat.
- Verification that Codex reasoning/tool traces are durably published in codex-usage.
- Initial model-efficiency findings and workflow/dashboard gaps.

## Remaining
- Stop/disable 788315 heartbeat and verify it no longer fires. PROMPT_ID 222733 is registered/materialized and ready for local execution.
- Check for any other active high-cost recurring Codex/model automations and disable/rewrite them when wasteful.
- Deploy/verify the new persistent-memory and Workflowy styling changes on Fedora when local runtime access is available.
- Reconcile roadmap lifecycle/PBF states. DONE for stale running states: 620949→994029, 254859→812553, 354882→blocked/manual-login. Only 354882 remains an unresolved PBF leaf.
- Repair codex-usage prompt attribution and cumulative goal accounting where needed. SOURCE FIX DONE; runtime deploy/backfill remains local.
- Enforce metadata-only model/reasoning in non-running prompt bodies.
- Implement Ready recommended-launch-order invariant.
- Implement Workflowy styling for model/reasoning and /goal. SOURCE DONE; local runtime deployment/readback remains.
- Reconcile open PRs (#35 PH, #3 ActivityWatch, #24 CCS). DONE: PH #35 closed stale; CCS #24 merged; ActivityWatch #3 merged.
- Complete PH P0 task graph and final APK/db migration workflow. Detailed ownership delegated to operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md.
- Then process remaining non-PH roadmap/repository work and perform final global gate.

## Blockers
- Local Fedora/device-only actions require Codex Desktop/local tooling.
- The exact current live PH database schema/identity on Pixel must be read locally before migration.
- activity-watch-uploader #3 had CI failure reportedly tied to GitHub billing and needs current recheck.

## Evidence
- gernalix/codex-roadmap prompt-registry / task materializations.
- gernalix/codex-usage index/prompts.jsonl and per-cycle metrics/transcripts.
- gernalix/PersonalHub main, Room schemas 21/22, PRs #38/#39 and open #35.
- gernalix/chrome-codex-switcher PR #24.
- gernalix/activity-watch-uploader PR #3.
- OpenAI model documentation checked during Phase 1.

## Acceptance criteria
- No runaway/pointless high-cost model automation remains active.
- Roadmap Running/Ready/Waiting/PBF states match authoritative lifecycle/integration state.
- Every real PBF is resolved, intentionally closed, or linked to an active/completed successor.
- Ready is in actual recommended execution order.
- Pending prompt bodies do not duplicate model/reasoning metadata.
- Workflowy shows requested model/reasoning and /goal styling.
- PH relevant work is complete before final build; final PH remote state is main-only.
- Live PH DB is backed up, externally migrated to the final schema with integrity/FK/data-preservation checks, and rollback retained.
- Final PH APK is minified/release-validated, tested, installed on Pixel, and all relevant modules open with preserved data.
- Involved repositories end tested, operational and clean.

## Next action
Read back the final pending queue after mutation #1028. Audit remaining non-PH pending tasks for semantic obsolescence or conditional cancellation (especially e-Boks bootstrap and other manual-prerequisite chains). Then identify any direct remote fixes still possible before declaring the infrastructure track ready for the local execution sequence 222733 -> 302284 and later non-PH runtime tasks.
