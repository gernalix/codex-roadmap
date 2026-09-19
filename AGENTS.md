# Codex instructions — codex-roadmap

## Canonical write boundary

For any roadmap data mutation, use the single writer. This rule is automatic and does not require the user to repeat it.

Never directly edit or commit canonical/generated roadmap state to perform a roadmap mutation:

- `roadmap.sqlite`
- `roadmap.md`
- `spiegazioni.md`
- `prompt-registry.md`
- `obsidian/`
- `prompts/`
- `completed/`
- `falliti/`
- `mutations/inbox/` or `mutations/applied/`

Instead, submit one immutable `codex-roadmap.mutation.v1` request as a GitHub Issue named `[roadmap-mutation] <request_key>`, normally through `tools/submit_mutation.py`. Let `.github/workflows/apply-roadmap-mutations.yml` serialize, apply, render, commit and push it.

Terminal Codex results must use `tools/roadmap_result.py` or `tools/roadmap_finish.py`; they already submit through the same writer.

## Generic repository single writer

For roadmap tasks targeting any Git repository other than `gernalix/codex-roadmap`, `roadmap_start.py` also allocates an isolated `task/<PROMPT_ID>` worktree through `~/projects/github-autosync/repo_single_writer.py`.

- Treat the returned `worktree_path` as authoritative even if the materialized prompt names the canonical checkout.
- Never edit/commit directly on the canonical branch of a target repository.
- Multiple tasks may run concurrently only because they have separate worktrees/branches.
- `roadmap_finish.py` waits for the task branch to be pushed, its `[single-writer]` PR to pass checks, and the per-repository writer to merge it before the roadmap task can become completed.
- Do not bypass a target repository's `single-writer protected` reference-transaction hook.
- BLOCKED/FAIL leaves the task worktree/branch preserved for diagnosis or a follow-up; no destructive cleanup is allowed.

The roadmap repository itself continues to use its dedicated mutation writer described above.

Live lifecycle protection is mandatory:
- `tools/roadmap_start.py` remains the authoritative synchronous launch claim and must run before substantive project work.
- `codex-roadmap-live-status.timer` is the passive fallback: it tails native Codex rollouts, claims newly observed six-digit PROMPT_IDs through the same single writer, and triggers the existing usage publisher + roadmap sync when a terminal event appears.
- The writer prioritizes start claims before ordinary mutations so a prompt that is actually running is locked before queued edits can supersede, reorder, retag, or otherwise mutate it.
- A terminal request alone does not unblock descendants. Only an authoritative `codex-usage` terminal execution with `PASS` changes the parent to `completed`; every child whose remaining dependencies are then satisfied becomes runnable automatically.

Every Codex report tied to a roadmap task must begin on line 1 with exactly `PROMPT_ID=<six-digit id>` for that task. This applies both to the final Codex response and to any Markdown/text report artifact Codex produces. When a terminal result is reported, `RESULT=PASS|BLOCKED|FAIL` belongs on line 2, not line 1.

`tools/import_codex_usage.py` and `tools/roadmap_sync.py` are writer clients, not local DB writers.

Do not invoke legacy direct-writer internals outside tests. Do not pass test-only/unsafe flags merely to bypass this boundary.

Changes to the writer implementation itself (Python, tests, workflows, documentation, schema) may be committed normally, but must not include hand-edited canonical/generated roadmap state.

If a requested roadmap change cannot be expressed by the current mutation schema, extend the writer/schema first; do not bypass it.

After the requested change is verified, stop. Do not perform unrelated audits, refactors or cleanup.
