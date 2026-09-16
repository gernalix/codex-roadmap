#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

PINNED_PACKAGE = "git-filter-repo==2.47.0"
DEFAULT_ROOT = Path("/tmp") / f"codex-git-filter-repo-{os.getuid()}"


def _under_tmp(path: Path) -> bool:
    tmp = Path("/tmp").resolve()
    resolved = path.expanduser().resolve()
    return resolved == tmp or tmp in resolved.parents


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=180,
    )


def ensure_git_filter_repo(root: Path = DEFAULT_ROOT) -> dict[str, str]:
    existing = shutil.which("git-filter-repo")
    if existing:
        return {"status": "ready", "source": "existing", "executable": existing}

    root = root.expanduser().resolve()
    if not _under_tmp(root):
        raise RuntimeError("ephemeral git-filter-repo root must be under /tmp")

    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)

    env_dir = root / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    pip = env_dir / "bin" / "pip"
    executable = env_dir / "bin" / "git-filter-repo"
    install = _run(
        [
            str(pip),
            "install",
            "--disable-pip-version-check",
            "--no-input",
            "--no-deps",
            PINNED_PACKAGE,
        ]
    )
    if install.returncode != 0 or not executable.is_file():
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError("failed to provision pinned git-filter-repo in ephemeral venv")

    probe = _run([str(executable), "--version"])
    if probe.returncode != 0:
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError("ephemeral git-filter-repo failed its version probe")

    return {"status": "ready", "source": "ephemeral", "executable": str(executable)}


def cleanup(root: Path = DEFAULT_ROOT) -> dict[str, str]:
    root = root.expanduser().resolve()
    if not _under_tmp(root):
        raise RuntimeError("cleanup root must be under /tmp")
    shutil.rmtree(root, ignore_errors=True)
    return {"status": "cleaned", "root": str(root)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve git-filter-repo without global installation. If absent, create a pinned "
            "ephemeral venv under /tmp and print only non-secret JSON metadata."
        )
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = cleanup(args.root) if args.cleanup else ensure_git_filter_repo(args.root)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
