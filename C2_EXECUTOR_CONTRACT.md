# C2 executor contract

## 0 Scope and precedence

- This is the sole common operating contract for C2 executors. Task-specific
  instructions may add constraints or make an explicit exception.
- Follow the assigned work item and its acceptance criteria.
- Keep work within its assigned repository, worktree, and resources.

## 1 READ / source of truth

- Read operational state from `roadmap.sqlite`, authoritative C2 receipts, and
  repository integration status where applicable.
- Treat Workflowy as the human-facing projection.
- Treat Markdown, Obsidian, prompt files, titles, branches, and chat text as non-authoritative projections or context.

## 2 WRITE / single writer

- Submit every canonical C2 mutation through the single writer.
- Do not edit canonical state, generated projections, or writer queues directly.
- Verify the writer receipt before relying on a mutation.

## 3 INTAKE

- Capture a new observation in the C2 Inbox; let fenced C2 triage promote or
  discard it. Capture alone does not start a run or create a work item.

## 4 CLAIM and EXECUTE / worktree and resource ownership

- Obtain the writer-owned `executor_started` receipt before substantive work;
  a claim or assignment alone is insufficient. Manual non-prompt work uses
  `tools/c2_executor_start.py --work-item-id`; prompt-backed work starts with
  `tools/roadmap_start.py`, then `c2_executor_start.py --prompt-id`.
- Use the assigned isolated worktree and task branch; never write the canonical branch directly.
- Acquire and release only the shared resources assigned to the run.
- Do not wait, poll, or act on resources owned by another active run.

## 5 CHECKPOINT and RECOVER

- Keep one durable operational checkpoint under `operations/task-state/` for
  non-trivial work; commit and push after important conclusions, phase changes,
  steering, or risky operations. Do not use stash or reflog as task memory.
- Record verified state, remaining work, blockers, evidence, and one next action.
- Resume from that checkpoint after interruption.
- Recover with the smallest evidence-supported fix and rerun the affected gate.

## 6 DISCOVERIES / bug-bottleneck intake

- Submit each incidental bug, blocker, bottleneck, fragility, or material
  improvement immediately with `tools/c2_issue_capture.py`, using only its
  known description.
- Do not research, deduplicate, triage, prioritize, or create work from the discovery.
- Continue the assigned task unless the discovery is its blocker or a safety-critical condition.

## 7 FINISH / stop conditions

- Submit prompt-backed terminal outcomes through `tools/roadmap_finish.py`;
  submit non-prompt work-item outcomes through `tools/c2_executor_result.py`.
  Both route to the single writer. Verify the applied receipt.
- Declare PASS only with evidence for every required acceptance criterion.
- A repository-backed PASS is complete only after canonical integration and
  the writer's terminal receipt. A queued PR is not PASS.
- Stop the run after its terminal receipt; preserve BLOCKED evidence and
  worktrees for recovery.
- Do not wait for asynchronous integration, CI, or manual external state.

## 8 INVARIANTS / ID and metadata

- Preserve the canonical work-item ID, run ID, PROMPT_ID, and repository identity.
- Keep execution metadata separate from prompt text.
- Do not change protected metadata or task semantics after the run starts.
