PROMPT_ID: 548263

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Complete PersonalHub's architectural encapsulation so every feature/module is isolated behind explicit contracts, while preserving the single canonical `personalhub.db`, current behavior, current persisted data and existing module interoperability.

This is an architecture-boundary refactor, not a feature rewrite. Make the minimum changes required to enforce real module boundaries; do not perform unrelated cleanup or redesign.

## Known decisive evidence
Start from MegaVault/`AGENTS.md`, then verify only the directly relevant Gradle/module/database files before editing.

Current state already has separate Gradle feature modules (`luoghi`, `multitimetracker`, `sostanze`, `supercontacts`, `wordpulse`, `soldi`) and they do not intentionally depend on one another. However encapsulation is incomplete because the shared database layer currently owns/contains module-specific persistence code and `PersonalHubDatabase` directly names concrete entities/DAOs from several feature namespaces. `core:database` also exports Room through `api(...)`. The app composition root directly knows feature entry activities; that is acceptable only as explicit composition metadata, not as a path for accessing feature internals.

The project must retain exactly one canonical Room/SQLite database. Do NOT solve encapsulation by giving each feature a separate database.

After verifying current state and before code changes, increment `version.txt` exactly once by `+1`.

## Required architecture
Enforce these boundaries with the smallest acyclic structure that fits the current codebase:

- no feature implementation may depend directly on another feature implementation;
- module-specific persistence/domain implementation must be owned by that module or by an explicit module-owned contract/data boundary, not stored as arbitrary implementation code inside a generic shared core package;
- cross-module access must go only through narrow explicit contracts/IDs/query interfaces intended for sharing;
- shared/core code may contain genuinely global infrastructure such as DB lifecycle, generation/export/import/sync plumbing and shared primitives, but must not become a grab-bag of feature internals;
- the single Room database assembly may know the minimum persistence contract types required at compile time, but those types must be deliberate exported DB contracts rather than unrelated feature implementation internals;
- do not expose Room broadly merely to make compilation convenient. Replace `api(Room...)` exposure with narrower dependencies/contracts where feasible without duplicating wrappers that add no boundary value;
- the app may remain the composition root and know public module entrypoints/metadata, but must not reach into feature-private repositories, DAOs, entities or implementation classes.

If the cleanest minimal solution requires splitting database API/contracts from database runtime/assembly, do so. Do not create extra modules unless they materially enforce one of the boundaries above.

## Work
1. Map only the current Gradle dependency graph and the concrete cross-module/core imports needed to identify boundary violations.
2. Classify each shared type as one of: genuinely global infrastructure, deliberate cross-module contract, or feature-owned implementation.
3. Move/refactor only the types needed to enforce the boundaries above and keep the dependency graph acyclic.
4. Replace direct access to foreign feature internals with explicit public entrypoints/contracts.
5. Preserve the exact canonical DB semantics. Avoid a Room schema/version change if the persisted schema does not need to change; moving Kotlin source ownership alone must not create a migration.
6. Preserve current import/export, generation/auto-export, sync journal/Datasette behavior, shortcut/module launch behavior and existing data.
7. Add lightweight architecture regression checks/tests where practical so future code cannot casually reintroduce feature→feature implementation dependencies or generic-core ownership of feature internals.

## Non-goals / safety
- no new user-facing feature;
- no redesign of navigation/UI;
- no schema normalization unrelated to encapsulation;
- no new relationship model between People/Timer/Places: the later cross-module roadmap task owns that;
- no generic plugin framework, service locator rewrite, DI-framework migration, repository-wide package renaming or aesthetic cleanup;
- no second database, no legacy per-feature databases, no destructive migration;
- preserve real-app destructive-test guardrails.

## Acceptance
- Gradle dependency graph is acyclic and contains no feature-implementation → feature-implementation dependency;
- each feature's implementation is owned within that feature boundary; generic core no longer contains arbitrary feature implementation source merely to assemble the DB;
- any feature persistence types that must be visible to the single Room assembly are explicit, minimal DB contracts and are not used as a general bypass around module APIs;
- `core` contains only shared infrastructure/contracts with clear cross-module purpose;
- app/composition code uses public module entrypoints/contracts only;
- Room exposure is narrowed so consumers do not receive implementation dependencies unnecessarily;
- existing `personalhub.db` opens without destructive migration and existing representative data remains readable/writable;
- import/export, auto-export generation, sync/Datasette and representative module writes still PASS targeted tests;
- no user-visible behavior or schema changes were introduced unless strictly required and explicitly justified;
- targeted architecture/build/tests PASS.

## Resource discipline
This is a cross-cutting refactor, but do not perform a general repository audit. Begin with `settings.gradle.kts`, relevant `build.gradle.kts`, `core/database`, `PersonalHubDatabase`, and imports that directly cross those boundaries. Expand only when compilation/tests reveal a required dependency. Batch searches/reads, avoid equivalent checks, do not investigate unrelated findings, and stop immediately after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, final dependency graph/boundaries, moved/exposed contracts, DB/schema impact, architecture guardrail, targeted tests, commit SHA.
