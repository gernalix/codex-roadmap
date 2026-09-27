# TASK_ID=C2-DESKTOP-SUPERVISOR-20260927

## Objective
Supervise the existing C2 roadmap executor for `PROMPT_ID=660629`, reuse its live Codex sessions and receipts, and intervene only on concrete stalls, drift, duplication, scope violations, or recoverable blockers.

## Constraints
- Supervisor only: do not claim C2 supervisor authority, create replacement runs/work items, or execute roadmap leaves.
- Preserve PersonalHub workers, devices, worktrees, and existing run/session identities.
- Use canonical `roadmap.sqlite`, runtime state, executor receipts, Codex thread state, and task-state files as evidence.
- Prefer one queued steer to the existing live thread; resume only when recovery is required.
- Recheck only after a meaningful state transition or intervention.
- Whenever monitoring incidentally exposes a concrete bug, bottleneck, inefficiency, fragility, recurring failure mode, or improvement opportunity that materially increases C2 time, cost, risk, or failure probability, immediately capture it through `python3 tools/c2_issue_capture.py` or the canonical current capture helper using only already-available context and evidence. Keep the Inbox title concise and human-readable and put actionable technical detail in the description. Do not research, deduplicate, triage, reprioritize, or create a new work item as part of capture. Record the resulting Inbox issue number/URL under Interventions and Evidence, then continue normal supervision unless the finding itself is blocking or critical.

## Observed executor/session map
- Canonical roadmap objective: `prompt:660629`, status `running`; its historical executor-start reference is `01a0e173-23e2-76d0-b9d5-d520ad172f0c`, which is no longer the live executor.
- Live operational executor: Codex thread `01a0e425-7cbe-7270-b9b4-6d074a91c1b6` (`Completa autonomamente la roadmap C2`), actively producing events during this pass and owning the current Uptime Kuma executor-start receipt.
- Active child `01a0e463-77c2-7121-a2fb-243d179b333a`: Project Capsule adoption for `wi:600e8f7b41324bd7b20ef71ef7b65b1d`.
- Resumed child `01a0e458-c6c3-77c2-8b62-d37581adf3be`: Uptime Kuma Inbox bridge; a follow-up turn started during this pass.
- Workflowy regression child `01a0e45f-009c-7552-a824-904593e00067` completed; the live parent was performing real UI reset/readback acceptance. Canonical item `wi:7b9d6266792b422281a397e610b9c1d7` still carries the stale `chatgpt-web-current` start reference pending parent reconciliation.
- Recent roadmap-backed sessions `377172`, `436865`, and `318410` are terminal in canonical C2 state (`PASS`, `BLOCKED`, and `PASS` respectively); do not relaunch them.

## Current health
- Canonical checkout was clean at snapshot start and matched `origin/main` at `b8080f75092ef2cd1cf154bb6e73f1891026b634`.
- Canonical C2 has four `running` work items and no active `claimed/running/recovering` row in `work_item_runs`; current ownership is evidenced by executor-start receipts and live Codex threads.
- C2 supervisor authority belongs to `d5f89429-7bf7-4b94-8ebd-d6133bb3d7d6`, fencing token `41`; this supervisor did not acquire or modify it.
- Runtime worktree guard is unhealthy only for `dirty_worktree`: untracked `operations/task-state/wi-600e8f7b41324bd7b20ef71ef7b65b1d.md`. Runtime branch is one commit behind local `main`.
- User-systemd status could not be read from this sandbox because access to the user bus is denied; no runtime-health claim is inferred from that failure.

## Interventions
- Queued message `01a0e467-e1e3-7c92-b982-aaf23540303d` to live thread `01a0e425-7cbe-7270-b9b4-6d074a91c1b6` after guard-confirmed runtime drift. It instructs the existing executor to preserve the active child checkpoint in its proper canonical/isolated location, avoid duplicate/replacement work, clean the runtime-only worktree safely, use the approved guarded sync path, and verify the guard after finishing the current UI acceptance boundary.
- The target thread emitted further execution events after the queue operation, confirming it remained live; the message was still queued for the next message boundary at final readback.
- User steering added the mandatory incidental-finding capture rule above. No Inbox issue was created for the instruction itself because it is not an incidental defect finding.

## Blockers
- Immediate runtime guard health is blocked by the misplaced untracked checkpoint until the live executor handles it safely.
- Direct systemd user-bus inspection is unavailable from this supervisor sandbox.

## Evidence
- Canonical DB read-only joins over `work_items`, `work_item_runs`, `work_item_executor_starts`, bindings, and result receipts.
- Codex state DB `/home/daniele/.codex/state_5.sqlite`, queue DB, and relevant rollout event tails.
- `python3 tools/c2_worktree_guard.py --canonical /home/daniele/projects/codex-roadmap --runtime /home/daniele/.local/share/c2-supervisor/worktree` returned `state=unhealthy`, `issues=[dirty_worktree]`, `ahead=0`.
- Runtime `git status`: `c2/supervisor-runtime...main [behind 1]` plus the single untracked checkpoint above.

## Next action
After the queued steer is consumed or another meaningful C2/session event occurs, verify the runtime checkpoint was preserved outside the runtime-only worktree, the guard is healthy, and the live parent reconciled the Workflowy item without creating a duplicate run.
