# C2 supervisor worktree guard

## Objective
Make `codex-roadmap` explicit as the canonical C2 repository and make the supervisor runtime worktree fail closed on unsafe Git drift.

## Constraints
- Do not mutate canonical roadmap state directly.
- Preserve PersonalHub workers/devices and the live C2 supervisor lease.
- Keep the runtime worktree a worktree of the same Git repository, not a second source of truth.

## Plan / checklist
- [x] Inspect canonical checkout, supervisor worktree, protocol and systemd runtime paths.
- [x] Confirm the current supervisor worktree is clean but its remote upstream is gone.
- [x] Add the compact canonical repo/worktree contract.
- [x] Add and test a deterministic worktree guard.
- [x] Wire the guard into C2 runtime/watchdog startup.
- [x] Integrate, realign the runtime worktree, deploy units, verify live checks.

## Current step
Completed.

## Verified facts
- Canonical repository checkout: `/home/daniele/projects/codex-roadmap`.
- Supervisor runtime path: `/home/daniele/.local/share/c2-supervisor/worktree`.
- The runtime worktree shares the canonical `.git`, is clean, but tracks a deleted upstream branch.
- Its code tree matches current `main`; observed tree divergence is writer-generated roadmap state only.

## Decisions
- `AGENTS.md` is the canonical compact executor contract; avoid a second prose protocol.
- Reserve branch `c2/supervisor-runtime` for the runtime worktree, tracking local `main`; development/checkpoints use separate task worktrees.
- Guard runtime-sensitive `tools/` and `systemd/` against drift from `main`; ordinary writer-generated roadmap commits may leave the runtime branch behind without breaking execution.

## Completed
Added the executor contract, deterministic guard, six focused guard tests and systemd preflight wiring; merged PR #1287 (`18ca6451`). Realigned the live runtime worktree to `c2/supervisor-runtime` tracking local `main`, deployed the units, and verified guard/watchdog/runtime live.

## Remaining
None.

## Blockers
None.

## Evidence
Pre-deploy guard caught the stale runtime branch (`wrong_branch`, missing upstream, 8 ahead commits). After cutover it reports `healthy`, branch `c2/supervisor-runtime`, upstream `main`, `ahead=0`, `dirty=false`. 131 C2 tests PASS; roadmap verify and diff check PASS. PR #1287 CI, Roadmap integrity and GitGuardian PASS. Live `c2-runtime.service` and `c2-supervisor-watchdog.service`: `Result=success`, `ExecMainStatus=0`; runtime readback `active=0`, `ready=0`.

## Acceptance criteria
Canonical repo/worktree roles documented; guard detects foreign repo, dirt, wrong branch/upstream, ahead commits and runtime-code drift; runtime/watchdog preflight it; focused/full relevant tests pass; branch is pushed/integrated; live runtime worktree and units pass.

## Next action
None; task complete.