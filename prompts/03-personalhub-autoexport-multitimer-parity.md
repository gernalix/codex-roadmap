PROMPT_ID: 914637

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Complete only the REMAINING old-MultiTimer parity for Personal Hub auto-export/status UX. Do not rebuild the auto-export engine: PH already has the durable generation-based implementation.

Known verified PH state to preserve:
- commit `e6f323c157ecd68cc41299a2d44367a66d895bc2` made SAF auto-export durable after mutations, with generation/exported-generation tracking, WorkManager recovery, persisted error/status state and retry behavior;
- commit `1b5053db4e8d768e1fa5cf212f12208629e67814` fixed the idle export loop: `requestIfDirty()` runs after mutations, internal sync/bookkeeping writes do not schedule clean-state exports, and the worker exits immediately when generation is already exported.

Resolve the old MultiTimer project/repository from MegaVault/project context. Inspect ONLY its home export-status UI and any directly required status presentation code, plus the corresponding PH home/status APIs.

## Requirements
- Reuse/adapt MultiTimer's proven home export-status UX as closely as practical.
- Add a tappable home-level `✅`/`❌` export indicator with MultiTimer-equivalent semantics.
- Tap must show useful status details including last successful export time and current stale/error/folder state where applicable.
- Use PH's existing `DatabaseVault.autoExportStatus`/generation/error machinery rather than replacing or duplicating it.
- Preserve the verified no-idle-loop behavior and durable export semantics above.

## Non-goals
No auto-export architecture rewrite, no backup/import redesign, no unrelated settings/UI work.

## Acceptance
Targeted tests and focused device/emulator verification show: indicator reflects healthy/current vs stale/error state; tap exposes last-export/status details; a real mutation still reaches current export; idle clean state causes no repeated SAF rewrite.

Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, reused MultiTimer UI/semantics, targeted verification, commit SHA.