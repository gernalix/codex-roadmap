PROMPT_ID: 741295

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STANDARD

# Goal
Convert the standalone Soldi Android app (`gernalix/Soldi`) into a native Personal Hub module and migrate its data model into PH, while removing all machine-learning/OCR functionality from the app/module.

ChatGPT will handle receipt OCR externally from now on; PH/Soldi only needs a clean canonical data model and normal CRUD/import paths.

## Work
Use PH project context first, then inspect only the relevant Soldi source/schema and PH module/database patterns.

### Module migration
- Port the useful non-ML Soldi functionality into PH following existing module conventions/navigation/storage.
- Remove/exclude ML models, training/inference, OCR pipelines and their dependencies/assets/UI.
- Preserve existing useful finance data/features unless incompatible with PH architecture.

### `soldi.db` redesign
Normalize the schema aggressively where it removes repeated descriptive values and gives stable reusable entities.
- In transaction-related data, replace repeated fields such as product/title, chain, place/store and similar dimensions with IDs referencing canonical tables wherever semantically correct.
- Create and populate the required referenced tables and foreign keys.
- Add a canonical product catalog so the same known product can be referenced across purchases/transactions.
- Add other tables/columns/indexes/constraints that are clearly required for a robust normalized finance/purchase model, but avoid speculative features.
- Where PH already has a canonical entity (especially Places or shared cross-module entities), reference it instead of creating redundant copies; store Soldi-specific attributes separately only when needed.
- Provide a safe migration for existing Soldi data, preserving values and relationships.

## Safety
No ML/OCR implementation. No unrelated PH refactor. Do not silently discard existing finance records. Keep sync/export compatibility with PH's database architecture. Respect the project's existing guardrails that protect the real installed PH app/data from destructive test/benchmark lifecycles; do not uninstall, wipe, reset, or replace real user data as part of testing unless the governing protocol explicitly provides a safe path.

## Acceptance
- Existing Soldi data migrates without loss.
- Referential integrity passes.
- Repeated products/chains/places are canonicalized and transactions reference IDs.
- Product catalog exists and is usable across transactions.
- Soldi works as a PH module and standalone ML/OCR code/dependencies are absent from the migrated module.
- Targeted DB/module tests and build pass.
- Perform focused verification on the Android device/emulator required by the project protocol: launch Soldi from PH; exercise representative create/read/update/delete behavior; confirm migrated data is visible/readable; close/reopen and confirm persistence; confirm removed ML/OCR UI is absent; verify no obvious regression in PH navigation and the existing sync/auto-export path touched by Soldi writes. Use the narrowest safe device checks and do not broaden into a full app audit.

Stop after PASS; do not continue testing once these criteria are satisfied.

Final output only: `PROMPT_ID`, `RESULT`, migrated schema summary, removed ML/OCR components, data-preservation checks, targeted tests, device/emulator checks, commit SHA.