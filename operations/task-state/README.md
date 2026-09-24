# Persistent operational task state

Use this file pattern for non-trivial ChatGPT work that could outlive one conversation turn or session.

## Naming
- Prefer `operations/task-state/<PROMPT_ID>.md` when one canonical prompt owns the work.
- Otherwise use `operations/task-state/<TASK_ID>.md` with a stable descriptive TASK_ID.

## Required sections
- Objective
- Constraints
- Plan / checklist (complete executable plan, updated as the task evolves)
- Current step
- Verified facts
- Decisions
- Completed
- Remaining
- Blockers
- Evidence
- Acceptance criteria
- Next action

## Rules
- Store conclusions and operational state only; never store chain-of-thought or hidden reasoning.
- Treat the checklist as the current executable plan. Add newly discovered sub-tasks/dependencies and split large work into phases; check items off only when verified.
- Never store secrets, credentials, or raw private transcripts.
- This is not canonical roadmap lifecycle state. Roadmap mutations still go through the single writer.
- Commit and push after important conclusions, completed sub-goals, expensive verification, user steering, before new phases/risky actions, and whenever losing the current session would cause material duplicate work.
- After interruption/freeze/resume, read this file first and continue from `Next action`.
- Update the existing file rather than creating competing state files for the same task.
- Do not use stash/reflog/uncommitted files as permanent memory.
