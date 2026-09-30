PROMPT_ID=731707

Implement the minimum C3/Symphony production pilot bridge in gernalix/codex-roadmap.

Goal:
Route eligible autonomous coding work from the C2/global control plane into the upstream-pure OpenAI Symphony execution backend, prove the authenticated pilot, and prepare an evidence-gated cutover. Do not extend legacy C2 Codex orchestration that Symphony is intended to replace.

Starting evidence:
- Read only the relevant state in operations/task-state/wi-52a87ab8460d479dbee0fc970cbc58a0.md and the current C3 parent/child state.
- Official Symphony checkout already exists at /home/daniele/projects/symphony and must remain upstream-pure.
- Technical canary, upstream tests and orchestration gates already PASS; do not repeat broad evaluation.
- Use a supported tracker bridge; do not implement a custom roadmap.sqlite tracker adapter or fork Symphony.
- For app-server model selection use explicit configuration overrides for the chosen model and reasoning effort, not the short model flag.
- Credentials must come from a proper host-managed path (systemd credentials/environment or equivalent), never WORKFLOW.md, prompt text, repo files or Codex-visible workspace secrets.

Implementation scope:
1. Add the thinnest bridge/config needed for eligible C2 coding work to publish/dispatch through Symphony using a supported tracker.
2. Keep roadmap/MegaVault as global policy/identity sources; do not duplicate Symphony runtime state into roadmap.sqlite.
3. Preserve ChatGPT Web/Desktop and native/Fedora lanes outside Symphony.
4. Make the cross-surface control plane observe and stop Symphony as one backend.
5. Encode model/reasoning and repo/workflow policy in derived execution config/WORKFLOW.md without modifying upstream Symphony source.
6. Run an authenticated supported-tracker E2E through the proper host credential mechanism.
7. Run a representative low-risk pilot batch and prove: no duplicate dispatch, no leaked app-server process, no repository-state corruption, deterministic cleanup/reconciliation.
8. Record the concrete cutover: legacy C2 components to bypass/remove, retained non-Codex lanes, rollback condition, and evidence required before switching production coding traffic.

Acceptance:
- Supported-tracker bridge works without a Symphony fork.
- Correct model/reasoning reaches app-server through config overrides.
- Authenticated tracker E2E passes with host-managed credentials.
- Representative low-risk pilot batch passes with no duplicate dispatch, leaked app-server processes, or repo corruption.
- Cross-surface registry can observe/stop Symphony while preserving non-Codex lanes.
- Cutover plan identifies exact legacy C2 Codex components to bypass/remove.

Execution rules:
- Minimum change only. Reuse verified Symphony evidence; no broad re-audit after PASS.
- Fix only blockers on this critical path. Capture incidental material findings to C2 Inbox without investigating them inline.
- Prefer deterministic/native checks over model polling.
- Test targeted first; expand only if evidence requires it.
- Checkpoint with commit+push after meaningful milestones; keep this task-state reconstructible.
- Do not claim PASS until code, authenticated E2E, pilot, process cleanup, repository integrity and cutover evidence are all verified.
