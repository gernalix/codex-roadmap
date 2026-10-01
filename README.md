# C3 / codex-roadmap

Operational AI entrypoint: [/home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md](/home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md).
This repository owns C3 lifecycle code and its batch-centric web application.
Do not derive current lifecycle from checked-in historical SQLite or generated files.

## Development

Use isolated test databases, never the live runtime database. Focused Python tests:
`PYTHONPATH=tools:tests python3 -m unittest TEST_MODULE`.
Web model tests: `node --test web/model.test.mjs`.
Source architecture: writer `tools/c3_local_writer.py`, API `tools/c3_api.py`,
runtime `tools/c3_runtime.py`, worker `tools/c3_worker.py`, Inbox job
`tools/c3_inbox_maintenance.py`, web `web/`, units `systemd/`.
Implementation details belong to source and targeted tests, not a second AI protocol.
