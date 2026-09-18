#!/usr/bin/env python3
"""Fail-closed fast-forward that preserves unrelated local dirty work."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


class SafeFFBlocked(RuntimeError):
    pass


def _git(repo: Path, *args: str, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SafeFFBlocked(f"git timeout: {' '.join(args)}") from exc


def _git_ok(repo: Path, *args: str, timeout: int = 20) -> str:
    result = _git(repo, *args, timeout=timeout)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit={result.returncode}"
        raise SafeFFBlocked(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def _nul_paths(raw: str) -> set[str]:
    return {part for part in raw.split("\0") if part}


def dirty_paths(repo: Path) -> set[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        result = _git(repo, *args)
        if result.returncode != 0:
            raise SafeFFBlocked(f"cannot inspect dirty paths: {' '.join(args)}")
        paths.update(_nul_paths(result.stdout))
    return paths


def summarize_paths(paths: set[str] | list[str] | tuple[str, ...], *, limit: int = 10) -> str:
    ordered = sorted(set(paths))
    shown = ", ".join(ordered[:limit])
    remaining = len(ordered) - limit
    return f"{shown}, ... (+{remaining} more)" if remaining > 0 else shown


def _git_dir(repo: Path) -> Path:
    value = _git_ok(repo, "rev-parse", "--git-dir")
    path = Path(value)
    return path if path.is_absolute() else repo / path


def _operation_in_progress(repo: Path) -> str | None:
    git_dir = _git_dir(repo)
    sentinels = {
        "MERGE_HEAD": git_dir / "MERGE_HEAD",
        "CHERRY_PICK_HEAD": git_dir / "CHERRY_PICK_HEAD",
        "REVERT_HEAD": git_dir / "REVERT_HEAD",
        "rebase-merge": git_dir / "rebase-merge",
        "rebase-apply": git_dir / "rebase-apply",
    }
    return next((name for name, path in sentinels.items() if path.exists()), None)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot_path(path: Path) -> tuple[str, str]:
    if path.is_symlink():
        return ("symlink", os.readlink(path))
    if path.is_file():
        return ("file", _sha256(path))
    if not path.exists():
        return ("missing", "")
    raise SafeFFBlocked(f"dirty path is not safely snapshotable: {path}")


def snapshot_dirty(repo: Path, paths: set[str]) -> dict[str, tuple[str, str]]:
    return {relative: _snapshot_path(repo / relative) for relative in sorted(paths)}


def safe_fast_forward(
    repo: Path,
    *,
    remote: str,
    branch: str,
    required_ancestor: str | None = None,
    preserve: tuple[str, ...] = (),
    fetch_timeout: int = 20,
) -> dict[str, object]:
    repo = repo.resolve()
    current_branch = _git_ok(repo, "branch", "--show-current")
    if current_branch != branch:
        raise SafeFFBlocked(f"branch mismatch: expected={branch} actual={current_branch or 'DETACHED'}")
    in_progress = _operation_in_progress(repo)
    if in_progress:
        raise SafeFFBlocked(f"git operation in progress: {in_progress}")

    before_head = _git_ok(repo, "rev-parse", "HEAD")
    dirty_before = dirty_paths(repo)
    missing_requested = sorted(set(preserve) - dirty_before)
    if missing_requested:
        raise SafeFFBlocked(
            "requested preserve path is not dirty: " + ", ".join(missing_requested)
        )
    dirty_snapshot = snapshot_dirty(repo, dirty_before)

    # Update the configured remote-tracking ref explicitly. This keeps the
    # subsequent ancestry/diff checks tied to the exact branch being fetched.
    refspec = f"refs/heads/{branch}:refs/remotes/{remote}/{branch}"
    _git_ok(repo, "fetch", remote, refspec, timeout=fetch_timeout)
    remote_ref = f"{remote}/{branch}"
    remote_head = _git_ok(repo, "rev-parse", remote_ref)
    ancestor = _git(repo, "merge-base", "--is-ancestor", before_head, remote_ref)
    if ancestor.returncode != 0:
        raise SafeFFBlocked(f"local HEAD is not an ancestor of {remote_ref}")

    changed = _git(repo, "diff", "--name-only", "-z", before_head, remote_ref)
    if changed.returncode != 0:
        raise SafeFFBlocked("cannot inspect remote changed paths")
    remote_changed = _nul_paths(changed.stdout)
    overlap = sorted(dirty_before & remote_changed)
    if overlap:
        raise SafeFFBlocked("dirty/remote overlap: " + ", ".join(overlap))

    merge = _git(repo, "merge", "--ff-only", remote_ref)
    if merge.returncode != 0:
        detail = merge.stderr.strip() or merge.stdout.strip() or f"exit={merge.returncode}"
        raise SafeFFBlocked(f"fast-forward failed: {detail}")

    after_head = _git_ok(repo, "rev-parse", "HEAD")
    if after_head != remote_head:
        raise SafeFFBlocked(f"post-merge HEAD mismatch: head={after_head} remote={remote_head}")
    if required_ancestor:
        required = _git(repo, "merge-base", "--is-ancestor", required_ancestor, "HEAD")
        if required.returncode != 0:
            raise SafeFFBlocked(f"required ancestor missing: {required_ancestor}")

    dirty_after = snapshot_dirty(repo, dirty_before)
    changed_dirty = sorted(
        relative
        for relative, before_state in dirty_snapshot.items()
        if dirty_after.get(relative) != before_state
    )
    if changed_dirty:
        raise SafeFFBlocked(
            "local dirty work changed during fast-forward: " + ", ".join(changed_dirty)
        )

    return {
        "status": "PASS",
        "before_head": before_head,
        "head": after_head,
        "remote_ref": remote_ref,
        "remote_changed_count": len(remote_changed),
        "dirty_count": len(dirty_before),
        "dirty_preserved": sorted(dirty_before),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--required-ancestor")
    parser.add_argument(
        "--preserve",
        action="append",
        default=[],
        help="Optional dirty path that must be present; all dirty paths are preserved automatically.",
    )
    parser.add_argument("--fetch-timeout", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        result = safe_fast_forward(
            args.repo,
            remote=args.remote,
            branch=args.branch,
            required_ancestor=args.required_ancestor,
            preserve=tuple(args.preserve),
            fetch_timeout=args.fetch_timeout,
        )
    except SafeFFBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
