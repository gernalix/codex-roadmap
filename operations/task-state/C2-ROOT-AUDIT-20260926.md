# C2 root audit — 2026-09-26

Scope: all 34 non-terminal root `work_items` in the canonical snapshot before Issue #1271. Evidence was checked against the named repository main or active PR, and runtime only where the task required it. PersonalHub was inspected read-only. No new C2 queue work was dispatched.

## Canonical action

- Supervisor: `245fc2d9-037a-41cb-9747-ce5b428051c0`, fencing token `6`; previous token `5` retired via Issue #1264. Local lease and canonical authority matched before mutation.
- Writer support: PR #1270 merged after CI pass (125 focused C2 tests, roadmap verify).
- Audit mutations: Issue #1271 classified 24 non-prompt roots and corrected prompt 812553 explanation; Issue #1272 put ten unconfigured intakes into waiting with explicit execution-context blockers. Both requests were preflighted on a copy of the canonical snapshot with zero foreign-key errors.
- Ten prompt roots were classified read-only; prompt text, active PH prompt and browser/device state were not changed.

## Repository and runtime matrix

The audit reused one bounded source/runtime pass for related roots:

| Source | Current evidence used | Roots |
| --- | --- | --- |
| `gernalix/codex-roadmap` main `a5873827` | PRs #1188/#1191 merged; C2 scheduler, writer, Git hook and prompt metadata checked; token 6 snapshot and receipts verified. | global recovery, 38b70, 8d17, a299, b505, f2d5, 992303, 302284 |
| `gernalix/chatgpt-rdc-supervisor` main `69b3b5cd` | Rollover, terminal-worker gate, resource lease and rate-limit source inspected; legacy PH worker left enabled. | 2e66, 3c7, 84f3, 9915 |
| `gernalix/workflowy-importer` main `9542b493` | Projection code, periodic timer and absence of writer-applied trigger / recent pending intake; live sync/readback verified. | cdab, e2dd, global recovery |
| `gernalix/PersonalHub` main `c9a574cf` | PH PR #43 integrated; prior PH chain terminal; PR #50/current prompt 669941 under external PH worker. Read-only inspection. | PH P0, PH Workflowy, a299, 669941 |
| `gernalix/fedora-system-monitor` main `a4eeebcad`; `telegram-notification-history` main `6cddc18d` | Telegram collectors/timers successful; no incident fix; future producer audit still needs real history. | Telegram archive/hygiene, memory incident, 714263 |
| `gernalix/whatsapp-exporter` main `247b227a`; `whatsapp-watcher` main inspected | Carlo-specific block tracking code/runtime and local timeline implemented; watcher handles separate read-state scope. | WhatsApp Carlo |
| `gernalix/adb-device-keeper` main `b5a2c223`, PR #2 `ff629562` | Runtime active; PR integration blocked by GitHub Actions billing/spending limit. | ADB keeper latency |
| `gernalix/MegaVault` master `6de87f1bf` | PR #108 integrated AndroidKeyStore rule; PR #107 open; canonical local checkout detached/dirty and preserved. | MegaVault 301269/c24bc, e-Boks 218695 |
| `gernalix/prompt-history` main `52a71632`; `gernalix/codex-usage-monitor` main `0a20bcf4` | ChatGPTExporter adapter exists but hardening absent; target cost source lacks successor goal cycles. | 812553, 302284 |
| `gernalix/grindr-export` main `6b77ac5d`; local `grindr-web-exporter` main `7d89974` | Export code/tests and separate auth tri-state exist; web-exporter remote absent, browser/login and routing gates remain. | 181259, 556372 |
| `gernalix/eboks-scraper` empty main, seed `13c104cf`; `gernalix/logseq_updates` main `8d0a752` | e-Boks scraper conditional on MitID export; Logseq updater code exists but old PAT revocation remains manual. | 582946, 218695, 588376 |
| `gernalix/vm_oracle` main `e5b559`; `sqlite-to-obsidian` main `04768257` | ntfy source exists without live credentials/subscriber; projector exists without confirmed live Kuma monitor. | ntfy checkpoints, 714263 |
| `activity-watch-uploader`, `chrome-codex-switcher`, `github-autosync`, `workflowy-importer`, `codex-roadmap`, `MegaVault` and `prompt-history` remote heads/branches | Active, unmerged or seed branches remain; deletion waits for terminal integration and patch-equivalence proof. | infrastructure branch cleanup |

## Non-prompt roots

| Root | Classification | Intended status | Repository/runtime evidence |
| --- | --- | --- | --- |
| `task:CHATGPT-20260924-GLOBAL-RECOVERY` | NEEDS_REWRITE | waiting | codex-roadmap main a5873827: prompt 175908 terminal; independent PH, Telegram, Grindr, ntfy and branch-cleanup roots retain residual work. |
| `task:CHATGPT-20260924-INFRA-BRANCH-CLEANUP` | CURRENT_WAITING | waiting | GitHub branch inventory 2026-09-26: codex-roadmap, MegaVault, workflowy-importer and other infrastructure repos still have active or seed branches; MegaVault PR 107 remains open. |
| `task:CHATGPT-20260924-NTFY-CHECKPOINTS` | CURRENT_WAITING | waiting | vm_oracle main e5b559 and codex-roadmap main: ntfy publisher/subscriber code and workflow exist; Fedora subscriber inactive and credential names absent on 2026-09-26. |
| `task:CHATGPT-20260924-PERSONALHUB-P0` | NEEDS_REWRITE | waiting | PersonalHub main c9a574cf and roadmap main a5873827: 707603, 840907, 788606, 913264 and 920550 terminal; separate PH prompt 669941 is running with PR 50 open. |
| `task:CHATGPT-20260924-PH-WORKFLOWY` | ALREADY_IMPLEMENTED | completed | PersonalHub main c9a574cf contains WorkflowyIntegration.kt and WorkflowyShareActivity.kt; PR 43 merged and prior prompt 920550 terminal. |
| `task:CHATGPT-20260924-TELEGRAM-AUTODELETE-ARCHIVE` | ALREADY_IMPLEMENTED | completed | fedora-system-monitor main a4eeebcad includes telegram_autodelete_archiver.py and telegram_history_collector.py; both user timers active and last services successful 2026-09-26. |
| `task:CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE` | NEEDS_REWRITE | waiting | fedora-system-monitor main a4eeebcad and telegram-notification-history main 6cddc18d: collector closure is implemented; only producer-specific audit after sufficient real history remains. |
| `task:CHATGPT-20260924-WHATSAPP-CARLO-BLOCK-TRACKING` | ALREADY_IMPLEMENTED | completed | whatsapp-exporter main 247b227a README/code implement Carlo-only block events, peer inference and local timeline; whatsapp-exporter/browser user services active on 2026-09-26. |
| `task:CHATGPT-20260925-ADB-KEEPER-LATENCY` | CURRENT_WAITING | waiting | adb-device-keeper PR 2 head ff629562 is open; GitHub Actions deterministic test cannot start due billing/spending-limit, while local adb-device-keeper service is active. |
| `wi:2e66af047c194439a8d0fbacaa937052` | CURRENT_WAITING | waiting | chatgpt-rdc-supervisor main 69b3b5cd supervisor.py rollover path still marks human-required when no persisted conversation URL. |
| `wi:38b70e5910464b40bbd52e080fb83abb` | ALREADY_IMPLEMENTED | completed | codex-roadmap main a5873827 includes PR 1191: c2_intake invokes structured configure_auto and c2_scheduler does not infer from title/prose. |
| `wi:3c7c9af3af3141b28b44f6d0016e41a4` | CURRENT_WAITING | waiting | chatgpt-rdc-supervisor main 69b3b5cd disables terminal workers only after browser COMPLETE; canonical terminal/lane gate absent. |
| `wi:84f3e2c4cc5b42b78db679d1eb02739f` | CURRENT_WAITING | waiting | chatgpt-rdc-supervisor main 69b3b5cd has no cross-chat worktree lease; C2 scheduler resource leases do not fence legacy RDC writers. |
| `wi:8d17c74314c84e6eb267f81143360b3e` | ALREADY_IMPLEMENTED | completed | codex-roadmap main a5873827 includes PR 1188: work_items_state_import._remaining_items filters terminal None-for/no-work-remains prose with tests. |
| `wi:991539d322764f218d8d584fcb8fccba` | CURRENT_WAITING | waiting | chatgpt-rdc-supervisor main 69b3b5cd storage.py persists global backoff and supervisor.py applies it to all active workers. |
| `wi:a299a4c1a72049b88f594587dc786768` | CURRENT_WAITING | waiting | codex-roadmap main a5873827 lacks structured ADB test metrics/ingest/query; PersonalHub main c9a574cf contains PersonalHubShortcutBenchmarks.kt. |
| `wi:b505b3ee6c0e439cba2fcc107395acf2` | CURRENT_WAITING | waiting | codex-roadmap main a5873827 submit_mutation.py detects request_key_conflict but c2_control.py still requires caller-generated keys without cross-chat namespace. |
| `wi:cdab43b2b6b64a5f9f118deb4d34d85e` | CURRENT_WAITING | waiting | workflowy-importer main 9542b493 uses periodic workflowy-roadmap-sync.timer; no writer-applied immediate projection trigger. |
| `wi:e2123dbf7f374c8ab01ea5af86850a02` | DUPLICATE_MERGE | superseded | fedora-system-monitor main a4eeebcad telemetry is already named in primary C2 incident objective wi:ff254f4139444dc8909c96324bb9a588; no separate fix lane needed. |
| `wi:e2dd3666c60c42298e63272af94df6bd` | CURRENT_WAITING | waiting | workflowy-importer main 9542b493 work_items_projection.py recent view includes completed only; pending intake stays collapsed. |
| `wi:f2d5d81a952b47b1bd4fa4c07d175265` | CURRENT_WAITING | waiting | codex-roadmap main a5873827 .githooks/reference-transaction still emits guarded-main/pack-refs failure on branch commit; reproduced during C2 branch merge/commit. |
| `wi:ff254f4139444dc8909c96324bb9a588` | CURRENT_WAITING | waiting | Fedora 2026-09-25/26 memory incident has no source fix in fedora-system-monitor main a4eeebcad; supporting telemetry intake merged into this primary task. |
| `wi:3012695ec46c4c3a8250c213be845783` | DUPLICATE_MERGE | superseded | MegaVault main 6de87f1bf contains merged AndroidKeyStore rule PR 108; local checkout remains detached/dirty; wi:c24bc183ffdc4e648d77190f2bf5d651 covers recovery plus collision guard. |
| `wi:c24bc183ffdc4e648d77190f2bf5d651` | NEEDS_REWRITE | waiting | MegaVault main 6de87f1bf has AndroidKeyStore rule via PR 108; local /home/daniele/MegaVault remains detached/dirty with pre-existing changes, and PR 107 is open. |

## Prompt roots (read-only lifecycle classification)

| PROMPT_ID | Classification | Evidence and gate |
| --- | --- | --- |
| `669941` | CURRENT_WAITING | PersonalHub main c9a574cf; PH PR 50 is open and roadmap prompt is running under the PH worker. C2 does not execute or mutate it. |
| `992303` | CURRENT_READY | codex-roadmap main a5873827 has current C2 run/worker metadata but no durable executor/chat handoff history or Workflowy projection. |
| `812553` | CURRENT_READY | prompt-history main 52a71632 has ChatGPTExporter adapter; no retry/failure/health hardening. gernalix/ChatGPTExporter remote is absent; 222733 completed; stale 302284 wait corrected by Issue 1271. |
| `181259` | CURRENT_WAITING | grindr-web-exporter local main 7d89974 has auth tri-state; gernalix/grindr-web-exporter remote is absent, and manual login/browser state is unresolved. |
| `556372` | CURRENT_WAITING | grindr-export main 6b77ac5d has exporter/tests, but local checkout and MegaVault registration are absent; retain separate browser/session gate from 181259. |
| `582946` | CURRENT_WAITING | e-Boks export still requires manual MitID authentication; preserve existing browser/session and progress rather than automating login. |
| `218695` | CURRENT_WAITING | gernalix/eboks-scraper public repository exists but main is empty; seed branch 13c104cf exists. Need result of 582946 before deciding whether scraper is necessary. |
| `588376` | CURRENT_WAITING | logseq_updates main 8d0a752 has updater code; user timer inactive; old PAT revocation remains manual prerequisite. |
| `302284` | CURRENT_WAITING | codex-roadmap target-session archive lacks successor goal cycles required for cost regeneration; preserve blocked checkpoint. |
| `714263` | CURRENT_WAITING | sqlite-to-obsidian main 04768257 includes projector; no corresponding live Kuma monitor in MegaVault monitor inventory; preserve blocked residual. |

## Queue decision

C2 code intakes with current source evidence are ordered by control-plane risk and marked waiting because no prompt, exact model/reasoning and isolated worktree execution context is registered. The human/RDC memory incident is waiting for its dedicated investigation. No `work_item_execution_specs` were guessed from prose. Waiting task-state roots have explicit blockers and are not C2-dispatchable. Prompt 669941 is running under the separate PersonalHub worker. The imported global recovery and PH P0 trees retain their pending descendants because their broad acceptance has not been proven; do not treat those prose descendants as fresh runnable work.

## Obstacles captured during the audit

Existing C2 intakes already cover the branch `reference-transaction`/`pack-refs` warning (`f2d5`), writer-to-Workflowy projection delay (`cdab`), and missing recent-intake visibility (`e2dd`); they were reconciled rather than duplicated. Three distinct residual weaknesses were submitted through the single writer as Issue #1273. Issue #1274 added explicit waiting blockers rather than leaving them falsely pending without specs:

1. `wi:b45503242af34c10ba32832d0645dbc6`: imported global recovery and PH P0 trees retain stale pending descendants even though the corresponding prompt chain is terminal; the current root-only reconciliation cannot close selected children safely while preserving the still-open root.
2. `wi:0fa0c1ccfc3d4d269d28225ee81161bc`: prompt 218695 still routes to `/home/daniele/MegaVault`; the conditional public `eboks-scraper` repo now exists, but there is no fenced pending-prompt repo-routing mutation. The task must remain behind MitID and the post-export need decision.
3. `wi:68ff0f7e2f00474094fb6dc54a4a9b05`: ten verified C2 intakes need separate prompt/materialization, exact metadata and isolated worktree preparation before `configure_auto` can make a safe spec. The preparatory path should be idempotent and separate from dispatch.

Next: verify the Issue #1273 followups and their waiting blockers, refresh roadmap integrity and Workflowy readback, then push the final checkpoint without dispatching a queue item.
