TASK_ID=C2-ROADMAP-RECONCILE-20260928

# Objective
Reconcile the full active C2 roadmap rationally: identify the canonical MegaVault project for every projectless task, partition every active task into one exclusive semantic batch, reconcile each batch before dispatch, and avoid the uncontrolled multi-worker behavior observed previously.

# Constraints
- MegaVault is authoritative for project identity; the stale C2 project registry is not.
- Inbox processing is intentionally out of scope until the user releases it.
- No new execution batch is dispatched before its semantic reconciliation is complete.
- At most one writer lane per repository; PersonalHub active work is preserved.
- Reuse existing verified work/checkpoints; do not create duplicate tasks.
- Prefer supersede/merge/close stale imported state over re-executing obsolete steps.

# Verified facts
- Active roadmap items: 275.
- Projectless active items before classification: 220; resolved against MegaVault: 220; unresolved: 0.
- Exclusive semantic batches: 47.
- C2 internal project registry is stale relative to MegaVault (notably project IDs around grindr-favorites-monitor/chatgpt-rdc-supervisor); assignments use MegaVault IDs/names.

# Project distribution
- codex-roadmap: 91
- personalhub: 56
- github-autosync: 23
- telegram_insert_bot: 11
- megavault: 10
- chatgpt-rdc-supervisor: 10
- adb-device-keeper: 9
- fedora-system-monitor: 8
- grindr-web-exporter: 7
- workflowy-importer: 6
- chrome-codex-switcher: 5
- datasette5: 5
- grindr-favorites-monitor: 4
- salute: 3
- logseq-updates: 3
- oracle-uptime-kuma: 3
- activity-watch-uploader: 3
- prompt-history: 3
- fedora-external-updater: 2
- vm_oracle: 1
- owntracks-watcher: 1
- oracle-backup-service: 1
- amici-fb: 1
- codex-usage: 1
- duplicate-photos-detector: 1
- livinggaul-x-downloader: 1
- fedora-t7-backup: 1
- windows-winget-daily-update: 1
- codex-usage-monitor: 1
- windows-flight-recorder: 1
- x-repost-downloader: 1
- fedora-diagnostics: 1

# Batch checklist
- [ ] personalhub/misc — 31 task(s)
- [ ] c2/lifecycle-scheduler — 30 task(s)
- [ ] c2/misc — 28 task(s)
- [ ] personalhub/final-p0-chain — 20 task(s)
- [ ] infra/monitoring-storage — 13 task(s)
- [ ] github-autosync/branch-cleanup — 12 task(s)
- [ ] grindr/ecosystem — 11 task(s)
- [ ] notifications/telegram — 11 task(s)
- [ ] github-autosync/misc — 10 task(s)
- [ ] android/adb-keeper — 9 task(s)
- [ ] c2/notifications-observability — 9 task(s)
- [ ] c2/git-worktree-integration — 8 task(s)
- [ ] c2/executor-rdc — 6 task(s)
- [ ] project/chrome-codex-switcher — 5 task(s)
- [ ] project/datasette5 — 5 task(s)
- [ ] megavault/authority-routing — 5 task(s)
- [ ] workflowy/sync-reliability — 5 task(s)
- [ ] c2/inbox-intake — 4 task(s)
- [ ] personalhub/ux-history-search — 4 task(s)
- [ ] megavault/database-datasette — 4 task(s)
- [ ] rdc/browser-control — 4 task(s)
- [ ] rdc/supervision-recovery — 4 task(s)
- [ ] project/salute — 3 task(s)
- [ ] project/logseq-updates — 3 task(s)
- [ ] project/activity-watch-uploader — 3 task(s)
- [ ] project/prompt-history — 3 task(s)
- [ ] c2/usage-runtime — 3 task(s)
- [ ] project/fedora-external-updater — 2 task(s)
- [ ] c2/project-capsule-identity — 2 task(s)
- [ ] project/vm_oracle — 1 task(s)
- [ ] project/owntracks-watcher — 1 task(s)
- [ ] project/oracle-backup-service — 1 task(s)
- [ ] personalhub/project-capsule — 1 task(s)
- [ ] project/amici-fb — 1 task(s)
- [ ] project/codex-usage — 1 task(s)
- [ ] project/duplicate-photos-detector — 1 task(s)
- [ ] project/livinggaul-x-downloader — 1 task(s)
- [ ] project/windows-winget-daily-update — 1 task(s)
- [ ] project/codex-usage-monitor — 1 task(s)
- [ ] project/windows-flight-recorder — 1 task(s)
- [ ] project/x-repost-downloader — 1 task(s)
- [ ] workflowy/project-capsule — 1 task(s)
- [ ] rdc/project-capsule — 1 task(s)
- [ ] c2/workflowy-dashboard — 1 task(s)
- [ ] megavault/misc — 1 task(s)
- [ ] github-autosync/reliability — 1 task(s)
- [ ] rdc/resource-stability — 1 task(s)

# Current step
Semantic reconciliation of batches. Begin with the largest/highest-impact legacy clusters and remove stale/duplicate/covered work before making anything runnable.

# Completed
- Full project attribution manifest built.
- Full exclusive batch manifest built and stored in C2-ROADMAP-BATCHES-20260928.json.

# Remaining
- Reconcile each batch semantically.
- Persist dispositions/dependencies/priorities into canonical roadmap only after each batch is internally coherent.
- Dispatch only reconciled batches under conservative repo/resource concurrency.

# Blockers
None for reconciliation. Existing active PersonalHub/Datasette work must be preserved and not duplicated.

# Acceptance criteria
- Every active work item has one canonical project attribution and one semantic batch.
- Every batch has a reviewed disposition for stale/duplicate/covered/current work.
- No unreconciled task is dispatched.
- No duplicate same-repo workers are launched.

# Next action
Reconcile personalhub/final-p0-chain and the imported PersonalHub legacy state against completed prompt evidence; collapse obsolete steps and preserve only real remaining work.
