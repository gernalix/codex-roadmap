# CHATGPT-20260926-CHATGPT-LIVE-DASH

## Objective
Track every persisted cloud ChatGPT conversation for the signed-in account, regardless of Web/Desktop/mobile visibility, and project title, link, creation time, last interaction time, and live/recent/idle state into Workflowy.

## Constraints
- Do not track or expose device origin.
- Reuse existing repositories where appropriate; avoid unrelated dirty worktrees.
- Workflowy API access stays in workflowy-importer.
- Persist meaningful progress with commit + push.
- Avoid aggressive ChatGPT polling; back off on HTTP 429.

## Plan / checklist
- [x] Inspect relevant repos and Workflowy integration.
- [x] Choose workflowy-importer; leave dirty chatgpt-rdc-supervisor untouched.
- [x] Identify the account-wide metadata source via the existing local browser session and supervisor inventory.
- [x] Implement durable SQLite conversation state and collector abstraction.
- [x] Implement Workflowy dashboard projection with stable dedup/update semantics.
- [x] Add systemd service/timer, bounded polling, full-sweep cadence, and 429 backoff.
- [x] Add tests for parsing, status transitions, dedup, links, and idempotent projection.
- [ ] Validate collector against real account metadata and deploy from integrated main.
- [x] Commit + push implementation checkpoint.
- [ ] Integrate linearly into main, deploy service, validate restart/live dashboard, final checkpoint.

## Current step
Run a metadata-only live collector smoke from the existing local ChatGPT browser session.

## Verified facts
- codex-roadmap is synchronized through tools/roadmap_pull.py.
- workflowy-importer owns the Workflowy API/bridge/cache/runtime and was clean before this task.
- chatgpt-rdc-supervisor already discovers account-synced persisted chats, including mobile-created chats, through a dedicated local browser session on 127.0.0.1:9333.
- chatgpt-rdc-supervisor has an unrelated modified systemd/chatgpt-rdc-browser.service and remains untouched.
- The live ChatGPT UI requested normal/tpp conversation lists, project sidebar metadata, and per-project conversation endpoints.
- Conversation-list requests returned HTTP 429 during probing, so the implementation uses bounded requests plus persisted backoff.
- New workflowy-importer tests pass; the full repository suite passed 76/76 before the final small empty-dashboard guard, and the subsequent targeted 7-test gate passed.

## Decisions
Extend workflowy-importer rather than create a duplicate Workflowy client. Reuse the existing local browser session. Do not store device origin. Classify RUNNING from async/in-progress/open-generation evidence, RECENT from last interaction, otherwise IDLE. Use a roughly 90-second timer, daily full sweep, and at most 20 Workflowy mutations per cycle.

## Completed
Implemented account-wide collector, SQLite state, project/normal chat discovery, title/link/timestamps, RUNNING/RECENT/IDLE classification, idempotent Workflowy hierarchy, systemd service/timer, backoff, tests and documentation. Pushed workflowy-importer feature commit f5c0ed8fee52b707a707ba56a1a8076bcb199138.

## Remaining
Live collector smoke; linear integration against latest origin/main; deploy canonical runtime; verify service/timer and real Workflowy dashboard; final tests/checkpoint.

## Blockers
None. A transient ChatGPT HTTP 429 may postpone live metadata retrieval; the runtime backs off rather than failing or creating an empty dashboard.

## Evidence
- codex-roadmap checkpoint: 8a5be4f51c0df04e374eb21082b5635c464d8ae3.
- workflowy-importer implementation: f5c0ed8fee52b707a707ba56a1a8076bcb199138 on feature/chatgpt-live-dashboard.
- Targeted gate: 7/7 PASS after final code changes.
- Full workflowy-importer suite: 76/76 PASS before the final empty-dashboard guard.
- git diff --check PASS.

## Acceptance criteria
Chats created from any device appear without needing that chat open locally; each row exposes clickable chat link, title, created timestamp, last-interaction timestamp, and RUNNING/RECENT/IDLE; refresh is idempotent; device origin is absent; 429 causes bounded backoff; systemd runtime survives restart; tests and live smoke PASS.

## Next action
Run one metadata-only collector smoke from feature/chatgpt-live-dashboard, printing counts/status only; if healthy, integrate linearly into current main and deploy the user timer.
