PROMPT_ID: 232884

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STANDARD

# Goal
Substances v2 — phase 5. Remove obsolete Substances-owned DB transfer behavior and integrate its import/export UI correctly with PersonalHub's single canonical `personalhub.db` infrastructure.

## Prerequisite / authoritative architecture
Use MegaVault/`AGENTS.md`. PersonalHub must remain single-DB and use the global `DatabaseVault`/Database & Backup flow, central `DatabaseGate` mutation tracking and durable auto-export. Verify this current architecture narrowly before changes; do not redesign it.

After prerequisite verification and before code changes, increment `version.txt` exactly once by `+1`.

## Known defects / work
- A selected Import URI must be passed to the real global validated/atomic import path and success shown only after actual success/restart/refresh behavior.
- Do not merely open the Database screen and call that an import.
- Remove Substances-specific full DB exports after each mutation/read/open; canonical mutations already participate in central generation/auto-export.
- Remove duplicate folder configuration or fake restore paths.
- Remove the legacy porter/path that creates or treats `sostanze.db` as authoritative, deletes unrelated files, or publishes non-atomically.
- Preserve any genuinely separate human-readable/manual data export only if it is clearly not presented as the authoritative DB backup and is still useful.
- Do not weaken `DatabaseVault` validation, rollback/recovery or the no-idle-loop guarantee.

## Safety
Never test a destructive import against irreplaceable live data. Use fixtures/temp DB/provider seams and the established real-app guardrails.

## Tests
Targeted tests must prove:
- chosen valid DB URI invokes the real global import path and success only follows verified success;
- invalid/failing import does not report success and preserves last-good data;
- no Substances mutation/read triggers its own duplicate full export path;
- no active code path creates/uses legacy `sostanze.db` as authoritative storage;
- central generation/auto-export still observes representative Substances writes exactly through normal PH infrastructure.

## Scope / resource discipline
Inspect only Substances import/export/porter UI/helpers and the global DB navigation/import APIs they call. No general DatabaseVault audit, sync redesign, history/UI redesign or unrelated cleanup. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, import wiring, legacy paths removed/retained, export semantics, tests, commit SHA.
