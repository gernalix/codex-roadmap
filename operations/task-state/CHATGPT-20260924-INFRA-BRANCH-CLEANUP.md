# Operational task state — infrastructure branch cleanup

TASK_ID: CHATGPT-20260924-INFRA-BRANCH-CLEANUP
Updated: 2026-09-24
Parent: operations/task-state/CHATGPT-20260924-GLOBAL-RECOVERY.md

## Objective
Leave the infrastructure repositories with only branches that still contain genuinely unintegrated work. Delete branches only after proving their commits are already contained or patch-equivalent to the canonical branch.

## Constraints
- Operational memory only; not roadmap lifecycle state.
- No chain-of-thought.
- Canonical branches: main for all listed repos except MegaVault=master.
- ahead_by=0 is sufficient evidence that a branch is safe to delete.
- ahead_by>0 requires git cherry/patch-id plus bounded semantic review.
- Never delete a running/integration branch.
- Keep seed/eboks-scraper-20260921 until 218695 is executed or cancelled with evidence.

## Plan / checklist
### Phase 1 — Inventory and safe ancestry classification
- [x] Enumerate remote branches across the eight infrastructure repositories.
- [x] Compare every non-canonical branch against current main/master.
- [x] Mark the 25 branches with `ahead_by=0` as ancestry-safe candidates.
- [x] Preserve every `ahead_by>0` branch for patch-equivalence/semantic review.
- [x] Protect active/integration branches and the conditional e-Boks seed branch.

### Phase 2 — Patch-equivalence review
- [ ] Wait until active infrastructure tasks are terminal.
- [ ] Fetch all refs locally once and run bounded `git cherry` / patch-id review on every `ahead_by>0` candidate.
- [ ] Integrate any genuinely unique useful commit before considering its branch deletable.
- [ ] Record explicit keep/delete disposition for every review branch.

### Phase 3 — Deletion and readback
- [ ] Delete ancestry-safe and proven-equivalent branches with authenticated local/GitHub tooling.
- [ ] Re-read all remote branch lists.
- [ ] Retain only canonical branches plus explicitly justified active/seed branches.
- [ ] Update this checkpoint with final evidence and close the cleanup lane.

## Current step
Wait for active infrastructure tasks to become terminal; then perform the single bounded local patch-equivalence/deletion pass. Do not delete active/integration branches early.

## Verified safe-to-delete branches (ahead=0)

### gernalix/activity-watch-uploader
- task/620949

### gernalix/codex-usage-monitor
- task/credential-provider-20260920

### gernalix/chrome-codex-switcher
- architecture/prompt-cockpit-proxy
- task/472615

### gernalix/workflowy-importer
- architecture/cockpit-migration-polish
- architecture/roadmap-cockpit
- task/credential-provider-20260920
- task/947306

### gernalix/github-autosync
- architecture/async-integrator-v2
- architecture/cockpit-state-polish
- architecture/prompt-cockpit-contract
- task/async-roadmap-finalize
- task/systemd-credential-provider-20260920
- task/246815
- task/246816
- task/246817
- task/246818
- task/814263

### gernalix/codex-roadmap
- architecture/async-integrator-v2
- architecture/workflowy-cockpit-backend
- chatgpt/running-first-roadmap-view
- task/async-roadmap-finish-handoff-v2
- task/wf-ready-463281

### gernalix/MegaVault
- task/credential-provider-policy-20260920
- task/613102

### gernalix/prompt-history
- none proven safe by ancestry

Total ancestry-safe branches: 25.

## Branches requiring patch-equivalence / semantic review

### gernalix/activity-watch-uploader
- chatgpt/libsecret-kuma

### gernalix/prompt-history
- task/571364

### gernalix/codex-usage-monitor
- analysis/404936-efficiency-hardening

### gernalix/chrome-codex-switcher
- architecture/prompt-cockpit-bindings
- chatgpt/systemd-resilience-20260921
- codex/fix-prompt-pairing
- feature/active-codex-notes
- feature/autonomous-runtime-verifier
- feature/autonomous-runtime-verifier-v2
- feature/context-search-dashboard
- feature/persist-full-note-state
- feature/url-persistent-notes
- fix/content-script-runtime-errors
- fix/gnome-clipboard-bridge-519564
- fix/preserve-flatpak-extension-path
- fix/workflowy-dashboard-reliability
- hardening/593872-gnome-heartbeat
- task/438216
- task/485236
- task/604812
- task/731805
- task/764382
- test/e2e-note-state-persistence

### gernalix/workflowy-importer
- chatgpt/global-python-systemd-resilience-20260921
- feature/ccs-runtime-verify-link
- feature/runtime-auto-deploy
- feature/workflowy-pbf-statuses
- fix/workflowy-blocked-projection
- fix/workflowy-dashboard-dedupe-20260920
- fix/workflowy-dashboard-reliability
- task/381904
- task/438217
- task/764381
- task/930174

### gernalix/github-autosync
- analysis/404936-efficiency-hardening
- chatgpt/libsecret-kuma
- feature/activity-audit-telegram-20260918
- feature/global-reconcile-command
- feature/per-repo-single-writer
- feature/private-activity-data-mirror-20260918
- feature/runtime-auto-deploy
- feature/single-writer-leases-cleanup
- fix/autonomous-roadmap-reconcile
- fix/global-reconcile-stale-upstream
- fix/single-writer-noop-task

### gernalix/codex-roadmap
- chatgpt/manual-prereq-runnable-fix-20260920
- codex/retry-rejected-terminal-request
- feature/repo-task-single-writer-bridge
- fix/roadmap-claim-gh-404-v2
- fix/roadmap-claim-gh-404
- fix/roadmap-start-canonical-repository
- seed/eboks-scraper-20260921
- task/async-roadmap-finish-handoff

### gernalix/MegaVault
- chatgpt/systemd-service-resilience-20260921
- chatgpt-805417-boundary-refactor
- policy/per-repo-single-writer
- task/prompt-id-943492-materialize-command
- task/prompt-id-fw123-pr-trigger2
- task/prompt-id-fw123-trigger
- task/prompt-id-fw123-trigger-v2
- task/prompt-id-issue-bridge-fix
- task/prompt-id-luks-recovery-followup-943492

## Completed
- Enumerated all remote branches in the eight infrastructure repositories.
- Compared every non-canonical branch against current main/master.
- Identified 25 branches with ahead_by=0.
- Preserved every branch with ahead_by>0 for later review.

## Remaining
- After active tasks finish, fetch all refs locally and run git cherry / patch-id checks on every review branch.
- Integrate genuinely unique useful commits before deletion.
- Delete ancestry-safe and subsequently proven-equivalent branches with authenticated local/GitHub tooling.
- Re-read remote branches and retain only canonical plus intentionally active/seed branches.

## Blockers
- The current ChatGPT GitHub connector can compare branches but exposes no branch-delete action.
- ahead_by>0 can still be squash/cherry-pick equivalent; ancestry alone is insufficient.

## Acceptance criteria
- No branch with unreviewed unique work is deleted.
- Every deleted branch is ahead_by=0 or proven equivalent/absorbed.
- No active task branch is deleted.
- Each repo ends with only canonical and explicitly justified retained branches.

## Next action
After active infrastructure tasks are terminal, execute one bounded local cleanup pass using this inventory, update patch-equivalence results, then delete only proven-safe branches.
