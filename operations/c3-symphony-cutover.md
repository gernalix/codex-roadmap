PROMPT_ID=731707

# C3 Symphony pilot and cutover gate

## Pilot boundary

- Source repository: `gernalix/codex-roadmap` only.
- Supported tracker: GitHub Issues in disposable `gernalix/symphony-canary` only.
- Eligible input: canonical read-only `v_work_item_runnable` row with `executor_policy=codex`, `activity=coding`, exact source repo, and explicit model/reasoning execution spec.
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

The generated workflow pins the derived model and reasoning using `codex -c model=... -c model_reasoning_effort=... app-server`, clones the source repo into an isolated workspace, and references only `$GITHUB_TOKEN`. It contains no credential value.

Install `operations/c3-symphony.service` as the user unit. Its `LoadCredential` source is the host-only `~/.config/c3-symphony/github-token` file, outside the repository and Codex workspace. `tools/c3_symphony_backend.py run` reads the systemd credential and executes the existing upstream Symphony binary. The unit owns the entire process group, including Codex app-server children. Never commit or print the token.

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
