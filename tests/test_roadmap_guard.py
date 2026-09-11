from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "roadmap_guard.py"
spec = importlib.util.spec_from_file_location("roadmap_guard", MODULE)
guard = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(guard)


def git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


class RoadmapGuardTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path]:
        bare = root / "remote.git"
        seed = root / "seed"
        local = root / "local"
        self.assertEqual(0, git(["init", "--bare", str(bare)]).returncode)
        self.assertEqual(0, git(["clone", str(bare), str(seed)]).returncode)
        git(["config", "user.email", "test@example.invalid"], seed)
        git(["config", "user.name", "Test"], seed)
        (seed / "prompts").mkdir()
        (seed / "completed").mkdir()
        (seed / "roadmap.md").write_text("1. [[prompts/first|first]]\n2. [[prompts/second|second]]\n", encoding="utf-8")
        (seed / "spiegazioni.md").write_text(
            "| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |\n"
            "|---|---|---|---|---|\n"
            "| 1 | [[prompts/first|first]] | First | medium | Prompt |\n"
            "| 2 | [[prompts/second|second]] | Second | low | Prompt |\n",
            encoding="utf-8",
        )
        (seed / "prompts" / "first.md").write_text("`PROMPT_ID=123456 | reasoning=medium`\n", encoding="utf-8")
        (seed / "prompts" / "second.md").write_text("`PROMPT_ID=654321 | reasoning=low`\n", encoding="utf-8")
        (seed / "README.md").write_text("base\n", encoding="utf-8")
        git(["add", "."], seed)
        git(["commit", "-m", "seed"], seed)
        git(["branch", "-M", "main"], seed)
        git(["push", "-u", "origin", "main"], seed)
        self.assertEqual(0, git(["clone", str(bare), str(local)]).returncode)
        git(["config", "user.email", "test@example.invalid"], local)
        git(["config", "user.name", "Test"], local)
        git(["checkout", "main"], local)
        return local, bare

    def test_select_reads_origin_without_touching_dirty_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local, _ = self.fixture(Path(tmp))
            (local / "README.md").write_text("dirty\n", encoding="utf-8")
            before = git(["status", "--porcelain"], local).stdout
            selected = guard.first_prompt(local)
            after = git(["status", "--porcelain"], local).stdout
            self.assertEqual("123456", selected["prompt_id"])
            self.assertEqual(before, after)

    def test_complete_uses_isolated_worktree_and_preserves_local_dirt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local, bare = self.fixture(Path(tmp))
            (local / "README.md").write_text("dirty\n", encoding="utf-8")
            result = guard.complete(local, "123456")
            self.assertEqual("completed", result["status"])
            self.assertEqual("dirty\n", (local / "README.md").read_text(encoding="utf-8"))
            verify = Path(tmp) / "verify"
            self.assertEqual(0, git(["clone", "--branch", "main", str(bare), str(verify)]).returncode)
            self.assertFalse((verify / "prompts" / "first.md").exists())
            self.assertTrue((verify / "completed" / "first.md").exists())
            self.assertEqual("1. [[prompts/second|second]]\n", (verify / "roadmap.md").read_text(encoding="utf-8"))
            self.assertIn("| 1 | [[prompts/second|second]]", (verify / "spiegazioni.md").read_text(encoding="utf-8"))
            changed = git(["show", "--name-only", "--format="], verify).stdout.splitlines()
            self.assertNotIn("README.md", changed)

    def test_wrong_prompt_id_blocks_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local, bare = self.fixture(Path(tmp))
            before = git(["--git-dir", str(bare), "rev-parse", "refs/heads/main"]).stdout.strip()
            with self.assertRaises(guard.RoadmapError):
                guard.complete(local, "654321")
            after = git(["--git-dir", str(bare), "rev-parse", "refs/heads/main"]).stdout.strip()
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
