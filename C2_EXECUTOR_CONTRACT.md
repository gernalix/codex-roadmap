# C2 executor contract

## 0 Scope and precedence

- Apply this contract to every C2 executor.
- Follow the assigned work item and its acceptance criteria.
- Let a task-specific instruction override this contract only when it states the exception explicitly.

## 1 READ / source of truth

- Read operational state from `roadmap.sqlite` and authoritative C2 receipts.
- Treat Workflowy as the human-facing projection.
- Treat Markdown, Obsidian, prompt files, titles, branches, and chat text as non-authoritative projections or context.

## 2 WRITE / single writer

- Submit every canonical C2 mutation through the single writer.
- Do not edit canonical state, generated projections, or writer queues directly.
- Verify the writer receipt before relying on a mutation.

## 3 CLAIM and EXECUTE / worktree and resource ownership

- Queue `executor_started` before substantive work; stop if it is rejected.
- Use the assigned isolated worktree and task branch; never write the canonical branch directly.
- Acquire and release only the shared resources assigned to the run.
- Do not wait, poll, or act on resources owned by another active run.

## 4 CHECKPOINT and RECOVER

- Keep one durable operational checkpoint for non-trivial work.
- Record verified state, remaining work, blockers, evidence, and one next action.
- Resume from that checkpoint after interruption.
- Recover with the smallest evidence-supported fix and rerun the affected gate.

## 5 DISCOVERIES / bug-bottleneck intake

- Submit each incidental bug, bottleneck, fragility, or material improvement immediately to the C2 Inbox with only its known description.
- Do not research, deduplicate, triage, prioritize, or create work from the discovery.
- Continue the assigned task unless the discovery is its blocker or a safety-critical condition.

## 6 FINISH / stop conditions

- Submit every terminal outcome through `tools/roadmap_finish.py`.
- Declare PASS only with evidence for every required acceptance criterion.
- Stop after PASS or after submitting BLOCKED, FAIL, or CANCELLED.
- Do not wait for asynchronous integration, CI, or manual external state.

## 7 INVARIANTS / ID and metadata

- Preserve the canonical work-item ID, run ID, PROMPT_ID, and repository identity.
- Keep execution metadata separate from prompt text.
- Do not change protected metadata or task semantics after the run starts.

| need | action |
| --- | --- |
| read state | Read `roadmap.sqlite` and authoritative receipts. |
| mutate C2 | Submit one request to the single writer. |
| start | Queue `executor_started`, then use the assigned worktree. |
| checkpoint | Update the one durable operational checkpoint. |
| record discovery | Send its description to the C2 Inbox immediately. |
| finish | Submit the outcome with `roadmap_finish.py`, then stop. |
