# C2 executor contract

## 0 Scope

- Sole common C2 executor contract; task-specific exceptions must be explicit.
- Follow the assigned work item, acceptance criteria, repository, worktree,
  and resources.

## 1 Read

- Read `roadmap.sqlite`, C2 receipts, and repository integration status.
- Treat Workflowy as the human-facing projection.
- Treat Markdown, prompt files, titles, branches, and chat as context, not
  lifecycle authority.

## 2 Write

- Submit canonical mutations through the single writer.
- Never edit canonical state, projections, or queues directly.
- Verify the writer receipt before relying on a mutation.

## 3 Intake

- Capture a new observation in the C2 Inbox; let fenced C2 triage promote or
  discard it. Capture alone does not start a run or create a work item.
- For Codex-backed non-prompt intake, use only `tools/c2_prepare_codex.py` with
  explicit source, model, reasoning, and activity; do not infer or dispatch.

## 4 Start and ownership

- Obtain the writer-owned `executor_started` receipt before substantive work;
  a claim or assignment alone is insufficient. Manual non-prompt work uses
  `tools/c2_executor_start.py --work-item-id`; prompt-backed work starts with
  `tools/roadmap_start.py`, then `c2_executor_start.py --prompt-id`.
- Use the assigned isolated worktree and task branch; never write the canonical branch directly.
- Acquire and release only the shared resources assigned to the run.
- Do not wait, poll, or act on resources owned by another active run.
- Treat `AndroidKeyStore` failures under Robolectric as environment evidence,
  not app bugs. Verify provider paths on canonical `Pixel_8a` AVD before
  physical device, per MegaVault protocol.

## 5 Checkpoint and recovery

- Keep one durable operational checkpoint under `operations/task-state/` for
  non-trivial work; commit and push after important conclusions, phase changes,
  steering, or risky operations. Do not use stash or reflog as task memory.
- Record verified state, remaining work, blockers, evidence, and one next action.
- Resume from that checkpoint after interruption.
- Recover with the smallest evidence-supported fix and rerun the affected gate.

## 6 Discoveries

- Submit each incidental bug, blocker, bottleneck, fragility, or material
  improvement immediately with `tools/c2_issue_capture.py`, using only its
  known description.
- Do not research, deduplicate, triage, prioritize, or create work from the discovery.
- Continue the assigned task unless the discovery is its blocker or a safety-critical condition.

## 7 Finish

- Submit prompt-backed terminal outcomes through `tools/roadmap_finish.py`;
  submit non-prompt work-item outcomes through `tools/c2_executor_result.py`.
  Both route to the single writer. Verify the applied receipt.
- Declare PASS only with evidence for every required acceptance criterion.
- A repository-backed PASS is complete only after canonical integration and
  the writer's terminal receipt. A queued PR is not PASS.
- Stop the run after its terminal receipt; preserve BLOCKED evidence and
  worktrees for recovery.
- Do not wait for asynchronous integration, CI, or manual external state.

## 8 Identities and metadata

- Preserve the canonical work-item ID, run ID, PROMPT_ID, and repository identity.
- Keep execution metadata separate from prompt text.
- Do not change protected metadata or task semantics after the run starts.
- Prompt-backed Codex reports begin `PROMPT_ID=<id>`; terminal reports put
  `RESULT=PASS|BLOCKED|FAIL` on line two.
