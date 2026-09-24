# Operational task state — checkpoint notifications via ntfy

TASK_ID: CHATGPT-20260924-NTFY-CHECKPOINTS
Updated: 2026-09-24 12:32 Europe/Copenhagen

## Objective
Implement reliable notifications for persistent ChatGPT/Codex checkpoints: Fedora publishes only after a successful Git push; a self-hosted ntfy service on the Oracle VM delivers to Android and browser/Fedora; Git remains canonical persistence.

## Constraints
- Do not expose secrets/tokens in Git.
- A checkpoint notification must mean the checkpoint is already present on the remote.
- Keep Uptime Kuma for availability/watchdog duties, not as the event bus.
- Prefer direct changes to canonical repos; no intermediate PRs unless technically required.
- Do not disturb unrelated dirty worktrees.
- Persist this task with commit + push checkpoints.

## Plan / checklist
### Phase 1 — Discovery
- [ ] Inspect vm_oracle deployment conventions and Oracle access path.
- [ ] Inspect codex-roadmap checkpoint workflow/hooks and identify the narrowest integration point.
- [ ] Check existing notification/credential conventions on Fedora.

### Phase 2 — Implementation
- [ ] Add reproducible ntfy server deployment/configuration to vm_oracle.
- [ ] Deploy and start ntfy on the Oracle VM with persistent storage and authentication.
- [ ] Add a Fedora checkpoint publisher that runs only after successful pushes containing task-state changes.
- [ ] Store ntfy credentials outside Git using the existing secure credential convention.
- [ ] Enable browser/Fedora consumption path and document Android subscription steps if device interaction is unavailable.
- [ ] Add/adjust Kuma watchdog for ntfy availability if the existing monitoring architecture supports it safely.

### Phase 3 — Validation
- [ ] Prove remote ntfy health.
- [ ] Prove one real checkpoint push produces one ntfy event.
- [ ] Verify no notification is emitted before/without a successful push.
- [ ] Verify affected repos are clean and pushed.
- [ ] Update protocol/docs and close this state file.

## Current step
Phase 1 discovery.

## Verified facts
- Fedora is reachable through Remote Desktop Commander.
- Local repos codex-roadmap and vm_oracle are clean at task start.
- MegaVault has unrelated local modifications and must not be touched casually.
- ntfy is not currently installed as a Fedora command or service.

## Decisions
- Use one central ntfy topic/event stream rather than one topic per PROMPT_ID.
- Git remote success is the event boundary; notification is downstream of push.
- Prefer Oracle VM as always-on ntfy server and Fedora as publisher/client.

## Completed
- Created this persistent task state.

## Remaining
All discovery, implementation, deployment and validation steps above.

## Blockers
None confirmed yet.

## Evidence
- codex-roadmap main was clean at task start.
- vm_oracle main was clean at task start.

## Acceptance criteria
- A pushed task-state checkpoint triggers a concise ntfy notification containing task ID and commit identity.
- Failed/unpushed checkpoints do not claim persistence.
- ntfy survives Oracle VM/service restarts and stores state persistently.
- Secrets are not committed.
- Browser/Fedora and Android can subscribe to the same authenticated stream.
- The implementation is documented, tested, committed and pushed.

## Next action
Inspect vm_oracle operations docs, Oracle SSH wrapper, and codex-roadmap Git hooks/checkpoint protocol before editing runtime configuration.
