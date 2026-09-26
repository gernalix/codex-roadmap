PROMPT_ID=384495

# Goal
Finish the PersonalHub→C2 control-plane cutover and add a canonical temporary execution-order override.

# Starting point
- C2 work item: wi:e1373812bc1444488c824c0e57812fc8
- Source Inbox chain: issue:ab65d686a4464e97860c009f8362d488 -> issue:5da10ee1e4e245339b3cd0decd23cced
- Repository: gernalix/codex-roadmap
- Legacy PH supervisor task CHATGPT-20260924-PERSONALHUB-P0 is already paused/disabled.
- Prior manual executor made no control-plane source edits; checkpoint branch task/wi-32ff-ph-cutover contains only durable handoff state.
- c2-runtime.timer and c2-runtime.path are intentionally paused during this cutover; watchdog stays active.
- Preserve current PH residual wi:02cab3c0c0324d0bbda572b81cfc71c3 until PersonalHub PR #55 reaches terminal integration. Do not duplicate that application work.
- Inspect current main before editing and preserve the completed request-key namespace change from PROMPT_ID 614593.

# Required implementation
- Remove every hard-coded external_personalhub exclusion from scheduler/intake/preparer/runtime. PH must use normal C2 execution specs, executor routing, worktrees and resource leases.
- Keep PH safety through explicit resource locks for shared device/runtime surfaces (Pixel/TCL/ADB/release/install), not a second scheduler.
- Add one canonical persistent temporary execution override, mutated only through fenced single-writer operations.
- Support set, clear and read plus selectors project/repo/tag.
- Implement drain_first: while at least one runnable item matches the scope, only matching new dispatches may start; when no runnable scoped item exists, normal scheduling resumes.
- Override execution ordering only; never mutate priority:p0/p1/p2 or sort_order.
- Persist override in canonical state so snapshot refresh and supervisor recovery preserve it.
- Add a compact standalone writer-backed CLI for override management.
- Expose override state in scheduler/runtime readback/events.
- Add focused tests for PH intake/preparation/scheduling, explicit device/resource collision, set/replay/clear, selector types, empty/non-runnable fallback, dependencies, parallelism, and unchanged semantic priorities.
- Update README/AGENTS: C2 is sole PH orchestrator; any PH adapter is an executor subordinate to C2; temporary override != permanent semantic priority.

# Integration/live cutover
- Work only in the assigned isolated task worktree; never edit main directly.
- Run targeted tests, then directly relevant scheduler/runtime/intake/preparer/writer tests.
- Integrate through the canonical repository path.
- After integration, realign ~/.local/share/c2-supervisor/worktree to current main and require c2_worktree_guard=healthy.
- Re-enable c2-runtime.timer and c2-runtime.path only after live runtime code contains the cutover.
- Verify legacy PH worker remains paused.
- Do not model-poll PR #55 or unrelated CI; leave that existing PH residual to C2 reconciliation.

# Stop condition
Finish only when code is integrated, tests pass, live runtime is aligned/healthy, timer/path are re-enabled, legacy PH scheduler is paused, future PH work is schedulable under C2, and the temporary override can be canonically set/read/cleared and obeyed.
