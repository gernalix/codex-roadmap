PROMPT_ID=340495

# Goal
Finish the remaining C2 execution-override CLI idempotency defect after the merged PH→C2 cutover.

# Canonical starting state
- C2 work item: wi:6d318704d7bd441c930832c927116a97
- Repository: gernalix/codex-roadmap
- PR #1563 is already merged on main and the PH→C2 cutover is live.
- Legacy PH worker CHATGPT-20260924-PERSONALHUB-P0 must remain paused.
- Default override read already syncs and reads the verified runtime snapshot; preserve that behavior.
- c2-runtime.timer/path are temporarily paused while this follow-up is prepared.

# Required fix
1. In tools/c2_execution_override.py remove random UUID request keys.
2. Build a deterministic request key from the canonical mutation document that is actually submitted (stable canonical JSON/hash). Exact replay with the same operation + same authority payload must produce the same request key/Issue; a changed authority/fence payload may produce a different key while the set/clear state mutation remains idempotent.
3. Preserve fenced single-writer set/clear semantics and the canonical snapshot read path.
4. Add focused CLI tests proving:
   - identical set replay with identical authority uses the same request key;
   - identical clear replay uses the same request key;
   - different operation/value/document produces a different key;
   - no random UUID is involved;
   - default read still syncs/reads the verified canonical snapshot.
5. Run the focused CLI/writer/scheduler/runtime tests and the smallest relevant broader C2 gate.

# Integration / live acceptance
- Work only in the assigned isolated worktree.
- Commit/push and integrate through the canonical codex-roadmap PR path.
- After exact branch integration to main, align the supervisor runtime worktree and require c2_worktree_guard=healthy.
- Live smoke: set one harmless tag-scoped override twice with identical CLI input without renewing the lease between calls; verify both calls resolve to the same request key/Issue, read shows the value, clear it, then read shows null.
- Leave no active override.
- Re-enable and verify c2-runtime.timer and c2-runtime.path.
- Confirm legacy PH worker is still paused.
- Return PASS only after merged-main and live-smoke evidence. Otherwise return BLOCKED with precise remaining work.
