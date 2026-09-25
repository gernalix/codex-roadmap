# Operational task state — PersonalHub P0

TASK_ID: CHATGPT-20260924-PERSONALHUB-P0
Updated: 2026-09-25 22:35 Europe/Copenhagen
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
- [x] Resume 857906 from post-Workflowy main and complete the shared host engine: bounded Activity DAO search, live time/module/text/entity filters, humanized/grouped cards, conservative undo, one Home 🔍 entry and Search/Event deep-link routing. Checkpoint `9d835d8`.
- [x] Pass consumer-preflight, targeted presentation/deep-link/Activity DAO+undo tests, app compile and `checkArchitectureBoundaries` for the shared-engine block.
- [x] Re-synchronize the P0 operational lane after chat handoff; verify clean `task/857906` HEAD and remote both equal `9d835d8198f7b088f6577cc404306e2a50d5a2aa`, with roadmap guarded pull PASS at `12ef9f8`.
- [x] Replace People legacy contact/global History runtime with the shared scoped History/Search route; remove `ContactHistoryCapsule`/owner/state while preserving and correctly re-wiring the separate initiative/calendar feature.
- [x] Replace Places legacy `ui/history/HistoryScreen` with a domain-only Visits surface; remove its duplicate change-history undo/redo UI and expose shared Places History/Search separately via `moduleHistoryUri("places")`.
- [x] Replace Timer and WordPulse legacy change-history/timeline surfaces; confirm Substances/Soldi retain domain chronology and expose the shared scoped History/Search route.
- [x] Remove the user-facing Git History/Time Machine settings page and technical Git-history injection from temporal episode search; keep the Git backend for sync/recovery.
- [x] Add the History/Search architecture guard and pass final consumer gates, touched-module compiles, app compile and `checkArchitectureBoundaries`.
- [x] Run canonical `Pixel_8a` emulator QA for global History/Search + at least two fixed-module entry points, including live filters, hidden before/after text search and one safe compensating undo: `HubHistorySearchQaDeviceTest` PASS 3/3 on `emulator-5554`.
- [x] Record canonical roadmap 857906 terminal PASS/completed and merge PR #44; 857906 is closed and must not be reopened.

### Phase 4 — 707603 Git History / restore
- [x] Run 707603 on the resulting schema; functional acceptance PASS and canonical terminal state completed.
- [x] Validate Git Data / Global History / restore only on safe copies/staging; unit/architecture/device gates PASS.

### Phase 5 — 840907 Datasette Lite offline
- [x] Run 840907 after 707603; implementation and acceptance gates PASS on task branch.
- [x] Verify true offline runtime, detached validated snapshots and acceptable artifact-size impact; host/browser/AVD offline gates PASS.

### Phase 6 — 788606 final release preflight
- [ ] Before release, disposition the three unique commits on `origin/c2/107210` (external DB migrator and startup gate changes) through the protected integration flow; retain only changes still needed.
- [ ] Continue already-running 788606 with no new features; do not re-claim or duplicate its gates.
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
PROMPT_ID 788606 remains canonical `running`, but its release artifact acceptance is complete on frozen FINAL_HEAD `3916e5d81200007bda7c939aaf3ed2b4948a8043`. Immutable version-61 APK/AAB are persisted under `/home/daniele/Documents/ChatGPT/Personal Hub/releases/61-3916e5d8`; no rebuild is permitted. PersonalHub PR #47 is open/mergeable and waiting only for remaining CI before single-writer merge/terminalization. 913264 stays pending until 788606 becomes canonical `completed`.

## Verified facts
- 857906 canonical emulator acceptance PASS on `task/857906@1f6e65f99d8f319213c7469c95ab6e29758022b6`: `ANDROID_SERIAL=emulator-5554 ... :app:connectedQaAndroidTest ... HubHistorySearchQaDeviceTest` completed `BUILD SUCCESSFUL`, 3 tests / 0 failures. It verifies global live filters, before/after-only human text search, safe compensating undo, immutable module scope, and shared Places+Timer entry points with legacy Timeline absent. QA-discovered product fixes are committed in ancestry (`f606a50`, `99165ee`, `f380fc0`); test-order stabilization is `1f6e65f`.
- Final 857906 branch head is `a4b9e82a8f95d2d24660cf09b393b5b4665d215b`, pushed exactly to `origin/task/857906`. The only post-emulator change suppresses UUID values and `_ms` technical fields from human history presentation/search; targeted `HubActivityPresentationTest`, app compile, architecture gate and `git diff --check` PASS.
- Interim daily-use artifacts were produced without changing the final P0 cutover contract. QA-PASS debug APK SHA-256 `37a3ff6a6d0bbcbff3fe25905cd784d9d8d2ee01711b6deaaf6a17ab6d04d180` was published via the stable development prerelease/Telegram. Corrected schema-23 DB SHA-256 `9d6c73c8319a7f605d4f10d8863b5ff344e3db7444317635d710fd9bec5bc2bc` passed host integrity/FK checks, direct Android `DatabaseVault.validate`, and a PersonalHub cold start on the emulator; corrected ZIP SHA-256 `4dba373995b13fc582dbcac14b6808b04cbfd9dc72c191a538e4f94ff615d87a` was sent on Telegram. The earlier DB delivery is superseded and must not be used. Physical Pixel installation was not performed because the canonical helper reported `pixel_physical_required_but_absent`.
- 857906 source convergence is pushed through PersonalHub `task/857906@1f94c49e6e7c88dbf337214b5d389a5321832831` (preceded by `0243e2ba5372876a73ef55ec17a1c60686723e3a`). Timer no longer exposes the Timeline screen/dialogs; WordPulse no longer exposes its Timeline tab; Substances preserves editable intake chronology and Soldi preserves transaction/domain chronology while both expose shared module History/Search. Settings Git History/Time Machine UI is removed; `HubTemporalSearchScreen` no longer mixes Git technical events into episode search.
- Final source gates before emulator QA PASS on the converged branch: consumer-forbid for removed legacy symbols PASS; `:feature:multitimetracker`, `:feature:wordpulse`, `:feature:sostanze`, `:feature:soldi`, `:feature:supercontacts` compile gates PASS; `:app:compileDebugKotlin` PASS; `checkArchitectureBoundaries` PASS; `git diff --check` PASS. The architecture guard now rejects the exact removed legacy History/Timeline surfaces and requires all six feature modules to route History/Search through `HubDeepLinkContract.moduleHistoryUri(...)`.
- 857906 People/Places checkpoint is pushed at PersonalHub `a1541d99e491228f76f61d792d1fcb396c8cfebd` and matches `origin/task/857906`. People consumer gate forbids `ContactHistoryCapsule`, `ContactHistoryOwner` and `ContactHistoryState`; `:feature:supercontacts:compileDebugKotlin` PASS. Places old package `com.gernalix.luoghi.ui.history` is absent by consumer gate; `:feature:luoghi:compileDebugKotlin` PASS after converting the surface to domain-only Visits and adding shared module History/Search.
- 2026-09-25 takeover checkpoint: guarded roadmap synchronization PASS to `12ef9f89eba6e32f006e280d2f4e715115ca7ff0`; the pre-sync dirty state files were proven byte-identical to `origin/main` before realignment. PersonalHub `task/857906` is clean at local+remote `9d835d8198f7b088f6577cc404306e2a50d5a2aa`; no WIP was lost.
- 857906 shared-engine checkpoint is safely committed+pushed as `9d835d8198f7b088f6577cc404306e2a50d5a2aa` on `task/857906` (remote hash verified exact). Home now has one 🔍 History/Search destination; Search/Event deep links route to the same `HubHistorySearchScreen`; module scoping is represented by the public `moduleHistoryUri` contract and hidden immutable scope state. No Room schema change; schema remains 23.
- Shared-engine verification PASS: consumer-forbid reports zero `HubActivityRegisterScreen` consumers; `:app:compileDebugKotlin` PASS; `checkArchitectureBoundaries` PASS; targeted `HubActivityPresentationTest`, `HubDeepLinkContractTest`, and `HubActivityRegisterTest` PASS. DAO coverage verifies time/module/entity/system/limit filters and newest-first ordering; presentation coverage verifies exact `EEE d/M/yy` date display, diacritic-insensitive search, hidden before/after search terms, technical-ID suppression, grouping and conservative grouped undo.
- 857906 handoff WIP checkpoint is safely committed+pushed as `ed21615445462c51762a633044db4eeaf02d21d4` on `task/857906`. It contains only the first partial block: Search deep-link query/entity parameters, a shared bounded Activity DAO search query, and the beginning of the unified History/Search host signature/imports/constants. This is intentionally incomplete and must be continued, not treated as PASS.
- 857906 design conclusion before coding: existing `hub_activity_log` schema 23 already carries occurred_at/module/action/entity label/detail/origin/system/source/before+after payload/group/reversible/status fields, and the generic undo engine already fails closed on stale/referenced/unsupported mutations. No schema 24 appears necessary for the unified History/Search work.
- 857906 scope distinction is pinned: remove/replace duplicate **change-history browsers** (global activity/Git-history split, People contact/global history, Places History screen, Timer Timeline browser, WordPulse Timeline tab) while preserving distinct domain data functionality (People initiative/calendar features, Substances intake list/history editing, prescription history, Timer session domain operations, WordPulse sessions/explore data, Soldi transactions).
- All six feature modules already depend on `:contracts:database`, so a canonical History/Search deep link can be shared without feature→app dependency violations. 857906 worktree remains clean at pre-Workflowy main `66dbe026...` and has no code edits yet.
- Workflowy CI lint blocker is fixed and pushed at `f8e454141fa9835041f83ea1255e257fa44a5f2d`; local hub-context lint + both targeted Workflowy tests PASS. PR #43 should rerun on this head.
- 857906 canonical claim succeeded: roadmap status `running`, issue #1064, branch `task/857906`, worktree `~/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/857906`. Claim occurred while Workflowy #43 was still in CI; no 857906 code is to be modified until the worktree is synced to post-Workflowy main.
- Workflowy source/task branch trees are byte-identical before final integration: `origin/chatgpt/workflowy-integration^{tree}` = `origin/task/workflowy-integration^{tree}` = `03fea6d0f2967cc1ae510957b17ccf313b3b8e68`. Remote PH branches are now only `main` plus those two Workflowy refs. Once PR #43 is contained in main, both side refs are safe to delete.
- Workflowy protected integration is now PR #43 from `task/workflowy-integration`; previous PR #42 was closed because the integrator correctly rejected the non-task branch naming. The new task branch is tree-identical to the already-tested reconciled Workflowy content.
- Workflowy reconciliation after 920550 is PASS on local branch head `3348a34`: zero conflicts, consumer-preflight PASS, targeted Workflowy tests PASS, app compile PASS, architecture PASS.
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
- 2026-09-25 22:35 Europe/Copenhagen: 788606 release freeze complete. FINAL_HEAD `3916e5d81200007bda7c939aaf3ed2b4948a8043`, version 61, Room schema 23 identity `4b9b96396c8f9e750d13b0e6da70fdd9`; one final Play build PASS with R8/resource shrink/lintVital/signing. Immutable APK SHA-256 `3677591701b24bf8cc645fa7579c42f0665a48ebb4b522a38fbddcbbe27607b5` (202,937,814 B), AAB SHA-256 `ac2d3665c51fb1b1e27020543054642c88a23932e3a9c9b463920538dacf7831` (99,158,685 B). APK/AAB signing + bundletool validation PASS; exact APK smoke PASS on `emulator-5554`, cold start 501 ms, UI `PersonalHub`. Release manifest SHA-256 `ae04d915c579f4d1b20300e867a8451525a1d94e209b302ecab557d9c0fe46e4`.
- 2026-09-25 22:22 Europe/Copenhagen: 840907 final acceptance reaffirmed on merged product: host gate PASS (47 vendored files verified; 10 envelope rows; 120 presentation tables; cross-module FK graph), and direct Pixel_8a AVD gate with `AIRPLANE=1` + external network probe offline returned `OK (1 test)` in 19.022s. Vendored runtime contributes ~11.68 MiB compressed to QA APK. No 840907 rerun is needed.
- 2026-09-25 22:22 Europe/Copenhagen: `origin/c2/107210` disposition completed before release: patch IDs match exactly `1990edbe→854a3732`, `d199f87b→d10c2df9`, `0851f6ec→b273a202`; 788606 worktree is based on merged 840907 main and already carries all three changes.
- 2026-09-25 22:21 Europe/Copenhagen: 840907 terminal PASS verified. PR #46 merged to PersonalHub main `ba61688ef1cc59b29d3400e0c0a16845a0b271f3`; canonical roadmap main reports 840907=`completed` and 788606=`running`. Final direct AVD gate installed the exact QA app/test APKs, then verified `AIRPLANE=1`, `NETWORK_PROBE=offline`, `OK (1 test)`, `INSTRUMENTATION_CODE: -1`, exit 0 for `DataExplorerOfflineQaDeviceTest`. No 840907 gate needs repeating.
- 2026-09-25 22:20 Europe/Copenhagen: 840907 fully closed: PR #46 merged into PersonalHub main as `ba61688ef1cc59b29d3400e0c0a16845a0b271f3`; final task head `f8f15feec27f29d5c63ba4764bdd922f23d41b39`; canonical roadmap main reports 840907=`completed`. Offline runtime/product gates already PASS and must not be repeated.
- 2026-09-25 22:03 Europe/Copenhagen: 840907 acceptance complete at `07148cd`: host projection/manifest/no-network gate PASS; browser E2E PASS with external DNS forced unavailable; `:app:compileDebugKotlin` PASS; `DataExplorerOfflineQaDeviceTest` PASS 1/1 on canonical Pixel_8a AVD with airplane mode enabled; vendored assets 24.55 MiB raw / 12,251,271 compressed bytes in QA APK; emulator network restored after test.
- 2026-09-25 21:43 Europe/Copenhagen: 840907 claimed successfully via roadmap Issue #1143; canonical status=`running`, executor policy=`chatgpt`, isolated worktree `/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/840907` based on PersonalHub main `5cda3ad6`.
- 2026-09-25 21:15 Europe/Copenhagen: 707603 fully closed: PR #45 merged into PersonalHub main as `5cda3ad6aff7b5e3fde2afd52ee9f3c2c54d7223`; roadmap terminal Issue #1140 applied `completed`; canonical roadmap main `50c09ef582f1b61727e99a1a80d764a1e5fc2bfe` confirms 707603=`completed`.
- 2026-09-25 21:15 Europe/Copenhagen: 707603 terminal PASS completed. PR #45 merged as `5cda3ad6aff7b5e3fde2afd52ee9f3c2c54d7223`; roadmap Issue #1141 closed `completed`; canonical `roadmap.sqlite` at `50c09ef582f1b61727e99a1a80d764a1e5fc2bfe` reports 707603=`completed`.
- 2026-09-25 20:53 Europe/Copenhagen: targeted `:core:database:connectedDebugAndroidTest` for `GitDataRestoreDeviceTest` PASS on explicit `emulator-5554` / Pixel_8a AVD: 1 test, 0 failures, 0 errors; test scaffolding committed as `d3fca297` and pushed to PR #45. github-autosync rollup fix PR #27 merged as `0a194cf`.
- 2026-09-25 20:49 Europe/Copenhagen: diagnosed 707603 integration blocker: single-writer treated superseded CANCELLED duplicate check runs as current failures. Fix `cf616aa` deduplicates by workflow/check and keeps latest pending/failing runs fail-closed; `tests.test_repo_single_writer` 21/21 PASS; github-autosync PR #27 opened.
- 2026-09-25 20:44 Europe/Copenhagen: 707603 final PR #45 CI gate is fully PASS: instrumentation, unit, both play-preflight jobs, capsule-boundaries and GitGuardian all PASS; no test rerun was performed.
- 2026-09-25 20:21 Europe/Copenhagen: 707603 acceptance evidence re-used from canonical checkpoint 19: GitDataFinalValidationTest + GitHubDataTransportTest PASS, architecture boundary PASS, HubHistorySearchQaDeviceTest PASS on Pixel_8a AVD; no rerun performed.
- 2026-09-25 20:15 Europe/Copenhagen: C2 / 175908 verified canonical `completed` from roadmap SQLite; the PH priority hold is released. No PH implementation/test work was repeated during this checkpoint.
- Mandatory checkpoint refresh 2026-09-25 20:12 Europe/Copenhagen: synchronized to current codex-roadmap main; no verified PH work was rerun. C2/175908 is still active in finalization, so PH remains parked; 857906 stays terminal PASS and 707603 remains the already-running next PH task.
- Mandatory checkpoint refresh 2026-09-25 16:12: canonical roadmap readback confirms 857906=`completed`, 707603=`running`, 840907/788606/913264=`pending`; no completed PH work was re-audited or rerun. Old PH supervisor worker was explicitly paused while C2 owns the priority lane.
- 857906 Git integration completed: PR #44 merged as PersonalHub `main@ba7089770b552f2c4a73c121ba1356862cec38e4`; task head `a4b9e82a8f95d2d24660cf09b393b5b4665d215b` is contained and tree-equivalent; remote/local `task/857906` plus 857906 QA/diagnostic worktrees were removed; final PersonalHub branch/worktree inventory is main-only.
- 857906 emulator acceptance completed: 3/3 `HubHistorySearchQaDeviceTest` cases PASS on canonical `Pixel_8a` only, after fixing Timer main-thread Choreographer startup and explicit package scoping for shared History/Search deep links. Final branch head additionally hardens technical-value suppression with targeted unit/compile/architecture PASS.
- 857906 source-side legacy convergence completed and pushed through `1f94c49`: shared host engine remains the only user-facing change History/Search UI; People/Places/Timer/WordPulse duplicate browsers are removed; Substances/Soldi domain chronology is preserved with shared History/Search entry points; Git History/Time Machine user UI and temporal-search Git injection are removed; source/compile/architecture gates PASS.
- 857906 People + Places legacy-surface sub-goal completed and pushed at `a1541d9`: People parallel history owner/state removed and history buttons route to the host shared engine (entity-scoped for contact detail); initiative/calendar stays domain-owned. Places legacy HistoryScreen/package became Visits, user-facing undo/redo change-history controls were removed, and a separate Places shared History/Search entry was added. Both feature compile gates PASS.
- New chat ownership checkpoint completed for PersonalHub P0 / 857906: roadmap re-synchronized through the guarded pull, current PH task hash/remote/worktree cleanliness verified, and execution resumes from the existing tested `9d835d8` shared-engine checkpoint rather than repeating discovery.
- 857906 block 1 completed and checkpointed at PersonalHub `9d835d8`: shared bounded Activity-backed History/Search host, semantic humanization/grouping, live filters, Home/deep-link unification, conservative undo refresh, public fixed-module deep-link contract, targeted tests, compile, consumer gate and architecture gate all PASS.
- Workflowy is fully merged and side branches deleted: PR #43 merged as `b1a7f22ef6f56be60cff47e7d8fec2805b088af1`; all required CI PASS after lint fix `f8e4541`. Both `chatgpt/workflowy-integration` and `task/workflowy-integration` were deleted locally/remotely after containment/tree-equivalence proof.
- PersonalHub branch set is now exactly `main` + active `task/857906`. The 857906 worktree was proven clean and fast-forwarded from pre-Workflowy `66dbe026...` to post-Workflowy `b1a7f22...` before any 857906 code edit.
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
- Let PR #47 finish CI, then single-writer merge + canonical 788606 PASS; do not rebuild or mutate the frozen APK/AAB.
- Before final migration, inspect the live Pixel DB schema/identity and take immutable backup.
- Execute external live DB migration to the exact frozen final schema; preserve rollback and validate data/integrity/FK.
- Install exact final APK on primary Pixel with explicit serial and verify Home + all modules with real data.
- Verify no open PH PR/issue/action remains relevant/unprocessed.
- Ensure PersonalHub repository ends clean and main-only.

## Blockers
- Non-human gate only: PR #47 CI is still running. One Play-preflight is PASS; unit, instrumentation and the current Play-preflight remain in progress. Frozen release artifacts must not be rebuilt while CI completes.
- Release serialization gate: 788606 owns final minified APK/AAB build, shrink/signing/Play validation and release freeze. Do not start live DB migration/install on Pixel until 788606 is canonical PASS.
- Primary Pixel 8a is currently reachable at explicit ADB serial `192.168.1.37:36755`; it remains protected from final APK/DB cutover until 913264.
- Physical Pixel 8a is currently online at explicit serial `192.168.1.37:36755`; do not modify its live DB until 913264 backup/migration gates begin.
- Release dependency, not a product blocker: before 788606 freezes main, disposition the three commits unique to `origin/c2/107210` through the protected integration flow.
- 857906 has no blocker and is already canonical `completed`; no CI polling or retry remains.
- Local Android build/device/real-DB work is available through Remote Desktop Commander on Fedora.
- The actual live Pixel DB schema/identity is not yet read and must not be guessed.
- Do not proceed to final Pixel cutover while any relevant PH PBF/integration is unresolved.

- Physical Pixel 8a was last verified online; re-resolve its explicit serial at final cutover rather than assuming continued availability.
## Evidence
- 2026-09-25 22:35 Europe/Copenhagen immutable 788606 release evidence: persistent dir `/home/daniele/Documents/ChatGPT/Personal Hub/releases/61-3916e5d8`; `release-manifest.json` SHA-256 `ae04d915c579f4d1b20300e867a8451525a1d94e209b302ecab557d9c0fe46e4`; R8 mapping SHA-256 `c3924eb620ecbfdd69a282af9c6a4dd945ed60728eabc4d268d5559f7ca10ed6`; APK signer cert SHA-256 `c8ff58d7cd66babb7d3ad4f4b95e6e558eb2229a0953df073d263795d3e35e73`; `c2/107210` three unique patches are exactly absorbed by 854a3732/d10c2df9/b273a202 via stable patch-id equality. PR #47 head is exact FINAL_HEAD and mergeable.
- 2026-09-25 22:22 Europe/Copenhagen current lane readback: roadmap reports 840907=`completed`, 788606=`running`, 913264=`pending`; PersonalHub main=`ba61688ef1cc59b29d3400e0c0a16845a0b271f3`. 788606 worktree HEAD `b273a20224a9dd37e9e4a372d8761b0265691e78` is three commits ahead of that main and those three commits are patch-equivalent to the full unique `origin/c2/107210` series. A targeted core DB/app compile/architecture gate is already running there; no duplicate worker should be started.
- 2026-09-25 22:22 Europe/Copenhagen 788606 ownership readback: canonical roadmap reports 840907=`completed`, 788606=`running`, 913264=`pending`; single-writer task 788606 is active in `/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/788606` at `b273a20224a9dd37e9e4a372d8761b0265691e78`; current Gradle gate is running there. ADB shows TCL `192.168.1.200:46451`, physical Pixel 8a `192.168.1.37:36755`, and emulator `emulator-5554` online. No 788606 work was re-claimed or duplicated.
- 2026-09-25 22:21 Europe/Copenhagen 840907 terminal readback: PersonalHub PR #46=`MERGED`, merge `ba61688ef1cc59b29d3400e0c0a16845a0b271f3`, final task head `f8f15feec27f29d5c63ba4764bdd922f23d41b39`; single-writer status=`merged`; canonical codex-roadmap main reports 840907=`completed`, 788606=`running`, 913264=`pending`. Direct offline instrumentation evidence: app install PASS, test APK install PASS, airplane mode 1, IP probe offline, `OK (1 test)`, `INSTRUMENTATION_CODE: -1`, exit 0.
- 2026-09-25 22:20 Europe/Copenhagen 840907 terminal evidence: PersonalHub PR #46 MERGED; task head `f8f15feec27f29d5c63ba4764bdd922f23d41b39`; merge commit `ba61688ef1cc59b29d3400e0c0a16845a0b271f3`; roadmap main `29a4b596f8d571e3aac0444bef0eabc2d34bb831` reports 840907=`completed`, 788606/913264=`pending`. Final device gate uses host-controlled offline mode and only verifies no validated Internet from instrumentation; product runtime unchanged from already-PASS host/browser/AVD evidence.
- 2026-09-25 22:03 Europe/Copenhagen 840907 evidence: branch head `07148cd14282a9f61a8928054197f223b5fd4588`; host gate `test_datasette_lite_offline.py` PASS with 10 envelope rows, 120 presentation tables and cross-module relation targets; browser E2E rendered `contact_fields`/`Ada Example` with external host resolution blocked; AVD XML reports tests=1 failures=0 errors=0 skipped=0 for `DataExplorerOfflineQaDeviceTest` (16.444s) under airplane mode; assets raw=25,743,829 bytes, QA APK compressed contribution=12,251,271 bytes across 52 entries; canonical roadmap main `adc8217d36a8779dd4a3490421dc7bdcf02c4da7` still has 840907=`running` and 788606/913264=`pending`.
- 2026-09-25 21:51 Europe/Copenhagen: guarded roadmap pull PASS at `654788b`; physical Pixel 8a is online at explicit ADB serial `192.168.1.37:36755` with currently installed PH v60. `c2-personalhub-p0.timer` is disabled/inactive. The obsolete `personalhub-consolidation.timer` was disabled after verifying its service failed every minute because its ExecStart script is absent. `origin/c2/107210` has three commits absent from main (`1990edbe`, `d199f87b`, `0851f6ec`), requiring semantic disposition before final freeze. User reconfirmed that both final minified APK and compatible migrated DB must be installed on Pixel before completion.
- 2026-09-25 21:43 Europe/Copenhagen 840907 ownership evidence: roadmap prompt 840907=`running` (GPT-6 Sol/medium, executor_policy=chatgpt); worktree HEAD remains `5cda3ad6...` while files under `app/src/main/assets/datasette-lite/` are receiving live writes from the active worker. Concurrent editing was stopped deliberately.
- 2026-09-25 21:15 Europe/Copenhagen 707603 terminal evidence: all PR #45 checks PASS on head `d3fca2972eb327dfaca79f2c3ff0130b2af72b49`; merge commit `5cda3ad6aff7b5e3fde2afd52ee9f3c2c54d7223`; roadmap Issue #1140 closed `completed`; `roadmap.sqlite` reports 707603=`completed`, 840907/788606/913264=`pending`.
- 2026-09-25 21:15 Europe/Copenhagen 707603 closure evidence: PR #45 merged; final complete-head CI PASS (instrumentation 18m1s, unit/lint 20m41s, both Play preflight, architecture, GitGuardian); targeted `GitDataRestoreDeviceTest` on explicit Pixel_8a AVD PASS 1/1; terminal request #1141 applied; 707603 canonical `completed`.
- 2026-09-25 20:53 Europe/Copenhagen leaf-gate evidence: `TEST-Pixel_8a(AVD) - 16.xml` reports `GitDataRestoreDeviceTest` tests=1 failures=0 errors=0 skipped=0, testcase `restoreUsesValidatedStagingBeforeReplacingLiveDatabase` 12.991s. PersonalHub branch local/remote exact head `d3fca2972eb327dfaca79f2c3ff0130b2af72b49`, worktree clean. PR #45 CI restarted on this head.
- 2026-09-25 20:49 Europe/Copenhagen single-writer regression evidence: `repo_single_writer.integrate_pr(gernalix/PersonalHub,45)` returned `checks-failed` despite all current checks PASS because old CANCELLED duplicates remain in `statusCheckRollup`. Fix branch `task/707603-rollup-fix@cf616aa412663ee6fd05282df0be01d55ecf4f24`; 21/21 unit tests PASS; PR #27 is open and mergeable with CI running.
- 2026-09-25 20:44 Europe/Copenhagen PR #45 readback: head `6c8b91e1b24ca1a83bad469cc38298abaefcde1e`; instrumentation PASS 16m37s, unit PASS 12m38s, play-preflight PASS 11m3s and 10m37s, capsule-boundaries PASS, GitGuardian PASS. Canonical roadmap at `8047c690a8f28b54c8696b12986f93b6d0e17b04` still reports 707603=`running`, 840907/788606/913264=`pending`.
- 2026-09-25 20:21 Europe/Copenhagen 707603 integration readback: canonical checkpoint 19 has `remaining=[]`; PR #45 head `6c8b91e1b24ca1a83bad469cc38298abaefcde1e` changes only `GitDataRestoreDeviceTest.kt` and `GitDataFinalValidationTest.kt`; architecture/GitGuardian PASS while Android unit/instrumentation/play-preflight remain pending.
- 2026-09-25 20:15 Europe/Copenhagen C2 terminality readback: canonical `roadmap.sqlite` on current main reports 175908=`completed`, 707603=`running`, 851204=`pending`. PH priority is therefore released to the already-running 707603 task; no duplicate claim is permitted.
- 2026-09-25 20:12 Europe/Copenhagen mandatory checkpoint readback: codex-roadmap main synchronized before edit; C2 remote task/175908 observed non-terminal and in final live-gate/terminalization work. PH execution therefore remains intentionally held. Existing PH acceptance evidence below remains authoritative and was not repeated.
- 2026-09-25 17:13 Europe/Copenhagen mandatory checkpoint refresh: synchronized against the then-current canonical `origin/main`; PH checklist, Completed, Remaining, Blockers and the single Next action remain current. 857906 stays terminal PASS, 707603 stays the already-running next PH task, and C2/175908 remains the active priority lane. No verified PH work was repeated.
- 2026-09-25 16:12 canonical `origin/main` roadmap readback (detached checkpoint base `638cb85360efeb264c7a8a803f81d8a217516e3f`): 857906=`completed`; 707603=`running`; 840907, 788606 and 913264=`pending`. Supervisor task `CHATGPT-20260924-PERSONALHUB-P0` was explicitly paused while this chat owns C2/175908.
- 2026-09-25 12:56 user override checkpoint: PH work is saved and parked; no further APK/DB compile/test/install is permitted until the remaining PH task chain is complete. C2 is now the active priority lane. Existing PH source/integration/artifact evidence below remains canonical; do not repeat it.
- 857906 integration evidence: PR #44 state `MERGED`, merge commit `ba7089770b552f2c4a73c121ba1356862cec38e4`; `git merge-base --is-ancestor a4b9e82a... origin/main` PASS; `git diff --quiet a4b9e82a... origin/main` PASS; remote `task/857906` absent after prune; local branch deleted; `git branch -vv` and `git worktree list` show only `main` at the merge commit.
- 857906 acceptance command on isolated canonical emulator: `ANDROID_SERIAL=emulator-5554 ./gradlew -Ppersonalhub.testBuildType=qa :app:connectedQaAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.gernalix.personalhub.HubHistorySearchQaDeviceTest --no-daemon --console=plain` → `BUILD SUCCESSFUL`, 3/3 PASS on `Pixel_8a(AVD) - 16`. Acceptance source commit: `1f6e65f99d8f319213c7469c95ab6e29758022b6`.
- Post-acceptance presentation hardening commit `a4b9e82a8f95d2d24660cf09b393b5b4665d215b` is pushed to `origin/task/857906`; targeted `HubActivityPresentationTest`, `:app:compileDebugKotlin`, `checkArchitectureBoundaries`, and `git diff --check` PASS.
- Interim artifact evidence (non-final): APK SHA-256 `37a3ff6a6d0bbcbff3fe25905cd784d9d8d2ee01711b6deaaf6a17ab6d04d180`; corrected DB SHA-256 `9d6c73c8319a7f605d4f10d8863b5ff344e3db7444317635d710fd9bec5bc2bc`; corrected DB ZIP SHA-256 `4dba373995b13fc582dbcac14b6808b04cbfd9dc72c191a538e4f94ff615d87a`; Android validator + cold-start PASS; Telegram delivery completed. Physical Pixel install blocked by device absence and was not attempted via unsafe fallback.
- PersonalHub source convergence checkpoint: `task/857906@1f94c49e6e7c88dbf337214b5d389a5321832831` pushed to `origin/task/857906`; source block commit `0243e2ba5372876a73ef55ec17a1c60686723e3a`; worktree clean after follow-up push. Final consumer-forbid PASS, touched-feature compiles PASS, app compile PASS, `ARCHITECTURE_BOUNDARIES=PASS`, and `git diff --check` PASS.
- Mandatory checkpoint refresh 2026-09-25 09:02: guarded roadmap sync PASS; PersonalHub `task/857906` is clean and local/remote HEAD remain exactly `a1541d99e491228f76f61d792d1fcb396c8cfebd`; checklist/current step/remaining/blockers/Next action were re-read from Git and remain authoritative.
- PersonalHub `task/857906@a1541d99e491228f76f61d792d1fcb396c8cfebd`: remote hash exact; clean worktree after push. People consumer-forbid PASS plus `:feature:supercontacts:compileDebugKotlin` PASS. Places old-package forbid PASS plus `:feature:luoghi:compileDebugKotlin` PASS. `git diff --check` PASS before commit.
- Takeover verification 2026-09-25: guarded roadmap pull PASS at `12ef9f89eba6e32f006e280d2f4e715115ca7ff0`; PersonalHub worktree status clean; local HEAD and `origin/task/857906` both `9d835d8198f7b088f6577cc404306e2a50d5a2aa`.
- 857906 PersonalHub checkpoint `9d835d8198f7b088f6577cc404306e2a50d5a2aa` on remote `task/857906`; consumer-forbid PASS, `ARCHITECTURE_BOUNDARIES=PASS`, app compile PASS, targeted app/deep-link/presentation tests PASS, targeted core Activity DAO/undo tests PASS.
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
- Both the exact final minified APK and the externally migrated, compatible real DB are installed on the primary Pixel using its explicit serial; no APK-only completion.
- Home and every module open without crash against the migrated real DB.
- Primary data remains present and representative user records survive migration.
- Obsolete PH branches/PR residue is removed only after work absorption is proved.
- PersonalHub ends with clean main and no relevant pending integration.

## Next action
When all remaining PR #47 checks are terminal PASS, let the protected single-writer merge PR #47, invoke/verify canonical 788606 PASS without any artifact rebuild, update this checkpoint to 913264, then start the final Pixel DB/APK cutover from the frozen release manifest.
