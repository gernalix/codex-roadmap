# Operational task state — Telegram auto-delete archive

TASK_ID: CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE
Updated: 2026-09-24 14:31 Europe/Copenhagen

## Objective
Preserve the complete available history of one Telegram chat configured with 1-day auto-delete, without duplicate storage, while retaining edits and deletion metadata and keeping archived content after Telegram removes it.

## Constraints
- Reuse the already-authorized Telethon account infrastructure where safe; never commit API credentials, session files, OTPs, target peer identifiers, chat contents, or other secrets.
- Do not mix private chat contents into roadmap checkpoints or source Git.
- Keep the existing technical-notification collector/history operational.
- Never allow concurrent Telethon clients to use the same SQLite session without a shared lock.
- Archive identity is (peer_id, message_id); repeated reconciliation must not duplicate messages.
- Deletion handling preserves archived content and records deletion metadata instead of deleting the local copy.
- The first sync must backfill all history still visible from Telegram; later syncs may use a bounded overlap window.
- This user-requested lane temporarily preempted the global master recovery lane without touching the repositories owned by 302284.
- Commit + push after important milestones.

## Plan / checklist
### Phase 1 — Inspect and isolate
- [x] Read persistent-state protocol and relevant global/Telegram checkpoints.
- [x] Inspect the existing Telethon collector, tests and systemd runtime.
- [x] Create isolated fedora-system-monitor worktree/branch from the verified task/422308 collector baseline.
- [x] Resolve exactly one recent peer with 86400-second auto-delete using Telegram metadata only; persist the peer only in local mode-0600 config.

### Phase 2 — Implement
- [x] Add a dedicated local SQLite archive with uniqueness on peer/message ID and revision history.
- [x] Add bounded reconciliation for new/edited messages and deletion tombstones while retaining original content.
- [x] Backfill all still-visible history on the first successful sync before switching to the overlap window.
- [x] Download media into the local archive and avoid re-downloading unchanged media.
- [x] Add a dedicated hardened systemd user service + 5-minute persistent timer.
- [x] Serialize the new collector and the existing technical collector on one shared Telethon session lock with bounded wait.
- [x] Preserve the existing technical-notification collector behavior and 15-minute timer.
- [x] Add focused tests for dedupe, edits, deletions, revisions, media retention, reappearance and initial full backfill.

### Phase 3 — Deploy and verify
- [x] Deploy the runtime on Fedora using the existing authorized account session.
- [x] Backfill all Telegram history still available for the target peer.
- [x] Verify a second reconciliation leaves the archive at the same 61 unique message IDs with no duplicate rows.
- [x] Verify edit/deletion/media behavior with focused tests.
- [x] Verify both user timers enabled+active.
- [x] Start both collectors concurrently and verify shared-lock serialization: both services Result=success, no session database-lock failure.
- [x] Verify the existing technical collector still syncs successfully after the lock change.
- [x] Push the fedora-system-monitor source branch through commit fe5d371.
- [ ] During global recovery Phase 4, reconcile/integrate this branch with the existing task/422308 Telegram source closure and remove the temporary branch after equivalence is proved.

## Current step
Runtime work is complete and operational. Source integration is intentionally parked until the global recovery reaches its Telegram Phase 4 lane; the preempted master lane can resume at 302284.

## Verified facts
- Source branch: gernalix/fedora-system-monitor chatgpt/telegram-autodelete-archive, based on task/422308; remote head fe5d371c2327da83e213cdd9154b608119378ba5.
- Target discovery returned exactly one recent dialog whose Telegram full metadata reports ttl_period=86400; its identifier/title remain local-only.
- Archive DB is local under ~/.local/share/fedora-telegram-autodelete with mode-restricted config/data; private chat contents are not committed.
- First live backfill inserted 61 messages and retained 3 media files; archive footprint at verification was about 1.2 MiB.
- Second live reconciliation kept 61 total rows / 61 distinct message IDs and inserted zero duplicates.
- Focused source gates PASS: 13/13 Telegram tests, py_compile, bash -n, systemd-analyze verify, git diff --check.
- telegram-autodelete-archive.timer is enabled+active at a 5-minute cadence; telegram-notification-history.timer remains enabled+active at 15 minutes.
- Concurrent live start of both services after the shared-lock change returned Result=success for both; auto-delete sync completed and technical history sync completed without sqlite3 database-lock errors.
- The first scheduled post-deploy cycle also passed: technical collector ran at 14:30:00 with new_messages=0; auto-delete collector ran at 14:30:02 with inserted=0/updated=0/unchanged=60/deleted=0; both timers remain active and the archive remains 61 rows / 61 distinct IDs.
- Before the shared lock was deployed, a discovery process reproduced a real Telethon session database-lock failure in the technical collector; the deployed serialization directly addresses that failure mode.

## Decisions
- Use SQLite as the canonical local archive for the private auto-delete chat; Git stores source/checkpoints, not the private transcript.
- Use periodic 5-minute reconciliation rather than a permanently connected second Telethon client. This reuses the already-authorized session without creating another authorization and avoids unsafe concurrent session access.
- First run scans all visible history; later runs scan a 30-hour overlap, enough to cover the 24-hour TTL plus margin and capture edits/deletions of auto-expiring messages.
- Preserve message/media bytes after remote deletion; deletion is represented by deleted_at_utc + deletion_reason.
- Keep the temporary source branch until global Telegram source closure, then integrate it together with the task/422308 baseline rather than bypassing the serialized recovery plan.

## Completed
- Implementation, target discovery, local deployment, first full backfill, duplicate-free second sync, systemd activation, shared-session race fix, concurrent runtime verification and pushed source checkpoint.

## Remaining
- No runtime action required now.
- In Phase 4, integrate the source branch into canonical fedora-system-monitor main together with the existing Telegram collector closure, rerun bounded tests/readback, then delete the temporary branch.

## Blockers
- No runtime blocker.
- Canonical main integration is deliberately gated by the global single-active-recovery-lane protocol.
- Inherent limitation: if Fedora and this collector are unavailable for longer than the chat's 24-hour retention window, messages created and auto-deleted entirely during that outage cannot be recovered afterward.

## Evidence
- fedora-system-monitor branch commits through fe5d371c2327da83e213cdd9154b608119378ba5.
- Test gate: 13 tests PASS plus py_compile, shell syntax, systemd unit verification and diff-check.
- Live archive: 61 rows / 61 distinct IDs after two reconciliations; 3 media files retained.
- Live systemd: both timers enabled+active; concurrent service start returned success for both collectors.
- Scheduled runtime proof at 2026-09-24 14:30 Europe/Copenhagen: both timer-triggered services completed successfully with no session lock error.
- Official Telethon documentation confirms that simultaneous clients should not share the same SQLite session; deployed services now serialize on ~/.cache/fedora-telegram-history/session.lock.

## Acceptance criteria
- [x] Available target history is archived once per peer/message ID and survives Telegram auto-delete locally.
- [x] Edits update current state while preserving revision history; deletions are recorded without erasing archived content/media.
- [x] Media is retained locally when accessible.
- [x] Runtime starts automatically on a persistent timer and reconciles after ordinary outages.
- [x] Shared-session access is serialized, preventing the reproduced concurrent SQLite-session lock failure.
- [x] Existing technical-notification archive remains operational.
- [x] Focused tests pass; deployed runtime is healthy; source and checkpoint are pushed with no secrets or private transcript content.
- [ ] Canonical fedora-system-monitor main contains the implementation and the temporary branch is removed; deferred to global Phase 4.

## Next action
Resume the global master recovery at 302284. When Phase 4 becomes active, reconcile chatgpt/telegram-autodelete-archive with task/422308, integrate the combined Telegram collector changes into fedora-system-monitor main through the canonical source-closure lane, rerun tests/runtime readback, and delete the temporary branch.
