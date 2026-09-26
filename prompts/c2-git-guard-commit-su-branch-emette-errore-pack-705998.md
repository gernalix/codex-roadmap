PROMPT_ID=705998

# Goal
Fix the codex-roadmap Git reference-transaction guard so allowed non-main branch work no longer emits the false guard/pack-refs error, while direct mutations of protected main remain blocked.

## Scope
Work only in this isolated codex-roadmap worktree. Start from the current hook/tests and make the minimum change required. Do not modify roadmap.sqlite directly, C2 scheduling semantics, PersonalHub, or unrelated code.

## Required behavior
- Allowed commit/push activity on non-main branches must not emit the false guard error.
- Benign reference maintenance such as pack-refs must not be rejected merely because main exists among refs being inspected.
- Actual prohibited updates to protected main must still be rejected deterministically.
- Add or adjust focused automated coverage that distinguishes a real main mutation from branch/ref-maintenance transactions.

## Verification
Run the narrow hook tests first; expand only if failures or risk require it. Also run git diff --check. Record the exact commands/results. Stop once the acceptance criteria pass.

## Persistence
Commit the focused fix on the current isolated branch and push it. Open or update a focused PR only if needed to integrate the code change; do not perform unrelated cleanup or refactors.
