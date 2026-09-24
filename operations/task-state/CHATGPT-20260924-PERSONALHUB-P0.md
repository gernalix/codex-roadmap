# Operational task state — PersonalHub P0

TASK_ID: CHATGPT-20260924-PERSONALHUB-P0
Updated: 2026-09-24 17:18 Europe/Copenhagen
Parent state: operations/task-state/CHATGPT-20260924-GLOBAL-RECOVERY.md

## Objective
Bring PersonalHub to its final usable state before producing the definitive Pixel build. Complete every still-relevant PH feature/fix/test/optimization identified in the global audit, converge all valid work onto main, freeze the final schema, externally migrate the user's real database to that final schema without adding permanent historical Room migrations, build and validate the final minified APK/AAB, install the exact final APK on the primary Pixel, and verify Home + all modules with preserved real data.

## Scope boundary
This file owns detailed PersonalHub P0 execution state.
The global recovery file owns cross-project orchestration, roadmap infrastructure, codex-usage, Workflowy, ChatGPTExporter, generic PBF/lifecycle work and the final global gate.
Do not duplicate detailed PH state back into the global file; keep only a concise progress/dependency summary there.

## Constraints
- Every non-main PersonalHub branch must be dispositioned before PH closure: compare against final `main`, integrate every unique valid change, prove already-absorbed branches contain no unique work, then delete the remote/local branch. Final accepted PH state is `main` only.
- User communication steer: status updates in this chat must use plain language with minimal technical jargon; report mainly what was done, what remains, blockers, and the next action.
- Operational memory only; not canonical roadmap lifecycle state.
- Do not store chain-of-thought. Store objective, constraints, verified facts, decisions, completed/remaining work, blockers, evidence, acceptance criteria and exactly one Next action.
- Canonical roadmap mutations go only through the codex-roadmap single writer.
- Use direct ChatGPT/GitHub work where possible; Codex only for local Fedora/device/build/runtime work.
- No generic ADB command when multiple devices are connected. Always use an explicit device serial.
- During Pixel testing before the final cutover, do not overwrite/touch the user's primary PH installation. Use emulator/TCL or a clone/test package with an equivalent DB when real-data behavior is required.
- The final APK installed on the primary Pixel must be the result of ALL still-relevant PH work below, not an emergency/intermediate build.
- Do not migrate the user's live DB to an intermediate schema. Back up/inspect early; apply the final external one-shot migration only after the PH schema is frozen.
- Do not add permanent historical Room migrations to the APK merely to migrate this one live DB. Migration of the user's DB is an external/local operation.
- Preserve immutable rollback: current DB + WAL/SHM where relevant + recoverable current APK/reference before final cutover.
- At final cutover, use the **freshest coherent PersonalHub DB available**, not automatically the oldest known backup or the easiest copy. Inventory the live Pixel DB plus viable local/export/backup candidates, compare real data freshness/provenance, and select the newest consistent source before migration.
- One PH schema-changing implementation at a time. Avoid concurrent PH tasks that touch PersonalHubDatabase/schema/DAO because previous overlap caused schema-version collisions.
- Final PH remote state should be `main` only. Before deleting any side branch, prove its useful work is either already patch/semantically present in `main` or integrate that work first; then delete local+remote branch and close any stale PR.
- Avoid intermediate PRs unless required by the repository single-writer/integrator protocol. Do not bypass protected writer flow.
- Model/reasoning live only in roadmap metadata, not prompt bodies.
- Stop Codex after queued integration/PASS; do not spend model turns polling CI/merge.

## Plan / checklist
### Phase 0 — Baseline and ordering
- [x] Complete the PH audit and identify the still-relevant P0 chain.
- [x] Revalidate the chain against current roadmap and `PersonalHub/main`.
- [x] Supersede obsolete intermediate live-DB migration 383662 with final cutover 913264.
- [x] Establish external one-shot live-DB migration and explicit-device safety rules.

### Phase 1 — No-op tag/history amplification hotfix
- [x] Implement and test hotfix commit `41920af`; integrated into `origin/main` and temporary hotfix branch removed.
- [x] Integrate `41920af` into `PersonalHub/main` and verify remote main contains it.
- [x] Remove the temporary hotfix branch/worktree after integration verification.

### Phase 2 — 920550 semantic photos / owned items
- [x] Claim 920550 and isolate `task/920550`.
- [x] Implement schema 23 photo index + optional owned items, local TinyCLIP/ONNX retrieval, OCR, text↔image, image↔image and “Trova questo oggetto”.
- [x] Verify tokenizer against the official model tokenizer and pass targeted unit/DB tests.
- [x] Pass consumer-preflight, Soldi compile, architecture gate and full debug app build.
- [x] Verify real-model synthetic same-object/text-image ranking and measure debug APK/runtime size.
- [x] Finish Play/minified artifact measurement for 920550 artifact; baseline-main comparison build is also running from an isolated temporary worktree for exact delta.
- [x] Run AVD-only synthetic QA for save→index, semantic text/image search, non-photo exclusion, same-object shortlist, owned-item create/remove and reopen/persistence: dedicated `FinanceSemanticPhotoQaDeviceTest` PASS 1/1 on canonical `Pixel_8a` emulator.
- [x] Finalize 920550 through canonical integration and inspect merged main: PR #41 merged at `66dbe0265ff4dcdba3221e12e7953518056ce951`; schema 23 identity `4b9b96396c8f9e750d13b0e6da70fdd9`; `finance_photo_index` + `finance_owned_items` present; all required CI PASS.

### Phase 3 — 857906 unified History/Search
- [ ] Run and review 857906 after 920550 integration.
- [ ] Verify one reused global/module search engine and removal/replacement of duplicate user-facing History/Log/Timeline surfaces.

### Phase 4 — 707603 Git History / restore
- [ ] Run 707603 on the resulting schema.
- [ ] Validate Git Data / Global History / restore only on safe copies/staging.

### Phase 5 — 840907 Datasette Lite offline
- [ ] Run 840907 after 707603.
- [ ] Verify true offline runtime, detached validated snapshots and acceptable artifact-size impact.

### Phase 6 — 788606 final release preflight
- [ ] Run 788606 with no new features.
- [ ] Pass minification/resource shrink, signing, bundletool/Play gates and bounded emulator smoke.
- [ ] Freeze exact final main commit, schema version/identity and final APK/AAB hashes/paths.

### Phase 7 — 913264 live DB migration and Pixel cutover
- [ ] Inventory all viable PH DB sources at cutover (live Pixel DB plus local/export/backup copies), record provenance/timestamps/data freshness, and select the freshest coherent source.
- [ ] Read the selected freshest source DB schema/identity; when the Pixel source is involved use the explicit Pixel serial.
- [ ] Take immutable rollback backup of the selected freshest source DB/WAL/SHM and recoverable current APK/reference before any migration/write.
- [ ] Externally migrate a copy of the real DB directly to the frozen final schema.
- [ ] Pass SQLite quick_check/integrity/FK and representative-data preservation checks.
- [ ] Install the exact frozen final APK on the primary Pixel using explicit serial.
- [ ] Verify Home + every module with preserved real data; retain rollback until acceptance.

### Phase 8 — Final PH cleanup
- [ ] Converge every still-relevant non-main PersonalHub branch into `main`: compare against current main for unique semantic work, integrate only valid unabsorbed changes through the canonical single-writer flow, then delete each absorbed/obsolete remote/local branch.
- [ ] Converge every remaining non-main PH branch: integrate all valid unique work into `main`, prove containment/patch-equivalence, then delete the branch; final remote target is `main` only.
- [ ] Prove obsolete PH branches/PRs contain no unique unabsorbed work, then remove them.
- [ ] Verify no relevant PH PBF/integration/action remains pending.
- [ ] End with clean, operational, main-only PersonalHub.

## Current step
920550 is merged and verified on `main`. Reconcile/integrate `chatgpt/workflowy-integration` onto main, rerun only its affected gates, delete absorbed Workflowy + local 920550 branch, then claim 857906.

## Verified facts
- Roadmap terminality and Git integration are temporarily split for 920550: canonical roadmap registry now says `completed / PASS`, but PersonalHub PR #41 is still open on head `3f32b8c` and `origin/main` does not yet contain the task. Operational gate for 857906 is therefore stricter than roadmap dependency alone: do not claim 857906 until #41 is merged and Workflowy is integrated.
- Exact zero-unique local branch set versus current `origin/main`: `feature/global-activity-register`, `feature/soldi-ui-v2`, `task/462279`, `task/514458`, `task/514458-23`, `task/522084`, `task/613102`, `task/620949`, `task/624831`, `task/637985`, `task/693278`, `task/728918`, `task/773323`, `task/822595`, `task/825147`, `task/879838`. These require no committed merge. Dirty uncommitted residues in 624831/728918 are separately classified as superseded and must not be integrated.
- Dirty historical worktree dispositions are now explicit: `task/624831` has no committed work unique versus current main and belongs to failed PROMPT_ID 624831, whose valid work is split into completed 613102 plus current 920550. Its uncommitted residue is superseded and must not be literal-merged. `task/728918` likewise has no committed work unique versus main; PROMPT_ID 728918 is superseded, its successor 649781 is also superseded, and roadmap evidence states the final PH chain no longer depends on the Obsidian archive. Its dirty uncommitted archive/Obsidian residue is obsolete, not a merge candidate. Preserve until final cleanup evidence is recorded, then remove the worktrees without integrating their superseded dirty state.
- Two historical PH worktrees are dirty and are **not safe to delete yet**: `task/624831` has modified Places/Soldi/photo/schema/UI files plus untracked schema19/photo UI files; `task/728918` has modified app/settings/database/sync/version files plus untracked archive/Obsidian code. All other listed historical worktrees are clean. Before final cleanup, diff these dirty worktrees against current/final `main` and either prove semantic absorption or checkpoint/integrate any genuinely unique valid work.
- Detached worktree cleanup evidence: `PersonalHub-capsule-isolation@c8fe8b7` and `/tmp/personalhub-main-play-baseline@57883c2` are direct ancestors of `origin/main`. `PersonalHub-autoexport-hotfix@30dba18` is not an ancestor but is patch-identical to main commit `af008c0cbc861a66099b5ffe61400b3501957f03` (same stable patch-id `3e507cc0b4aebdabc6f7445e2455e6b47cdb5749`). All three are safe final-cleanup candidates after active PH work completes.
- `codex/pr35-cleanup` is now classified as **semantically absorbed/obsolete**, not a branch to literal-merge. Its functional shared-tags/Soldi content corresponds to PR #34 / task 522084 head `fabb5a53c7a8deafe70ffc8ff310e003d45bd826`, which is already an ancestor of current `main`. Relative to that integrated head, the branch differs in only 9 cleanup/test/resource files and would even remove 110 lines from the Italian Sostanze strings file. Literal merge would risk regression; final action is containment proof + deletion.
- Local branch/worktree cleanup inventory at 16:34: `task/920550` is 4 commits ahead / 0 behind current `origin/main`; `chatgpt/workflowy-integration` is 11 ahead / 2 behind. All ordinary historical local task/feature branches inspected have 0 commits unique versus `origin/main` **except** `codex/pr35-cleanup`, which is 10 ahead / 58 behind and therefore requires patch/semantic absorption analysis before deletion. Several obsolete detached worktrees also remain and must be removed during final cleanup.
- Workflowy prospective reconciliation against 920550 head `b10117a` is already PASS in a temporary detached worktree: zero merge conflicts, one auto-merged overlap (`.codex/CODE_MAP.tsv`), consumer-preflight PASS, targeted Workflowy/Workflowy-days tests PASS, app compile PASS, architecture PASS. No published branch/main mutation was made.
- Canonical MegaVault emulator launch command was re-verified exactly as documented: with current GNOME `DISPLAY/WAYLAND_DISPLAY/XAUTHORITY`, `python3 tools/android_target_preflight.py start` returned `status=ok`, AVD `Pixel_8a`, serial `emulator-5554`, state `device`.
- `~/Downloads/personalhub (2).db` exactly matches the exported PH schema-22 Room identity: both report version 22 and identity hash `1b60cb2d2925f84f9ee2c527a4090ff5`. Combined with its additional domain rows versus the v59 snapshot, it is a structurally valid and substantively fresher local migration candidate, but still not automatically authoritative over the live Pixel DB.
- PR #41 CI timing was rechecked against the real Fedora clock: jobs started at 15:59 Europe/Copenhagen and were only ~9 minutes old at 16:08. This is within the observed normal range (previous Play preflight ~9m54s), so no cancel/retry is justified; leave checks to complete normally.
- The schema-22 `personalhub (2).db` is not merely larger because of Git history: versus the latest local Pixel-v59 snapshot it also contains +60 `word_entries`, +5 `quick_event_entries`, +3 `intake_events`, +3 `place_events`, +3 `stock_adjustments`, +2 `sessions`, +1 quick-event template, plus newer Hub Context/tag structures. It is therefore the current **freshest local candidate by substantive row evidence**, while the final authority still requires comparison with the live Pixel DB at 913264.
- Local DB candidate inventory for the final cutover is now recorded read-only. `~/Downloads/personalhub (2).db`: mtime 2026-09-24 11:11, 173,481,984 bytes, SQLite/Room user_version 22, identity `1b60cb2d2925f84f9ee2c527a4090ff5`, quick_check OK, 103 tables, 108,767 `hub_git_events`. Three Pixel v59 snapshots from ~01:19–01:31 are user_version 19, identity `f260af7cdaff1e252ecefb283da4445c`, quick_check OK, ~22.2 MB.
- Freshest-DB selection remains intentionally unresolved: sampled user-data signals are identical across those local candidates (94 contacts and 2 finance transactions with matching max update timestamps). File mtime/schema/history volume alone is not sufficient. 913264 must compare the live Pixel DB and any newer candidate at cutover before choosing the migration source.
- Expected post-920550 Room schema readback is pinned before merge: schema version 23, identity hash `4b9b96396c8f9e750d13b0e6da70fdd9`, 96 entities, including `finance_photo_index` and `finance_owned_items`. After PR #41 merges, `main` must reproduce this exact schema evidence.
- 920550 worker finalization is now correctly routed: `repo-task finish` created PersonalHub PR #41 after `roadmap_finish` alone had only queued the terminal roadmap mutation. One bounded integrator pass returned `checks-pending`; no model/CI polling is running. The non-model repo-integrator timer owns the next integration attempt.
- R8 mapping confirms the exact ONNX JNI contract now survives Play minification: `ai.onnxruntime.TensorInfo -> ai.onnxruntime.TensorInfo` and constructor `<init>(long[], String[], int)` is retained. This directly covers the JNI crash observed during QA.
- Final 920550 local gate set is complete at clean pushed HEAD `0834a2434abe9ddd3a1c43caf23ba646c5bc3923`: dedicated AVD QA PASS 1/1, final Play APK+AAB PASS, `checkArchitectureBoundaries` PASS, `git diff --check` PASS, clean worktree.
- Canonical emulator cleanup completed: repaired the official API36 Google APIs x86_64 system image to revision 7 (restoring missing `encryptionkey.img`), recreated `Pixel_8a`, and proved `emulator-5554` reaches ADB `device` + `sys.boot_completed=1`. Runtime identity: API 36, 1080×2400, 420 dpi. All other legacy/temporary AVDs were deleted; `emulator -list-avds` now returns only `Pixel_8a`.
- MegaVault emulator docs were updated in isolated repo task 920550 and queued as MegaVault PR #106: canonical AVD `Pixel_8a`, API36 rev7, screen coordinate bounds x=0..1079/y=0..2399, center=(540,1200), live serial resolution, and real GNOME-session launch requirements.
- 920550 QA packaging blocker fixed locally: QA previously packaged only `armeabi-v7a` for the TCL, so x86_64 emulator install failed with `INSTALL_FAILED_NO_MATCHING_ABIS`. QA now packages both `armeabi-v7a` and `x86_64`; rebuilt QA + androidTest artifacts PASS and install successfully on the canonical emulator.
- First real `FinanceSemanticPhotoQaDeviceTest` execution now reaches app logic but fails at `HubContextRepository.bind` with `IllegalArgumentException: Canonical entity does not exist` during `FinanceCapsule.saveTransaction`. This is the current concrete 920550 blocker; diagnose/fix only this path before rerunning the single QA test.
- Emulator cleanup investigation: installed API35/API36 Google APIs x86_64 system images are incomplete for current emulator runtime because they lack `encryptionkey.img`; all AVDs based on them fail immediately with “Encryption is requested but failed to create encrypt partition.”
- Emulator 37.1.11 crashes when launched outside the real GNOME graphics session (including headless/systemd launches using SwiftShader/off), but remains stable when launched inside the user GNOME environment with `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, current Mutter Xauthority, `-qt-hide-window`, cold boot and no snapshots.
- New candidate AVD `PersonalHub_API37_1_Pixel8a` uses Pixel 8a profile + API37.1 `google_apis_playstore_ps16k/x86_64`, 1080×2400, 420 dpi. It remains alive under the real GNOME session and currently presents as `emulator-5554 offline`; final ADB boot validation is the next gate before deleting legacy AVDs or declaring it canonical.
- Current PH remote branch inventory at 2026-09-24 14:53: only `task/920550` and `chatgpt/workflowy-integration` are real non-main branches. `task/920550` is 2 ahead / 0 behind main; `chatgpt/workflowy-integration` is 11 ahead / 2 behind main. No other PH side branch needs recovery.
- 920550 Play/minified artifact gate is complete: `app/build/outputs/apk/play/app-play.apk` = 191,469,880 bytes; `app/build/outputs/bundle/play/app-play.aab` = 87,776,741 bytes. Release/play inherit minification and resource shrinking; TinyCLIP weights remain downloaded on demand outside the APK.
- Current lateral-branch inventory at 2026-09-24 14:24: `task/920550` = 2 ahead / 2 behind main; `chatgpt/workflowy-integration` = 11 ahead / 2 behind; `chatgpt/105883-since-when` = 0 ahead / 32 behind. The last branch has no unique work and is safe to delete immediately; the first two must be integrated only after their respective validation/reconciliation gates.
- Current remote branch inventory at 2026-09-24 14:23: `task/920550` is 2 commits ahead / 2 behind `main`; `chatgpt/workflowy-integration` is 11 ahead / 2 behind; `chatgpt/105883-since-when` is 0 ahead / 32 behind. Therefore 920550 and Workflowy contain unique work that must be integrated; 105883 contains no unique commit and needs no merge, only final deletion after containment readback.
- A pre-schema-upgrade PersonalHub DB was measured at ~173 MB because `hub_git_events` contained 108,401 `UPDATE hub_tags` events; 108,123 had identical before/after payloads. The confirmed code path is Timer `persist()` -> `syncTimerNowTags()` -> `TimerSharedTagBridge.syncNow()` -> `SharedTagEngine.replace()/assign()` -> global `HubTagDao.refreshUsage()` plus an unconditional Git `AFTER UPDATE` trigger.
- Tag/history write-amplification hotfix `41920af` is integrated into PersonalHub `origin/main`; follow-up `57883c2` adds a safe no-op Git-history compactor. Neither changes Room schema/version.
- For 920550, the selected implementation path is TinyCLIP ONNX int8 downloaded on demand, not bundled in the base APK. Local verification found a ~24 MiB ONNX model with native 512-dimensional text/image embeddings; model card metadata reports MIT license. Verified model SHA-256: `844d1a46ab18acf50c989e541b12fe3b6dc7f8d6004725b4e992d142788e0600`. Tokenizer/preprocessor assets remain separate and downloadable.
- PersonalHub main is version.txt 60 and currently declares Room schema 22.
- Schema 21 -> 22 only adds since_when_counters and since_when_migration_state; existing schema-21 entities are otherwise unchanged.
- The old live-DB task 383662 (20 -> 21) is obsolete/superseded; do not launch it.
- Current final DB target must NOT be assumed to be 22 because remaining PH tasks can still change schema.
- DatabaseStartupGate on current main intentionally rejects a DB whose schema does not exactly match the app's expected schema, explaining why an older real DB can make current builds unusable.
- 613102 is PASS and main contains the shared photo engine, removal of People legacy photo pipeline, Places photo_uri, common previews/cache and the already-completed Soldi photo/search surfaces.
- 624831 was only partially satisfied. The still-missing residual is semantic/local photo intelligence and owned-items functionality; this is now isolated in PROMPT_ID 920550 rather than requiring a wholesale rerun of 624831.
- Current main did not contain finance_photo_index, finance_owned_items, embedding/OCR/cosine retrieval, image-to-image retrieval or “Trova questo oggetto” at audit time.
- PROMPT_ID 920550 exists for this residual scope and is the first PH P0 implementation task.
- PROMPT_ID 857906 exists for unified cross-module History/Search and depends on 920550.
- PROMPT_ID 707603 validates Git Data / Global History / restore on the final schema and depends on 857906 and 920550.
- PROMPT_ID 840907 completes Datasette Lite offline and depends on 707603 (and already-completed 489818).
- PROMPT_ID 788606 is the final Play/release preflight and depends on 840907.
- PROMPT_ID 913264 is the final live-DB migration + definitive APK/Pixel task and depends on 788606.
- Canonical intended PH P0 chain is therefore:
  920550 -> 857906 -> 707603 -> 840907 -> 788606 -> 913264
- Revalidation at 2026-09-24 11:54 confirms all six chain tasks are still `pending`; 920550 is listed as launchable now and none of its downstream tasks has started.
- PersonalHub `main` is currently commit `2d9c5e782d94cb37747b607b7bdb46a5ea61849f`, `version.txt` is 60, and `PersonalHubDatabase` still declares Room `version = 22` / `SCHEMA_VERSION = 22`.
- PersonalHub PR #40 (`task/620949`) merged after the previous audit but only removed the stale consolidated-main Pixel updater service/timer; it did not change app functionality or schema and does not invalidate the P0 chain.
- PersonalHub currently has no open PRs. The only non-main branch remains `chatgpt/105883-since-when`, confirmed `ahead_by=0`, `behind_by=30`; it still contains no unique work requiring recovery.
- The chain is intentionally serial to avoid schema/worktree collisions.
- PersonalHub PR #35 was stale/non-mergeable and has been closed.
- Recent PH PRs #38/#39 had green CI; #39 was large and therefore requires semantic confidence, not CI alone.
- At audit time the only non-main PH branch was chatgpt/105883-since-when, 0 commits ahead and 30 behind main; it contained no unique work to recover and should be deleted after final consolidation if still present.
- Task 822595 (Since When) eventually reached PASS but was extremely expensive (>1000 tool calls across published cycles) and once used a generic install path that touched both Pixel and TCL. Future PH tasks must use serial-scoped device commands and bounded tool usage.
- Task 522084 also had hundreds of model/tool round trips and collided on schema work. Do not reproduce that orchestration pattern.
- User requires the final APK to include ALL relevant work from the initial global request, not merely enough to make the app launch.
- User's real PH DB must be migrated without permanent in-app historical migration code.
- The primary installed PH app is currently unusable, so this PH track has priority over unrelated project work after the emergency runaway-Codex fix in the global track.

## Canonical task chain

### 920550 — residual semantic photo / owned items
Goal: implement only the missing residual from old 624831 above current main; do not redo 613102.
Expected scope includes local photo indexing, text<->photo semantic retrieval, photo<->photo retrieval, “Trova questo oggetto”, optional owned-items layer, and any focal-point metadata still genuinely needed.
It may change the DB schema, so it must run before downstream “final schema” validation.

### 857906 — unified History/Search
Goal: replace user-facing per-module History/Log/Timeline duplication with one canonical cross-module activity/history/search engine reused globally and prefiltered within modules.
Depends on 920550 to serialize schema/worktree changes.

### 707603 — Git History / restore final validation
Goal: validate and close the existing Git Data / Global History / Time Machine implementation on the actual final schema after 920550 + 857906.
Destructive tests only on copies/staging, never the live DB.

### 840907 — Datasette Lite offline
Goal: finish the already-designed offline Data Explorer using vendored Datasette Lite/Pyodide assets and detached validated snapshots; no live DB/WAL exposure and no runtime network dependency.
Runs only after history/schema are final enough to validate correctly.

### 788606 — release preflight
Goal: no new features. Produce/validate the release artifacts with minification/resource shrink, signing, bundletool/Play gates, size reporting and bounded emulator smoke.
Its output defines the exact final main commit/schema/artifact for the Pixel cutover.

### 913264 — final live DB migration + Pixel cutover
Goal: operate only after 788606 PASS.
Read the actual final app schema/Room identity from the final commit. Inspect the actual live DB schema/identity on Pixel. Take immutable rollback first. Externally migrate a copy of the real DB through every required delta to the final schema, validate quick_check/integrity/FK and preservation of representative data, then transfer/install the exact final APK and migrated DB using explicit Pixel serial. Smoke Home + every module. Keep rollback until final acceptance.

## Decisions
- User steer 16:22: execute 857906 in this chat via Remote Desktop Commander and converge **all** PersonalHub non-main branches into `main`, deleting them only after main-containment/semantic-absorption proof. Operational order: resolve PR #41 CI blocker → integrate 920550 → reconcile/integrate `chatgpt/workflowy-integration` → execute/integrate 857906 → inventory remaining non-main branches → delete every absorbed/obsolete branch.
- Branch convergence rule: no valid PH feature remains stranded on a side branch. For each non-main branch, first prove unique work is valid/needed, merge/integrate it into current `main`, verify containment, then delete local/remote branch. Branches with `ahead_by=0` need no dummy merge because their work is already contained and may be deleted directly.
- At 913264, choose the freshest coherent DB candidate available at cutover using actual data freshness/provenance and consistency checks; do not prefer an older backup merely because it is already local.
- Global priority override: PersonalHub P0 is the master recovery lane again. 920550 resumes from its safe pushed checkpoint; non-PH recovery remains parked until PH 913264 PASS unless PH becomes truly blocked.
- Keep the PH P0 chain serial whenever schema/database work can overlap: `920550 -> 857906 -> 707603 -> 840907 -> 788606 -> 913264`.
- Do not migrate the live Pixel DB to intermediate schemas; perform one external migration only after the final schema is frozen.
- Do not add permanent historical Room migrations solely for the user's current live DB.
- Do not touch the primary Pixel during pre-final QA; use emulator/TCL or isolated QA data until the definitive cutover.
- The definitive Pixel APK must be the exact artifact produced after the entire P0 lane, not an emergency/intermediate build.

## Completed
- Superseded dirty residues 624831 and 728918 were removed after verifying their preserved external evidence hashes exactly match the checkpoint and both branches have 0 commits unique versus `origin/main`. Their dirty worktrees were force-removed and local branches deleted. No remote refs existed. PersonalHub local branch set is now only `main`, active `task/920550`, and `chatgpt/workflowy-integration`.
- Detached-worktree cleanup advanced: removed `PersonalHub-autoexport-hotfix`, `PersonalHub-capsule-isolation`, and `/tmp/personalhub-main-play-baseline` after their previously recorded ancestor/patch-equivalence proof. Removed local `codex/pr35-cleanup` worktree+branch after re-proving the integrated functional head is contained in `origin/main`. Remaining local branches are only Workflowy, `main`, superseded dirty evidence branches 624831/728918, and active 920550.
- PR #41 instrumentation CI is now PASS on head `3f32b8c`; Play preflight and architecture are also PASS. Only Android unit CI remains non-terminal.
- Branch cleanup checkpoint: 14 clean historical local branches with 0 commits unique versus `origin/main` were deleted after proof of absorption: `feature/global-activity-register`, `feature/soldi-ui-v2`, `task/462279`, `task/514458`, `task/514458-23`, `task/522084`, `task/613102`, `task/620949`, `task/637985`, `task/693278`, `task/773323`, `task/822595`, `task/825147`, `task/879838`. Clean worktree for `task/514458` was removed first. Remaining local branches are only `chatgpt/workflowy-integration`, `codex/pr35-cleanup`, `main`, `task/624831`, `task/728918`, `task/920550`.
- PR #41 unit failure fixed and verified: schema 23 adds two sync-journal tables, so `SyncJournalTest` expected count changed 87→89 with explicit coverage for `finance_photo_index` and `finance_owned_items`. Full targeted `SyncJournalTest` PASS locally. Test-only fix committed+pushed as `3f32b8cb86552f07bcbf92042db34f4e839969eb`; no Play rebuild is required because product/release code is unchanged from the previously verified artifact.
- PR #41 instrumentation failure was reproduced locally and fixed. Root cause: QA had been temporarily minified, so R8 removed instrumentation-only hook `DatasetteSync.setSchedulerForTests`; production Play minification was not the cause. QA is unminified again while keeping `armeabi-v7a+x86_64`. Local canonical-emulator reruns PASS: `FinanceSemanticPhotoQaDeviceTest` 1/1 and `DatasetteSyncInstrumentedTest#journalMutationTriggersDatasetteWorkAndRecoveryWithoutPolling` 1/1. Fix committed+pushed as `b10117adc84efe3afb4de20c350b411e7b1be055`.
- MegaVault emulator documentation is merged via PR #106, merge `167b928b8478f9567fef57372845d3b937625c56`. It records the sole canonical AVD `Pixel_8a`, API36 Google APIs x86_64 rev7, 1080×2400 @420dpi coordinate bounds, live serial resolution and GNOME launch requirements. Legacy/temporary AVDs were deleted and only `Pixel_8a` remains configured.
- 920550 AVD QA PASS 1/1 on canonical `Pixel_8a` (API36, 1080×2400, 420 dpi). The test exercised isolated synthetic transaction save, two photo indexes, semantic text→image, image→image same-object ranking, non-photo exclusion, owned-item persistence across DB reopen and removal.
- QA uncovered and fixed three concrete release-relevant issues, now committed+pushed as `0834a2434abe9ddd3a1c43caf23ba646c5bc3923`: QA supports TCL `armeabi-v7a` + emulator `x86_64`; temp/staging FinanceCapsule DBs no longer write links into the global canonical Hub Context DB; R8 keeps `ai.onnxruntime.**` so JNI constructors survive minification.
- 920550 rebased cleanly onto current PersonalHub main `57883c2531400efacbefd2c63182bc11833f9537` and force-with-lease pushed as `02f79639dde0797b44a242f931366b0038556193`; no conflicts.
- 920550 minified Play build PASS after rebase: `:app:assemblePlay :app:bundlePlay --no-configuration-cache` completed successfully. Produced signed/minified APK 191,469,880 bytes (182.60 MiB) and AAB 87,776,741 bytes (83.71 MiB). ONNX Runtime compressed payload is 129.04 MiB in the universal APK and 51.59 MiB across all ABI slices in the AAB; model weights remain outside the app artifact.
- Deleted absorbed branch `chatgpt/105883-since-when` after proving it was 0 commits ahead / 32 behind current main; no merge was needed because it contained no unique work.
- 920550 full `:app:assembleDebug` PASS on the task worktree. Baseline `PersonalHub/main` debug APK = 144,942,990 bytes (138.23 MiB); 920550 debug APK = 280,674,045 bytes (267.67 MiB); universal-debug delta = 135,731,055 bytes / 129.44 MiB (+93.64%). Zip inspection shows 129.04 MiB of that is ONNX Runtime native libraries duplicated across arm64-v8a, armeabi-v7a, x86 and x86_64; the arm64-v8a runtime payload actually needed by the primary Pixel is ~31.57 MiB. Model weights remain outside the APK.
- Host-side real-model synthetic retrieval check PASS for the acceptance intent: same synthetic jacket under changed background/rotation scored 0.8904 vs 0.7926 for a shoe distractor, so the same object enters and ranks above the distractor shortlist; `black jacket` text-image scores ranked both jacket variants above the shoe.
- Consumer-preflight scans for the new Soldi photo-index/owned-item APIs completed without unexpected consumers; `:feature:soldi:compileDebugKotlin` PASS and `checkArchitectureBoundaries` returned `ARCHITECTURE_BOUNDARIES=PASS`.
- Implemented tag/history write-amplification hotfix at PersonalHub commit `41920af`: `refreshUsage()` updates only stale derived values; replace/assign/remove skip unchanged relationships; tag projections/rename/archive/pin skip semantic no-ops; Timer avoids repeated archive writes; Git UPDATE triggers ignore exact row no-ops for both pending revisions and semantic history.
- Added regression coverage proving exact no-op UPDATEs create neither `hub_git_events` nor `hub_git_pending`, repeated Timer projection produces zero Git writes, and a redundant `refreshUsage()` causes zero SQLite row changes. Combined targeted tests PASS; focused low-level regression PASS; `:app:compileDebugKotlin` PASS.
- Verified the Kotlin CLIP tokenizer against the official TinyCLIP `tokenizer.json` using six reference phrases (`red jacket`, `black winter jacket`, `giubbotto nero`, `NORTH FACE SUMMIT`, `Copenhagen café`, `shoe 42`); token ID sequences matched exactly. The verification used temporary test resources and left the worktree clean.
- 920550 implementation checkpoint exists on `task/920550`: foundation commit `8c34afcc94031deef7b59aae4f8ba762449c5326`, refinement commit `36fff1d` pushed to origin. Worktree is clean after the push.
- Verified 920550 targeted unit tests from one execution: 12 tests / 0 failures / 0 errors across `FinanceCapsuleTest`, `ClipBpeTokenizerTest`, `FinanceSemanticAssetStoreTest`, `FinanceSemanticMathTest`, and `SoldiSearchTest`.
- 920550 implementation checkpoint committed+pushed on `task/920550`: `8c34afc` (`Checkpoint 920550 semantic photo foundation`). Current task schema is 23 with exported Room schema 23 JSON; no historical Room migration chain was added.
- 920550 foundation now includes local TinyCLIP/ONNX semantic photo indexing, OCR text capture, text-to-photo and photo-to-photo ranking, `Trova questo oggetto` camera/gallery flow, optional owned-items persistence/UI, model/checksum pinning with weights outside the APK, and targeted unit/DB tests. Full app `:app:compileDebugKotlin` PASS after three bounded compiler fixes.
- TinyCLIP candidate was locally quality-checked before integration: synthetic red-object vs blue-circle text ranking behaved correctly in English and simple Italian; transformed same-object image similarity was 0.959 vs distractor 0.784.
- PROMPT_ID 920550 successfully claimed at 2026-09-24 12:18 local; roadmap status `running`, issue #1030, branch `task/920550`, worktree `/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/920550`.
- Fixed the local roadmap/Obsidian collision that blocked claims: `Generated/PersonalHub/**` is sqlite-to-obsidian output inside the active codex-roadmap vault, now ignored by Git via codex-roadmap commit `d0d6b1384a6fcc7ead2e4d15eb0207158b9808fa`; 3,138 generated notes were preserved. Local roadmap pull then fast-forwarded cleanly.
- Revalidated the PH P0 chain against current canonical roadmap and current `PersonalHub/main`; no newer work invalidates or reorders it.
- Confirmed exact current PH baseline: main `2d9c5e782d94cb37747b607b7bdb46a5ea61849f`, app v60, Room schema 22, no open PRs, stale non-main branch 0 ahead/30 behind.
- Global Phase-1 PH audit.
- Verified current main schema 22 and 21->22 delta.
- Identified 624831 residual vs work already completed by 613102.
- Created/registered 920550 for the residual photo/owned-items scope.
- Created/registered 913264 for the final DB/APK/Pixel cutover.
- Reordered/dependency-linked PH P0 so schema-changing work is serialized.
- Closed stale PersonalHub PR #35.
- Superseded obsolete 383662.
- Established rule that final APK comes only after all relevant PH work/tests/optimizations.
- Established rule that live DB migration is external/one-shot and targets the final schema, not an intermediate version.
- Established serial-specific ADB rule and primary-PH protection during pre-final testing.

## Remaining
- Run/review 920550 and inspect its actual diff, schema changes, tests and integration result before allowing 857906.
- Run/review 857906; ensure old duplicate user-facing History/Log/Timeline surfaces are actually removed/replaced where intended and global/module search reuse is real.
- Run/review 707603 on the resulting final-ish schema.
- Run/review 840907, including true offline behavior and artifact-size impact.
- Run/review 788606 and freeze exact release commit, schema version/identity, APK/AAB hashes/paths and shrink state.
- Before final migration, inspect the live Pixel DB schema/identity and take immutable backup.
- Execute external live DB migration to the exact frozen final schema; preserve rollback and validate data/integrity/FK.
- Install exact final APK on primary Pixel with explicit serial and verify Home + all modules with real data.
- Integrate `task/920550` and `chatgpt/workflowy-integration` into `main` at their proper serial points; after final containment proof delete them plus `chatgpt/105883-since-when` (already 0-ahead) and any later temporary PH branches.
- Verify no open PH PR/issue/action remains relevant/unprocessed.
- Ensure PersonalHub repository ends clean and main-only.

## Blockers
- Local Android build/device/real-DB work requires Codex/local Fedora access.
- The actual live Pixel DB schema/identity is not yet read and must not be guessed.
- Final DB target cannot be frozen until upstream PH tasks are complete.
- Do not proceed to final Pixel cutover while any relevant PH PBF/integration is unresolved.

## Evidence
- Superseded dirty-worktree rollback evidence has been preserved outside Git at `~/Documents/ChatGPT/Personal Hub/evidence/recovery-20260924-superseded-worktrees/`: tracked binary patches, untracked-source tarballs and status snapshots for 624831 and 728918. Key SHA-256: 624831 patch `14c03f819adcc62af000243cc5f42ccd7b7c149bb5ec412508210bacc2840b00`, untracked archive `8005432ae18d89f42a9a9b5b489327f3c776a611dd3bd0799273d2b071f7b387`; 728918 patch `658514dfa31381b68dc94d9d018ad840569a12cc2013b7e6acbe4f3cdc858f11`, untracked archive `f7b1de3f90e25715f755f25b6b2762619aa0732526d051cf7166a7936f699436`.
- PersonalHub `origin/main` contains hotfix `41920af` (`Fix tag history no-op write amplification`) and compactor `57883c2` (`Add safe Git no-op history compactor`). Targeted Gradle regression tests and `:app:compileDebugKotlin` PASS; `python3 tools/test_cleanup_hub_git_noop_events.py` PASS on exact `origin/main`.
- gernalix/PersonalHub main and Room schema JSON 21/22.
- codex-roadmap canonical prompt materializations for 920550, 857906, 707603, 840907, 788606, 913264.
- 613102 PASS evidence and PersonalHub merged implementation.
- Phase-1 branch/PR audit and closed PH #35.
- Global checkpoint operations/task-state/CHATGPT-20260924-GLOBAL-RECOVERY.md.

## Acceptance criteria
- Every still-relevant PH task from the global audit is completed or proven obsolete/covered; no unmanaged PH PBF remains.
- PH main includes the final intended functionality from 920550, 857906, existing 613102/822595 work and all other already-merged valid PH work.
- Git History/restore and Datasette Lite offline gates PASS on the resulting final schema.
- Release preflight PASS with minification and resource shrinking active; exact APK/AAB artifacts and sizes are known.
- Final schema version and Room identity are explicitly recorded from the frozen release commit.
- Live Pixel DB is backed up before modification and can be restored.
- External migration preserves user data, passes SQLite quick_check/integrity and FK checks, and produces the exact schema expected by the final app.
- The exact final APK is installed on the primary Pixel using an explicit serial.
- Home and every module open without crash against the migrated real DB.
- Primary data remains present and representative user records survive migration.
- Obsolete PH branches/PR residue is removed only after work absorption is proved.
- PersonalHub ends with clean main and no relevant pending integration.

## Next action
Reconcile `chatgpt/workflowy-integration` onto current `origin/main=66dbe026...`, rerun WorkflowyIntegrationTest + WorkflowyDaysTest + app compile + architecture gate, publish/integrate through the single-writer path, verify main containment, then delete Workflowy and local 920550 branches and immediately claim 857906.
