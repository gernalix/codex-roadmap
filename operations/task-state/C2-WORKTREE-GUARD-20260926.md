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
- [ ] Integrate, realign the runtime worktree, deploy units, verify live checks.

## Current step
Checkpoint the tested implementation, then integrate it and realign/deploy the live supervisor runtime worktree.

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
Added the executor contract, deterministic guard, six focused guard tests, and systemd preflight wiring. Focused tests plus all 131 C2 tests, roadmap verification and diff check pass.

## Remaining
Commit/push, integrate to canonical main, realign live runtime branch to `c2/supervisor-runtime` tracking `main`, deploy units, verify guard/runtime/watchdog readback.

## Blockers
None.

## Evidence
Current runtime branch reports `origin/codex/c2-root-audit-checkpoint [gone]`; pre-deploy guard returns unhealthy with `wrong_branch`, `wrong_or_missing_upstream`, and 8 ahead commits. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_c2_*.py' -v`: 131 PASS; `roadmap_db.py verify`: PASS; `git diff --check`: PASS.

## Acceptance criteria
Canonical repo/worktree roles documented; guard detects foreign repo, dirt, wrong branch/upstream, ahead commits and runtime-code drift; runtime/watchdog preflight it; focused/full relevant tests pass; branch is pushed/integrated; live runtime worktree and units pass.

## Next action
Commit and push `chatgpt/c2-worktree-guard`, integrate it to main, then perform the live runtime worktree cutover and systemd verification.