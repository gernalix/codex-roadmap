PROMPT_ID=592759

Implement the MegaVault Phase C source task for work item wi:adeb5da884a6464d9b0b00497b79eb98.

Goal: In the MegaVault source schema creation/migration code, add a human-readable database inventory view joining existing project, repository, and host foreign keys for Datasette navigation. Preserve useful raw values and timestamps for audit and sorting. Never patch a live database.

Acceptance:
- Changes are limited to source schema creation/migration code and its necessary focused tests.
- A human-readable inventory view joins the existing project, repository, and host relationships, preserving source inventory fields.
- Migration/generation is idempotent.
- SQLite integrity_check and foreign_key_check pass in a disposable/test database.

Starting point: canonical MegaVault checkout /home/daniele/MegaVault, project_id=23; task worktree returned by C2/roadmap_start is authoritative. Follow /home/daniele/MegaVault/ai/BOOTSTRAP.md and /home/daniele/MegaVault/ai/database_inventory_phase_c.json. Keep scope only to this source view/migration and directly required tests. Do not touch the live megavault.sqlite, runtime deployments, inventory decisions, unrelated Phase C repositories, or the older mixed Phase A/B/C recovery worktree.

Inspect only the directly relevant schema creation/migration implementation and tests. Verify migration idempotence and integrity/foreign-key checks using a temporary database. Do not add broad audits or unrelated cleanup.
