PROMPT_ID=731707

# C3 Symphony pilot and cutover gate

## Pilot boundary

- Source repository: `gernalix/codex-roadmap` only.
- Supported tracker: GitHub Issues in disposable `gernalix/symphony-canary` only.
- Eligible input: canonical read-only `v_work_item_runnable` row with `executor_policy=auto` or `codex`, `activity=coding`, exact source repo, and explicit model/reasoning execution spec. Human-readable model labels are resolved to CLI model IDs.
- `tools/c3_symphony_bridge.py` publishes one issue with a stable `wi:` identity and the `c3-symphony-ready` dispatch label. A local publisher lock plus complete tracker readback make replays idempotent on the single pilot host. More than one issue with the same identity fails closed.
- The bridge never writes roadmap SQLite. Symphony's issue, process, workspace, retry, and turn state remain in GitHub/Symphony.

## Host setup and controls

Generate the workflow outside the Codex workspace for one eligible item:

```sh
python3 tools/c3_symphony_bridge.py workflow --db /path/to/roadmap.sqlite \
  --work-item-id 'wi:...' \
  --workspace-root "$HOME/.local/share/c3-symphony/workspaces" \
  --output "$HOME/.local/share/c3-symphony/WORKFLOW.md"
```

The generated workflow pins the derived model and reasoning using `codex -c model=... -c model_reasoning_effort=... app-server`, clones the source repo into an isolated workspace's `source/` subdirectory, and references only `$GITHUB_TOKEN`. The Symphony child starts in the workspace root so the repository's legacy C2 launch instructions are not automatically applied to the disposable pilot; the workflow explicitly forbids duplicate C2 start/finish calls. It contains no credential value.

Install `operations/c3-symphony.service` as the user unit. Its `LoadCredentialEncrypted` source is the user-scoped systemd-creds file at `~/.config/c3-symphony/credentials/github-token.cred`, outside the repository and Codex workspace. `tools/c3_symphony_backend.py run` reads the decrypted credential from `$CREDENTIALS_DIRECTORY/GITHUB_TOKEN` inside the service and executes the existing upstream Symphony binary. The unit owns the entire process group, including Codex app-server children. Never commit or print the token.

```sh
python3 tools/c3_symphony_backend.py status
python3 tools/c3_symphony_backend.py stop
```

These are the cross-surface control plane's pilot backend operations. `status` reports unit state, API health, and aggregate Symphony counts only. `stop` stops one systemd unit; it does not touch ChatGPT Web/Desktop or native/Fedora lanes. The unit and adapter require actual host installation before live stop/observe acceptance.

Publish only after the host service and workflow are ready:

```sh
python3 tools/c3_symphony_bridge.py publish --db /path/to/roadmap.sqlite --work-item-id 'wi:...'
```

## Cutover map

| Legacy C2 Codex component | Cutover action |
| --- | --- |
| `tools/c2_appserver_rpc.py` | Bypass/remove for Symphony coding tasks; Symphony owns app-server protocol. |
| `tools/c2_codex_executor.py` | Bypass/remove for Symphony coding tasks; Symphony owns worker and turn lifecycle. |
| Codex branch in `tools/c2_worker.py` | Bypass after the bridge publishes an eligible issue. |
| Codex retry, stall, concurrency and workspace logic in `tools/c2_scheduler.py` | Bypass/remove for Symphony coding tasks; Symphony owns these per-issue functions. |
| `tools/c2_prepare_codex.py` and `tools/c2_codex_sandbox.py` | Bypass for Symphony tasks; keep only for still-active legacy/direct Codex work until drained. |
| C2 per-Codex recovery in supervisor/watchdog | Bypass for Symphony tasks; retain global cross-surface authority and non-Codex recovery. |
| `tools/c2_executor_start.py` / result receipts | Adapt to one backend handoff and aggregate reconciliation; do not record Symphony's internal turns in roadmap SQLite. |

Keep MegaVault identity, roadmap policy/dependencies, Inbox, Workflowy, repository single-writer integration, ChatGPT Web/Desktop, and native/Fedora execution. The bridge is a pilot handoff, not authority to switch production traffic yet. Multi-repo configuration and repository-specific integration remain post-cutover work.

## Evidence required before production coding traffic switches

1. Authenticated upstream GitHub tracker E2E using the host-managed credential, including issue comment/close and explicit app-server model/reasoning readback.
2. At least two low-risk coding issues through this bridge with unique identities and a replay of each: one dispatch per issue, no duplicates, bounded concurrency, deterministic terminal cleanup and restart reconciliation.
3. No remaining pilot-owned `codex app-server` process after stop or completion; verify source and scratch repository refs/state are unchanged except intended isolated task artifacts.
4. Live `status` API observation and systemd `stop` of the Symphony unit, with ChatGPT Web/Desktop and native/Fedora lanes unaffected.
5. A compatible mitigation or upstream fix for deployment-relevant dependency advisories recorded in the prior Symphony evaluation.

Rollback condition: any duplicate dispatch, orphan app-server, repository-state corruption, lost stop authority, credential exposure, or tracker reconciliation failure. On trigger, stop `c3-symphony.service`, remove the ready label from outstanding pilot issues, preserve workspaces/logs for diagnosis, and keep coding traffic on the existing C2 path. No canonical roadmap or MegaVault state is rewritten by this rollback.

The first disposable live batch (#7/#8) was invalidated and closed because a child in the cloned repository followed legacy C2 launch instructions. That batch is evidence for the workflow isolation requirement, not acceptance evidence.

## Corrected live pilot evidence

- Correction checkpoint: `f834577d7b9291617dfa6e533cf282cf134aa537`.
- Corrected tracker issues: GH-9 and GH-10, unique identities, both closed successfully.
- Both workers started in parent `workspaces-v2/GH-*` directories and used a cloned `source/` repository, preventing automatic inheritance of the source repo's legacy C2 launch instructions.
- Live app-server readback for both corrected workers: `gpt-6-sol`, `reasoningEffort=medium`.
- GH-9 created exactly `source/PILOT_C.txt`; its evidence comment reported only `?? PILOT_C.txt` and no push.
- GH-10 created exactly `source/PILOT_D.txt`; its evidence comment reported only `?? PILOT_D.txt` and no push/merge.
- Finalizer hardening after the GH-10 reconciliation ambiguity pins every `github_api` read/comment/close to tracker repository `gernalix/symphony-canary` and `{{ issue.identifier }}`, explicitly forbids using the source repository as tracker target, and requires exact-target `state=closed` readback before success.
- With `max_concurrent_agents=1`, terminal GH-9 was cleaned up before Symphony automatically backfilled GH-10.
- After GH-10, the pilot workspace root was empty.
- `c3-symphony.service` was stopped through systemd and no Symphony process remained.
- Live bridge/backend child acceptance is PASS. This does **not** clear production gate 5 below: the dependency-security/hardening gate remains a separate parent-C3 requirement.

## Remaining production cutover gate

The corrected pilot satisfies readiness items 1–4 above. Production traffic must remain HOLD until deployment-relevant upstream dependency advisories are resolved or explicitly mitigated without creating a permanent Symphony fork.
