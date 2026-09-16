from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from tools import ensure_git_filter_repo as helper


class EnsureGitFilterRepoTests(unittest.TestCase):
    def test_existing_binary_is_reused_without_install(self) -> None:
        with mock.patch.object(helper.shutil, "which", return_value="/usr/bin/git-filter-repo"), mock.patch.object(
            helper.venv.EnvBuilder, "create"
        ) as create:
            result = helper.ensure_git_filter_repo(Path("/tmp/unused"))

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["source"], "existing")
        self.assertEqual(result["executable"], "/usr/bin/git-filter-repo")
        create.assert_not_called()

    def test_ephemeral_root_must_be_under_tmp(self) -> None:
        with mock.patch.object(helper.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "under /tmp"):
                helper.ensure_git_filter_repo(Path.home() / "unsafe-git-filter-repo")

    def test_missing_binary_gets_pinned_ephemeral_environment(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temp:
            root = Path(temp) / "tool"
            commands: list[list[str]] = []

            def fake_create(self, env_dir: Path) -> None:  # noqa: ANN001
                del self
                bin_dir = Path(env_dir) / "bin"
                bin_dir.mkdir(parents=True)
                (bin_dir / "pip").write_text("", encoding="utf-8")
                (bin_dir / "git-filter-repo").write_text("#!/usr/bin/env python3\n", encoding="utf-8")

            def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
                commands.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

            with mock.patch.object(helper.shutil, "which", return_value=None), mock.patch.object(
                helper.venv.EnvBuilder, "create", fake_create
            ), mock.patch.object(helper, "_run", side_effect=fake_run):
                result = helper.ensure_git_filter_repo(root)

        self.assertEqual(result["source"], "ephemeral")
        self.assertTrue(any(helper.PINNED_PACKAGE in command for command in commands))
        self.assertTrue(any(command[-1] == "--version" for command in commands))

    def test_cleanup_is_bounded_to_tmp(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temp:
            root = Path(temp) / "tool"
            root.mkdir()
            result = helper.cleanup(root)
            self.assertFalse(root.exists())
            self.assertEqual(result["status"], "cleaned")


if __name__ == "__main__":
    unittest.main()
