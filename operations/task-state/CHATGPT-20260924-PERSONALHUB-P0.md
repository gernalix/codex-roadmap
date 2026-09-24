# Operational task state — PersonalHub P0

TASK_ID: CHATGPT-20260924-PERSONALHUB-P0
Updated: 2026-09-24 13:01 Europe/Copenhagen
Parent state: operations/task-state/CHATGPT-20260924-GLOBAL-RECOVERY.md

## Objective
Bring PersonalHub to its final usable state before producing the definitive Pixel build. Complete every still-relevant PH feature/fix/test/optimization identified in the global audit, converge all valid work onto main, freeze the final schema, externally migrate the user's real database to that final schema without adding permanent historical Room migrations, build and validate the final minified APK/AAB, install the exact final APK on the primary Pixel, and verify Home + all modules with preserved real data.

## Scope boundary
This file owns detailed PersonalHub P0 execution state.
The global recovery file owns cross-project orchestration, roadmap infrastructure, codex-usage, Workflowy, ChatGPTExporter, generic PBF/lifecycle work and the final global gate.
Do not duplicate detailed PH state back into the global file; keep only a concise progress/dependency summary there.

## Constraints
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
- One PH schema-changing implementation at a time. Avoid concurrent PH tasks that touch PersonalHubDatabase/schema/DAO because previous overlap caused schema-version collisions.
- Final PH remote state should be main only; delete obsolete/fully absorbed branches after final verification.
- Avoid intermediate PRs unless required by the repository single-writer/integrator protocol. Do not bypass protected writer flow.
- Model/reasoning live only in roadmap metadata, not prompt bodies.
- Stop Codex after queued integration/PASS; do not spend model turns polling CI/merge.

## Verified current facts
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

## Completed
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
- Reconcile/delete obsolete non-main PH branches after proving their work is absorbed.
- Verify no open PH PR/issue/action remains relevant/unprocessed.
- Ensure PersonalHub repository ends clean and main-only.

## Blockers
- Local Android build/device/real-DB work requires Codex/local Fedora access.
- The actual live Pixel DB schema/identity is not yet read and must not be guessed.
- Final DB target cannot be frozen until upstream PH tasks are complete.
- Do not proceed to final Pixel cutover while any relevant PH PBF/integration is unresolved.

## Evidence
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
Continue 920550 from pushed checkpoint `8c34afc`: run the targeted Soldi semantic/search/database tests, fix only concrete failures, update docs/CODE_MAP, then run architecture/build and AVD QA including real on-device model download, indexing, semantic text query, same-object shortlist with distractor, owned-item persistence/removal and reopen. Measure model/APK/runtime impact. If all acceptance gates pass, call `roadmap_finish.py` and stop waiting for asynchronous integration; inspect canonical merged evidence before 857906.
