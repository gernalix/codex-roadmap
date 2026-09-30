# C3 production cutover — operational checkpoint

Objective: implement the production Symphony coding handoff in the isolated `task/c3-production-cutover` worktree, with hardened artifact, host controls, exact tracker ownership, existing repository integration, focused tests, and PR. Deployment and canary happen after merge.

Constraints: edit this worktree only; no C2 lifecycle helper or roadmap mutation; preserve pilot/security evidence; no production traffic from this branch.

Checklist:

- [x] Read cutover document, bridge, backend, scheduler/runtime/worker, integration writer, and tests.
- [x] Add explicit host routing mode, tracker, source allowlist, and canary rejection in production.
- [x] Add production workflow with exact model/reasoning, isolated task worktree, exact tracker target, and terminal contract.
- [x] Add pinned build/install helper, artifact hash gate, durable service path, and user-bus fallback.
- [x] Add worker routing, durable owner fence, tracker terminal readback, and existing integration queue.
- [x] Add focused bridge/backend/routing tests; scheduler/runtime/worker tests passed (108 total).
- [ ] Resolve remaining implementation review issues and verify production behavior with focused tests.
- [ ] Run `git diff --check`, commit and push the task branch, then open a PR to main with evidence.

Verified facts: pinned source archive and exact hardened lock/manifest preparation passed locally; 108 focused tests passed. Full production escript rebuild could not run in this shell because `mix` is absent from `PATH`; the established gate already reports audit 0, 299/0 tests, and the expected artifact SHA-256. No install or traffic deployment was attempted.

Decision: the production service uses the durable `~/.local/share/c3-symphony/bin/symphony` path. The host must explicitly set `mode=production` and a non-canary tracker. A preexisting Symphony owner prevents legacy fallback for that work item.

Blockers: local shell lacks the Elixir `mix` toolchain for rebuilding the binary here. The full artifact build remains an operator/deployment gate after merge.

Acceptance: coding-only routing, explicit tracker/allowlist/model/reasoning, one owner/issue, exact closed-state result, one integration queue, healthy artifact and stop control, focused tests, clean diff, pushed PR.

Next action: review routing and worktree edge cases, then run the focused suite and final diff check.
