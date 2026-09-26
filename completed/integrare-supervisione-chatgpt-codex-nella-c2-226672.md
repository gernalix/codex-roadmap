PROMPT_ID=226672
C2_WORK_ITEM_ID=wi:10974cc59a13437fa273b34d83085631

Complete only the remaining non-PersonalHub C2 supervision/control-plane gaps. Start from the current repository state and read operations/task-state/C2-SUPERVISOR-20260926.md plus the canonical work item. Do not request any prior transcript.

Hard constraints:
- Preserve every PersonalHub worker, worktree, repository checkout, Android device, ADB state, and ownership. Do not use Pixel/TCL/emulator.
- roadmap.sqlite is read-only locally; lifecycle mutations go only through the existing GitHub single writer and current supervisor fencing.
- Never create a second primary scheduler/supervisor.
- Reuse merged C2 work from PRs #1171, #1174, #1177, #1178, #1184, #1188, #1191, #1193, #1196 and the discovery-capture rule from #1113. Do not reimplement verified work.
- Make the minimum changes required; no unrelated refactor, cleanup, modernization, or broad audit.

Verified residual gaps to solve:
1. A completed/terminal task-state owner must not leave imported phase descendants falsely running. The repair must be bounded, idempotent, fenced, writer-only, and must not touch PH. Current stale examples are the Phase 2/3/4 children of completed prompt:175908.
2. Integrate C2 with the existing ChatGPT/RDC supervisor so registered ChatGPT workers are monitored for absence of new generation output around 40 seconds and receive bounded recovery, without changing PH ownership or device allocation. Prefer a narrow adapter/configuration over duplication.
3. Prove C2-started Codex executions remain attached to one C2 run through terminal turn/reconciliation and do not duplicate a turn after restart/ambiguous acknowledgement. Fix only if the current merged transport still has a concrete gap.
4. C2 may advance only explicitly configured runnable work while respecting dependencies and resource locks; never infer missing execution metadata.

Acceptance:
- C2-started Codex executions remain tied to their run and are supervised/reconciled through terminal state.
- Registered ChatGPT workers have ~40s no-new-output stall detection with bounded recovery.
- Completed historical task-state items/phases do not remain falsely IN CORSO and projections read the canonical state.
- Newly discovered bugs/bottlenecks/concrete improvements are captured as canonical C2 work items; reuse #1113 rather than duplicating it.
- C2 continues only the next explicitly runnable work item with priority/dependency/lock safety.

Use targeted tests first and expand only if evidence requires it. Maintain the durable task-state checkpoint with objective, checklist, completed/remaining, evidence, blockers and one Next action. Commit and push checkpoints. Stop when these acceptance criteria pass.