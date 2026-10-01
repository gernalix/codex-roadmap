# Migration handoff

Status: migration in progress. This is the single canonical handoff for this migration.

Architecture: MegaVault owns project identity and desired inventory/policy; C3 owns work and prompt lifecycle; github-autosync owns Git integration; Fedora System Monitor owns observed health; codex-usage-monitor owns usage telemetry. PROMPT_ID registry and monitoring cutovers are still pending.

Current state: C3's local writer is active over a private Unix socket, with WAL and atomic/idempotent mutation receipts. The canonical DB is `~/.local/state/c3-control/roadmap.sqlite`; the web app reads it directly. GitHub Actions no longer writes it. Remote ingress is an asynchronous bounded delivery job. Automatic scheduling remains suspended during retirement; writer and web remain available.

M1: **pre-migration / retired**, historical evidence only. Commit `0c7d1f9ce8ecf48eb39387a30dcb79a34745f54e` is retained by `archive/pre-migration-m1`. Its old thread/session/checkpoint must never be used as an executable recovery point.

Retirement: the recursive Inbox-triage item and the old architecture-audit item are superseded. Run `abddbd99029d41af9969572eb20bdce7` is retired with cancellation metadata; its worker reference and lease are cleared. All 50 pre-migration run ownership records and 26 executor bindings were retired; execution receipts and verified backups preserve history. No pre-migration active run or resource lease remains.

Recovery boundary: the old supervisor lease is retired with zero expiry and no recovery pointer. Current C3 coordination uses the relocated `runtime-lease.sqlite3`. Legacy C2 runtime, C3 snapshot/recursive-maintenance units and global ChatGPT supervisor are masked. Live attempts to start them, invoke the old recovery/cutover helpers, run the global supervisor or reinstall it failed closed. Canonical DB/WAL/runtime-lease hashes remained unchanged; the rejected request created no receipt. M1's checkpoint PR #9721 is closed. Independent user changes to `chatgpt-rdc-supervisor/systemd/chatgpt-rdc-browser.service` were preserved.

Workflowy retired: dashboard root and its 1,812 nodes backed up privately then deleted; personal capture/import remains live. Roadmap sync, daily C2 mirror, manual-order authority, launch/fix routes and unused modules are removed; five installed units masked. C3 retains its own UI order; Inbox remains chronological. Canonical DB backup verified before removing 313 legacy overrides. Kuma monitor 63 removed after offline verified backup; all 34 other monitors preserved. Fedora excludes the retired service, including historical heartbeat samples. Tests: 95 targeted C3, 38 personal Workflowy; Fedora suite includes the retirement exclusion. Web/API and personal bridge readbacks passed.

Project identity cutover: MegaVault is canonical; C3 caches its 106 projects, aliases and desired repository/operation inventory. Writer refreshes the cache atomically before mutations and denies local cache writes; local intake/resolution reads MegaVault directly. Historical supervisor references moved 104→105, including prompt registry and its untyped allocation receipt; 104/105/106 now match MegaVault. Both migration steps had verified backups; integrity/FK/readback and 29 targeted tests passed. MegaVault's pre-existing dirty DB was preserved, not changed.

Real residuals: PROMPT_ID authority reconciliation; no-op audit compaction; bounded technical Inbox triage; final runtime consolidation; projection retirement; automatic safe Git GC; monitoring deduplication; full scheduler/Symphony/integrator/recovery and reboot-safety gates. No final PASS is claimed.

Next action: reconcile and reserve all historical PROMPT_IDs in C3, cut over the allocator and retire MegaVault prompt-ID producers, then continue E–J and the final gates from current DB/runtime state.
