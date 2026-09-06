PROMPT_ID: 952671

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: STRICT

# Goal
Complete Hub Context Graph adoption across all PersonalHub modules present at execution time, add generic external Resources, and harden the finished cross-module system end-to-end.

This task extends the already validated architecture. It must **not** redesign HubContext, the Composer or the recursive Explorer.

## Prerequisite
The recursive HubContext Explorer must already exist and the HubContext foundation/Composer/explorer architecture tests must pass. Verify those prerequisite checks narrowly. If they fail for unrelated reasons, stop `BLOCKED` rather than reopening the design.

Increment `version.txt` exactly once by `+1` for this goal.

## Determine modules at execution time
Read the current app module registry/composition metadata (currently `HubModule.entries` in `app/src/main/java/com/gernalix/personalhub/capsules/shortcuts/LauncherShortcutsCapsule.kt`) and `settings.gradle.kts` to identify modules actually present.

People, Timer and Places should already be integrated by previous tasks. Integrate every remaining real module that exposes user-meaningful canonical entities. At the time this prompt was written, expected remaining modules include:
- Substances;
- WordPulse;
- Soldi.

If a seventh functional module has been added by execution time, integrate it too. Do not invent/create a new module merely because one was anticipated.

For each remaining module, initially inspect only:
- public module entrypoint/navigation boundary;
- canonical entity/repository contract;
- DB contract/binding boundary needed for HubContext;
- detail flow if one exists.

Open more implementation only when one of those concrete symbols or a targeted test requires it.

## Entity-kind integration rule
Expose only user-meaningful canonical entity kinds with stable identity and useful navigation/selection semantics. Do not expose internal join rows, caches, sync rows, technical logs or implementation-only tables.

A module may expose more than one legitimate entity kind. Examples to evaluate from the real current schema rather than assume blindly:
- Soldi: Transaction, Account, Product or other canonical finance entities;
- Substances: Substance, Intake, Prescription or other canonical entities;
- WordPulse: its actual stable user-facing objects.

Each entity kind gets the same generic adapter/binding pattern already proven by Person/Place/Session.

Adding that adapter must automatically make the entity kind available to:
- ad-hoc Composer selection;
- Context Type/template fields;
- recursive Explorer facets/reverse traversal;
- user-configurable related sections;
without pair-specific UI or schema code.

## No pairwise integrations
Do **not** implement separate feature paths such as:
- Soldi↔People;
- Soldi↔Places;
- Soldi↔Timer;
- Substances↔People;
- WordPulse↔Places;
- or any other pair matrix.

The acceptance criterion is that one adapter registration is sufficient for all existing HubContext mechanisms.

## Preserve domain-specific relationships
Do not force every existing cross-domain relation into HubContext.

Relations with specific domain meaning/cardinality should remain explicit where appropriate, for example a Prescription referencing a particular doctor or finance transaction. HubContext represents the broader fact that entities participated in the same activity/event/context; it is not a replacement for every semantically strong foreign key.

If an older generic-link mechanism overlaps with HubContext, migrate/retire it only when semantic equivalence is certain, migration is non-destructive and focused tests prove no data loss/double counting. Otherwise leave it isolated and document why it remains domain-specific/legacy.

## Generic Resource entity
Add a host-owned user-facing `Resource` entity kind for external information that should participate in Contexts without requiring a full PersonalHub module.

Support at least:
- normal web URL;
- Android URI/deep link, including Workflowy deep links;
- short text/note;
- user-selected document/image URI via SAF where appropriate;
- optional title/label.

Resource requirements:
- stable HubEntity identity;
- usable in ad-hoc Composer and Context Types;
- visible/traversable in Explorer and reverse views;
- open URL/URI through a safe Android Intent when a handler exists;
- missing/invalid handler must fail visibly without crashing;
- persist URI permission when required for SAF resources;
- do not copy external files into PersonalHub merely to create a link unless existing app safety/storage semantics explicitly require it.

Required example path:

`Giovanni → Luoghi → Piazza Savona → Sessioni → 12/02/2026 → Resources → Workflowy note`

Tapping the Workflowy Resource must invoke the stored deep link rather than opening the wrong PersonalHub module.

## Entry points
Every HubContext-enabled entity kind with a suitable detail flow should be able to:
- open related Context/Explorer information;
- start the shared Composer with itself preselected;
- open the recursive Explorer rooted at itself.

Do not force every module screen to display every possible related section; the existing user show/hide/order preferences remain authoritative presentation settings.

## Data/migration/shared-infrastructure hardening
Verify the completed graph system across:
- current Room migration chain;
- canonical binding/FK integrity;
- archive/delete/tombstone/orphan behavior;
- Context edit/delete;
- Context Type persistence;
- related-section preference persistence;
- Activity/process recreation where relevant;
- import/export and auto-export generation;
- sync journal/Datasette behavior;
- duplicate prevention and distinct counts;
- no feature implementation → feature implementation dependency;
- no obvious N+1/full-graph loading regression;
- Resource URI permission/deep-link handling.

## Test strategy
Do not test every theoretical module combination. Use equivalence classes proving the generic extension point:
1. existing People + Places + Timer baseline remains correct;
2. at least one Context containing a Soldi entity kind;
3. at least one Context containing a Substances entity kind;
4. at least one Context containing a WordPulse entity kind;
5. one Context for any additional module present at execution time;
6. one Context with at least four different entity kinds;
7. one Context with multiple entities of the same kind;
8. one Workflowy deep-link Resource;
9. one SAF/document Resource where supported;
10. reverse traversal from at least three different module/entity starting points;
11. create a Context Type from the UI using an entity kind first registered in this task, with **no template-specific code**;
12. export/reimport/reopen representative graph data successfully.

Run focused module/adapter tests first, then one consolidated safe Android end-to-end pass for the completed HubContext system.

## Non-goals
- no HubContext architecture redesign;
- no visual graph canvas;
- no AI recommendation system;
- no global search;
- no unrelated new domain features;
- no aesthetic refactors;
- no replacement of semantically stronger domain relations solely for uniformity.

## Acceptance
PASS only if:
1. every currently present module with appropriate canonical user-facing entities is HubContext-enabled through the generic adapter pattern;
2. adding each adapter automatically exposes it to Composer, Context Types, Explorer and related-section configuration;
3. no pairwise integration code is needed for new combinations;
4. Resources behave as normal HubContext participants and Workflowy deep links open correctly;
5. domain-specific relationships remain semantically correct and non-duplicated;
6. graph data survives DB reopen, migration, export/import and shared sync/auto-export flows;
7. reverse recursive navigation works across newly integrated modules;
8. architecture/performance/integrity guardrails remain green;
9. the consolidated Android end-to-end flow passes.

Stop after acceptance passes.

Final output only: `PROMPT_ID`, `RESULT`, modules/entity kinds integrated, Resource support, legacy/domain-specific relationship decisions, proof of generic/no-pairwise extension, migration/data-safety checks, tests/device check, commit SHA, blocker.