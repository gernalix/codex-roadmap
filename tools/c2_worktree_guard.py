#!/usr/bin/env python3
"""Validate the dedicated C2 supervisor runtime worktree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

DEFAULT_CANONICAL = Path.home() / "projects/codex-roadmap"
DEFAULT_RUNTIME = Path.home() / ".local/share/c2-supervisor/worktree"
EXPECTED_BRANCH = "c2/supervisor-runtime"
EXPECTED_UPSTREAM = "main"
RUNTIME_PATHS = ("tools", "systemd")


class GuardError(RuntimeError):
    pass


def _git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        if check:
            raise GuardError(proc.stderr.strip() or "git_command_failed")
        return ""
    return proc.stdout.strip()

def _identity(repo: Path) -> tuple[Path, Path]:
    top = Path(_git(repo, "rev-parse", "--show-toplevel")).resolve()
    common = Path(_git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = (top / common).resolve()
    else:
        common = common.resolve()
    return top, common


def inspect_worktree(
    canonical: Path = DEFAULT_CANONICAL,
    runtime: Path = DEFAULT_RUNTIME,
    *,
    expected_branch: str = EXPECTED_BRANCH,
    expected_upstream: str = EXPECTED_UPSTREAM,
    runtime_paths: tuple[str, ...] = RUNTIME_PATHS,
) -> dict:
    canonical = canonical.expanduser().resolve()
    runtime = runtime.expanduser().resolve()
    issues: list[str] = []
    canonical_top, canonical_common = _identity(canonical)
    runtime_top, runtime_common = _identity(runtime)

    if canonical_top != canonical:
        issues.append("canonical_checkout_mismatch")
    if runtime_top != runtime:
        issues.append("runtime_worktree_mismatch")
    if runtime_common != canonical_common:
        issues.append("foreign_git_repository")

    branch = _git(runtime, "branch", "--show-current")
    if branch != expected_branch:
        issues.append("wrong_branch")

    upstream = _git(
        runtime,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        check=False,
    )
    if upstream != expected_upstream:
        issues.append("wrong_or_missing_upstream")

    dirty = bool(_git(runtime, "status", "--porcelain"))
    if dirty:
        issues.append("dirty_worktree")

    ahead = None
    if _git(runtime, "rev-parse", "--verify", expected_upstream, check=False):
        ahead = int(_git(runtime, "rev-list", "--count", f"{expected_upstream}..HEAD"))
        if ahead:
            issues.append("unpushed_or_unintegrated_commits")

        diff = subprocess.run(
            ["git", "-C", str(runtime), "diff", "--quiet", expected_upstream, "--", *runtime_paths]
        )
        if diff.returncode == 1:
            issues.append("runtime_code_drift")
        elif diff.returncode:
            raise GuardError("runtime_diff_failed")
    else:
        issues.append("missing_expected_upstream_ref")

    canonical_origin = _git(canonical, "remote", "get-url", "origin", check=False)
    runtime_origin = _git(runtime, "remote", "get-url", "origin", check=False)
    if not canonical_origin or runtime_origin != canonical_origin:
        issues.append("origin_mismatch")

    return {
        "state": "healthy" if not issues else "unhealthy",
        "issues": issues,
        "canonical_repo": str(canonical_top),
        "runtime_worktree": str(runtime_top),
        "branch": branch,
        "upstream": upstream or None,
        "ahead": ahead,
        "dirty": dirty,
    }


def sync_runtime_worktree(
    canonical: Path = DEFAULT_CANONICAL,
    runtime: Path = DEFAULT_RUNTIME,
    *,
    recover_equivalent_dirty: bool = False,
) -> dict:
    """Fast-forward a clean runtime branch to accepted local main, then guard it."""
    before = inspect_worktree(canonical, runtime)
    allowed = {"runtime_code_drift"}
    if recover_equivalent_dirty:
        allowed.add("dirty_worktree")
    if set(before["issues"]) - allowed:
        raise GuardError("unsafe_runtime_worktree:" + ",".join(before["issues"]))
    ancestor = subprocess.run(
        ["git", "-C", str(runtime), "merge-base", "--is-ancestor", "HEAD", "main"]
    )
    if ancestor.returncode:
        raise GuardError("runtime_not_ancestor_of_main")
    if before["dirty"]:
        # Only discard a local patch when every byte is already in accepted
        # main. Reject staged, untracked, deleted, renamed and symlink state.
        status = subprocess.run(
            ["git", "-C", str(runtime), "status", "--porcelain=v1", "-z"],
            check=True, stdout=subprocess.PIPE,
        ).stdout
        for entry in status.split(b"\0"):
            if not entry:
                continue
            if not entry.startswith(b" M "):
                raise GuardError("runtime_dirty_not_equivalent")
            relative = entry[3:].decode("utf-8", "surrogateescape")
            local = runtime / relative
            if not local.is_file() or local.is_symlink():
                raise GuardError("runtime_dirty_not_equivalent")
            accepted = subprocess.run(
                ["git", "-C", str(canonical), "show", "main:" + relative],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            if accepted.returncode or local.read_bytes() != accepted.stdout:
                raise GuardError("runtime_dirty_not_equivalent")
        _git(runtime, "reset", "--hard", "main")
    else:
        _git(runtime, "merge", "--ff-only", "main")
    after = inspect_worktree(canonical, runtime)
    if after["state"] != "healthy":
        raise GuardError("runtime_guard_after_sync:" + ",".join(after["issues"]))
    return after


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--expected-branch", default=EXPECTED_BRANCH)
    parser.add_argument("--expected-upstream", default=EXPECTED_UPSTREAM)
    parser.add_argument("--sync", action="store_true", help="Guarded fast-forward to local main before validation")
    parser.add_argument("--recover-equivalent-dirty", action="store_true",
                        help="With --sync, clear only tracked local bytes already identical to accepted main")
    args = parser.parse_args()
    if args.sync:
        if args.expected_branch != EXPECTED_BRANCH or args.expected_upstream != EXPECTED_UPSTREAM:
            raise GuardError("custom_sync_target_forbidden")
        result = sync_runtime_worktree(args.canonical, args.runtime,
                                       recover_equivalent_dirty=args.recover_equivalent_dirty)
    else:
        if args.recover_equivalent_dirty:
            raise GuardError("equivalent_recovery_requires_sync")
        result = inspect_worktree(
            args.canonical,
            args.runtime,
            expected_branch=args.expected_branch,
            expected_upstream=args.expected_upstream,
        )
    print(json.dumps(result, sort_keys=True))
    if result["state"] != "healthy":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
