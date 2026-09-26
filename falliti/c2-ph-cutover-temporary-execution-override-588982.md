PROMPT_ID=588982

# Goal
Make C2 the sole PersonalHub orchestrator and add a canonical temporary execution-lane override.

# Canonical starting state
- C2 work item: wi:282d4fca25f2466d9fdd501bb567e125
- Repository: gernalix/codex-roadmap
- Legacy worker CHATGPT-20260924-PERSONALHUB-P0 is already paused. Do not resume it.
- Current PH residual wi:02cab3c0c0324d0bbda572b81cfc71c3 is already running and waiting for PersonalHub PR #55 integration. Preserve it; do not duplicate or restart it.
- c2-runtime.timer/path are intentionally paused during this control-plane cutover. Restore them only after the integrated main/runtime worktree is safe.

# Required implementation
1. Remove the PersonalHub external-orchestrator special case from C2 scheduling/preparation/runtime. Future PH items must use the same C2 lifecycle, execution specs, worktrees, executor routing and resource leases as every other work item.
2. Preserve collision safety. Demonstrate PH tasks can declare explicit shared resources (for example PH repo/device/ADB/release resources) and that scheduler leases prevent incompatible concurrent use. Do not invent a second PH scheduler.
3. Add one canonical persistent temporary execution override, mutated only through fenced single-writer operations. Support set/read/clear and idempotent replay.
4. Override scope must support project, repo, or tag. Drain-first semantics: if runnable work exists inside the active scope, new out-of-scope dispatch is suppressed; when no scoped work is runnable, normal scheduling may use available capacity. Do not mutate priority:p0/p1/p2 or sort_order to represent the override.
5. Override applies to new dispatch only; do not semantically mutate or forcibly rewrite running work. State must survive canonical snapshot/supervisor recovery.
6. Add a compact CLI for set/status/clear. Writer operations must be fenced; status/read must be read-only.
7. Expose override state/reason in scheduler/runtime readback/events sufficiently for operators and recovery.
8. Update README/AGENTS: C2 is the sole PH orchestrator; legacy PH worker stays paused; temporary execution override is distinct from permanent semantic priority.
9. Add focused tests for PH scheduling, explicit resource locks, override set/replay/clear, project/repo/tag matching, empty/non-runnable scope fallback, dependencies, parallelism, runtime readback, and recovery persistence.

# Safety / protocol
- Work only in the assigned isolated worktree.
- Single writer only for canonical C2 mutations.
- Do not touch or execute the existing PH residual application task; this task changes C2 control-plane ownership/routing.
- Do not use model-driven polling. Use deterministic checks and stop after bounded verification.
- Preserve all unrelated active workers and repos.
- Incidental bugs/bottlenecks go to C2 Inbox with description only.

# Verification / finish
Run targeted scheduler/runtime/intake/preparer/mutation tests, then the smallest relevant broader gate.
For codex-roadmap source changes, do not claim PASS until the exact branch is integrated to canonical main and read back there. If integration cannot be proven through the current canonical path, return BLOCKED with the exact integration blocker rather than treating an unmerged branch as complete.
