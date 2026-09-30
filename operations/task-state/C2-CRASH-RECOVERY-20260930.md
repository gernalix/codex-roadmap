# C2 crash recovery 2026-09-30

Objective: restore C2 after Chrome crash and reboot with minimal local hardening.
Constraints: retain canonical writer/fencing/run identities; no browser restart or broad refactor.

- [x] Confirm old stale items canonically completed/blocked.
- [x] Acquire fenced native supervisor authority; receipt #7034 applied.
- [x] Restore native Inbox worker on existing run 8e134c021b2e4809a95c78bc8535789b.
- [x] Restore recurring Master watcher ticks with OnUnitInactiveSec=30s.
- [x] Verify py_compile, systemd unit validation, active/expired authority recovery and duplicate-worker protection.
- [x] Verify autonomous runtime tick, recurring watcher working/delegated, health success, enabled boot timers and Linger=yes.
- [x] Verify first native triage mutation #7045 applied by writer with canonical receipt readback.
- [x] Terminal recovery receipt #7048 applied.
- [x] Version the four deployed files byte-for-byte in an isolated branch.
Publication target: task/c2-crash-recovery-20260930; commit and remote SHA are reported in the Codex chat.

Master coordinator exists and remains inactive while delegated worker progresses.
No reboot was performed for verification; boot enablement and expired-authority recovery were checked.

Install the scripts from tools/c2_crash_recovery into ~/.local/lib/c2-crash-recovery.
Install the two systemd drop-in directories into ~/.config/systemd/user.
Then systemctl --user daemon-reload; restart c2-master-watcher.timer; start c2-runtime.service.
The adapter uses the clean C2 runtime worktree and existing bounded native Inbox fallback.
Rollback: remove the two installed drop-ins, daemon-reload, restart the watcher timer.

## Next action
Review the published task branch; runtime recovery is already deployed and verified.
