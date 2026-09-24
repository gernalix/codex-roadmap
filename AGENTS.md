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

All terminal Codex results must use `tools/roadmap_finish.py --result PASS|BLOCKED|FAIL|CANCELLED`. `roadmap_result.py` is an internal compatibility helper only and must not be used as a second operational entry point.


## Persistent operational task memory

For every non-trivial ChatGPT task that spans multiple steps, repositories, expensive verification, user steering, or more than a short interaction, keep a durable operational checkpoint under `operations/task-state/`.

- Use the canonical `PROMPT_ID` when one prompt owns the task; otherwise use a stable explicit `TASK_ID`.
- The file is operational memory, not roadmap lifecycle state and not a substitute for `roadmap.sqlite`.
- Record only: objective, constraints, a complete executable checklist/plan, current step, verified facts, decisions, completed work, remaining work, blockers, evidence, acceptance criteria, and exactly one `Next action`.
- Keep the checklist current as new sub-tasks, dependencies, or plan changes are discovered; split large work into phases and mark items complete only after verification.
- Never store private chain-of-thought, hidden reasoning, secrets, raw private transcripts, or credentials.
- Commit and push meaningful checkpoints after important conclusions, completed sub-goals, expensive verification, user steering that changes execution, before a new phase/risky operation, and whenever a task becomes long enough that session loss would cause duplicated work.
- After a freeze, interruption, model restart, or resumed chat, read the checkpoint first and continue from `Next action`. Do not rediscover already verified facts unless new evidence contradicts them.
- Do not use stash, reflog, uncommitted work, terminal scrollback, or an ephemeral worktree as permanent task memory.
- Direct commits to these non-canonical operational files are allowed; canonical roadmap mutations still go only through the single writer.

## Waiting, polling and token discipline

A Codex/model session must not be kept alive merely to wait for an external or manual condition.

- Never create a periodic model-driven heartbeat/goal continuation whose only purpose is to re-check unchanged state, CI, a manual browser action, login, export progress, PR integration, or another external condition.
- In particular, do not run repeated high-context Codex continuations that return only `DONT_NOTIFY`, `still waiting`, or equivalent no-progress output.
- If progress depends on user input or an external state change, persist the state, terminalize/pause according to the lifecycle contract, release the model session, and use an event-driven/non-model mechanism when monitoring is genuinely required.
- After `roadmap_finish.py` queues repository integration, stop immediately. Do not spend model turns polling CI, PR merge, or the asynchronous integrator.
- A retry/continuation is justified only by new evidence or a concrete state transition. Identical retry without new evidence is forbidden.
- Prefer one bounded native check over a model round-trip. Prefer Luna over Sol for frequent/repetitive checks, but the default for pure waiting is no model call at all.


## Hard workflow for human requests to add/update the roadmap

When the user says **“metti/aggiungi/aggiorna questo prompt nella roadmap”**, the request is not satisfied by creating a normal GitHub Issue, a `[plan]` Issue, a prose handoff, or a prompt file. Those are explicitly non-canonical.

Use this exact workflow:

1. **Decide whether this is a new materialized prompt or a mutation of an existing PROMPT_ID.**
   - Existing prompt: do not allocate another ID unless the prompt text/meaning itself changes and therefore requires a revision.
   - New/revised prompt: allocation is mandatory before the roadmap mutation.
2. **For a new/revised prompt, allocate PROMPT_ID through the canonical MegaVault allocator.**
   - When operating remotely from ChatGPT, create one immutable GitHub Issue `[prompt-id-command] <request_id>` in `gernalix/MegaVault` with `command=allocate` in the JSON body.
   - Wait until that Issue is processed successfully by the canonical allocator. Receipt files are audit/projection only, not the command transport.
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
   - Create one immutable `[prompt-id-command] <request_id>` Issue with `command=materialize`, pointing `content_url` at the exact writer-materialized canonical prompt file.
   - Wait for the allocator Issue to complete successfully with the same PROMPT_ID.
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
- `codex-roadmap-live-status.timer` is a start-claim safety net only: it tails native Codex rollouts and claims a newly observed six-digit PROMPT_ID when the explicit start path was missed. Terminal events never trigger publication, sync or finalization from this watcher.
- The writer prioritizes start claims before ordinary mutations so a prompt that is actually running is locked before queued edits can supersede, reorder, retag, or otherwise mutate it.
- `roadmap_finish.py` is the only operational terminal entry point. Its explicit terminal request is authoritative. `codex-usage` is strictly telemetry/audit: it may record outcome mismatches or missing-finalization anomalies, but it never starts, completes, blocks or fails a prompt.

Every Codex report tied to a roadmap task must begin on line 1 with exactly `PROMPT_ID=<six-digit id>` for that task. This applies both to the final Codex response and to any Markdown/text report artifact Codex produces. When a terminal result is reported, `RESULT=PASS|BLOCKED|FAIL` belongs on line 2, not line 1.


Prompt execution metadata is separate from prompt text:
- `model` and `reasoning` live only in structured roadmap metadata and must not be embedded in the canonical prompt body.
- Changing only model/reasoning before a prompt is running does not change prompt semantics, does not require a new PROMPT_ID, and must update only metadata.
- Once a prompt is running, its execution metadata is immutable for that run.

`tools/import_codex_usage.py` and `tools/roadmap_sync.py` are writer clients, not local DB writers.

Do not invoke legacy direct-writer internals outside tests. Do not pass test-only/unsafe flags merely to bypass this boundary.

Changes to the writer implementation itself (Python, tests, workflows, documentation, schema) may be committed normally, but must not include hand-edited canonical/generated roadmap state.

If a requested roadmap change cannot be expressed by the current mutation schema, extend the writer/schema first; do not bypass it.

After the requested change is verified, stop. Do not perform unrelated audits, refactors or cleanup.
