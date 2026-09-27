# Grindr Favorites card identity

Objective: Use canonical identity for Grindr Web Favorites cards and fail closed after opening a profile if its identity differs from the requested profile.

Constraints:
- Work item `wi:fdd72bab3cd44ee89decb25f910b87c6` targets `gernalix/grindr-favorites-monitor`.
- Do not commit credentials, profile data, screenshots, or captured response bodies.
- Use an isolated repository task worktree and the C2 single writer for lifecycle changes.
- Make only changes supported by an existing flow and verifiable acceptance evidence.

Checklist:
- [x] Queue the `executor_started` receipt.
- [x] Allocate an isolated repository worktree.
- [x] Identify the Favorites enumeration and profile-opening paths in the target repository.
- [x] Check whether the target repository extracts card identity from React props or navigates to a card by ID.
- [x] Capture the repository routing issue in the C2 Inbox.
- [ ] Identify the repository or existing flow that owns the requested card opening behavior.
- [ ] Implement canonical identity and post-open verification there, with focused tests.
- [ ] Commit, push, and queue guarded integration only after acceptance passes.

Current step: Owner discovery is blocked by absence of the described UI flow in the target repository.

Verified facts:
- `c2_executor_start.py --work-item-id wi:fdd72bab3cd44ee89decb25f910b87c6 --executor codex` queued mutation Issue #2528.
- The repository writer allocated `wi-fdd72bab3cd44ee89decb25f910b87c6` as an isolated worktree for the target repository.
- `src/grindr_favorites_monitor/scan.py` extracts numeric `profileId` and `lastUpdatedTime` from `GET /api/v5/favorites`; its React access reads pagination/count state and does not extract a card ID or name.
- The scanner navigates only to `/favorites`, counts `[role=gridcell]` elements, and never opens a card.
- `src/grindr_favorites_monitor/open_profile.py` opens a local Datasette view from a photo filename, not a Grindr Web card.
- Targeted search of the target repository's source, scripts, and tests found no card click, navigation by card ID, or post-open UI flow.
- Targeted search of the adjacent `grindr-web-exporter` browser module found a chat-opening method but no Favorites card flow.
- `c2_issue_capture.py` queued C2 Inbox Issue #2532 for the missing owner/code path.

Decisions: Do not add an unrequested new browser interaction workflow to a read-only scanner to satisfy an absent call site.

Completed work: Repository and related module inspection; no project files changed.

Remaining work: Locate the actual owner or obtain a concrete UI flow, then implement and verify the requested identity guard.

Blockers: The described React card ID/name extraction and card opening do not exist in the assigned repository.

Evidence: `rg` over `src`, `scripts`, and `tests`; direct review of `scan.py` and `open_profile.py` in the isolated task worktree.

Acceptance criteria: Card navigation uses a canonical identity source; each opened profile is verified against the requested ID; missing or mismatched evidence stops processing.

Next action: Resolve the owning repository or provide the intended Favorites card opening flow before changing project code.
