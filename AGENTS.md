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


## Hard workflow for human requests to add/update the roadmap

When the user says **“metti/aggiungi/aggiorna questo prompt nella roadmap”**, the request is not satisfied by creating a normal GitHub Issue, a `[plan]` Issue, a prose handoff, or a prompt file. Those are explicitly non-canonical.

Use this exact workflow:

1. **Decide whether this is a new materialized prompt or a mutation of an existing PROMPT_ID.**
   - Existing prompt: do not allocate another ID unless the prompt text/meaning itself changes and therefore requires a revision.
   - New/revised prompt: allocation is mandatory before the roadmap mutation.
2. **For a new/revised prompt, allocate PROMPT_ID through the canonical MegaVault allocator.**
   - When operating remotely from ChatGPT, use the existing MegaVault remote bridge: write an `allocate` request to `gernalix/MegaVault:.github/prompt-id-request.json`.
   - Wait until `.github/prompt-id-response.json` contains the **same request_id** and `status=allocated`.
   - Never guess a six-digit ID, reuse an old one, derive one from an Issue number, or proceed while the allocation response is stale/missing.
   - If the remote bridge is unavailable but the user has the canonical local MegaVault checkout, use the same canonical CLI allocator locally (`megavault.py prompt-id allocate`) and continue only with its returned ID. This is a supported fallback, not a bypass. The matching final `materialize` must likewise use the canonical CLI if the remote bridge remains unavailable.
3. **Submit the canonical roadmap mutation.**
   - Create exactly one `codex-roadmap.mutation.v1` Issue named `[roadmap-mutation] <request_key>` using `tools/submit_mutation.py` or an equivalent GitHub API call.
   - For `register`, include the allocated `prompt_id`, final `prompt_text`, `current_path`, model/reasoning/project metadata and any dependencies/relations in the mutation.
   - A title beginning with `[plan]` is never a substitute for this step and must not be presented to the user as “added to the roadmap”.
4. **Wait for the roadmap single writer to apply the mutation.**
   - Do not claim success merely because the Issue was created.
   - Verify that the mutation Issue was applied/closed successfully and that the new PROMPT_ID is present in canonical roadmap state/materialization.
5. **Materialize the allocated PROMPT_ID in MegaVault.**
   - Send a `materialize` request through `.github/prompt-id-request.json`, pointing `content_url` at the exact writer-materialized `gernalix/codex-roadmap/main/prompts/...md`.
   - Wait for the matching `.github/prompt-id-response.json` with `status=materialized`.
6. **Only after steps 1–5 succeed may ChatGPT tell the user that the prompt is in the roadmap.**
   - If any stage fails or is pending, say exactly which stage is incomplete.
   - Do not create a parallel `[plan]` Issue as a fallback.
7. **Clean up process mistakes.** If a non-canonical `[plan]`/handoff Issue was created by mistake for a roadmap request, close it as superseded after the real mutation is queued/applied; do not leave two competing task representations.

For ordinary metadata/state changes to an existing prompt, skip PROMPT_ID allocation/materialization and use only the appropriate `codex-roadmap.mutation.v1` operation through the single writer. Running prompts remain subject to the immutable-field rules below.

## Operational cockpit

Workflowy is the only human-facing operational cockpit. `roadmap.sqlite` remains canonical. Markdown/Obsidian projections are compatibility/audit output and MUST NOT be used to infer whether a prompt is ready, running, integrating, blocked or done.

Prompt bodies are canonical SQLite materializations keyed by PROMPT_ID. Legacy `prompts/*.md` files may remain as writer-owned compatibility materializations, but state protection and copy/launch actions must prefer the SQLite body.

Repository-backed operational state is composed from two authorities:
- roadmap lifecycle from `roadmap.sqlite`;
- integration lifecycle from `github-autosync repo-task status-all --roadmap-only`.

Workflowy may project both, but must never invent state from titles, Markdown rows, URLs or branch naming.

## Generic repository single writer

For roadmap tasks targeting any Git repository other than `gernalix/codex-roadmap`, `roadmap_start.py` also allocates an isolated `task/<PROMPT_ID>` worktree through `~/projects/github-autosync/repo_single_writer.py`.

- Treat the returned `worktree_path` as authoritative even if the materialized prompt names the canonical checkout.
- Never edit/commit directly on the canonical branch of a target repository.
- Multiple tasks may run concurrently because they have separate worktrees/branches; repository-wide worker leases are forbidden. Only genuinely shared runtime resources such as a physical device, emulator session or release/signing operation may be serialized separately by the target project.
- `roadmap_finish.py` checkpoints/pushes the task branch, queues its PR, and returns immediately with `RESULT=QUEUED`; the asynchronous repository integrator later merges it and queues terminal PASS automatically. Codex must not wait for CI or canonical merge.
- Do not bypass a target repository's `single-writer protected` reference-transaction hook.
- BLOCKED/FAIL leaves the task worktree/branch preserved for diagnosis or a follow-up; no destructive cleanup is allowed.

The roadmap repository itself continues to use its dedicated mutation writer described above.

Live lifecycle protection is mandatory:
- `tools/roadmap_start.py` remains the authoritative synchronous launch claim and must run before substantive project work.
- `codex-roadmap-live-status.timer` is the passive fallback: it tails native Codex rollouts, claims newly observed six-digit PROMPT_IDs through the same single writer, and triggers the existing usage publisher + roadmap sync when a terminal event appears.
- The writer prioritizes start claims before ordinary mutations so a prompt that is actually running is locked before queued edits can supersede, reorder, retag, or otherwise mutate it.
- An explicit terminal request from `roadmap_finish.py` / `roadmap_result.py` is authoritative and applies the terminal roadmap state immediately. `codex-usage` arrives later for telemetry/audit and must not keep completed repository work stuck in `running`.

Every Codex report tied to a roadmap task must begin on line 1 with exactly `PROMPT_ID=<six-digit id>` for that task. This applies both to the final Codex response and to any Markdown/text report artifact Codex produces. When a terminal result is reported, `RESULT=PASS|BLOCKED|FAIL` belongs on line 2, not line 1.

`tools/import_codex_usage.py` and `tools/roadmap_sync.py` are writer clients, not local DB writers.

Do not invoke legacy direct-writer internals outside tests. Do not pass test-only/unsafe flags merely to bypass this boundary.

Changes to the writer implementation itself (Python, tests, workflows, documentation, schema) may be committed normally, but must not include hand-edited canonical/generated roadmap state.

If a requested roadmap change cannot be expressed by the current mutation schema, extend the writer/schema first; do not bypass it.

After the requested change is verified, stop. Do not perform unrelated audits, refactors or cleanup.
