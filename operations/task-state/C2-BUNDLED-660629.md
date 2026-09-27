TASK_ID=C2-BUNDLED-660629

# Objective
Implement the three already-started C2 control-plane work items for scoped external-worktree Git writes, activity-backed supervisor liveness, and deterministic bounded supervisor resume.

# Constraints
- Do not call roadmap_start.py, c2_executor_start.py, roadmap_finish.py, or create replacement work items.
- Preserve per-repository isolation, fencing, single-writer semantics, and all PersonalHub workers/devices.
- No model-driven polling; only bounded deterministic checks.
- Modify only C2 control-plane code, focused tests, and short normative documentation.
- Commit and push the verified task/660629 branch.

# Checklist
- [x] Read repository instructions, current branch state, relevant prior supervisor checkpoint, and the three canonical work-item objectives.
- [x] Verify the current Codex app-server sandbox contract for explicit workspace-write roots.
- [x] Add exact Git metadata writable-root discovery and launch regression coverage.
- [x] Tie real runtime writer/launch operations to fenced supervisor progress renewal.
- [x] Implement and document the bounded c2_supervisor_resume state machine.
- [x] Run focused tests, git diff --check, and the full C2 subset if practical.
- [ ] Commit and push task/660629.

# Current step
Run the final focused gates, review the bounded diff, then commit and push.

# Verified facts
- Branch task/660629 started clean.
- Canonical work items remain pending but the user confirms executor_started receipts already exist for all three.
- Codex app-server 0.157.1 accepts a workspaceWrite sandbox object with an explicit writableRoots array.
- External linked worktrees require their worktree git dir and common git dir for commits; the worktree itself remains the normal workspace root.
- Local supervisor lease TTL is 180 seconds and currently separates heartbeat from progress timestamps.
- The final focused modified-component suite passes 58 tests.
- The full `test_c2_*.py` subset ran 209 tests; its only failure is the unrelated ambient-thread isolation defect in `test_c2_executor_start.test_run_identity_is_minimal_and_idempotent`.
- The full subset passes all 210 tests when C2/Codex session identity variables are removed from the test environment, proving the failure is ambient-test isolation rather than this bundle.

# Decisions
- Derive Git writable roots from the assigned worktree at launch; never accept arbitrary roots from prompt metadata.
- Renew progress only after concrete runtime operations succeed, using the current fenced identity.
- Keep resume decision logic pure and bounded; perform no polling or repository/history scan.

# Completed work
- Added derived workspace-write policy using only the assigned linked worktree's out-of-workspace Git metadata ancestor; thread start/resume/turn all receive the same policy.
- Added prepare-time Git metadata validation and focused linked-worktree commit coverage.
- Added fenced `record_activity`, wired runtime writer submissions and executor/notification launches to it, and encoded watchdog states at 40/90/180 seconds.
- Added deterministic `c2_supervisor_resume.py`, strict pointer contract, idempotent authority reuse/claim, resource/run preservation, and normative documentation.
- Captured the unrelated full-suite test-isolation defect as C2 Inbox Issue #2166 without investigating or fixing it.

# Remaining work
Commit and push.

# Blockers
No implementation blocker. The full C2 subset passes in an isolated test environment.

# Evidence
- git status initially showed only branch task/660629 with no changes.
- Canonical roadmap rows provide the exact three objectives and required 40/90/180 second thresholds.
- Focused suite: 58 PASS; `git diff --check` PASS.
- Full C2 subset: 208 PASS, 1 unrelated FAIL; C2 Inbox Issue #2166 queued.
- Full C2 subset with inherited session identity removed: 210 PASS.

# Acceptance criteria
Focused regressions prove scoped commit-capable sandbox roots, automatic activity-backed liveness, and idempotent resume outcomes RESUMED/ALREADY_ACTIVE/STALE_TAKEOVER/BLOCKED; focused tests and diff check pass; commit is pushed.

# Next action
Commit and push task/660629.
