from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c2_worktree_guard import inspect_worktree


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


class C2WorktreeGuardTests(unittest.TestCase):
    def make_repo(self, root: Path) -> tuple[Path, Path]:
        repo = root / "codex-roadmap"
        repo.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, stdout=subprocess.PIPE)
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "C2 Test")
        git(repo, "remote", "add", "origin", "https://example.invalid/codex-roadmap.git")
        (repo / "tools").mkdir()
        (repo / "systemd").mkdir()
        (repo / "tools" / "runtime.py").write_text("v1\n")
        (repo / "systemd" / "runtime.service").write_text("v1\n")
        git(repo, "add", ".")
        git(repo, "commit", "-m", "base")
        runtime = root / "runtime"
        git(repo, "worktree", "add", "-b", "c2/supervisor-runtime", str(runtime), "main")
        git(runtime, "branch", "--set-upstream-to=main", "c2/supervisor-runtime")
        return repo, runtime

    def test_clean_runtime_worktree_is_healthy(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            result = inspect_worktree(repo, runtime)
            self.assertEqual(result["state"], "healthy")
            self.assertEqual(result["upstream"], "main")
            self.assertEqual(result["ahead"], 0)

    def test_dirty_runtime_worktree_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            (runtime / "dirty.txt").write_text("dirty\n")
            result = inspect_worktree(repo, runtime)
            self.assertIn("dirty_worktree", result["issues"])

    def test_ahead_commit_is_rejected_even_outside_runtime_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            (runtime / "checkpoint.txt").write_text("local\n")
            git(runtime, "add", "checkpoint.txt")
            git(runtime, "commit", "-m", "local-only")
            result = inspect_worktree(repo, runtime)
            self.assertIn("unpushed_or_unintegrated_commits", result["issues"])
    def test_runtime_code_drift_from_main_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            (repo / "tools" / "runtime.py").write_text("v2\n")
            git(repo, "add", "tools/runtime.py")
            git(repo, "commit", "-m", "runtime update")
            result = inspect_worktree(repo, runtime)
            self.assertEqual(result["ahead"], 0)
            self.assertIn("runtime_code_drift", result["issues"])

    def test_missing_upstream_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            git(runtime, "branch", "--unset-upstream")
            result = inspect_worktree(repo, runtime)
            self.assertIsNone(result["upstream"])
            self.assertIn("wrong_or_missing_upstream", result["issues"])

    def test_wrong_branch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, runtime = self.make_repo(Path(directory))
            git(runtime, "branch", "-m", "wrong")
            result = inspect_worktree(repo, runtime)
            self.assertIn("wrong_branch", result["issues"])


if __name__ == "__main__":
    unittest.main()
