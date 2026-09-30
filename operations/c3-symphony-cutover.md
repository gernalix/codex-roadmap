PROMPT_ID=998028

# C3 Symphony production cutover

## Authority and routing

The established pilot, cleanup, model/reasoning, encrypted credential, and dependency-security gates passed. Production remains an explicit host action after this branch merges. Keep `mode=legacy` until the supervising ChatGPT authorizes a canary. The host configuration is `~/.config/c3-symphony/config.json` (mode `0600`); there is no tracker or source inference from issue prose. A missing file means legacy rollback. An invalid file fails closed.

```json
{
  "mode": "production",
  "tracker_repo": "gernalix/c3-symphony",
  "source_repos": ["gernalix/codex-roadmap"]
}
```

Use `gernalix/c3-symphony` only after the operator has explicitly configured it and verified authenticated access with `gh api repos/gernalix/c3-symphony`. If unavailable, configure an exact other production tracker. `mode=production` rejects `gernalix/symphony-canary`. `mode=canary` requires that exact disposable tracker. `mode=legacy` keeps C2 Codex. Add source repositories explicitly to the allowlist only when their isolated task worktree and existing repository writer are ready.

Only autonomous `coding` with `executor_policy=auto|codex`, a canonical runnable/claimed item, an allowlisted source repo, an explicit model/reasoning pair, and an existing `task/<PROMPT_ID>` worktree can route to Symphony. Diagnostic, GUI, native, semantic, external, and human work retain their current executors. The scheduler's canonical run remains the single global claim. The host reserves one durable `wi:` to run/tracker owner before tracker publication; retry with another run or tracker fails closed. Symphony children never call C2 start/finish/result helpers. The roadmap and its single writer remain authoritative.

The bridge creates or reuses exactly one tracker issue by canonical `wi:` identity under a local publication lock and reads it back. The exact tracker repository comes from host config; the source repo comes from the canonical row plus allowlist. The production workflow links the already isolated task worktree into Symphony's per-issue workspace as `source/`, gives that path explicitly to Codex with `--add-dir`, and pins `model` and `model_reasoning_effort` in the app-server command. The child commits tested changes but does not push or merge. It posts exactly one `C3_RESULT=<JSON>` comment on the tracker issue, closes that exact issue, and reads back `state=closed`. The parent requires that same issue and one terminal contract, submits one idempotent result receipt, and queues the existing repository integration writer from the isolated worktree. The existing merge readback finalizes PASS; no second merger is introduced.

## Reproducible artifact and host controls

The only approved source is official `openai/symphony` commit `1c0fb6c8e8ef9031a2c861e62af5f9e66cee39cb`. The build helper checks the upstream lock, applies exactly the Req and Decimal manifest edits documented below, copies the exact hardened lock, runs `MIX_ENV=prod make setup`, `make build`, and `mix hex.audit`, checks the production escript hash, and atomically installs `~/.local/share/c3-symphony/bin/symphony`. It leaves the upstream checkout untouched.

```sh
python3 tools/c3_symphony_install.py --source /home/daniele/projects/symphony
sha256sum ~/.local/share/c3-symphony/bin/symphony
```

Expected SHA-256: `25cdc28aaa8009ab1c3ef842b0925baa70923869000a557f8edafabc822b9c2b`. The helper requires the hardened lock SHA-256 `296b13c88039f5912ef47bab3acbc1b68718aa4ee4a6eace28e36b6026f7d6b3` and audit exit 0; any source, lock, or artifact drift stops installation. Never use `~/.local/share/symphony-eval` for production.

Install `operations/c3-symphony.service` as the user unit after merge. It points to the durable binary and loads `GITHUB_TOKEN` from `~/.config/c3-symphony/credentials/github-token.cred` with `LoadCredentialEncrypted`. The backend checks the production artifact hash, the workflow tracker, and loopback listener before start. `status` and `stop` derive `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` from `/run/user/<uid>` for RDC/noninteractive callers; `stop` affects only the Symphony unit.

```sh
python3 tools/c3_symphony_bridge.py workflow --db /home/daniele/projects/codex-roadmap/roadmap.sqlite --work-item-id 'wi:...' --workspace-root "$HOME/.local/share/c3-symphony/workspaces" --output "$HOME/.local/share/c3-symphony/WORKFLOW.md"
python3 tools/c3_symphony_backend.py status
python3 tools/c3_symphony_backend.py stop
```

The worker writes the exact item workflow and starts the user unit when the selected backend is inactive. If the unit is already active, the workflow must match that item byte for byte. The scheduler holds `symphony:backend` as one shared lease, so a second eligible item waits until the first has a canonical terminal result. After exact tracker close and integration queue, the worker stops the unit; the next item receives its own workflow. A healthy backend and exact workflow are required before publication. Production backend/config/artifact failure blocks selected Symphony coding rather than falling back to legacy. Change to `mode=legacy` only after the Symphony owner is reconciled; a durable owner record prevents a concurrent legacy worker. Preserve tracker/worktree evidence for rollback. Do not deploy production traffic from this branch.

## Prior pilot and security evidence

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

## Final dependency-security gate (2026-09-30)

**GATE PASS.** The corrected pilot already satisfied readiness items 1–4. Production cutover may proceed only with the hardened artifact contract below. The existing `symphony-v0.0.3-linux_x86_64` pilot binary and the upstream lockfile are not approved for production coding traffic.

### Exact source and advisory baseline

- Official `openai/symphony` remote refs were checked once with `git ls-remote`: `main=be10a1b79df723d6d7612b5651c8522704dafb2e`; annotated `v0.0.3` tag `3efccfe499b6b50bdbfb674c4c9603aaa13da06d` dereferences to `1c0fb6c8e8ef9031a2c861e62af5f9e66cee39cb`. The tag is the chosen source. `git diff v0.0.3 main -- elixir` changes only `elixir/README.md`; the Elixir manifest, lock, and code match.
- The unmodified tag's `elixir/mix.lock` SHA-256 is `f707a715e6a4e91fc865c1c78d286a5211759a94659caa87e6cd6bad12a6f90c`. `mix hex.audit` on that exact lock reports **35 advisories: 17 high, 13 medium, 5 low**. This includes test-only and currently unused paths so no relevant finding is silently discarded.
- Exposure codes: **L** = HTTP/LiveView path reachable from the intended loopback-only observability listener by local users; **G** = outbound GitHub API client path reachable, with exploitation requiring a malicious or compromised HTTPS peer/response; **C** = conditional Solid numeric-filter path if the trusted workflow template applies such a filter to tracker text; **T** = test-only dependency, absent from the production dependency set; **N** = path disabled or unused by this deployment. `longpoll: false`, no permessage-deflate option, fixed GitHub request methods, no multipart upload, no untrusted redirect target, and no dynamic cookie attributes were checked in the upstream source. The `N` classification does not excuse a vulnerable production binary.

| Locked package | Advisory (severity) | First fixed in same line | Exposure |
| --- | --- | --- | --- |
| `lazy_html 0.1.10` | [GHSA-8rqp-v692-v82q](https://github.com/advisories/GHSA-8rqp-v692-v82q) (low) | `0.1.13` | T |
| `req 0.5.17` | [GHSA-px9f-whj3-246m](https://github.com/advisories/GHSA-px9f-whj3-246m) (low) | `0.6.0` | N |
| `req 0.5.17` | [GHSA-655f-mp8p-96gv](https://github.com/advisories/GHSA-655f-mp8p-96gv) (high) | `0.6.1` | G |
| `phoenix 1.8.4` | [GHSA-6983-jfq8-485w](https://github.com/advisories/GHSA-6983-jfq8-485w) (high) | `1.8.9` | L |
| `phoenix 1.8.4` | [GHSA-628h-q48j-jr6q](https://github.com/advisories/GHSA-628h-q48j-jr6q) (high) | `1.8.6` | N |
| `phoenix 1.8.4` | [GHSA-63mc-hw7g-86rr](https://github.com/advisories/GHSA-63mc-hw7g-86rr) (medium) | `1.8.9` | N |
| `phoenix_live_view 1.1.25` | [GHSA-36m4-rm57-3prf](https://github.com/advisories/GHSA-36m4-rm57-3prf) (low) | `1.1.33` | N |
| `bandit 1.10.3` | [GHSA-q6v9-r226-v65f](https://github.com/advisories/GHSA-q6v9-r226-v65f) (medium) | `1.11.0` | L |
| `bandit 1.10.3` | [GHSA-c67r-gc9j-2qf7](https://github.com/advisories/GHSA-c67r-gc9j-2qf7) (medium) | `1.11.0` | L |
| `bandit 1.10.3` | [GHSA-375f-4r2h-f99j](https://github.com/advisories/GHSA-375f-4r2h-f99j) (medium) | `1.11.0` | L |
| `bandit 1.10.3` | [GHSA-frh3-6pv6-rc8j](https://github.com/advisories/GHSA-frh3-6pv6-rc8j) (high) | `1.11.0` | N |
| `bandit 1.10.3` | [GHSA-pf94-94m9-536p](https://github.com/advisories/GHSA-pf94-94m9-536p) (high) | `1.11.0` | L |
| `bandit 1.10.3` | [GHSA-rf5q-vwxw-gmrf](https://github.com/advisories/GHSA-rf5q-vwxw-gmrf) (high) | `1.11.1` | L |
| `bandit 1.10.3` | [GHSA-9q9q-324x-93r2](https://github.com/advisories/GHSA-9q9q-324x-93r2) (high) | `1.11.1` | L |
| `bandit 1.10.3` | [GHSA-xj8g-532w-jv94](https://github.com/advisories/GHSA-xj8g-532w-jv94) (high) | `1.12.5` | L |
| `bandit 1.10.3` | [GHSA-x3gh-xhj4-3vq8](https://github.com/advisories/GHSA-x3gh-xhj4-3vq8) (medium) | `1.12.5` | L |
| `mint 1.7.1` | [GHSA-rj5m-69wp-cxq9](https://github.com/advisories/GHSA-rj5m-69wp-cxq9) (medium) | `1.10.1` | G |
| `mint 1.7.1` | [GHSA-2p26-p43x-fhp8](https://github.com/advisories/GHSA-2p26-p43x-fhp8) (high) | `1.9.0` | G |
| `mint 1.7.1` | [GHSA-2pg6-44cx-c49v](https://github.com/advisories/GHSA-2pg6-44cx-c49v) (low) | `1.9.0` | N |
| `mint 1.7.1` | [GHSA-g586-ccqf-7x4r](https://github.com/advisories/GHSA-g586-ccqf-7x4r) (high) | `1.9.0` | G |
| `mint 1.7.1` | [GHSA-mjqx-c6f6-7rc2](https://github.com/advisories/GHSA-mjqx-c6f6-7rc2) (medium) | `1.9.0` | G |
| `mint 1.7.1` | [GHSA-9x8p-qrf4-jq7g](https://github.com/advisories/GHSA-9x8p-qrf4-jq7g) (high) | `1.10.2` | G |
| `mint 1.7.1` | [GHSA-qrfr-wh4c-3qhw](https://github.com/advisories/GHSA-qrfr-wh4c-3qhw) (high) | `1.9.2` | G |
| `mint 1.7.1` | [GHSA-q95c-ccq6-j5j6](https://github.com/advisories/GHSA-q95c-ccq6-j5j6) (medium) | `1.10.2` | G |
| `mint 1.7.1` | [GHSA-gvrc-75rc-7gj9](https://github.com/advisories/GHSA-gvrc-75rc-7gj9) (medium) | `1.10.2` | G |
| `mint 1.7.1` | [GHSA-8pf6-g464-h6h9](https://github.com/advisories/GHSA-8pf6-g464-h6h9) (medium) | `1.9.2` | G |
| `mint 1.7.1` | [GHSA-c59h-fq4p-r36r](https://github.com/advisories/GHSA-c59h-fq4p-r36r) (high) | `1.9.1` | G |
| `mint 1.7.1` | [GHSA-g83f-2j6r-q6m4](https://github.com/advisories/GHSA-g83f-2j6r-q6m4) (high) | `1.10.0` | G |
| `mint 1.7.1` | [GHSA-x3x7-96vm-6h2w](https://github.com/advisories/GHSA-x3x7-96vm-6h2w) (medium) | `1.9.3` | G |
| `decimal 2.3.0` | [GHSA-rhv4-8758-jx7v](https://github.com/advisories/GHSA-rhv4-8758-jx7v) (medium) | `3.0.0` | C |
| `hpax 1.0.3` | [GHSA-jj2p-32j7-whj2](https://github.com/advisories/GHSA-jj2p-32j7-whj2) (high) | `1.0.4` | G |
| `plug 1.19.1` | [GHSA-j43x-5hjq-rgxf](https://github.com/advisories/GHSA-j43x-5hjq-rgxf) (high) | `1.19.3` | L |
| `plug 1.19.1` | [GHSA-468c-vq7p-gh64](https://github.com/advisories/GHSA-468c-vq7p-gh64) (high) | `1.19.2` | L |
| `plug 1.19.1` | [GHSA-wpmj-jh88-rpgm](https://github.com/advisories/GHSA-wpmj-jh88-rpgm) (low) | `1.19.5` | N |
| `plug 1.19.1` | [GHSA-95qv-c9g9-rm63](https://github.com/advisories/GHSA-95qv-c9g9-rm63) (medium) | `1.19.5` | L |

### Smallest compatible locked resolution found

The tested manifest changes in a disposable source archive are limited to `{:req, "~> 0.5"}` to `{:req, "~> 0.7"}` and one explicit `{:decimal, "~> 3.0", override: true}` entry. The override is needed because upstream Ecto and Solid still request Decimal 2.x. Their exercised Symphony behavior passed the full repository suite with Decimal 3. No Symphony application source file changed.

[`c3-symphony-hardened.mix.lock`](c3-symphony-hardened.mix.lock) is the exact tested lockfile (SHA-256 `296b13c88039f5912ef47bab3acbc1b68718aa4ee4a6eace28e36b6026f7d6b3`). Eleven package versions differ from upstream: the nine advisory-affected packages `bandit 1.12.5`, `decimal 3.1.1`, `hpax 1.1.0`, `lazy_html 0.1.13`, `mint 1.11.0`, `phoenix 1.8.15`, `phoenix_live_view 1.1.33`, `plug 1.20.3`, `req 0.7.4`; plus required `plug_crypto 2.2.0` and `thousand_island 1.5.0`. Restoring the other ten incidental solver updates preserved a valid resolution. Bandit requires Thousand Island 1.5 and Phoenix requires Plug Crypto 2.2. A blind update-all is not part of this contract.

Rebuild from the pinned upstream commit in a fresh `/tmp` directory; keep `/home/daniele/projects/symphony` untouched. Elixir 1.19.5 / OTP 28 are the tested toolchain. The official checkout stays upstream-pure and no fork is created. From the `codex-roadmap` root with `mix` on `PATH`:

```sh
roadmap_root=$(pwd)
scratch=$(mktemp -d /tmp/c3-symphony-cutover.XXXXXX)
git -C /home/daniele/projects/symphony archive 1c0fb6c8e8ef9031a2c861e62af5f9e66cee39cb | tar -x -C "$scratch"
python3 - "$scratch/elixir/mix.exs" <<'PYEDIT'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
assert s.count('{:req, "~> 0.5"}') == 1
assert s.count('{:ecto, "~> 3.13"},') == 1
s = s.replace('{:req, "~> 0.5"}', '{:req, "~> 0.7"}')
s = s.replace('{:ecto, "~> 3.13"},', '{:ecto, "~> 3.13"},\n      {:decimal, "~> 3.0", override: true},')
p.write_text(s)
PYEDIT
cp "$roadmap_root/operations/c3-symphony-hardened.mix.lock" "$scratch/elixir/mix.lock"
printf '%s  %s\n' 296b13c88039f5912ef47bab3acbc1b68718aa4ee4a6eace28e36b6026f7d6b3 "$scratch/elixir/mix.lock" | sha256sum -c -
cd "$scratch/elixir"
MIX_ENV=test make setup build test
MIX_ENV=test mix hex.audit
MIX_ENV=prod make setup build
MIX_ENV=prod mix hex.audit
sha256sum mix.lock bin/symphony
```

Observed in the disposable copy with the narrowed lock: test audit **0 advisories**, `mix setup` PASS, `mix build` PASS, `mix test` **299 tests, 0 failures, 6 skipped**; production `mix setup` PASS, production `mix build` PASS, production audit **0 advisories**. The production escript SHA-256 in this build was `25cdc28aaa8009ab1c3ef842b0925baa70923869000a557f8edafabc822b9c2b`. The prior Phoenix 1.8.15 `phoenix.js` failure did not reproduce with this pinned lock and toolchain; the production escript build succeeded and `deps/phoenix/priv/static/phoenix.js` exists.

### Cutover and rollback contract

- Install only the production escript built from the pinned source, two manifest edits, and exact hardened lock; update `c3-symphony.service` to point at that artifact before sending coding traffic. Verify its SHA-256 and rerun `MIX_ENV=prod mix hex.audit` from the build tree at deployment. Never point production at the old pilot binary or a fresh unpinned `mix deps.update` result.
- Keep the observability listener bound to `127.0.0.1` (`server.host`) and accessible only within the trusted-user host boundary. Keep the GitHub tracker endpoint/HTTPS fixed to the authenticated GitHub API and the credential in the existing systemd credential path. These are defense-in-depth conditions; **no dependency advisories remain in the chosen lock**.
- Preserve the pilot's existing one-issue-at-a-time dispatch, tracker-target, process-group stop, and reconciliation controls. Do not rerun pilot gates 1–4 for this security gate.
- Roll back to the existing C2 coding path and stop `c3-symphony.service` on any renewed advisory, lock/source drift, failed build/test/audit, non-loopback bind, unexpected outbound tracker endpoint, duplicate dispatch, orphan app-server, credential exposure, or lost tracker reconciliation/stop authority. Do not roll back to the vulnerable pilot binary. Preserve workspaces/logs for diagnosis; do not rewrite canonical roadmap state.
