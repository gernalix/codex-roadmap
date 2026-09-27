"""Derive the minimal Codex workspace-write policy for one assigned Git worktree."""
from __future__ import annotations

from pathlib import Path
import subprocess


class SandboxPathError(RuntimeError):
    pass


def _git_path(worktree: Path, argument: str) -> Path:
    result = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--path-format=absolute", argument],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise SandboxPathError("git_metadata_path_unavailable:" + argument.removeprefix("--"))
    path = Path(result.stdout.strip()).resolve()
    if not path.is_dir():
        raise SandboxPathError("git_metadata_path_missing:" + argument.removeprefix("--"))
    return path


def git_metadata_writable_roots(worktree: str | Path) -> list[str]:
    """Return only out-of-workspace Git metadata ancestors needed by Git writes."""
    root = Path(worktree).expanduser().resolve()
    if not root.is_dir():
        raise SandboxPathError("assigned_worktree_missing")
    git_dir = _git_path(root, "--git-dir")
    common_dir = _git_path(root, "--git-common-dir")
    candidates = [path for path in (git_dir, common_dir) if not path.is_relative_to(root)]
    minimal: list[Path] = []
    for path in sorted(set(candidates), key=lambda value: (len(value.parts), str(value))):
        if not any(path == parent or path.is_relative_to(parent) for parent in minimal):
            minimal.append(path)
    return [str(path) for path in minimal]


def workspace_write_policy(worktree: str | Path) -> dict:
    return {
        "type": "workspaceWrite",
        "writableRoots": git_metadata_writable_roots(worktree),
        "networkAccess": False,
    }
