PROMPT_ID=528123

# Goal
Make C2 the sole PersonalHub orchestrator and add a canonical temporary execution-lane override.

# Canonical starting state
- Legacy worker CHATGPT-20260924-PERSONALHUB-P0 is paused; keep it paused.
- Existing PH residual wi:02cab3c0c0324d0bbda572b81cfc71c3 remains owned by its current lifecycle until PR #55 reaches terminal integration; do not duplicate it.
- Prior handoff prompt 588982 was superseded before any run; do not reuse its branch or treat it as executed.
- Work only in the assigned isolated codex-roadmap worktree.

# Required changes
1. Remove the legacy external_personalhub exclusion from C2 scheduling/intake/preparation/runtime so future PH work uses normal C2 lifecycle, execution specs, worktrees and resource leases.
2. Model PH shared repo/device/runtime exclusivity with explicit C2 resources; do not introduce another scheduler.
3. Add canonical persistent temporary execution-override state, mutated only through the fenced single writer.
4. Provide compact set/read/clear CLI/API. Scope must support project/repo/tag and drain-first semantics:
   - while scoped work is runnable, suppress new out-of-scope dispatch;
   - if scoped work is genuinely non-runnable, allow normal scheduling outside scope;
   - never rewrite semantic priority tags or sort_order.
5. Override must survive snapshot/recovery and be visible in runtime/scheduler readback.
6. Cover replay/idempotency, clear, empty/non-runnable scope, dependencies, resource locking and parallel scheduling with focused tests.
7. Update README/AGENTS: C2 is the sole PH orchestrator; legacy PH worker remains paused/retired from scheduling.

# Constraints
- Minimum scope; no unrelated C2 refactor.
- Preserve current active runs and the existing PH residual.
- Do not directly manipulate roadmap.sqlite; use schema/migrations + writer operations.
- Capture incidental bugs to C2 Inbox only; do not expand scope.
- Use targeted tests, then directly related scheduler/runtime/writer tests.
- Integrate through the normal codex-roadmap PR path; do not report PASS before the exact tested head is merged to main.

# Acceptance
- New PH tasks are schedulable by C2 with normal executor/resource semantics and no external-PH special-case.
- Temporary override is canonical, fenced, persistent, recoverable and does not alter semantic priorities.
- drain-first behavior and fallback when scope is not runnable are proven by tests.
- legacy PH worker stays paused and no duplicate of wi:02cab3c0c0324d0bbda572b81cfc71c3 is created.
