TASK_ID=C2-AUTODRAIN-20260927
PROMPT_ID=660629
C2_RECOVERY_STATE={"previous_supervisor_id":"8eb05a5e-b928-44b6-bd69-6e60b9912c1a","previous_fencing_token":21,"active_runs":["22bbc9a625bc443a89e6d2f6424a9074","b2744c52472c42718af5a73d4f27ecd1"],"active_executors":["codex://threads/01a0e173-23e2-76d0-b9d5-d520ad172f0c","codex://threads/01a0e297-19c1-7c80-aa9e-dfa9b2215c43","codex://threads/01a0e297-e543-7242-8ec7-41a89d41c59e"],"preserve_resources":["repo:gernalix/PersonalHub","worktree:/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_PersonalHub/436865","repo:gernalix/telegram_insert_bot","worktree:/home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_telegram_insert_bot/377172"],"blocker":null}

# Objective
Continue C2 autonomously until quiescence. NEW USER STEER: in the successor chat, PROCESS THE C2 INBOX FIRST because it contains urgent issues. After actionable Inbox is drained/reconciled, resume highest-priority roadmap work and parallelize maximally where locks/dependencies permit, including Codex CLI.

# Supervisor handoff
- Current supervisor before handoff: a920f0c2-c0f9-411b-8656-0f65cd833689
- fencing_token: 20
- This authority is being intentionally retired for chat handoff.
- Successor MUST acquire a NEW unique supervisor_id by omitting --supervisor-id and obtain fencing token >20 before fenced mutation/scheduling.
- Do not request the prior transcript.

# Inbox — FIRST ACTION IN SUCCESSOR CHAT
Canonical pending rows at handoff:
1. issue:bfcfdb13f8b647c3b667dbc7af832b30 — Linux periodic-service registry + automatic Kuma monitors. EXPLICIT USER CONSTRAINT: Inbox-only; do NOT promote/schedule/start until explicit user release.
2. issue:b6bc31c985fa48beaf53c2826a28789b — protocol P0: define “esegui C2” = process entire Inbox + entire roadmap, maximize parallelism, freely use Codex CLI until quiescence.
3. issue:a945951b39da4d04a54381b9571279d5 — github-autosync regression tests invoke real bootstrap/systemd without mocking and fail with systemd runtime coupling.
Process/reconcile #2 and #3 before resuming ordinary roadmap work; preserve #1 pending.

# Canonical state
- PROMPT_ID 999198 completed.
- Phase A MegaVault PROMPT_ID=853479 is now canonical COMPLETED.
- Its run ca41243058a34906a088c21c271dba56 is still marked recovering even though terminal was confirmed; reconcile the run after the urgent Inbox pass.
- MegaVault P0 umbrella: wi:68cd5b09eae24fe59352bd0750a559c1.
  - A wi:c615636f22314b2c89c3a8b037d2d6cc / PROMPT_ID=853479 — completed.
  - B wi:9b77740b71c44e728490cf1f96415a6d — next dependency-unblocked phase.
  - C wi:c0d99c19998740e2b386bb2bf54ae106.
  - D wi:6a187c7e94be40daba8dce5678ba64f6.
  - E wi:9116862e72024e89b0033b4c6eeb146c.
  - final gate wi:e20d87af9a6641c385b03b40aa72ab8a.
- Legacy overlapping MegaVault roots c24bc..., 05f8..., 6d4b... were superseded by the umbrella.
- C2 repo-lock defect: wi:09c58fd538c3440a9e44d2414ddea29f (P0).
- C2 ACK renewal idempotency defect is promoted as P0 work item (query by title: “Rendere idempotente ACK C2 attraverso rinnovi di supervisor authority”).
- C2 promote_issue contract + mandatory queue reprioritization/dependency re-evaluation were captured as P0 Inbox items and submitted for promotion shortly before handoff; verify their canonical state during Inbox pass.

# Parallel Codex CLI lanes prepared but NOT launched
These were roadmap_start-claimed and are status=running, but no Codex CLI thread/process was launched by this chat:
- PROMPT_ID=625582 — wi:cc78ff4dcaf942f998d821fb48826d23 — Grindr photo/profile_id + Nautilus/Datasette UX.
  Worktree: /home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_grindr-favorites-monitor/625582
  model/reasoning/MegaVault: GPT-5.6 Terra / medium / FAST.
- PROMPT_ID=545953 — wi:8bbbddd5318f44ee89decb25f910b87c6 — telegram_insert_bot Grindr historical diff regression.
  Worktree: /home/daniele/.local/share/codex-github-autosync/worktrees/gernalix_telegram_insert_bot/545953
  model/reasoning/MegaVault: GPT-5.6 Terra / medium / FAST.
Do NOT call roadmap_start again. After Inbox priority work, launch each exactly once via Codex CLI if repo ownership is still safe; then bind/record executor identity and supervise through terminal/integration.

# Runtime/control-plane facts
- Runtime worktree ~/.local/share/c2-supervisor/worktree was safely realigned to main and c2_worktree_guard reported healthy.
- The prior runtime dirty/drift incident was captured to Inbox and attached to the global dirty-worktree remediation item.
- c2_runtime ACK replay can conflict after supervisor renewal because request key omits changing authority payload; incident captured and promoted as P0.
- Long-running macrogoal 660629 consumes same-repo lock despite no worker/spec; defect promoted as P0. Do not weaken same-repo safety for real workers.

# Durable evidence
- Phase A thread: codex://threads/01a0e264-8472-7573-b67c-f8650a78b701.
- Phase A run: ca41243058a34906a088c21c271dba56.
- Phase A terminal confirmed by roadmap_pull; work item status completed.
- Recovery branch for this file: chatgpt/c2-autodrain-20260927.

# Exact next action
1. Acquire new local supervisor lease with NEW supervisor_id and token >20 using this file as recovery pointer; claim canonical authority.
2. Pull canonical roadmap.
3. PRIORITIZE INBOX: triage/process all actionable pending rows; preserve the Kuma row as Inbox-only.
4. Re-read Inbox before leaving triage; recompute priorities and dependencies after every promotion.
5. Reconcile terminal Phase A run ca41243058a34906a088c21c271dba56.
6. Resume/launch the already-claimed 625582 and 545953 lanes exactly once via Codex CLI when safe, while also starting independent eligible leaves up to resource/repo constraints.
7. Continue MegaVault Phase B→C→D→E→gate and remaining roadmap work, returning to Inbox/reconcile between transitions.
8. Stop only at quiescence; user-deferred Inbox rows do not count as actionable until released.


# FINAL HANDOFF DELTA — authoritative over earlier Inbox section
- Canonical supervisor authority token 20 has been retired; local lease state is retired. Successor can acquire token 21 immediately.
- Actionable Inbox was processed before handoff. Canonical pending Inbox now contains ONLY issue:bfcfdb13f8b647c3b667dbc7af832b30 (Kuma/service registry), still explicitly Inbox-only/deferred.
- Urgent Inbox-derived work is now canonical:
  - wi:8eb0f2e8ed2c46349114896c9007a46d — “Definire il comando canonico «esegui C2»” — pending, P0, codex-roadmap. PRIORITIZE FIRST.
  - wi:853f2846c06d406bb19cf53e20afec5c — “Isolare il bootstrap systemd nei regression test github-autosync” — pending. PRIORITIZE immediately after/parallel where safe.
- Phase A 853479 is completed canonically.
- PROMPT_ID=625582 and PROMPT_ID=545953 are status=running from roadmap_start, but this chat did NOT launch Codex CLI processes/sessions for them. Do not roadmap_start again; after the two urgent Inbox-derived items, launch/bind each exactly once if still safe.
- User’s latest steer: in the successor chat, prioritize Inbox-derived urgent work before ordinary roadmap continuation, then maximize parallelism using Codex CLI wherever repo/resource/dependency constraints allow.


# CHECKPOINT 2026-09-27 — USER PRIORITY #2330
- User ordered: save current work, then give ABSOLUTE PRIORITY to GitHub issue #2330 until completion; after #2330 resume the prior drain from this checkpoint.
- Canonical supervisor currently active locally as supervisor_id=28ae628c-081f-4128-add9-277e45aafc3b, fencing_token=22. Preserve its authority/lease and do not create a duplicate supervisor while active.
- #2330 is capture issue issue:e21c3528a43a4c539c4c23a1c3525e89 in gernalix/workflowy-importer. Goal: fix live C2 Workflowy dashboard Inbox/Roadmap freshness, compact Inbox rendering, idempotent Reset to AI order, stale-node cleanup, stable continuous sync; acceptance is defined in GitHub issue #2330.
- Workflowy baseline already merged before this steer: PR #29 (manual-order projection) and PR #30 (deploy .path fix). Current #2330 is a follow-up correctness/freshness P0 and must supersede ordinary drain work.
- Current non-#2330 work to preserve and resume AFTER #2330:
  - wi:7d582a5bab484b7b8a9fc559b6bdfcbd (MegaVault capsule inventory/tooling): Codex completed, commit 2907daa7fd53a881b0074da8125c27e2a2f8ff64 pushed on task/wi-7d582a5bab484b7b8a9fc559b6bdfcbd; 85 tests PASS, MegaVault validate PASS, SQLite integrity/FK PASS. Worktree is ahead by 1 and awaits integration/terminalization. Inventory result: 36 eligible, 72 excluded; artifact_missing=31, repository_unavailable=5.
  - wi:72083276ee994f5b97113da073005ad3 (Fedora Python/SQLite journald history): active Codex thread codex://threads/01a0e2fc-a4e8-7f52-924b-3a47cd819798, process pid 4028185 when checkpointed; worktree has active uncommitted implementation changes. Do not duplicate/restart this thread; supervise/resume it after #2330.
  - wi:2f02116ccfaf4454b1872d7c636a9c99 (C2 capture-only frictionless path): executor_started mutation #2333 was applied successfully after scheduler fix; no Codex worker had been launched yet at checkpoint. Start only after #2330.
  - wi:d6185f8fb88d466f907814bf6125890e (Project Capsule standard) pending; wi:344346f8ef8446cabac86d947fde9c64 (Capsule Score) depends on it; resume after #2330.
  - wi:7ee12d74262b498f892f51de128e041b PersonalHub remains pending behind existing PersonalHub worker; preserve PH worker/device.
- Scheduler monopoly bug was fixed and merged via PR #2324, merge ef911a6697f16bb42f9f49804248a6b835085749. issue:5575650c19224036a171af15d95b6cf8 was absorbed/resolved.
- Fedora Bash journald collector wi:593ca7211d154268aa839cb1b0d7e697 merged as PR #17; dependency for Python/SQLite collector is satisfied.
- Inbox was drained to zero before issue:557... appeared; #2330 now has absolute priority. Re-read Inbox after #2330 because new rows may accumulate while it runs.

## Exact next action (OVERRIDES all earlier Next action until #2330 completes)
1. Resolve/promote/find the canonical work item for issue:e21c3528a43a4c539c4c23a1c3525e89 / GitHub issue #2330.
2. Execute #2330 to completion in gernalix/workflowy-importer, using Codex CLI and live Workflowy/systemd verification as needed. Do not consider it complete until live dashboard Inbox matches canonical pending count, compact rendering is verified, Roadmap is visible/fresh, reset is repeatable/idempotent, sync service is stable, and regression tests pass.
3. Notify the user clearly when #2330 is completed/live.
4. Resume exactly the preserved work above: integrate/terminalize MegaVault capsule tooling, continue the existing Fedora journald Python/SQLite thread, then launch capture-path and continue capsule standard/score and remaining roadmap/Inbox until quiescence.


# HANDOFF CHECKPOINT — #2330 LIVE E2E — 2026-09-27 16:28 CEST
- User requested continuation in a NEW ChatGPT chat now. Stop this chat after successor is launched.
- Keep absolute priority on GitHub issue #2330 / issue:e21c3528a43a4c539c4c23a1c3525e89 / work item wi:214f6cf5571d426dba2373960a6bfdf1 until full live E2E acceptance passes.
- Active supervisor identity at handoff: supervisor_id=fd368caf-8d31-42a5-979e-b67fae4484b5, fencing_token=25. This is a session handoff, NOT a supervisor takeover: successor should reuse this active authority from ~/.config/c2-supervisor/runtime.env if still valid/canonical; do not mint a competing supervisor token while 25 is live.
- Canonical/local token25 were renewed with long lease and monotonic-lease fix; canonical expiry was extended to ~16:48 CEST during this turn.
- Merged fixes for #2330:
  - workflowy-importer PR #31 merged; live UI/freshness/compact rendering/reset lifecycle fixes.
  - codex-roadmap PR #2360 merged; reset-event idempotency and stable authority payload.
  - codex-roadmap PR #2369 merged; same-generation activity/heartbeat no longer shortens an already-longer supervisor lease.
- Runtime deployment completed:
  - workflowy-roadmap-sync.service runs successfully.
  - c2_workflowy_order.py, c2_control.py and c2_supervisor_lease.py runtime copies updated to merged versions without touching roadmap.sqlite.
- LIVE E2E gates already proven on real dashboard https://workflowy.com/#/98c00c618b80:
  - Root visibly reached ✅ “Proiezione Workflowy allineata alla roadmap canonica.”
  - Inbox real projection visible, compact titles + repo/executor tags + collapsed Dettagli; no normal-view C2_ISSUE_ID/URL.
  - Roadmap populated/navigable with 1209 canonical work items in Ready/Blocked/Paused/Running/Waiting/Done/Archive groups.
  - Inbox manual reorder was real and persisted canonically: AI order had issue:c74bea... before issue:68ac..., manual override reversed them; survived sync + hard refresh.
  - Roadmap manual reorder was real and persisted canonically: hotfix wi:296cf... rank 40 before #2330 wi:214f... rank 41 even though AI sort_order puts #2330 first; survived sync + hard refresh.
  - Reset mutations were applied by canonical single writer: #2380 roadmap clear, #2381 inbox clear.
  - After reset, manual_order_overrides were cleared; visible AI order restored in both Inbox and Running.
  - After reset, fresh Reset to AI order nodes were recreated, new node IDs, unchecked in both Inbox and Roadmap.
  - Retry/sync stability after monotonic-lease fix: three consecutive manual starts succeeded, no request_key_conflict/stale_or_expired errors. Latest two/three runs had mutations_submitted=0; service Result=success ExecMainStatus=0.
- Important current dashboard/canonical state is changing because the C2 retrospective continues creating new Inbox issues. At latest sync the dashboard reported issues=21. Therefore equality gate must compare LIVE UI against a fresh canonical clone/readback at the same verification point, not older count 14/19/20.
- Remaining mandatory #2330 gates before PASS:
  1. Fresh exact equality check: live Inbox visible set == canonical pending issue_inbox set, no stale/missing rows, using current count/state.
  2. Verify current live Roadmap remains populated/navigable after latest sync.
  3. Verify no visible technical IDs/URLs in normal Inbox cards; long-description cards remain compact/collapsed.
  4. Real canonical state-change propagation: choose a safe real pending issue that is genuinely resolved/absorbed, disposition/promote/discard it through canonical C2 writer, then verify dashboard automatically removes/changes it without manual projection edits.
  5. Hard refresh AND navigate away/reopen https://workflowy.com/#/98c00c618b80; verify Inbox, Roadmap, reset controls and AI order remain correct.
  6. If any failure occurs, fix and repeat the live gate; do NOT terminalize #2330 based on DB/cache/tests alone.
  7. On final PASS, terminalize/reconcile wi:214f6cf5571d426dba2373960a6bfdf1 and backend hotfix wi:296cf26cd863421a88b1296387492807 with merged/live evidence; send Fedora notification that #2330/dashboard is fully ready.
- Latest repeated sync evidence immediately before handoff:
  - SYNC1 success / ExecMainStatus=0
  - SYNC2 success / ExecMainStatus=0
  - SYNC3 success / ExecMainStatus=0
  - no request_key_conflict in those runs.
- AFTER #2330 final PASS, resume the prior drain from the earlier saved checkpoint: integrate/terminalize MegaVault capsule tooling wi:7d582a5..., continue existing Fedora journald Python/SQLite thread wi:720832... without duplicating it, then capture-path and capsule standard/score, PersonalHub preserved, and continue Inbox/roadmap until quiescence.

## Exact next action for successor chat
1. Read this durable pointer and ~/.config/c2-supervisor/runtime.env.
2. Reuse active supervisor token25 if still valid and canonical; only if truly expired/stale perform deterministic takeover per C2 recovery rules.
3. Complete the six remaining #2330 live E2E gates above on the real Workflowy page.
4. Only after live PASS, terminalize #2330/hotfix and notify the user; then resume the saved C2 drain.
