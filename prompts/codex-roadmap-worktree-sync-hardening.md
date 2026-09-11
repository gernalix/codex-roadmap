[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=561274 | project_id=51 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Remove recurring Codex bootstrap/finalization cost and correctness risk caused by dirty local worktrees, accidental edits, temporary stashes, ambiguous active-task identity, and commits that absorb pre-existing unrelated changes.

# Starting point
Recent runs exposed two related failure modes:
- reading the canonical roadmap required inspecting/stashing a dirty local `spiegazioni.md`, even though `origin/main` is authoritative;
- an ad-hoc blocker-fix prompt (`PROMPT_ID=483210`) later inferred that the first pending roadmap prompt was "coherent" with the existing tree and archived that different prompt (`PROMPT_ID=762451`). The same run committed pre-existing modifications together with its own R8 fix.

These must become impossible by workflow, not by operator memory.

# Scope
Harden the codex-roadmap/task-finalization workflow with the minimum safe changes. Prefer Git-native read-only access to `origin/main` or an equivalent isolated mechanism. Add a precise active-task identity/ownership guard for roadmap completion and commit scope.

Required behavior:
- selecting/reading the canonical pending roadmap must work even when the local worktree has unrelated uncommitted changes;
- do not discard, overwrite, normalize, auto-commit, or silently stash genuine user changes;
- avoid creating persistent stashes merely to read canonical remote files;
- when a write/update to codex-roadmap is required, use a clean isolated state or stop with a precise blocker if genuine conflicting work must be reconciled;
- an ad-hoc prompt, blocker-fix prompt, or continuation may archive/remove a roadmap prompt only when its identity is explicitly tied to that exact roadmap prompt (same roadmap prompt/PROMPT_ID or an explicit continuation relationship supplied by the user/workflow). Never infer completion merely because the first pending prompt looks related to the current diff;
- before moving anything to `completed/`, verify and report the exact roadmap file/PROMPT_ID being completed;
- snapshot or otherwise identify pre-existing dirty changes before task edits. A task commit must contain only task-owned changes, except when an explicit continuation says those existing changes belong to the same task;
- if unrelated pre-existing changes prevent a clean task commit, isolate the task safely (for example via a worktree/index strategy) or stop; do not sweep them into the commit;
- clean up the existing `codex-preserve-local-spiegazioni` stash only after inspecting it and only if provably redundant/already represented upstream; otherwise preserve it and report why;
- document the canonical minimal bootstrap/finalization path so future sessions do not re-investigate these cases.

Do NOT redesign the roadmap format, rewrite unrelated prompt contents, or perform general repository cleanup. Do not delete any user work merely because it appears trivial.

# Verification
Use targeted reproducible cases proving all of the following:
1. canonical roadmap reading/selection works with a dirty local worktree without creating a stash;
2. a genuine local modification remains untouched;
3. an ad-hoc prompt cannot archive a different first-pending roadmap prompt by inference;
4. pre-existing unrelated changes are not included in the task commit path;
5. the documented write path either isolates or safely refuses a real conflict.

# Acceptance / stop
PASS when roadmap bootstrap is independent of local dirtiness, roadmap completion is identity-safe, task commits cannot silently absorb unrelated pre-existing work, and no unnecessary stash is created. Stop immediately after targeted verification and current stash disposition are complete.

Final output concise: `PROMPT_ID`, `RESULT`, root cause, canonical bootstrap/write behavior, task-identity guard, dirty-change/commit isolation behavior, existing stash disposition, verification, files changed, blocker if any.