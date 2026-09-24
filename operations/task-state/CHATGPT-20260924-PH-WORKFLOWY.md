# Operational task state — PersonalHub Workflowy integration

TASK_ID: CHATGPT-20260924-PH-WORKFLOWY
Updated: 2026-09-24 14:06 Europe/Copenhagen
Parent state: operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md
Global state: operations/task-state/CHATGPT-20260924-GLOBAL-RECOVERY.md

## Objective
Implement the optional low-friction PersonalHub ↔ Workflowy integration discussed with the user, reuse the existing Hub Context graph, and leave it ready for safe integration into the current PersonalHub main without colliding with other PH work.

## Constraints
- `Integra Workflowy` is the single global feature gate and is OFF by default.
- OFF hides/disables Workflowy-specific UI, linked resources, settings, Android Share target and Workflowy-days background work without deleting stored links.
- Reuse generic Hub Context resources; no provider-specific Room table or schema migration.
- Support PH → new Workflowy note, PH → existing Workflowy link, Workflowy Share → PH, and multiple Workflowy nodes per PH entity.
- API credentials stay outside PersonalHub DB/export/Git-data paths and are encrypted with Android Keystore.
- Do not touch `version.txt`, the live Pixel DB, or the primary Pixel installation.
- Do not duplicate schema-changing work owned by other PH tasks.

## Plan / checklist
- [x] Reuse existing Hub Context WEB_URL resources for Workflowy links.
- [x] Add global OFF-by-default `Integra Workflowy` feature gate in Home settings.
- [x] Hide subordinate Workflowy settings/actions/resources while the gate is OFF.
- [x] Preserve existing Workflowy relationships while OFF and restore visibility when ON.
- [x] Add encrypted Workflowy API-key storage and configurable new-node parent target; default `today`.
- [x] Add direct PH → Workflowy quick-note creation with immediate node-id/deep-link capture.
- [x] Add optional immediate open of the newly created Workflowy node.
- [x] Add compensating remote node deletion if Workflowy node creation succeeds but local PH linkage fails.
- [x] Keep manual existing-node linking available without requiring the API key.
- [x] Support multiple Workflowy links per PH entity through normal Hub Context semantics.
- [x] Route linked Workflowy nodes to the Workflowy Android app when possible, with safe generic fallback.
- [x] Add Workflowy → Android Share → PersonalHub path.
- [x] Reuse `HubContextComposerScreen` for Share→PH entity selection rather than adding a second picker.
- [x] Dynamically disable the Android Share component while integration is OFF.
- [x] Gate Workflowy-days visibility/background scheduling with the same global feature gate.
- [x] Remove the user-specific hard-coded Workflowy-days default feed URL from the settings default.
- [x] Filter Workflowy resources from generic Hub resource summaries/search/open-target behavior while OFF.
- [x] Update CODE_MAP and Workflowy/deep-link documentation.
- [x] Run consumer preflight for `HubContextComposerScreen` and the new Workflowy public symbols.
- [x] Targeted Workflowy policy/API tests PASS.
- [x] Workflowy-days feature-gate regression test PASS.
- [x] App compile path PASS through targeted app unit-test execution.
- [x] `checkArchitectureBoundaries` PASS.
- [x] Verify the branch diff does not touch Room schema files or `version.txt`.
- [ ] Reconcile `chatgpt/workflowy-integration` with the latest PersonalHub `main` when the master recovery lane returns to PH.
- [ ] Re-run only affected gates after reconciliation.
- [ ] Integrate into PersonalHub `main`, push, then delete the temporary branch.
- [ ] Update PersonalHub P0 checkpoint and global checkpoint with final merged commit evidence.

## Current step
Implementation and host verification are complete. The feature is deliberately parked before final integration so it does not race the serialized master recovery/PersonalHub lanes.

## Verified facts
- PersonalHub remote branch: `chatgpt/workflowy-integration`.
- Latest verified remote branch commit: `edd08138702f9ae6cc54c2964f109343a356a149`.
- Current comparison against PersonalHub `main` at 2026-09-24 14:06: branch is `ahead 11 / behind 2`; current `main` base commit is `57883c2531400efacbefd2c63182bc11833f9537`. Final integration therefore remains intentionally parked until the serialized PH lane resumes.
- Existing Hub Context WEB_URL resources already provide the required 0..N relation from a PersonalHub entity to Workflowy nodes.
- No new PersonalHub Room table, Room schema JSON, `PersonalHubDatabase.kt` version change, migration file or `version.txt` change is part of this flow.
- Consumer preflight found the expected app/core consumers; existing callers remain compatible because the new composer anchor is optional.
- Targeted `WorkflowyIntegrationTest` PASS after moving Android-dependent policy tests under Robolectric.
- Targeted `WorkflowyDaysTest` PASS; the app compile path also completed successfully.
- Architecture boundary gate PASS.
- Final diff audit found no newly introduced personal Workflowy feed URL; the previous hard-coded personal default is removed by this branch.

## Decisions
- The proposed temporary 3-digit matching code is not used in the primary flow.
- Direct creation is lower-friction and simpler: PH creates the Workflowy node, immediately receives its stable id, derives/stores the deep link, and can open it.
- Existing-node linking remains a first-class fallback.
- No Workflowy-specific relation table is needed; provider-specific persistence would duplicate the existing Hub Context abstraction.
- Disabling the integration means hide/suspend, not delete.
- Share→PH must reuse the canonical Hub composer/search instead of introducing another cross-module selector.

## Completed
- Full source implementation, tests, docs and routing map are remotely persisted on the PersonalHub feature branch.
- Host verification gates listed above are PASS.
- A dedicated persistent checkpoint now exists in codex-roadmap main.

## Remaining
- Final reconciliation with the then-current PersonalHub main.
- Bounded affected-gate rerun after reconciliation.
- Integration to main and temporary branch deletion.
- PH P0/global checkpoint readback after merge.

## Blockers
- No implementation blocker.
- Final merge is intentionally deferred until the serialized master recovery returns to the PersonalHub lane, so concurrent valid PH work is not overwritten or duplicated.

## Evidence
- PersonalHub branch `chatgpt/workflowy-integration`, commit `edd08138702f9ae6cc54c2964f109343a356a149`.
- Main implementation surfaces include `WorkflowyIntegration.kt`, `HubContextLinks.kt`, `WorkflowyShareActivity.kt`, `WorkflowyIntegrationSettings.kt`, Workflowy-days gating, manifest/application wiring, targeted tests, CODE_MAP and `docs/deep-links-v1.md`.
- Local gate evidence: consumer preflight PASS; targeted core Workflowy tests PASS; targeted app Workflowy-days tests/app compile PASS; architecture gate PASS.

## Acceptance criteria
- When OFF, ordinary users see no Workflowy-specific PH surface and no Workflowy background work runs, while stored links remain intact.
- When ON, users can create a Workflowy note from a PH entity, attach an existing Workflowy node, open linked nodes, and Share a Workflowy node into PH.
- Multiple nodes per PH entity work through Hub Context.
- API credential is encrypted and absent from PH DB/source/export/Git-data.
- No Room schema/version migration is introduced by this feature.
- Host tests/compile/architecture gates remain PASS after reconciliation.
- Final implementation is merged into current PersonalHub main and the temporary branch is removed.

## Next action
Keep this feature parked. When the global master lane explicitly returns to PersonalHub, fetch current `origin/main`, reconcile `chatgpt/workflowy-integration`, inspect overlaps semantically, rerun only affected gates, integrate to main, delete the branch, and checkpoint the merged commit.
