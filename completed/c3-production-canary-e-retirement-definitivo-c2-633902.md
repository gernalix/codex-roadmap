PROMPT_ID=633902

Implement the final C3 production-cutover retirement package in codex-roadmap.

Context:
- C3 Symphony production routing code is already merged.
- This task is deliberately the first real production Symphony coding canary.
- C2 must not remain as a permanent parallel runtime after C3 is validated.
- Do not perform live host retirement from inside this task. Produce reviewed code, tests, unit definitions and runbook only; the supervising ChatGPT performs deployment after merge.

Required target architecture:
1. Active production orchestration is C3-owned. Add C3-named service/entrypoint definitions for the control-plane functions that must survive: canonical roadmap scheduling/control, bounded Inbox observation maintenance, and any minimal authority/recovery mechanism still required. Do not keep C2 Master Goal, C2 Codex execution, or C2 watchdog/recovery daemons active under another name merely for compatibility.
2. Legacy C2 daemon/timer/path units must be permanently retired after cutover: stop + disable + mask. Include at least c2-master-goal, c2-master-watcher.*, c2-runtime.*, c2-supervisor-watchdog.*, c2-supervisor-recovery.*, and c2-inbox-maintenance.*. Historical source/unit files may remain in repository for audit, but no installed legacy unit may be enabled/runnable after retirement.
3. Implement one explicit guarded retirement command/script. It must:
   - verify C3 prerequisites before destructive retirement;
   - refuse retirement if the C3 Symphony backend/config/artifact is unhealthy;
   - stop/disable/mask legacy C2 units;
   - write a durable retirement marker outside the repo and an audit manifest listing retired units, timestamp, C3 artifact/config evidence and prior unit states;
   - be idempotent and safe to rerun;
   - never delete canonical roadmap.sqlite, Inbox/observation provenance, repository integration history, task worktrees or Git history.
4. Prevent resurrection: legacy C2 installers/start helpers must fail closed when the retirement marker exists. Do not rely only on systemd masks because a later installer could overwrite/unmask them.
5. C3 service definitions must use existing canonical roadmap/single-writer data and keep non-coding lanes/control-plane facts available, but legacy Codex worker orchestration must not be selected once C3 production retirement is complete.
6. Preserve rollback only before retirement is finalized. After the durable retirement marker is written, rollback to C2 must require an explicit manual unretire procedure; normal runtime must never auto-fallback to C2.
7. Update operations/c3-symphony-cutover.md with exact install/canary/retire verification steps and the post-retirement invariant: zero active/enabled legacy C2 orchestration units.
8. Add focused tests for retirement preconditions, idempotency, unit list completeness, marker/audit creation, resurrection prevention, and C3 service handoff.
9. Keep official openai/symphony checkout upstream-pure. Do not modify it.

Do not expand scope into the C3 web app; that is the next P0 after this cutover.
Run focused tests plus relevant scheduler/runtime/service tests and git diff --check.
Commit and push the task branch. Do not merge your own PR if repository policy uses the existing integrator.
