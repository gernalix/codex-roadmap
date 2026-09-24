# Operational task state — checkpoint notifications via ntfy

TASK_ID: CHATGPT-20260924-NTFY-CHECKPOINTS
Updated: 2026-09-24 14:18 Europe/Copenhagen

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
- [x] Deploy/start ntfy on Oracle with persistent storage and authentication; protected publisher/subscriber users and ACLs verified.
- [x] Remove the duplicate Nginx ntfy server block while preserving the verified public route.
- [x] Add a GitHub Actions publisher triggered only by accepted pushes changing `operations/task-state/**`.
- [ ] Store publisher credential in GitHub Actions secret; never commit it.
- [ ] Store subscriber credential in Fedora Secret Service; never commit it.
- [x] Add tracked Fedora desktop subscriber + user-service installer and install/verify the unit locally.
- [ ] Enable/validate the Fedora subscriber after its Secret Service credential is present.
- [x] Document the browser/PWA and Android one-time authenticated subscription path.
- [ ] Add/adjust Kuma watchdog for ntfy availability if the existing monitoring architecture supports it safely.

### Phase 3 — Validation
- [x] Prove remote ntfy health.
- [ ] Prove one real checkpoint push produces one ntfy event.
- [ ] Verify no notification is emitted before/without a successful push.
- [ ] Verify affected repos are clean and pushed.
- [ ] Update protocol/docs and close this state file.

## Current step
Phase 2: publisher workflow and Fedora subscriber are implemented. Credential transfer into GitHub Actions/Secret Service is blocked by the current remote-tool safety layer; continue with Kuma availability monitoring and any validation that does not require exposing credentials.

## Verified facts
- Fedora is reachable through Remote Desktop Commander.
- Local repos codex-roadmap and vm_oracle are clean at task start.
- MegaVault has unrelated local modifications and must not be touched casually.
- ntfy is not currently installed as a Fedora command or service.
- Oracle VM already has Docker, cloudflared and a validated `/etc/cloudflared/config.yml`; the existing tunnel can safely add a dedicated `ntfy.danielegalati.com` ingress without opening a host firewall port.
- Fedora already uses owner-only `~/.config/codex/secrets/` files; this is the established unattended-service credential convention.
- ntfy server v2.28.0 is the current stable release and supports private ACLs plus persisted Web Push subscriptions.
- First Oracle deployment reached a healthy loopback ntfy service, created the Cloudflare DNS route and exposed a healthy public endpoint from Fedora. The only failure was Oracle's resolver not seeing the just-created hostname within the bootstrap timeout; this was a validation-location bug, not an ntfy/edge failure.
- Oracle VM has Docker/Compose, 14 GiB free disk, and Uptime Kuma already bound to loopback; the canonical Cloudflare tunnel can route another hostname.
- Fedora already has `secret-tool`, `notify-send`, and authenticated `gh` access.
- A GitHub `push` workflow scoped to `operations/task-state/**` is a stronger event boundary than a local Git hook: it covers checkpoints pushed by any chat/client and runs only after GitHub accepted the commit.
- `.github/workflows/notify-task-state-checkpoint.yml` is now on `codex-roadmap/main`; it emits one authenticated event per accepted push containing the changed task IDs plus repository/commit identity.
- Fedora subscriber code, user unit and installer are tracked on `vm_oracle/main`; Python/bash syntax checks pass and the installed user unit passes `systemd-analyze verify`.
- The existing deploy wrapper copied `/opt/ntfy/client.env` to Fedora as `~/.config/codex/secrets/ntfy-checkpoints.env` mode 0600 without exposing values.
- Remote tool safety blocks automated transfer of the stored passwords into both GitHub Actions secrets and GNOME Secret Service; no credential value was printed or committed.
- Oracle currently runs ntfy healthy on loopback `127.0.0.1:3003`; Nginx host routing is HTTP 200 and `https://ntfy.danielegalati.com/v1/health` returns `{"healthy":true}`.
- A stale duplicate Cloudflare ingress for `ntfy.danielegalati.com` pointed at unused port 8084 and caused the initial public 502; it was removed and the bootstrap now normalizes all duplicate entries to one `127.0.0.1:8001` route.
- `/opt/ntfy/credentials.env` remains root-owned mode 0600 with the generated publisher/subscriber passwords; the corrected bootstrap has now created both users in the ntfy auth DB.
- The bootstrap fix for password injection plus duplicate-ingress normalization is on `vm_oracle/main` in substantive commit `19b4dc3`; remote head at this checkpoint is `dd60451`.
- Corrected bootstrap rerun completed successfully: public/origin health PASS; `checkpoint-publisher` is write-only on `chatgpt-checkpoints`, `checkpoint-subscriber` is read-only, and anonymous access remains denied.
- The duplicate legacy Nginx block at `/etc/nginx/conf.d/ntfy-checkpoints.conf` was removed; the canonical `sites-enabled` block is the only remaining server block and public health remains PASS.

## Decisions
- Use one central ntfy topic/event stream rather than one topic per PROMPT_ID.
- Git remote success is the event boundary; notification is downstream of push.
- Prefer Oracle VM as always-on ntfy server.
- Publish checkpoint events from a GitHub Actions `push` workflow on `codex-roadmap`, not from a Fedora Git hook, so every accepted remote checkpoint from any chat/client is covered.
- Keep a Fedora subscriber/desktop notification path as a local convenience; Chrome/Android use ntfy subscriptions directly.

## Completed
- Created this persistent task state and updated the persistent-state protocol to require a complete executable checklist/current step.
- Added reproducible Oracle deployment files to `gernalix/vm_oracle`: pinned ntfy v2.28.0 Docker Compose, private server config, bootstrap and Fedora deployment wrapper.
- Deployed ntfy, Nginx routing, Cloudflare DNS/ingress and Web Push keys; public health is PASS.
- Diagnosed and repaired the duplicate stale Cloudflare ingress that caused HTTP 502.
- Hardened the bootstrap so the two ntfy account passwords are passed via environment rather than argv and all duplicate ntfy ingress entries are normalized before adding the canonical route.
- Reran the corrected Oracle bootstrap and verified the protected publisher/subscriber users plus their write-only/read-only topic ACLs.
- Removed the legacy duplicate Nginx server block and hardened `vm_oracle/ntfy/bootstrap.sh` to remove it on future deploys; clean redeploy returned `NTFY_ORIGIN=PASS` and `NTFY_PUBLIC=PASS`.
- Added and pushed the GitHub Actions checkpoint publisher to `codex-roadmap/main` (commit `237bfdd`).
- Added and pushed Fedora subscriber code/service/installer plus client documentation to `vm_oracle/main` (head `a1d3df2`).
- Installed the tracked Fedora subscriber executable/unit locally for static verification; activation is intentionally deferred until its read-only credential is in Secret Service.

## Remaining
Populate the GitHub Actions publisher secret and Fedora Secret Service subscriber credential when the tool can perform credential-store writes; enable/test Fedora subscriber; add Kuma watchdog; run one real checkpoint end-to-end; perform browser/Android one-time subscription where device UI is available; finalize docs/state.

## Blockers
Credential-store writes are currently blocked by the Remote Desktop tool safety layer: attempts to pipe the existing passwords into GitHub Actions secrets or GNOME Secret Service are rejected before execution. Do not expose, regenerate or commit them. Other implementation/monitoring work can continue.

## Evidence
- codex-roadmap persistent-state protocol now requires an executable checklist/current step.
- Public ntfy health: HTTP 200 with `{"healthy":true}`.
- Oracle ntfy container: healthy, bound to `127.0.0.1:3003`; Nginx host route: HTTP 200.
- Cloudflare config now has a single ntfy hostname route to `127.0.0.1:8001`.
- `/opt/ntfy/credentials.env`: root:root mode 0600; values were not recorded.
- After corrected bootstrap rerun, `ntfy user list` shows `checkpoint-publisher` with write-only access and `checkpoint-subscriber` with read-only access to `chatgpt-checkpoints`; anonymous has no access.
- `vm_oracle` auth/ingress hardening commit: `19b4dc3`; legacy Nginx cleanup is on remote history.
- GitHub publisher workflow: `codex-roadmap/main` commit `237bfdd`.
- Fedora subscriber implementation/docs: `vm_oracle/main` head `a1d3df2`.
- Fedora static validation: `python3 -m py_compile` PASS; installer `bash -n` PASS; installed unit `systemd-analyze verify` PASS.
- Credential materialization wrapper rerun: `NTFY_ORIGIN=PASS`, `NTFY_DEPLOY=PASS`; local client env path exists mode 0600 (values not read into chat).

## Acceptance criteria
- A pushed task-state checkpoint triggers a concise ntfy notification containing task ID and commit identity.
- Failed/unpushed checkpoints do not claim persistence.
- ntfy survives Oracle VM/service restarts and stores state persistently.
- Secrets are not committed.
- Browser/Fedora and Android can subscribe to the same authenticated stream.
- The implementation is documented, tested, committed and pushed.

## Next action
Inspect the existing Uptime Kuma management path and add the narrow ntfy health watchdog if safe. Then checkpoint. Credential-store population/real end-to-end notification remains the only blocked validation lane.