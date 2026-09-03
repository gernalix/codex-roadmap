PROMPT_ID: 582104

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Add canonical SAF-folder metadata to MegaVault for Android apps, and set Personal Hub's value to exactly `Internal storage/Personal Hub` (preserve the repository's canonical casing/format if an existing convention requires it).

Use project_id 49 to resolve Personal Hub and its governing MegaVault context. Read the relevant `AGENTS.md`/protocol first, then inspect only the MegaVault schema/migrations/CLI paths needed for this metadata change.

## Requirements
- Add one nullable field/column representing the full SAF folder path for Android apps/projects.
- Name it consistently with existing MegaVault naming conventions; do not invent a parallel metadata mechanism if one already exists.
- Populate Personal Hub with `Internal storage/Personal Hub`.
- Leave non-Android projects and Android apps without a known SAF folder unset.
- Update schema version/migration/validation/fixtures only where the existing MegaVault architecture requires it.
- Preserve backward compatibility of existing MegaVault commands/views unless the schema change strictly requires an additive update.

## Scope / safety
Minimal diff only. No unrelated schema cleanup, normalization, refactors, or broad project-data audit. Do not try to discover SAF paths for other apps.

## Acceptance
- Existing MegaVault validation/tests relevant to the schema pass.
- SQLite integrity/foreign-key checks pass if they are part of the established protocol.
- Personal Hub resolves to the exact intended SAF path through the canonical data access path.
- No unrelated project records changed.

Stop immediately after these checks pass.

Final output only: `PROMPT_ID`, `RESULT=PASS|BLOCKED`, field name, PH stored value, targeted tests, commit SHA.