# Operational task state — PersonalHub C2 pending fixes

TASK_ID: CHATGPT-20260926-PERSONALHUB-C2-PENDING
Updated: 2026-09-26 Europe/Copenhagen

## Objective
Complete all currently pending C2 work items for gernalix/PersonalHub using Remote Desktop Commander, integrate only minimal necessary changes through the repository single-writer flow, and validate device-facing acceptance on the physical Pixel 8a.

## Constraints
- Use RDC for Fedora/repository/device operations.
- Use physical Pixel 8a serial `192.168.1.37:39233` for device acceptance; never use unscoped ADB.
- Work only in protected worktree `task/CHATGPT-20260926-PERSONALHUB-C2-PENDING`.
- Keep changes minimal; no unrelated refactor.
- Preserve production network/security behavior; test-only permissions/policies stay under androidTest.
- Do not touch the live PersonalHub database unless a task explicitly requires it.
- Final integration must go through repo_single_writer; no direct main commit.
- Maintain the eight C2 work items as separate acceptance units even when implemented together.

## Plan / checklist
- [x] Synchronize C2/roadmap and identify the eight active PH work items.
- [x] Verify PersonalHub main clean and Pixel connected.
- [x] Create isolated single-writer worktree.
- [x] Reproduce Kotlin nullability and KT-71420 warnings.
- [x] Fix DatabasePreferences nullability and production KT-71420 warnings.
- [x] Fix KT-71420 warnings in HubActivityRegisterTest and GitDataFinalValidationTest.
- [x] Add targeted CODE_MAP Git Data/History route.
- [x] Verify INTERNET + cleartext allowance already exists only in core:database androidTest manifest.
- [x] Verify GitDataRestoreDeviceTest already validates the restored DB via raw read-only SQLite without reopening frozen Room.
- [x] Make instrumentation gate fail-closed when runner reports INSTRUMENTATION_FAILED/uninstall failure.
- [x] Run targeted host/unit/compile gates and prove warnings removed.
- [x] Run physical Pixel instrumentation with explicit serial; official JUnit report PASS 1/1.
- [x] Commit and push protected task branch at fb6ee0cc76207e4f3cc45a1e931746031dc40320.
- [ ] PR #48 queued through repo_single_writer; verify main containment only after integrator event.
- [ ] Update/terminalize the eight C2 work items with evidence.

## Current step
Implementation and targeted acceptance are complete. PR #48 is queued to the asynchronous repository integrator; no CI/merge polling is permitted.

## Verified facts
- PersonalHub main and origin/main were both `b736ee83724bf53a04ac43495c93af38cd42e67d` and clean at task start.
- Physical Pixel 8a is connected as `192.168.1.37:39233`; TCL is also connected and must not be targeted accidentally.
- Protected worktree: `/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/CHATGPT-20260926-PERSONALHUB-C2-PENDING`.
- Baseline compile reproduced DatabasePreferences String?/String mismatches at lines 36/38 and KT-71420 warnings in DatabasePreferences, HubActivityUndo, GitDataTracking, GitHistory, GitHistoryStore and DatasetteSync.
- Baseline test compilation reproduced KT-71420 in HubActivityRegisterTest and GitDataFinalValidationTest.

## Decisions
- The eight PH C2 items are closely related and will share one protected branch/worktree, but each acceptance criterion will be verified separately.
- Full repository audits and unrelated cleanup are out of scope.
- The broad baseline unit-test run was terminated after the required warning evidence was captured; targeted tests will replace it.

## Completed
- C2 discovery, Pixel discovery, protected worktree creation, warning reproduction.

## Remaining
- Repository integration/main containment and C2 terminalization after the integrator produces new evidence.

## Blockers
- PR #48 integration is external/asynchronous. Protocol forbids model-driven polling; resume only on a concrete integrator state transition.

## Evidence
- Baseline log: `/tmp/ph-c2-baseline.log`.
- Targeted host gate: HubActivityRegisterTest + GitDataFinalValidationTest BUILD SUCCESSFUL; /tmp/ph-c2-targeted-host.log contains no KT-71420 or Java type mismatch.
- Fail-closed wrapper regression: 4/4 PASS for normal success, INSTRUMENTATION_FAILED, DELETE_FAILED_INTERNAL_ERROR and nonzero child status.
- Physical Pixel report: core/database/build/outputs/androidTest-results/connected/debug/TEST-Pixel 8a - 17.xml = tests=1 failures=0 errors=0; device 192.168.1.37_34375.
- Gradle reported a post-test task failure despite the generated Pixel report being 100% successful; this remains explicit evidence and is not hidden.
- PersonalHub task commit fb6ee0cc76207e4f3cc45a1e931746031dc40320 pushed; repo_single_writer queued PR #48.
- Eight C2 IDs: wi:5c4748d2131a46a3b1ecb41cacd16206, wi:61d05a0b3e7f4651b17be8c3f5ea5257, wi:754f0b89b1b3427e93b97d85219d4914, wi:a75becd338ea44138e78281f3d5af267, wi:a99670bf017e4962822b9c8765ebd178, wi:b3c7c89500754d8c929a3a7076a200a1, wi:cad05c039f464596aafa11ea15283496, wi:e7e578ba356a475e89857d53cd04b673.

## Acceptance criteria
All eight work-item acceptance lists pass, Pixel-required tests use the explicit Pixel serial, the task branch integrates cleanly to main, and C2 contains terminal evidence for every item.

## Next action
On the next concrete repo-integrator state transition for PR #48, verify PersonalHub main contains fb6ee0cc76207e4f3cc45a1e931746031dc40320, then terminalize all eight C2 work items with merged evidence.
