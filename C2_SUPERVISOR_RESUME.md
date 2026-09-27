# C2 supervisor resume contract

- Run `tools/c2_supervisor_resume.py` once per recovery event. Do not scan repository history or poll from a model turn.
- Read the lease recovery pointer once. Require one `C2_RECOVERY_STATE=<single-line JSON>` record with `previous_supervisor_id`, `previous_fencing_token`, `active_runs`, `active_executors`, `preserve_resources`, and `blocker`.
- Require one `# Exact next action` section. After acquiring authority, execute that action; do not rediscover prior work.
- Treat progress age `40s` as `suspected_stall`, `90s` as `final_verification`, and `180s` as stalled and takeover-eligible.
- Return only `RESUMED`, `ALREADY_ACTIVE`, `STALE_TAKEOVER`, or `BLOCKED`. Use `BLOCKED` only for a concrete pointer, authority, snapshot, or writer impediment.
- Reuse an already-acquired successor identity and deterministic claim key. Never create a duplicate supervisor, Codex thread, or C2 run.
- Preserve every active run and listed resource, including PersonalHub workers and devices. This command only acquires supervisor authority; it never terminates or recreates workers.
