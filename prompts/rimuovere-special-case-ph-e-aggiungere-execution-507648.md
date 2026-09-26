PROMPT_ID=507648

# Goal
Make C2 the sole orchestrator for PersonalHub and implement a canonical temporary execution-lane override.

# Canonical identity
- Work item: wi:b0887f09d1484998b64c59c13801be47
- Origin: C2 Inbox issue:d9a808ec220d484cac49595a2a65ba37.
- The legacy supervisor task CHATGPT-20260924-PERSONALHUB-P0 is already paused and must remain paused.
- Preserve the existing PH residual wi:02cab3c0c0324d0bbda572b81cfc71c3 while PR #55 is integrating; do not duplicate or reimplement it.
- Follow the canonical C2 executor/start/result/single-writer contracts. Capture incidental issues to C2 Inbox and continue.

# Required changes
1. Remove the PersonalHub external-workload special case from scheduler/runtime/intake/preparer so future PH work uses the normal C2 lifecycle, execution specs, isolated worktrees, executor routing and resource leases.
2. Keep the old PH worker paused. C2 becomes the sole scheduler/orchestrator; any PH-specific helper may exist only as a subordinate executor/adapter.
3. Represent PH shared resources through explicit C2 resource leases where needed (Pixel, TCL, ADB, release/signing or equivalent) and prove collision safety.
4. Add canonical temporary execution override state:
   - persistent in roadmap.sqlite;
   - single-writer and supervisor-fenced;
   - idempotent set/read/clear;
   - scopes at least project, repo and tag;
   - drain-first: if scoped work is runnable, do not start new out-of-scope work; if scoped work is genuinely non-runnable, normal scheduling may use capacity;
   - never rewrite priority:p0/p1/p2 or sort_order;
   - survives snapshot refresh and supervisor recovery.
5. Add compact CLI/control support for set/show/clear with no direct DB writes.
6. Expose the active override and its scheduling decision in runtime/readback.
7. Update README/AGENTS so C2 is the sole PH orchestrator and temporary execution ordering is distinct from permanent semantic priority.

# Verification
Add focused tests for PH preparation/scheduling, explicit resource/device conflicts, override set/replay/clear, project/repo/tag scopes, runnable-scope suppression, blocked-scope fallback, dependencies, max_parallel, snapshot/recovery persistence, and unchanged semantic priority. Run directly related C2 tests.

Integrate through the canonical codex-roadmap path. Do not poll CI or wait for PR integration in a model turn; use the terminal/result contract and stop after handoff.
