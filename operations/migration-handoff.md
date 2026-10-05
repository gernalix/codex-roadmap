> FROZEN C3 ARCHIVE (2026-10-05). Historical reference only. Do not execute these operating instructions. Current task flow: /home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md.

# Canonical handoff
STATUS=POST_CUTOVER
Operational authority: /home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md (AI-only; 90%+ normal-case single-document contract).

## Architecture
MegaVault=identity/desired inventory; C3=local lifecycle/Inbox/PROMPT_ID; github-autosync=Git/integration/GC; Fedora=observed health/Kuma; usage-monitor=telemetry. C3 canonical DB=/home/daniele/.local/state/c3-control/roadmap.sqlite; sole writer=c3-writer.service; primary UI=http://127.0.0.1:8767.

## Current state
Writer/web/Symphony healthy, enabled. Event runtime path + 15-minute safety timer active; native cycles successful. 140 pending items, 124 dependency-ready, zero with execution specifications; zero active runs. No legacy ownership/bindings/resource leases/recovery checkpoints. Project caches equal MegaVault; IDs 104/105/106 correct. C3 permanently reserves 500 prompt IDs, including all 347 historical MegaVault IDs. Audit=1859 rows, terminal_reconcile_skipped=0; idle cycle adds no rows/receipts.

M1/checkpoint commit 0c7d1f9ce8ecf48eb39387a30dcb79a34745f54e retained by archive/pre-migration-m1: pre-migration / retired, historical-only. Run abddbd99029d41af9969572eb20bdce7 cancelled in retirement metadata (terminal failed); its recursive triage item superseded. No old chat/session required.

## Verification / residuals
Real Unix-writer/native scheduler/start/crash-recovery/restart E2E passes; web, Codex adapter, Symphony and Git integration/GC suites pass. Remote tracker/CI boundaries tested with fixtures, not new goal Issues. Enabled units/order/readiness/linger verified; no physical reboot performed. Retired unit/direct-script launch attempts reject with canonical DB/WAL/coordination/event hashes unchanged.

Verified DB backups and historical frozen MegaVault prompt registry retained read-only. Latest cutover backup: backups/final-runtime-cutover/roadmap-20261001T210039.126576Z.sqlite (SHA256 9900127403b36d7225473aede91f94da463ffb1cce9399120f3fcc146470815e). Unknown/dirty/unintegrated/recovery Git evidence preserved. Personal Workflowy retained. Pre-existing staged browser-unit edit in canonical chatgpt-rdc-supervisor untouched; deployed pinned source is clean. Independent PersonalHub Obsidian projection has a Git fast-forward failure; not C3 authority and outside this goal.

## Next action
Handle only the next user-scoped request through the sole AI operational document; no master-goal recovery or migration continuation is needed.
