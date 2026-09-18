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

`tools/import_codex_usage.py` and `tools/roadmap_sync.py` are writer clients, not local DB writers.

Do not invoke legacy direct-writer internals outside tests. Do not pass test-only/unsafe flags merely to bypass this boundary.

Changes to the writer implementation itself (Python, tests, workflows, documentation, schema) may be committed normally, but must not include hand-edited canonical/generated roadmap state.

If a requested roadmap change cannot be expressed by the current mutation schema, extend the writer/schema first; do not bypass it.

After the requested change is verified, stop. Do not perform unrelated audits, refactors or cleanup.
