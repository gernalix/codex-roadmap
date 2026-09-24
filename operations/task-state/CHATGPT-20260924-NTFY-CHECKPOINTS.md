# Operational task state — checkpoint notifications via ntfy

TASK_ID: CHATGPT-20260924-NTFY-CHECKPOINTS
Updated: 2026-09-24 12:55 Europe/Copenhagen

## Objective
Implement reliable notifications for persistent ChatGPT/Codex checkpoints: GitHub publishes only after accepting a task-state push; a self-hosted ntfy service on the Oracle VM delivers to Android and browser/Fedora; Git remains canonical persistence.

## Constraints
- Do not expose secrets/tokens in Git.
- A checkpoint notification must mean the checkpoint is already present on the remote.
- Keep Uptime Kuma for availability/watchdog duties, not as the event bus.
- Prefer direct changes to canonical repos; no intermediate PRs unless technically required.
- Do not disturb unrelated dirty worktrees.
- Persist this task with commit + push checkpoints.

## Plan / checklist
### Phase 1 — Discovery
- [x] Inspect vm_oracle deployment conventions and Oracle access path.
- [x] Inspect codex-roadmap checkpoint workflow/hooks and identify the narrowest integration point.
- [x] Check existing notification/credential conventions on Fedora.

### Phase 2 — Implementation
- [x] Add reproducible ntfy server deployment/configuration to vm_oracle.
- [ ] Deploy and start ntfy on the Oracle VM with persistent storage and authentication.
- [ ] Add a GitHub Actions publisher triggered only by accepted pushes changing `operations/task-state/**`.
- [ ] Store ntfy publishing credentials outside Git (GitHub Actions secrets; Fedora Secret Service for local subscriber credentials if needed).
- [ ] Add Fedora desktop subscription/notification support and enable the browser/PWA path; document the Android one-time subscription step if device interaction is unavailable.
- [ ] Add/adjust Kuma watchdog for ntfy availability if the existing monitoring architecture supports it safely.

### Phase 3 — Validation
- [ ] Prove remote ntfy health.
- [ ] Prove one real checkpoint push produces one ntfy event.
- [ ] Verify no notification is emitted before/without a successful push.
- [ ] Verify affected repos are clean and pushed.
- [ ] Update protocol/docs and close this state file.

## Current step
Phase 2: add the reproducible ntfy deployment and edge configuration to `vm_oracle`, then deploy it.

## Verified facts
- Fedora is reachable through Remote Desktop Commander.
- Local repos codex-roadmap and vm_oracle are clean at task start.
- MegaVault has unrelated local modifications and must not be touched casually.
- ntfy is not currently installed as a Fedora command or service.
- Oracle VM already has Docker, cloudflared and a validated `/etc/cloudflared/config.yml`; the existing tunnel can safely add a dedicated `ntfy.danielegalati.com` ingress without opening a host firewall port.
- Fedora already uses owner-only `~/.config/codex/secrets/` files; this is the established unattended-service credential convention.
- ntfy server v2.28.0 is the current stable release and supports private ACLs plus persisted Web Push subscriptions.
- Oracle VM has Docker/Compose, 14 GiB free disk, and Uptime Kuma already bound to loopback; the canonical Cloudflare tunnel can route another hostname.
- Fedora already has `secret-tool`, `notify-send`, and authenticated `gh` access.
- A GitHub `push` workflow scoped to `operations/task-state/**` is a stronger event boundary than a local Git hook: it covers checkpoints pushed by any chat/client and runs only after GitHub accepted the commit.

## Decisions
- Use one central ntfy topic/event stream rather than one topic per PROMPT_ID.
- Git remote success is the event boundary; notification is downstream of push.
- Prefer Oracle VM as always-on ntfy server.
- Publish checkpoint events from a GitHub Actions `push` workflow on `codex-roadmap`, not from a Fedora Git hook, so every accepted remote checkpoint from any chat/client is covered.
- Keep a Fedora subscriber/desktop notification path as a local convenience; Chrome/Android use ntfy subscriptions directly.

## Completed
- Created this persistent task state.
- Added reproducible Oracle deployment files to `gernalix/vm_oracle`: pinned ntfy v2.28.0 Docker Compose, private server config, secure first-run bootstrap and Fedora deployment wrapper. Final pre-deploy commit is `6ab39cf` on remote `main`.

## Remaining
Oracle runtime deployment, Fedora remote-checkpoint publisher, subscriptions/watchdog decision, end-to-end validation and protocol finalization.

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
Add versioned ntfy Docker/edge deployment files to `vm_oracle`, validate them locally, checkpoint them, then deploy to the Oracle VM.
