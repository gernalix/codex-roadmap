PROMPT_ID=484338

Fix the C2 lifecycle semantics that caused the Workflowy dashboard to report 14 RUNNING tasks even though there were no corresponding active work_item_runs.

Scope: codex-roadmap. Keep the change minimal and focused; do not refactor unrelated C2 components and do not launch unrelated workers.

Verified starting evidence:
- work_items previously had 14 status='running' rows.
- work_item_runs had no claimed/running/recovering rows; only completed/failed.
- most stale RUNNING rows had executor_started history with run_id NULL; one had a failed expired run.
- direct reconciliation reduced canonical RUNNING from 14 to 3; the three residual rows are two PersonalHub items that recovery explicitly preserves plus supervisor prompt 660629.
- Workflowy projection currently groups raw work_items.status='running' as RUNNING, which is not equivalent to a live executor.

Implement the narrowest durable fix so C2 distinguishes lifecycle state from actual live execution. In particular:
1. Define/use authoritative live-execution evidence from work_item_runs states claimed/running/recovering and any explicitly supported status-only supervisor case.
2. Prevent orphaned/stale RUNNING work items from indefinitely blocking scheduling or being counted as live execution.
3. Preserve genuinely active/recovering work, especially PersonalHub resources; do not infer completion from absence of local CPU activity.
4. Expose a deterministic state/contract that the Workflowy dashboard can consume without treating raw status='running' as proof of activity. If a workflowy-importer code change is strictly required, record the exact follow-up instead of making broad cross-repo edits from this worktree.
5. Add focused regression tests for stale RUNNING rows, real active runs, failed/expired runs, and status-only supervisor orchestration.
6. Do not reintroduce duplicate dispatch, repo-writer conflicts, or broad polling.

Acceptance:
- stale orphan RUNNING entries are reconciled or excluded from live-executor accounting deterministically;
- real active runs remain protected;
- scheduler capacity/repo locks do not treat status-only stale rows as writers;
- focused tests pass;
- report any necessary Workflowy follow-up precisely.

Stop once these criteria are verified.