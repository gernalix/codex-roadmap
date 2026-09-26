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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--expected-branch", default=EXPECTED_BRANCH)
    parser.add_argument("--expected-upstream", default=EXPECTED_UPSTREAM)
    args = parser.parse_args()
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
