PROMPT_ID=653776

Fix only the C2 successor-supervisor authority handoff bug discovered during recovery.

Context:
- A new local supervisor lease can acquire fencing token N+1 after token N expires.
- The canonical roadmap may still contain expired authority token N.
- Current runtime logic can attempt renew_supervisor for canonical token N while injecting local authority N+1, which the writer rejects.

Requirements:
- In the runtime authority preflight, distinguish a matching current authority from a successor handoff.
- When canonical authority is missing or expired and does not match the current local supervisor id/token, submit exactly one claim_supervisor for the current local authority and return before any scheduling/worker launch.
- Use renew_supervisor only when canonical supervisor id/token already match the current local supervisor and the canonical expiry needs extension.
- Never take over an unexpired different canonical supervisor; remain fenced instead.
- Preserve PersonalHub exclusion and all existing scheduling/locking semantics. Do not touch PersonalHub worktrees, workers, devices, or the shared PH checkout.
- Add focused tests for successor claim, matching renewal, and refusal/no-scheduling while a different unexpired authority exists.
- Run the smallest relevant test set, then the existing focused C2 unittest suite needed to prove no regression.
- Commit and push only the minimal code/test changes on the current branch. Create a PR to main, wait for required CI gates, and merge only if they pass. Do not modify roadmap.sqlite directly.
- Report exact tests, commit, PR, merge result, and any blocker. Stop after the acceptance criteria are verified; no unrelated refactor or cleanup.