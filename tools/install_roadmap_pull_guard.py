#!/usr/bin/env python3
"""Install the local Git guard that makes guarded roadmap pulls mandatory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


class InstallError(RuntimeError):
    pass


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise InstallError(proc.stderr.strip() or proc.stdout.strip() or "git_failed")
    return proc.stdout.strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install(repo: Path) -> dict[str, str]:
    repo = repo.expanduser().resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    source = root / ".githooks" / "reference-transaction"
    if not source.is_file():
        raise InstallError(f"tracked_hook_missing:{source}")
    raw_git_dir = Path(git(root, "rev-parse", "--git-dir"))
    git_dir = raw_git_dir if raw_git_dir.is_absolute() else (root / raw_git_dir).resolve()
    hooks = git_dir / "roadmap-hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    target = hooks / "reference-transaction"
    shutil.copyfile(source, target)
    os.chmod(target, 0o700)
    git(root, "config", "--local", "core.hooksPath", str(hooks))
    git(root, "config", "--local", "pull.ff", "only")
    configured = Path(git(root, "config", "--get", "core.hooksPath")).resolve()
    if configured != hooks.resolve() or digest(source) != digest(target):
        raise InstallError("guard_install_verification_failed")
    return {
        "status": "PASS",
        "hooks_path": str(hooks),
        "hook_sha256": digest(target),
        "pull_ff": git(root, "config", "--get", "pull.ff"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("~/projects/codex-roadmap"))
    args = parser.parse_args(argv)
    try:
        result = install(args.repo)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
