#!/usr/bin/env python3
"""Build and install the audited Symphony escript from one pinned source tree."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


SOURCE_COMMIT = "1c0fb6c8e8ef9031a2c861e62af5f9e66cee39cb"
UPSTREAM_LOCK_SHA256 = "f707a715e6a4e91fc865c1c78d286a5211759a94659caa87e6cd6bad12a6f90c"
HARDENED_LOCK_SHA256 = "296b13c88039f5912ef47bab3acbc1b68718aa4ee4a6eace28e36b6026f7d6b3"
ARTIFACT_SHA256 = "25cdc28aaa8009ab1c3ef842b0925baa70923869000a557f8edafabc822b9c2b"
ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT/"operations/c3-symphony-hardened.mix.lock"
DESTINATION = Path.home()/".local/share/c3-symphony/bin/symphony"


class InstallError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hash(path: Path, expected: str) -> None:
    if sha256(path) != expected:
        raise InstallError("hash_mismatch:" + path.name)


def command(*args: str, cwd: Path | None = None, env: dict | None = None) -> bytes:
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, check=False)
    if result.returncode:
        raise InstallError("command_failed:" + " ".join(args[:3]))
    return result.stdout


def prepare(source: Path, scratch: Path) -> Path:
    commit = command("git", "-C", str(source), "rev-parse", SOURCE_COMMIT).decode().strip()
    if commit != SOURCE_COMMIT:
        raise InstallError("source_commit_mismatch")
    archive = scratch/"source.tar"
    archive.write_bytes(command("git", "-C", str(source), "archive", SOURCE_COMMIT))
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            target = (scratch/"source"/member.name).resolve()
            if not target.is_relative_to((scratch/"source").resolve()):
                raise InstallError("archive_path_escape")
        tar.extractall(scratch/"source", filter="data")
    elixir = scratch/"source/elixir"
    require_hash(elixir/"mix.lock", UPSTREAM_LOCK_SHA256)
    require_hash(LOCK, HARDENED_LOCK_SHA256)
    manifest = elixir/"mix.exs"
    body = manifest.read_text(encoding="utf-8")
    edits = [
        ('{:req, "~> 0.5"}', '{:req, "~> 0.7"}'),
        ('{:ecto, "~> 3.13"},', '{:ecto, "~> 3.13"},\n      {:decimal, "~> 3.0", override: true},'),
    ]
    for old, new in edits:
        if body.count(old) != 1:
            raise InstallError("manifest_edit_anchor_mismatch")
        body = body.replace(old, new)
    manifest.write_text(body, encoding="utf-8")
    shutil.copyfile(LOCK, elixir/"mix.lock")
    require_hash(elixir/"mix.lock", HARDENED_LOCK_SHA256)
    return elixir


def build(source: Path, destination: Path = DESTINATION) -> Path:
    if shutil.which("mix") is None or shutil.which("make") is None:
        raise InstallError("elixir_build_toolchain_missing_from_path")
    with tempfile.TemporaryDirectory(prefix="c3-symphony-cutover-", dir="/tmp") as directory:
        elixir = prepare(source, Path(directory))
        env = {**os.environ, "MIX_ENV": "prod"}
        command("make", "setup", cwd=elixir, env=env)
        command("make", "build", cwd=elixir, env=env)
        command("mix", "hex.audit", cwd=elixir, env=env)
        require_hash(elixir/"mix.lock", HARDENED_LOCK_SHA256)
        artifact = elixir/"bin/symphony"
        require_hash(artifact, ARTIFACT_SHA256)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".symphony-", delete=False) as target:
            staged = Path(target.name)
            target.write(artifact.read_bytes())
        try:
            staged.chmod(0o755)
            require_hash(staged, ARTIFACT_SHA256)
            os.replace(staged, destination)
        finally:
            staged.unlink(missing_ok=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path.home()/"projects/symphony")
    args = parser.parse_args()
    print(build(args.source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
