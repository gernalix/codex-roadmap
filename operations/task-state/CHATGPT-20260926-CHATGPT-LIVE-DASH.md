# CHATGPT-20260926-CHATGPT-LIVE-DASH

## Objective
Track every cloud ChatGPT conversation for the signed-in account, regardless of Web/Desktop/mobile visibility, and project title, link, creation time, last interaction time, and live/recent/idle state into Workflowy.

## Constraints
- Do not track or expose device origin.
- Reuse existing repositories where appropriate; avoid touching unrelated dirty worktrees.
- Workflowy API access stays in workflowy-importer; no secrets in Git.
- Persist meaningful progress with commit + push.

## Plan / checklist
- [x] Inspect relevant repos and Workflowy integration.
- [x] Choose workflowy-importer; leave dirty chatgpt-rdc-supervisor untouched.
- [ ] Inspect existing ChatGPT importer/runtime and identify authenticated account-wide source.
- [ ] Implement durable SQLite conversation state and collector abstraction.
- [ ] Implement Workflowy live dashboard projection with stable dedup/update semantics.
- [ ] Add systemd service/timer or event-driven runtime and configuration.
- [ ] Add tests for parsing, status transitions, dedup, links, and idempotent projection.
- [ ] Deploy locally and validate against real account data, including chats not currently open.
- [ ] Commit + push implementation and final checkpoint.

## Current step
Inspect workflowy-importer ChatGPT code and the local authenticated ChatGPT surfaces.

## Verified facts
- codex-roadmap synchronized via tools/roadmap_pull.py.
- workflowy-importer main is clean and already owns official Workflowy API/bridge/runtime.
- chatgpt-rdc-supervisor has an unrelated modified systemd/chatgpt-rdc-browser.service.

## Decisions
Extend workflowy-importer rather than create a duplicate Workflowy client. Device origin is intentionally excluded.

## Completed
Repository/protocol discovery and implementation placement decision.

## Remaining
Collector, storage, dashboard projection, runtime, tests, live validation, push.

## Blockers
None known yet.

## Evidence
workflowy-importer README documents official API, credential handling, local bridge, cache, timers, and existing ChatGPT integration.

## Acceptance criteria
Chats created from any device appear without needing that chat open locally; each row exposes clickable chat link, title, created timestamp, last-interaction timestamp, and RUNNING/RECENT/IDLE; refresh is idempotent; service survives restart; tests and live smoke PASS.

## Next action
Read existing ChatGPT importer/CLI and inspect the authenticated local ChatGPT interfaces needed for account-wide enumeration and activity state.
