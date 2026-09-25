# Operational task state — ADB Wi-Fi keeper latency

TASK_ID: CHATGPT-20260925-ADB-KEEPER-LATENCY
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Restore reliable always-on Android wireless-debug reconnect behavior on Fedora and persist the verified latency fix safely to the canonical adb-device-keeper main branch.

## Constraints
- Use Remote Desktop Commander for Fedora/runtime work.
- Preserve existing Android pairing/authentication state.
- Do not reset devices or ADB keys unless evidence requires it.
- Reuse already verified runtime evidence; do not repeat destructive reconnect tests without need.
- Treat Git/checkpoint state as canonical memory for continuation.

## Plan / checklist
- [x] Diagnose why the service appears not to reconnect promptly after an ADB Wi-Fi disconnect.
- [x] Reduce normal health-check interval from 60 s to 15 s.
- [x] Reduce missing-device retry interval from 25 s to 10 s.
- [x] Verify forced disconnect/reconnect on Pixel 8a and TCL 6102H.
- [x] Commit and push the fix on isolated task branch.
- [ ] Integrate PR #2 into main once GitHub Actions can run or an approved equivalent gate is available.
- [ ] Verify the service remains enabled/active and reconnect behavior survives one normal Fedora reboot.
## Current step
The runtime fix is already deployed and verified. Source is pushed at task branch commit ff629562164d20449a41f4a9780490ce6dfa2c1e. The only source-integration blocker is GitHub Actions billing/spending-limit refusal; do not rerun identical CI until that account condition changes.

## Verified facts
- Repository: gernalix/adb-device-keeper.
- Task branch: task/CHATGPT-20260925-ADB-KEEPER-LATENCY.
- Pushed task commit: ff629562164d20449a41f4a9780490ce6dfa2c1e (Reduce ADB reconnect detection latency).
- PR #2 targets main and is OPEN.
- Real reconnect smoke previously passed on both physical devices: Pixel 8a approximately 15 s; TCL 6102H approximately 15 s.
- Service was reported enabled + active with no abnormal restarts after the fix.
- Current canonical checkout main is b5a2c22375d16d9d433ebfbf51909e6b6e6ec4db and does not yet contain ff62956.
- GitHub Actions run 36108598671 failed before executing any steps; annotation states recent account payments failed or spending limit must be increased.
- GitGuardian Security Checks pass.
- Task worktree is clean and tracks origin/task/CHATGPT-20260925-ADB-KEEPER-LATENCY.

## Decisions
- Do not reinterpret the CI failure as a product/test failure; no CI steps actually ran.
- Do not retry the same GitHub Actions job without a billing/spending-limit state change.
- Keep the verified runtime fix deployed while source integration waits.
- Reboot verification remains the final runtime acceptance gate after source persistence is settled or when a safe reboot is otherwise appropriate.

## Completed
- Root cause narrowed to excessively slow polling/retry cadence rather than a dead service.
- Runtime polling intervals tightened.
- Two-device reconnect smoke verified.
- Fix committed and pushed to the isolated task branch.
## Remaining
- Resolve/clear the external GitHub Actions billing/spending-limit prerequisite or use the repository's approved integration path if it can accept existing deterministic local evidence.
- Merge/integrate PR #2 to main without bypassing repository protections.
- Perform one normal Fedora reboot and verify adb-device-keeper returns enabled/active and reconnects both devices automatically.

## Blockers
- GitHub Actions cannot start the deterministic job because of the account billing/spending-limit condition. This is external to the code change.

## Evidence
- Task commit ff629562164d20449a41f4a9780490ce6dfa2c1e.
- PR #2: [single-writer] CHATGPT-20260925-ADB-KEEPER-LATENCY.
- GitHub Actions run 36108598671: deterministic job conclusion=failure with zero steps; billing/spending-limit annotation.
- GitGuardian Security Checks: PASS.
- Remote task branch contains ff62956 and worktree is clean.
- Prior live reconnect test: Pixel 8a PASS ~15 s, TCL 6102H PASS ~15 s.

## Acceptance criteria
- [x] Wireless ADB reconnect latency is reduced and verified on both physical devices.
- [x] Source fix is committed and pushed on an isolated task branch.
- [ ] Fix is integrated into canonical main through the repository's safe integration flow.
- [ ] One post-reboot live readback confirms service enabled/active and automatic reconnect still works.

## Next action
Do not rerun the blocked GitHub Actions job. First verify whether the billing/spending-limit prerequisite has changed; if unchanged, leave PR #2 safely pending and perform only non-destructive service health readback. When CI/integration becomes available, integrate ff62956 to main, then perform the single post-reboot acceptance check.
