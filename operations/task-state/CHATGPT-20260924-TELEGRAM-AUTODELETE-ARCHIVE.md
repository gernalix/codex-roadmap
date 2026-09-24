# Operational task state — Telegram auto-delete archive

TASK_ID: CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE
Updated: 2026-09-24 17:17 Europe/Copenhagen

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
- [x] Preserve Telegram service actions, including phone-call events, as structured action_type/action_json plus human-readable action_text.
- [x] Add sender_name capture and a no-ID `messages_human` SQLite view with Italian/relative date formatting, sender name, human message/action text, media and state.
- [x] Add relationship-state snapshots/events for own block/unblock and peer last-seen transitions, without storing raw peer IDs in human output.
- [x] Detect own block/unblock as certain events from Telegram `blocked` state; use server block date when available, otherwise observation time.
- [x] Detect probable peer block/unblock only as inference from abrupt last-seen-status transitions compatible with Telegram's blocked-user behavior; retain raw status evidence and confidence.
- [x] Interleave relationship events into the human-readable chronological view and backfill only evidence Telegram still exposes now.

### Phase 3 — Deploy and verify
- [x] Deploy the runtime on Fedora using the existing authorized account session.
- [x] Backfill all Telegram history still available for the target peer.
- [x] Verify a second reconciliation leaves the archive at the same 61 unique message IDs with no duplicate rows.
- [x] Verify edit/deletion/media behavior with focused tests.
- [x] Verify both user timers enabled+active.
- [x] Start both collectors concurrently and verify shared-lock serialization: both services Result=success, no session database-lock failure.
- [x] Verify the existing technical collector still syncs successfully after the lock change.
- [x] Push the fedora-system-monitor source branch through commit 2fc6c38.
- [x] Backfill the live DB after the human-view/action migration; verify the four call rows visible in the supplied Telegram screenshot now render as `Chiamata annullata` with sender name.
- [x] Deploy relationship-state capture after a consistent SQLite backup (`quick_check=ok`), backfill the current own-block event using Telegram's exact server block date, and verify no false peer-block inference from the current `UserStatusRecently` baseline.
- [x] Verify a second systemd sync is a relationship no-op (`relationship_events=0`), runtime/source hashes match, both Telegram timers remain active, and the archive stays duplicate-free.
- [x] Verify `messages_human` exposes only `quando`, `mittente`, `messaggio`, `media`, `stato`, uses `oggi`/`ieri` or Italian weekday abbreviations, and has no unknown sender after same-sender fallback.
- [x] Reconcile/integrate this branch with the existing task/422308 Telegram source closure and remove the temporary branch after equivalence is proved.

## Current step
Runtime and canonical source integration are complete. The stable non-model collector remains active; no further source-closure task is required.

## Verified facts
- Canonical source closure completed through PROMPT_ID 966124. `fedora-system-monitor/main` contains the full Telegram implementation including relationship/block-state tracking; terminal checkpoint records main `7c18ac68134b616228cc1e49f29b8be42eaebec4`, focused/CI/runtime PASS and deletion of absorbed temporary branches.
- Relationship-state deployment PASS: a consistent pre-migration SQLite backup was created and returned `quick_check=ok`; installed runtime hash equals the source branch hash.
- Live baseline after deployment: peer name resolves as Carlo Visda 2; own `blocked=true`; Telegram blocklist server timestamp is 2026-09-24T14:20:43Z, rendered in `chat_human` as `oggi 16:20 · Sistema · Hai bloccato Carlo Visda 2 · certo`.
- Peer status is currently `UserStatusRecently(by_me=true)`; therefore no peer-block inference was created. A second systemd sync created zero additional relationship events.
- Live archive after verification: 79 rows / 79 distinct message IDs; relationship_events=1; peer inferred events=0; both Telegram timers active; auto-delete service Result=success.
- Relationship-state implementation was checkpointed at `f588fd96b849495ffafa05e881dae8361e91c29e` and is now integrated into canonical `fedora-system-monitor/main`; 16/16 Telegram tests PASS plus py_compile/diff-check.
- Live API pre-deploy readback: target currently reports `UserStatusRecently(by_me=true)`; the user currently has the peer blocked, and Telegram's blocklist provides an exact server block timestamp. No peer-block event is inferred from this baseline because the peer status is not long-time-ago.
- Historical source lineage was `task/422308` → `chatgpt/telegram-autodelete-archive`; both temporary branches are now absorbed and removed. Canonical source is `fedora-system-monitor/main` at the 966124 terminal checkpoint.
- Target discovery returned exactly one recent dialog whose Telegram full metadata reports ttl_period=86400; its identifier/title remain local-only.
- Archive DB is local under ~/.local/share/fedora-telegram-autodelete with mode-restricted config/data; private chat contents are not committed.
- First live backfill inserted 61 messages and retained 3 media files; archive footprint at verification was about 1.2 MiB.
- Second live reconciliation kept 61 total rows / 61 distinct message IDs and inserted zero duplicates.
- Focused source gates PASS after the human-view/action update: 14/14 Telegram tests, py_compile and git diff --check; earlier shell/systemd unit gates remain PASS.
- telegram-autodelete-archive.timer is enabled+active at a 5-minute cadence; telegram-notification-history.timer remains enabled+active at 15 minutes.
- Concurrent live start of both services after the shared-lock change returned Result=success for both; auto-delete sync completed and technical history sync completed without sqlite3 database-lock errors.
- The first scheduled post-deploy cycle also passed: technical collector ran at 14:30:00 with new_messages=0; auto-delete collector ran at 14:30:02 with inserted=0/updated=0/unchanged=60/deleted=0; both timers remain active and the archive remains 61 rows / 61 distinct IDs.
- Before the shared lock was deployed, a discovery process reproduced a real Telethon session database-lock failure in the technical collector; the deployed serialization directly addresses that failure mode.
- The supplied UI/DB comparison was verified against Telegram itself: the blank rows at the corresponding call times are `MessageActionPhoneCall` records with `PhoneCallDiscardReasonMissed`; the collector previously archived their rows but discarded the action object. The live DB now preserves those actions and renders them human-readably.
- `messages_human` formats current dates as `oggi H:MM`, previous-day dates as `ieri H:MM`, older dates as Italian `EEE d/m/yy H:MM`, and resolves sender names without exposing IDs. One already-expired legacy blank row could no longer have its action reconstructed, but its sender name is resolved from other rows with the same sender identity.
- Fresh live readback at 15:09 confirmed `messages_human` contains 8 phone-call rows: the screenshot-era 19:37/19:40/19:42/19:48 events render as `ieri … · Daniele · Chiamata annullata`, and newer call events are also classified; archive remains 61 rows / 61 distinct message IDs. Both Telegram timers are active and the auto-delete service Result remains success.

## Decisions
- Use SQLite as the canonical local archive for the private auto-delete chat; Git stores source/checkpoints, not the private transcript.
- Use periodic 5-minute reconciliation rather than a permanently connected second Telethon client. This reuses the already-authorized session without creating another authorization and avoids unsafe concurrent session access.
- First run scans all visible history; later runs scan a 30-hour overlap, enough to cover the 24-hour TTL plus margin and capture edits/deletions of auto-expiring messages.
- Preserve message/media bytes after remote deletion; deletion is represented by deleted_at_utc + deletion_reason.
- The temporary source branch was retained until serialized Telegram source closure, then integrated with the task/422308 baseline through 966124 and removed after containment was proved.
- Own block/unblock events are factual; peer-block events are never promoted beyond inferred confidence because Telegram exposes no direct `blocked_by_peer` flag. A change to the UI's long-time-ago state is evidence, not proof, because the same label also represents genuine >1-month inactivity/privacy behavior.

## Completed
- Relationship/block-state persistence, exact current own-block backfill, inferred peer block/unblock transition logic, combined human timeline, tests, backup, deployment and live no-op verification.
- Implementation, target discovery, local deployment, first full backfill, duplicate-free second sync, systemd activation, shared-session race fix, concurrent runtime verification and pushed source checkpoint.

## Remaining
- No runtime or source-integration action required for relationship/block tracking.
- Historical peer-block cycles that were never observed cannot be reconstructed from Telegram retroactively; future compatible status transitions will be recorded with inferred confidence.

## Blockers
- No runtime or source-integration blocker.
- Inherent limitation: if Fedora and this collector are unavailable for longer than the chat's 24-hour retention window, messages created and auto-deleted entirely during that outage cannot be recovered afterward.

## Evidence
- Historical branch commits through `2fc6c38be783bc2022fa267f0fa46f349c19a39a`, followed by relationship-state reconciliation; canonical integrated main is recorded in `operations/task-state/966124.md`.
- Test gate after the human-view/action update: 14 tests PASS plus py_compile and diff-check; previously verified shell/systemd gates remain valid.
- Live archive: 61 rows / 61 distinct IDs after two reconciliations; 3 media files retained.
- Live systemd: both timers enabled+active; concurrent service start returned success for both collectors.
- Scheduled runtime proof at 2026-09-24 14:30 Europe/Copenhagen: both timer-triggered services completed successfully with no session lock error.
- Live migration backup created before schema/view update; post-deploy service Result=success. The live human view shows the supplied call events as `ieri 19:37/19:40/19:42/19:48 · Daniele · Chiamata annullata`, with zero `Sconosciuto`/`Sistema` senders after fallback resolution.
- 15:09 live readback: `messages_human` reports 8 call-action rows total; DB uniqueness still 61/61; both Telegram timers `active`; `telegram-autodelete-archive.service` Result=`success`.
- Official Telethon documentation confirms that simultaneous clients should not share the same SQLite session; deployed services now serialize on ~/.cache/fedora-telegram-history/session.lock.

## Acceptance criteria
- [x] Available target history is archived once per peer/message ID and survives Telegram auto-delete locally.
- [x] Edits update current state while preserving revision history; deletions are recorded without erasing archived content/media.
- [x] Media is retained locally when accessible.
- [x] Runtime starts automatically on a persistent timer and reconciles after ordinary outages.
- [x] Shared-session access is serialized, preventing the reproduced concurrent SQLite-session lock failure.
- [x] Existing technical-notification archive remains operational.
- [x] Focused tests pass; deployed runtime is healthy; source and checkpoint are pushed with no secrets or private transcript content.
- [x] Human-readable no-ID view, Italian relative dates, sender names and phone-call action rendering are deployed and verified on the live archive.
- [x] Own block/unblock tracking is factual, current block is backfilled from Telegram's server date, probable peer block/unblock transitions are stored only as inferred evidence, and relationship events are interleaved in `chat_human` without IDs.
- [x] Canonical fedora-system-monitor main contains the implementation and the temporary branch is removed.

## Next action
Return control to the current master recovery lane and keep the Telegram runtime running as a stable non-model service. No Telegram source-closure task remains.
