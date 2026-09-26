# CHATGPT-20260926-PH-ALERTS-UNIFIED

## Objective
Unify PersonalHub alert management in one Home-level Alerts surface covering Timer and Places; preserve domain-specific semantics/storage while eliminating duplicate CRUD UI. Make Places alert creation/editing explicit and discoverable.

## Constraints
- Work only in isolated PersonalHub worktree `/home/daniele/.local/share/chatgpt-ph-alerts-unified`.
- Base: `origin/main@d7501af46e96e32da56431d6e7f6e53939038f70`.
- Do not touch other PH worktrees/devices.
- Keep Timer persistence compatibility; no database migration solely for UI unification.
- Respect feature boundaries: app may consume only explicit feature api/hub surfaces.
- No version bump/final APK release in this task unless needed only for targeted QA.
- C2 observation captured as issue #1329.

## Plan / checklist
- [x] Verify current Timer/Places alert UIs and Home architecture.
- [x] Create isolated PH and task-state worktrees.
- [ ] Define shared alert management contract/model in the existing alerts core.
- [ ] Add Timer adapter/API for list/create/update/delete/enable and tag lookup.
- [ ] Add Places adapter/API for list/create/update/delete/enable plus place/tag lookup.
- [ ] Implement one Home Alerts screen with unified list/filter and shared editor.
- [ ] Add Home Alerts tile and navigation.
- [ ] Make legacy Timer/Places alert entry points route to the unified surface or remain thin compatibility entry points without duplicated CRUD UI.
- [ ] Add/update focused tests.
- [ ] Run consumer preflight before Gradle for changed public APIs.
- [ ] Run compile/unit/architecture gates.
- [ ] Perform focused UI QA if a safe emulator/device path is available without interfering with active PH workers.
- [ ] Commit + push PersonalHub branch.
- [ ] Update this state with evidence and terminal result; commit + push.

## Current step
Inspect Timer and Places alert persistence/controller APIs and determine the minimal shared adapter boundary.

## Verified facts
- Places engine already supports exact-place or tag-set targets with ALL/ANY and check-in/check-out/both.
- Pixel v63 exposes Alerts in place detail; the dialog has This place / Places tags. Add/update lives inside scroll content while footer only has Close.
- Timer already has a full Alerts screen with list, add/edit/delete, enable/disable, trash, Save/Cancel.
- Home supports non-module action tiles such as Tags, Audit, Since when, Data and Settings.
- Existing non-main PH worktrees are clean; one shared-final branch has an alert-notification-tap change but no unified alert management UI.
- C2 supervisor lease observed expired; no repository helper named executor_started is currently available on canonical codex-roadmap.

## Decisions
- Use a single host-level UI backed by domain adapters; do not force Timer storage migration.
- Keep trigger/target semantics domain-specific but normalize presentation and CRUD.
- Avoid importing feature-private implementation packages into app.

## Completed
Initial architecture/UI verification; isolated worktrees created.

## Remaining
Implementation, tests, QA, commit/push, final C2/state update.

## Blockers
None for implementation. C2 executor_started helper is absent from current canonical tooling; do not mutate supervisor authority solely for this PH task.

## Evidence
- C2 issue #1329 captures the duplicate/inconsistent alert-management problem.
- PersonalHub isolated branch: `chatgpt/unified-alerts-home`.

## Acceptance criteria
- Home has a dedicated Alerts tile.
- Unified Alerts screen lists both Timer and Places rules and clearly labels domain.
- User can add/edit/enable-disable/delete both kinds from that screen.
- Places can target one place or one/many Places tags with ALL/ANY and check-in/out/both.
- Timer retains existing trigger/tag/cooldown/random semantics.
- No duplicate full CRUD UI remains in Timer/Places; legacy entry points are thin redirects/compatibility.
- Focused tests + compile + architecture boundary checks pass.

## Next action
Read Timer AlertsCapsuleViewModel/model APIs and Places alert repository/container wiring; design the minimal shared adapter API before editing.
