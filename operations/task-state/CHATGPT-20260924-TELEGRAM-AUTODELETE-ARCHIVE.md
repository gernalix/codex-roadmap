# Operational task state — Telegram auto-delete archive

TASK_ID: CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE
Updated: 2026-09-24 14:05 Europe/Copenhagen

## Objective
Preserve the complete available history of one Telegram chat configured with 1-day auto-delete, without duplicate storage, while retaining edits and deletion metadata and keeping archived content after Telegram removes it.

## Constraints
- Reuse the already-authorized Telethon account infrastructure where safe; never commit API credentials, session files, OTPs, chat contents, or other secrets.
- Do not mix private chat contents into roadmap checkpoints.
- Keep the existing technical-notification collector/history operational.
- Avoid concurrent use of one Telethon SQLite session by multiple processes.
- Archive identity is (peer_id, message_id); repeated reconciliation must not duplicate messages.
- Deletion handling preserves archived content and records deletion metadata instead of deleting the local copy.
- Persistent runtime must recover after reboot/network failure and reconcile missed updates.
- This user-requested lane temporarily preempts the global master recovery lane without touching the repositories currently owned by 302284.
- Commit + push after important milestones.

## Plan / checklist
### Phase 1 — Inspect and isolate
- [x] Read persistent-state protocol and relevant global/Telegram checkpoints.
- [x] Inspect the existing Telethon collector, tests and systemd runtime.
- [x] Create isolated fedora-system-monitor worktree/branch from the verified task/422308 collector baseline.
- [ ] Identify the target 1-day-auto-delete peer without exposing message contents.
### Phase 2 — Implement
- [ ] Add a dedicated local SQLite archive with uniqueness on peer/message ID and revision history.
- [ ] Add Telethon reconciliation for new and edited messages plus deletion tombstones while retaining original content.
- [ ] Download media into the local archive without re-downloading unchanged files.
- [ ] Add a persistent listener with periodic reconciliation/catch-up.
- [ ] Add hardened systemd user service and installation/update path.
- [ ] Preserve backward compatibility for the existing technical-notification history collector.
- [ ] Add focused unit tests for dedupe, edits, deletions, revisions and reconciliation.

### Phase 3 — Deploy and verify
- [ ] Deploy the new runtime on Fedora without concurrent session use.
- [ ] Backfill all Telegram history still available for the target peer.
- [ ] Verify a second reconciliation is a no-op for unchanged messages.
- [ ] Verify edit handling and deletion retention with bounded tests/live-safe evidence.
- [ ] Verify service enablement/restart behavior and existing notification-history runtime health.
- [ ] Commit and push fedora-system-monitor code and roadmap checkpoint.

## Current step
Implement the dedicated archive path on the isolated fedora-system-monitor worktree, then use its discovery/backfill path to resolve the target peer safely.

## Verified facts
- Existing collector is on fedora-system-monitor branch task/422308 through commit 5d8ed32; it currently mirrors exactly one configured peer to a private text-only Git archive every 15 minutes.
- Current collector already deduplicates new messages by message_id but does not retain edit revisions, deletion state or media bytes.
- Existing runtime uses an authorized Telethon SQLite session under ~/.local/share/fedora-telegram-history.
- Telethon documentation warns that two simultaneous clients must not share one SQLite session file; the new design must avoid concurrent session access.

## Decisions
- Build on the verified task/422308 collector baseline in a separate ChatGPT worktree so the parked Phase-4 integration branch is not mutated unexpectedly.
- Use SQLite as the canonical local message archive for the auto-delete chat; Git remains source/checkpoint persistence, not the storage format for private chat contents.
- Preserve old message bodies/media after Telegram deletion; deletion is metadata, not destructive archive cleanup.
- Prefer one long-lived Telethon client for live events plus periodic reconciliation; if the existing authorized session cannot be shared safely, deployment must use a separate session or serialize access.

## Completed
- Repository/runtime inspection and architecture selection.
- Isolated branch chatgpt/telegram-autodelete-archive created from origin/task/422308.

## Remaining
Implementation, peer discovery, deployment, backfill, live-safe verification, source/checkpoint push, and restoration/continuation of the global master lane.

## Blockers
- Target peer is not yet resolved. Discovery should infer the 86400-second TTL peer from Telegram metadata; only if multiple indistinguishable candidates remain will manual selection be required.

## Evidence
- operations/task-state/README.md and global/Telegram checkpoints read on 2026-09-24.
- fedora-system-monitor task/422308 files and tests inspected locally.
- Official Telethon docs: separate clients should not concurrently use the same SQLite session file.

## Acceptance criteria
- Available target history is archived once per peer/message ID and survives Telegram auto-delete.
- Edits update current state while preserving revision history; deletions are recorded without erasing archived content/media.
- Media is retained locally when accessible.
- Runtime starts automatically, reconnects/reconciles after outages, and cannot overlap unsafely with another process using the same Telethon session.
- Existing technical-notification archive remains operational.
- Focused tests pass; deployed service is healthy; source and checkpoint are committed/pushed with no secrets or private transcript content.

## Next action
Implement the SQLite/event/reconciliation archiver and focused tests in the isolated fedora-system-monitor worktree.
