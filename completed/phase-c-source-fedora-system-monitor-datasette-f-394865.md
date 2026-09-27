PROMPT_ID=394865

Implement child work item wi:ec03473291134d70aa9b9b4c4414b98f in gernalix/fedora-system-monitor.

Objective: make the source SQLite schema Datasette-friendly by adding bounded, human-readable current-alert and recent-event views over existing keys. Preserve details_json and both UTC/local timestamps. Make changes only in the code that creates or migrates source schema; do not patch the live database.

Follow the verified Phase C source plan for inventory DBI-7e22912087e96489bac60e60. Datasette source policy is to read the latest consistent backup matching /var/lib/fedora-system-monitor/backups/monitor-????????T??????Z.sqlite3, at most 93600 seconds old, opened with mode=ro&immutable=1. Do not change runtime deployment in this task.

Acceptance:
- Add bounded human-readable current-alert and recent-event views over existing keys without dropping details_json or UTC/local timestamps.
- Preserve useful raw values and timestamps for audit and sorting.
- Implement only source-schema creation/migration code.
- Prove idempotent schema generation or migration plus SQLite integrity_check and foreign_key_check.
- Add targeted tests covering view contents, ordering/bounds, raw-field preservation, and repeated migration/generation.

Inspect the repository's own AGENTS.md and existing schema/migration conventions first. Keep changes within this child scope. Commit the implementation and report commit, PR, and verification evidence.
