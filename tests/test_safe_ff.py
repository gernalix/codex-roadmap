import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.safe_ff import SafeFFBlocked, safe_fast_forward


def git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


class SafeFastForwardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote = root / "remote.git"
        self.seed = root / "seed"
        self.local = root / "local"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "init", "-b", "main", str(self.seed)], check=True, stdout=subprocess.DEVNULL)
        git(self.seed, "config", "user.name", "Test")
        git(self.seed, "config", "user.email", "test@example.com")
        (self.seed / "tracked.txt").write_text("v1\n", encoding="utf-8")
        (self.seed / "data.sqlite").write_bytes(b"db-v1\x00")
        (self.seed / "notes.md").write_text("base\n", encoding="utf-8")
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "initial")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        subprocess.run(["git", "clone", "-b", "main", str(self.remote), str(self.local)], check=True, stdout=subprocess.DEVNULL)
        git(self.local, "config", "user.name", "Test")
        git(self.local, "config", "user.email", "test@example.com")

    def tearDown(self):
        self.tmp.cleanup()

    def push_remote_change(self, path: str, content: bytes) -> str:
        target = self.seed / path
        target.write_bytes(content)
        git(self.seed, "add", path)
        git(self.seed, "commit", "-m", f"update {path}")
        git(self.seed, "push", "origin", "main")
        return git(self.seed, "rev-parse", "HEAD")

    def test_all_disjoint_dirty_files_are_preserved_while_tracked_db_updates(self):
        modified = self.local / "notes.md"
        modified.write_text("local unsaved note\n", encoding="utf-8")
        untracked = self.local / "scratch.txt"
        untracked.write_text("local scratch\n", encoding="utf-8")
        expected_modified = modified.read_bytes()
        expected_untracked = untracked.read_bytes()
        remote_head = self.push_remote_change("data.sqlite", b"db-v2\x00")

        result = safe_fast_forward(
            self.local,
            remote="origin",
            branch="main",
            required_ancestor=remote_head,
        )

        self.assertEqual("PASS", result["status"])
        self.assertEqual(remote_head, git(self.local, "rev-parse", "HEAD"))
        self.assertEqual(b"db-v2\x00", (self.local / "data.sqlite").read_bytes())
        self.assertEqual(expected_modified, modified.read_bytes())
        self.assertEqual(expected_untracked, untracked.read_bytes())
        self.assertEqual(["notes.md", "scratch.txt"], result["dirty_preserved"])

    def test_disjoint_deleted_file_stays_deleted(self):
        (self.local / "notes.md").unlink()
        remote_head = self.push_remote_change("data.sqlite", b"db-v2\x00")

        result = safe_fast_forward(
            self.local,
            remote="origin",
            branch="main",
            required_ancestor=remote_head,
        )

        self.assertEqual("PASS", result["status"])
        self.assertFalse((self.local / "notes.md").exists())
        self.assertIn("notes.md", result["dirty_preserved"])

    def test_requested_preserve_path_must_actually_be_dirty(self):
        with self.assertRaisesRegex(SafeFFBlocked, "requested preserve path is not dirty"):
            safe_fast_forward(
                self.local,
                remote="origin",
                branch="main",
                preserve=("notes.md",),
            )

    def test_dirty_overlap_blocks_without_advancing_head(self):
        (self.local / "tracked.txt").write_text("local change\n", encoding="utf-8")
        before = git(self.local, "rev-parse", "HEAD")
        self.push_remote_change("tracked.txt", b"remote change\n")

        with self.assertRaisesRegex(SafeFFBlocked, "dirty/remote overlap"):
            safe_fast_forward(self.local, remote="origin", branch="main")

        self.assertEqual(before, git(self.local, "rev-parse", "HEAD"))
        self.assertEqual("local change\n", (self.local / "tracked.txt").read_text(encoding="utf-8"))

    def test_divergence_blocks_without_merge(self):
        (self.local / "local-only.txt").write_text("local\n", encoding="utf-8")
        git(self.local, "add", "local-only.txt")
        git(self.local, "commit", "-m", "local commit")
        before = git(self.local, "rev-parse", "HEAD")
        self.push_remote_change("tracked.txt", b"remote divergent\n")

        with self.assertRaisesRegex(SafeFFBlocked, "not an ancestor"):
            safe_fast_forward(self.local, remote="origin", branch="main")

        self.assertEqual(before, git(self.local, "rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
