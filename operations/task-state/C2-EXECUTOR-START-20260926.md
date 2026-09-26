# TASK_ID C2-EXECUTOR-START-20260926
Objective: every executor must notify C2 when it actually starts handling a work item, distinct from scheduler assignment/claim.
Constraints: reuse single writer and existing run/binding lifecycle; idempotent; no second lifecycle; automatic for C2-launched workers; manual fallback for externally launched executors.
Checklist:
- [x] Verify current claimed/running/bind semantics.
- [x] Add writer-owned executor_started receipt.
- [x] Auto-submit before substantive C2 worker execution; enrich from chat/thread binding.
- [x] Add manual helper for ChatGPT/RDC/Codex/external executor first-action notification.
- [x] Update canonical repo contracts plus global Codex and ChatGPT instructions.
- [x] Add focused tests and fail-closed worker test.
- [x] Run C2-focused gate.
- [x] Commit/push to existing PR #1325.
Current step: complete.
Verified facts: scheduler assignment/ack remains distinct from executor_started; worker submission occurs before native/browser/Codex work and failure prevents execution; binding enriches start receipt only after run+item are truly running. Manual non-prompt start now atomically claims a runnable pending work item by work_item_id; prompt-backed work still requires roadmap_start first. PROMPT_ID is not required for non-prompt work.
Blocker: none.
Acceptance: C2 distinguishes assigned/claimed from actually-started; every C2 worker emits start before task work; manual executor can claim+start a runnable non-prompt work item or start a prompt-backed task after roadmap_start; duplicate/replay is idempotent; writer remains authoritative.
Evidence: thread 01a0df78-d3a0-7491-893d-01fa3e66af7c exposed rollout bug: helper absent on main and canonical PH work item wi:02cab3c0c0324d0bbda572b81cfc71c3 has prompt_id NULL/status pending. Inbox #1339 captured. Focused manual claim/start tests PASS; full C2 suite 172/172 PASS; ChatGPT Custom Instructions readback 4907 chars with work-item-id/non-prompt rule; ~/.codex/AGENTS.md corrected.
Next action: commit/push PR #1325, then integrate once required checks pass so helper exists on main.
