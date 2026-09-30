PROMPT_ID=998028

Resolve the final C3/Symphony dependency-security and compatible-hardening gate for work item wi:1be2f30c543e4429a72af6c6bfb1d32d.

This is the only remaining production-cutover gate after the authenticated Symphony pilot passed.
Keep the official OpenAI Symphony checkout upstream-pure. Do not create or maintain a permanent fork.
Do not modify /home/daniele/projects/symphony for experiments; use disposable scratch clones/worktrees under /tmp.
Durable evidence, tests, and the final cutover decision belong in gernalix/codex-roadmap.

Verified starting evidence:
- Latest stable upstream release is v0.0.3, published 2026-09-15.
- Current upstream main was last verified at be10a1b79df723d6d7612b5651c8522704dafb2e; verify remote refs once before relying on this.
- Stable/current locked Elixir dependencies emitted multiple 2026 security advisories, including HIGH advisories affecting Bandit, Mint, Phoenix and Plug.
- A prior isolated full dependency update removed the advisories but broke the build because Symphony static_assets.ex expects phoenix/priv/static/phoenix.js, absent after Phoenix 1.8.15.
- C3 bridge/pilot readiness gates 1–4 already passed and must not be rerun.

Required work:
1. Reproduce and record the exact deployment-relevant advisory set for the chosen stable/current source: affected package/version, advisory identifier/severity, fixed version, and whether the affected surface is reachable in our intended localhost/trusted-user deployment.
2. Compare stable v0.0.3 and current upstream main. Prefer an upstream release/commit or a compatible dependency resolution over local source changes.
3. In disposable scratch copies, find the smallest compatible hardened dependency set that resolves the relevant advisories while preserving Symphony behavior. Do not use blind update-all as the final solution.
4. Verify the candidate with the repository's normal setup/build/test path plus the relevant advisory audit. Re-run only security/build tests needed for this gate; reuse prior orchestration/pilot PASS evidence.
5. If no compatible advisory-free set exists without changing Symphony source, determine whether a narrow deployment mitigation is sufficient for this exact deployment. Mitigation must be concrete and enforceable (for example loopback-only HTTP surface, trusted-user boundary, process isolation) and must explicitly state which residual advisories remain and why their exploit path is blocked or accepted.
6. Never patch or push OpenAI Symphony. Any candidate source/dependency experiment stays disposable. Do not create a fork.
7. Update codex-roadmap/operations/c3-symphony-cutover.md with reproducible evidence and one unambiguous final decision:
   - GATE PASS: production cutover may proceed, with the exact upstream ref/dependency/mitigation contract; or
   - GATE HOLD: state the smallest remaining blocker and exact next action.
8. Add focused regression/verification tooling only if it materially improves reproducibility. Avoid refactors and unrelated C2 cleanup.
9. Commit and push all useful codex-roadmap changes, with a concise task-state checkpoint for this work item.

Acceptance:
- Deployment-relevant advisories are enumerated against the exact chosen Symphony release/dependency set.
- A compatible upstream release/dependency set builds and tests clean with advisories resolved, or remaining exposure is explicitly mitigated without a permanent fork.
- The production cutover decision is updated with reproducible evidence and rollback conditions.

Stop as soon as these acceptance criteria are verified.