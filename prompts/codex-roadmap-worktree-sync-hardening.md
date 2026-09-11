[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=561274 | project_id=51 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Remove the recurring codex-roadmap bootstrap cost caused by dirty local worktrees, trivial accidental edits, and temporary stashes when Codex only needs the canonical remote roadmap state.

# Starting point
A recent roadmap run found a local `spiegazioni.md` modification consisting only of invisible characters. Codex had to inspect it, stash it, sync, and later leave `codex-preserve-local-spiegazioni` behind. The canonical authority is `origin/main`, so read-only roadmap selection should not require mutating or cleaning the user's local worktree.

# Scope
Harden the codex-roadmap sync/bootstrap workflow with the minimum safe change, preferring Git-native read-only access to `origin/main` (or an equivalent isolated mechanism) over automatic stashing of user work.

Required behavior:
- selecting/reading the canonical pending roadmap must work even when the local worktree has unrelated uncommitted changes;
- do not discard, overwrite, normalize, auto-commit, or silently stash genuine user changes;
- avoid creating persistent stashes merely to read canonical remote files;
- when a write/update to codex-roadmap is actually required, use a safe path that either operates from a clean isolated state or stops with a precise blocker if genuine conflicting local work must be reconciled;
- clean up the existing `codex-preserve-local-spiegazioni` stash only after inspecting it and only if its contents are provably redundant/already represented upstream; otherwise preserve it and report why;
- document the canonical minimal bootstrap so future Codex sessions do not re-investigate this problem.

Do NOT redesign the roadmap format, reorder pending tasks, rewrite prompt contents, or perform general repository cleanup. Do not delete any user work merely because it appears trivial.

# Verification
Use a safe simulated dirty-worktree case or equivalent reproducible check to prove that canonical roadmap reading/selection no longer requires stashing. Also verify that a genuine local modification remains untouched and that the documented write path refuses or isolates conflicts safely.

# Acceptance / stop
PASS when read-only roadmap bootstrap is independent of local dirtiness and no unnecessary stash is created, while genuine user work remains protected. Stop immediately after the targeted workflow and current stash disposition are verified.

Final output concise: `PROMPT_ID`, `RESULT`, root cause, new canonical bootstrap/write behavior, existing stash disposition, verification, files changed, blocker if any.