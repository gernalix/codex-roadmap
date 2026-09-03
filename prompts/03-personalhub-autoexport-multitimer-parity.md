PROMPT_ID: 914637

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Make Personal Hub auto-export behavior and status UX match the old MultiTimer implementation as closely as practical, reusing its proven code/semantics instead of redesigning them.

Known current state: PH already has generation-based auto-export and a recent fix so internal sync/bookkeeping writes do not cause export loops; `requestIfDirty()` is called after real mutations and the export worker exits when `generation == exported_generation`. Preserve these guarantees.

Resolve the old MultiTimer project/repository from MegaVault/project context. Inspect only its auto-export/status implementation and the corresponding PH paths.

## Requirements
- Port/reuse the maximum sensible amount of MultiTimer's auto-export behavior, scheduling/status logic and UX.
- Add the same home-level export-status indicator concept: `✅` when healthy/current and `❌` when failed/stale/unavailable, following MultiTimer semantics.
- Tapping the indicator must show useful export details equivalent to MultiTimer, including at least last successful export time and relevant current/error state.
- Keep PH's SAF destination and current generation/dirty-state correctness.
- Do not reintroduce exports caused only by internal sync/bookkeeping writes or repeated clean-state rewrites.

## Scope / safety
Minimal diff. No unrelated backup/import redesign. Prefer direct reuse/adaptation over new abstractions.

## Acceptance
Targeted unit tests plus a focused device/emulator verification prove: real mutation -> one eventual current export; idle clean state -> no repeated rewrite; status indicator reflects success/failure; tap exposes last-export details.

Stop after PASS; no broader audit.

Final output only: `PROMPT_ID`, `RESULT`, reused MultiTimer components/semantics, tests/device checks, commit SHA.