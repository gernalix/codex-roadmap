TASK_ID=C2-AUTODRAIN-20260927
PROMPT_ID=660629

# Objective
Continue C2 autonomously until quiescence: Inbox -> reconcile -> priority -> execute -> repeat. Preserve existing runs/threads and use C2/Git as canonical memory.

# Current supervisor authority
- supervisor_id: a920f0c2-c0f9-411b-8656-0f65cd833689
- fencing_token: 20
- Previous token 19 expired during the handoff; token 20 was claimed canonically.
- Durable recovery pointer is this file; runtime worktree is disposable.

# Completed since recovery
- PROMPT_ID 999198 completed canonically after PR #1965 merge.
- Added verified resolved_by relations 528123 -> 886300 and 340495 -> 886300; historical BLOCKED outcomes preserved; PBF dispositions resolved.
- Fresh Inbox triage processed actionable rows; one user-deferred Kuma row remains intentionally pending and MUST NOT be promoted/scheduled until explicit release.
- Stale P0 finalizer regression and executor_started recovery items reconciled as already implemented with evidence.
- New P0 umbrella created: wi:68cd5b09eae24fe59352bd0750a559c1.
- Legacy overlapping MegaVault roots c24bc..., 05f8..., 6d4b... superseded by that umbrella.
- P0 umbrella phases: A c615636..., B 9b77740..., C c0d99c..., D 6a187c..., E 911686..., final gate e20d87....
- Duplicate final gate 879ae... superseded by e20d87....
- C2 repo-lock defect promoted as wi:09c58fd538c3440a9e44d2414ddea29f.

# Current active leaf
- Phase A work item: wi:c615636f22314b2c89c3a8b037d2d6cc
- PROMPT_ID=853479
- Run ID: ca41243058a34906a088c21c271dba56
- Model/reasoning/MegaVault: GPT-5.6 Sol / medium / STRICT
- Worktree: /home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_MegaVault/853479
- Branch task/853479; clean at creation, initially equal to origin/master.
- Run is canonically running/acknowledged but no worker unit/receipt was created because c2-runtime.service failed its worktree guard.

# Current blocker
c2-runtime.service reports runtime worktree unhealthy: dirty_worktree + runtime_code_drift. Runtime worktree ~/.local/share/c2-supervisor/worktree is branch c2/supervisor-runtime, 116 commits behind main, with only operations/task-state/C2-AUTODRAIN-20260927.md modified. Incident captured as C2 Inbox issue #2026 / issue:1ae99de21cff4d33a87aac4ea6ada7bf.

# Deferred Inbox item
issue:bfcfdb13f8b647c3b667dbc7af832b30 — automatic Uptime Kuma monitors + Linux service registry. Explicit user constraint: Inbox only; do not promote, schedule, or start until explicit release. Triage work item wi:c01fa42e01da48be80bd048ad5e07653 is BLOCKED on this intentional deferral.

# Exact next action
1. Preserve this checkpoint with commit+push.
2. Update local supervisor lease recovery_pointer to this durable file.
3. Restore the disposable runtime worktree: discard its pointer edit, fast-forward/reset c2/supervisor-runtime to local main, preserve upstream=main, then verify tools/c2_worktree_guard.py reports healthy.
4. Run one fenced c2_runtime cycle with supervisor token 20. Do NOT schedule a duplicate: recover/launch existing run ca41243058a34906a088c21c271dba56.
5. Confirm executor_started receipt + Codex thread binding for PROMPT_ID=853479; supervise that thread until terminal/integration.
6. Then continue Phase B -> C -> D -> E -> final gate, returning to Inbox/reconcile between transitions.
7. After P0 umbrella is complete, execute wi:09c58fd... and resume normal priority.
8. Ignore/defer the Kuma Inbox row until explicit user release.

# Quiescence
Quiescence requires no actionable pending Inbox rows (explicit user-deferred rows may remain), no unreconciled running/recovering work, no configured runnable/schedulable work, and no recoverable local blocker or completed integration left unreconciled.
