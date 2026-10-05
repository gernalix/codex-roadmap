> FROZEN C3 ARCHIVE (2026-10-05). Historical reference only. Do not execute these operating instructions. Current task flow: /home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md.

# Project Capsule v1

A capsule is the local entry point for a new executor. Put `project-capsule.yaml` at the repository root, with concise `AGENTS.md` and linked local architecture, operations and data model documents where relevant. The [JSON Schema](schema-v1.json) defines the machine readable contract; [template.yaml](template.yaml) is the starting point. The manifest records project facts and executable commands, while source paths and the freshness review commit make those facts checkable.

## Authority and coverage

MegaVault `megavault.sqlite` owns project IDs, repository locations, services, databases and cross-project routing. C2 `roadmap.sqlite` owns work items and lifecycle. The capsule names their identifiers and links to them; it does not copy inventories, task status, secrets, or global protocols. Local source and configuration own local architecture and commands. A mismatch is a failing check, never an invitation to silently reconcile an authority.

The MegaVault `capsule_inventory` view is the coverage input. A canonical repository of an active or plausibly reusable project is eligible. Exclude only obsolete, generated, vendor, mirror, throwaway, or fully absorbed repositories, with an explicit reason in `capsule_repository_policy` when the derived view is insufficient. Remote-only services still need a capsule in their source repository or a linked C2 adoption task; lack of a local worktree is a blocker, not an exclusion. One capsule per canonical source repository; do not add copies to task worktrees.

## Verification contract

`python3 tools/project_capsule.py --repo PATH --mode FAST` is the deterministic preflight. FAST parses the manifest, checks schema-required fields, project identity against the read-only MegaVault DB when available, relative paths, command argv, and freshness. It never runs declared project commands or touches runtime resources. `--mode FULL` additionally runs only hooks marked `safe: true`, with a timeout and no shell. The command emits JSON with per-check evidence and exits 0 only on PASS. Use `--changed-file PATH` for each changed file to require a mapped minimum verification command. If MegaVault is unavailable, identity is `unverified`, not PASS.

Every repository exposes a single `verify.fast` and `verify.full` argv in its capsule. Full verification must include the project's appropriate tests/static checks, but release, deployment, device, data mutation and destructive commands remain manual and separate. `commands` carries canonical setup/build/test/lint/deploy/smoke entry points; `not_applicable` explains absent capabilities.

`freshness.reviewed_commit` is an ancestor commit whose code/config `watch_paths` were reviewed for the capsule. A changed watched path between that commit and HEAD, or a dirty watched path, fails freshness until a maintainer reviews the capsule and advances the commit. Watch architecture, DB migrations, service definitions, dependencies and command definitions. A capsule edit without corresponding review must not auto-advance the commit. CI should run FAST on capsule or watched-path changes; scheduled MegaVault `capsule-check` may record inventory evidence, not rewrite local facts.

## Adoption acceptance

For each eligible repository, verify identity and canonical workdir from MegaVault; write the manifest and only essential local docs; verify FAST; run safe targeted tests; review FULL coverage and risky operations; deliver via isolated worktree and integration PR. Mark adoption complete only after the integrated head passes verification. Parent C2 work remains nonterminal while repository children are pending. The separate Capsule Score item owns aggregate scoring; this contract supplies raw checks only.
