PROMPT_ID=205775

Implement the Phase C source schema changes for the codex-usage-monitor repository.

Source plan: /home/daniele/MegaVault/ai/database_inventory_phase_c.json. Scope is inventory IDs DBI-2b69ae6583fc2ecb09cd61ef and DBI-afa8c16b058aed689a67bb3b, at source databases /home/daniele/.local/share/codex-session-archive/index/archive.sqlite and /home/daniele/.local/share/codex-usage-monitor/codex_usage_monitor.db. Use the repository's existing schema creation and migration code. Never patch live databases.

Acceptance criteria:
- Normalize sessions.prompt_ids into a session_prompt_ids junction table and preserve the raw prompt_ids value for audit.
- Add a human-readable session catalog view.
- Add indexes for last_timestamp_utc and updated_at_utc.
- Add indexes on quota_snapshots.run_id and notification_events.snapshot_id.
- Preserve useful raw values and timestamps for audit and sorting.
- Prove idempotent generation or migration, SQLite integrity_check, and foreign_key_check.

Make only changes necessary for these source schema/migration requirements and their focused tests. Inspect repository instructions and relevant schema code, implement and verify, commit the complete change, and report commit and verification evidence.
