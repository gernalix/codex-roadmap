# Operational task state — PersonalHub Workflowy integration

TASK_ID: CHATGPT-20260924-PH-WORKFLOWY
Updated: 2026-09-24 13:04 Europe/Copenhagen
Parent state: operations/task-state/CHATGPT-20260924-PERSONALHUB-P0.md

## Objective
Implement the optional low-friction PersonalHub ↔ Workflowy integration without colliding with running schema-changing task 920550.

## Constraints
- `Integra Workflowy` is the single global feature gate, OFF by default.
- OFF hides/disables Workflowy UI, share target and background work without deleting stored links.
- Reuse Hub Context generic resources; no provider-specific Room tables or schema change.
- Support PH→new Workflowy note, PH→existing Workflowy link, Workflowy Share→PH, and multiple nodes per PH entity.
- API credentials stay outside the PersonalHub DB/export path and are encrypted with Android Keystore.
- Do not touch version.txt, the live Pixel DB, or the primary Pixel installation.

## Verified facts
- Existing Hub Context WEB_URL resources already support multiple Workflowy links per entity.
- Workflowy-days can be feature-gated without a Room migration.
- Official create-node API supports parent_id `today`, requires name, and returns item_id.
- Remote implementation checkpoint exists on `chatgpt/workflowy-integration` through `ee538e9`.
- No Room schema/version file has changed in this task.

## Decisions
- The proposed 3-digit handshake is not part of the primary flow.
- Direct creation stores the returned node deep link immediately.
- Existing-node linking works without an API key.
- Share→PH reuses HubContextComposerScreen.
- Share component is package-manager disabled while the feature gate is OFF.

## Checklist
- [x] Global feature gate + encrypted API settings.
- [x] Workflowy API client and URL policy.
- [x] Direct quick note + optional open.
- [x] Existing-node linking and multiple links via Hub Context.
- [x] Hide Workflowy links/actions while OFF.
- [x] Home checkbox and subordinate settings gating.
- [x] Workflowy-days background gating.
- [x] Android Share→PH via shared composer.
- [x] Targeted tests added; docs and CODE_MAP updated.
- [ ] Consumer preflight for changed HubContextComposerScreen API.
- [ ] Targeted unit tests + app compile + architecture gate.
- [ ] Fix only concrete failures and rerun affected gates.
- [ ] Final diff/schema/version/user-visible-value audit.
- [ ] Reconcile with latest main, integrate, push, delete branch.
- [ ] Update PH P0 checkpoint with final evidence.

## Completed
- Source implementation is remotely persisted on `chatgpt/workflowy-integration`.

## Remaining
- Verification, any leaf fixes, final integration/cleanup, final checkpoint.

## Blockers
- None. Concurrent 920550 may advance main; final integration must refresh first.

## Evidence
- PersonalHub remote branch `chatgpt/workflowy-integration` and implementation/test/docs files recorded in Git.

## Acceptance criteria
- OFF is invisible/non-running and preserves links; ON exposes all agreed Workflowy flows.
- Credential is encrypted and absent from DB/source/export.
- No Room schema or app version change.
- Targeted tests, app compile and architecture gate PASS.
- Result lands on current main without losing concurrent valid work.

## Next action
Run android_consumer_preflight for HubContextComposerScreen, then the smallest targeted Gradle tests/compile/architecture gates.