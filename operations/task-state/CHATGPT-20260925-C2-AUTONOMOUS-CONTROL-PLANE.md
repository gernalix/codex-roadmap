# C2 state
TASK_ID: CHATGPT-20260925-C2-AUTONOMOUS-CONTROL-PLANE
Updated: 2026-09-25 Europe/Copenhagen

## Objective
Transform C2 into the canonical autonomous control plane described by the user. Phase 0 comes first: make this same supervisor chat recoverable through an external deterministic watchdog, lease/fencing, and tested replacement-session recovery. After Phase 0 PASS, continue the original macro-goal through reconciliation, optimization, cutover, and real C2 execution.

## Constraints
- roadmap.sqlite is canonical for C2 work items/lifecycle; Workflowy/dashboard are projections.
- Canonical roadmap mutations go only through the existing single writer.
- The watchdog must be native/local, deterministic, low-cost, and independent from model reasoning.
- Exactly one primary supervisor may hold scheduling authority at a time.
- Do not perform extended C2 audit/refactor before Phase 0 recovery is PASS.
- Reuse the existing chatgpt-rdc-supervisor browser/CDP new-chat capability instead of rebuilding browser automation.
- Do not lose or duplicate currently running C2/Codex work during migration.

## Plan / checklist
### Phase 0 — supervisor recovery bootstrap
- [x] Locate C2 canonical control plane and read the governing protocols.
- [x] Identify existing C2 runtime scheduler and legacy chatgpt-rdc-supervisor.
- [x] Verify legacy supervisor already provides deterministic browser new-chat/rollover primitives.
- [ ] Implement local supervisor runtime store with unique supervisor_id, expiring lease, monotonic fencing token, heartbeat, progress, current action, status, and recovery pointer.
- [ ] Implement watchdog expiry/death detection, retirement/fencing, and exactly-once recovery-session launch.
- [ ] Make replacement handoff reconstruct from C2 persistent state only.
- [ ] Gate global C2 scheduling so stale/non-primary supervisors cannot schedule after fencing.
- [ ] Deploy native systemd watchdog without model polling.
- [ ] Acquire the lease for this supervisor and begin heartbeat/progress updates.
- [ ] Run focused unit tests.
- [ ] Run end-to-end recovery acceptance: expiry -> detection -> recovery launch -> replacement acquisition -> state reconstruction -> stale-primary write rejection -> single scheduler/writer.
- [ ] Persist evidence and commit/push Phase 0.

### Original macro-goal after Phase 0 PASS
- [ ] Reconcile every relevant C2 work item against current code/runtime evidence.
- [ ] Optimize/split/merge/reprioritize the roadmap and eliminate obsolete/duplicate work.
- [ ] Finish the autonomous scheduler/executor/control-plane architecture.
- [ ] Improve dashboard semantics/progress/critical-path/parallelism visibility.
- [ ] Audit and consolidate C2 code/repository boundaries where materially useful.
- [ ] Activate maximum useful parallelism and execute ready C2 work under supervision.
- [ ] Continue until global acceptance criteria or only genuine human blockers remain.

## Current step
Implement the minimal supervisor lease/fencing/watchdog in the isolated codex-roadmap worktree, then deploy and prove recovery before any broader C2 work.

## Verified facts
- codex-roadmap/roadmap.sqlite is the canonical roadmap source; GitHub Actions is the canonical roadmap writer.
- tools/c2_runtime.py is an event-triggered local runtime bridge; tools/c2_scheduler.py implements transactional work-item scheduling/resource leases.
- chatgpt-rdc-supervisor is currently a separate browser/chat worker supervisor; its ChatGPTBrowser.new_chat() can create a fresh persisted ChatGPT session in an exact project and send a handoff.
- The legacy supervisor has already proven browser rollover and systemd process recovery, but it has no C2 primary-supervisor lease/fencing contract.
- Canonical codex-roadmap main is currently 3032bde after protected synchronization.
- Existing running work must not be duplicated during the Phase 0 cutover.

## Decisions
- Keep roadmap.sqlite authoritative for durable C2 work; use a small local SQLite runtime store as the authority for volatile primary-supervisor lease/heartbeat/fencing.
- Reuse legacy browser new-chat only as a recovery actuator; it will not be a second intelligent C2 supervisor.
- Fence the old supervisor at expiry before any replacement can acquire ownership.

## Completed
- Minimal architecture/protocol inspection required by Phase 0.
- Isolated source worktree created at /home/daniele/.local/share/c2-bootstrap/codex-roadmap.

## Remaining
Everything unchecked in the plan.

## Blockers
None currently.

## Evidence
- codex-roadmap AGENTS.md and operations/task-state/README.md read in full.
- codex-roadmap README.md and SQLITE_ROADMAP.md read in full.
- Current C2 runtime/scheduler/service files inspected.
- chatgpt-rdc-supervisor README.md, browser.py, supervisor.py, cli.py, handoff.py, and model.py inspected.

## Acceptance criteria
Phase 0 is PASS only when the live recovery path proves: primary lease acquired; heartbeat and progress recorded; expiry is detected; old token is fenced; replacement session is launched; replacement can acquire; persistent C2 state is reconstructable; stale primary writes fail; no dual primary scheduler/writer exists. Then continue the original prompt automatically.

## Next action
Implement the supervisor runtime lease/fencing/watchdog and focused tests in the isolated worktree.
