from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db
import roadmap_pull
from install_roadmap_pull_guard import install


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


class RoadmapPullTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.remote = base / "remote.git"
        self.seed = base / "seed"
        self.local = base / "local"

        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "init", "-b", "main", str(self.seed)], check=True, stdout=subprocess.DEVNULL)
        git(self.seed, "config", "user.name", "Test")
        git(self.seed, "config", "user.email", "test@example.com")

        (self.seed / "prompts").mkdir()
        (self.seed / "tools").mkdir()
        (self.seed / ".githooks").mkdir()
        shutil.copyfile(ROOT / ".githooks" / "reference-transaction", self.seed / ".githooks" / "reference-transaction")
        (self.seed / "prompts" / "one.md").write_text("PROMPT_ID=123456\n", encoding="utf-8")
        (self.seed / "README.md").write_text("base\n", encoding="utf-8")

        conn = db.connect(self.seed)
        db.register_prompt(
            conn,
            prompt_id="123456",
            slug="one",
            title="One",
            current_path="prompts/one.md",
            explanation="original",
            model="GPT-5.6 Terra",
            reasoning="medium",
            queue_position=1,
        )
        db.refresh_materialization_hashes(conn, self.seed)
        db.set_status(conn, "123456", "running", actor="codex", note="launch")
        conn.commit()
        conn.close()
        db.render(self.seed)

        git(self.seed, "add", ".")
        git(self.seed, "commit", "-m", "initial running roadmap")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")

        subprocess.run(
            ["git", "clone", "-b", "main", str(self.remote), str(self.local)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        git(self.local, "config", "user.name", "Test")
        git(self.local, "config", "user.email", "test@example.com")
        install(self.local)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def push_seed(self, message: str) -> str:
        git(self.seed, "add", "-A")
        git(self.seed, "commit", "-m", message)
        git(self.seed, "push", "origin", "main")
        return git(self.seed, "rev-parse", "HEAD").stdout.strip()

    def test_raw_git_pull_is_blocked_by_reference_transaction_hook(self) -> None:
        before = git(self.local, "rev-parse", "HEAD").stdout.strip()
        (self.seed / "README.md").write_text("remote\n", encoding="utf-8")
        remote_head = self.push_seed("remote change")

        proc = git(self.local, "pull", "--ff-only", check=False)

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("codex-roadmap main is guarded", proc.stderr)
        self.assertEqual(before, git(self.local, "rev-parse", "HEAD").stdout.strip())
        self.assertNotEqual(remote_head, before)

    def test_guarded_pull_preserves_running_prompt_and_view(self) -> None:
        (self.seed / "README.md").write_text("remote\n", encoding="utf-8")
        remote_head = self.push_seed("remote unrelated change")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(["123456"], result["preserved_running"])
        self.assertEqual(remote_head, git(self.local, "rev-parse", "HEAD").stdout.strip())
        conn = sqlite3.connect(self.local / "roadmap.sqlite")
        self.assertEqual("running", conn.execute("SELECT status FROM prompts WHERE prompt_id='123456'").fetchone()[0])
        conn.close()
        self.assertIn("| 123456 | running |", (self.local / "spiegazioni.md").read_text(encoding="utf-8"))

    def test_guarded_pull_does_not_depend_on_markdown_dashboard_state(self) -> None:
        (self.seed / "spiegazioni.md").write_text(
            "# intentionally stale compatibility view\n",
            encoding="utf-8",
        )
        (self.seed / "roadmap.md").write_text(
            "# intentionally stale compatibility view\n",
            encoding="utf-8",
        )
        remote_head = self.push_seed("stale generated views only")
        result = roadmap_pull.guarded_pull(self.local)
        self.assertEqual("PASS", result["status"])
        self.assertEqual(remote_head, result["head"])
        self.assertEqual(["123456"], result["preserved_running"])

    def test_guarded_pull_blocks_remote_operational_modification_of_running_prompt(self) -> None:
        before = git(self.local, "rev-parse", "HEAD").stdout.strip()
        conn = sqlite3.connect(self.seed / "roadmap.sqlite")
        conn.execute("UPDATE prompts SET model='GPT-5.6 Sol' WHERE prompt_id='123456'")
        conn.commit()
        conn.close()
        db.render(self.seed)
        self.push_seed("invalid running prompt mutation")

        with self.assertRaisesRegex(roadmap_pull.RoadmapPullBlocked, "running_prompt_modified_remote"):
            roadmap_pull.guarded_pull(self.local)

        self.assertEqual(before, git(self.local, "rev-parse", "HEAD").stdout.strip())

    def test_guarded_pull_allows_remote_explanation_update_for_running_prompt(self) -> None:
        conn = sqlite3.connect(self.seed / "roadmap.sqlite")
        conn.execute(
            "UPDATE prompts SET explanation='Simple dashboard explanation' WHERE prompt_id='123456'"
        )
        conn.commit()
        conn.close()
        db.render(self.seed)
        remote_head = self.push_seed("presentation-only explanation update")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(remote_head, result["head"])
        self.assertEqual(["123456"], result["preserved_running"])
        conn = sqlite3.connect(self.local / "roadmap.sqlite")
        try:
            explanation = conn.execute(
                "SELECT explanation FROM prompts WHERE prompt_id='123456'"
            ).fetchone()[0]
        finally:
            conn.close()
        self.assertEqual("Simple dashboard explanation", explanation)

    def test_generated_view_dirt_is_restored_before_guarded_pull(self) -> None:
        spiegazioni = self.local / "spiegazioni.md"
        spiegazioni.write_text(
            spiegazioni.read_text(encoding="utf-8") + "\nformatter-noise\n",
            encoding="utf-8",
        )
        (self.seed / "README.md").write_text("remote\n", encoding="utf-8")
        remote_head = self.push_seed("remote unrelated change")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual("PASS", result["status"])
        self.assertIn("spiegazioni.md", result["restored_generated_views"])
        self.assertEqual(remote_head, git(self.local, "rev-parse", "HEAD").stdout.strip())
        self.assertNotIn("formatter-noise", spiegazioni.read_text(encoding="utf-8"))

    def test_partial_remote_fast_forward_is_recovered_before_pull(self) -> None:
        conn = db.connect(self.seed)
        db.register_prompt(
            conn, prompt_id="654321", slug="two", title="Two",
            current_path="prompts/two.md", queue_position=2,
        )
        conn.commit()
        conn.close()
        (self.seed / "prompts" / "two.md").write_text("two\n", encoding="utf-8")
        db.render(self.seed)
        remote_head = self.push_seed("remote prompt")
        git(self.local, "fetch", "origin", "main")
        git(self.local, "restore", f"--source={remote_head}", "--staged", "--worktree", "--", ".")
        git(self.local, "restore", "--source=HEAD", "--worktree", "--", "roadmap.sqlite")
        self.assertEqual(0, git(self.local, "diff", "--cached", "--quiet", remote_head).returncode)

        first = roadmap_pull.guarded_pull(self.local)
        second = roadmap_pull.guarded_pull(self.local)

        self.assertEqual(remote_head, first["recovered_interrupted_fast_forward"])
        self.assertEqual("PASS", first["status"])
        self.assertEqual("PASS", second["status"])
        self.assertEqual("", git(self.local, "status", "--porcelain").stdout)

    def test_partial_fast_forward_does_not_discard_independent_db_edit(self) -> None:
        conn = db.connect(self.seed)
        db.register_prompt(
            conn, prompt_id="654321", slug="two", title="Two",
            current_path="prompts/two.md", queue_position=2,
        )
        conn.commit()
        conn.close()
        (self.seed / "prompts" / "two.md").write_text("two\n", encoding="utf-8")
        db.render(self.seed)
        remote_head = self.push_seed("remote prompt")
        git(self.local, "fetch", "origin", "main")
        git(self.local, "restore", f"--source={remote_head}", "--staged", "--worktree", "--", ".")
        conn = sqlite3.connect(self.local / "roadmap.sqlite")
        conn.execute("UPDATE prompts SET title='local change' WHERE prompt_id='123456'")
        conn.commit()
        conn.close()
        local_db = (self.local / "roadmap.sqlite").read_bytes()

        with self.assertRaisesRegex(roadmap_pull.RoadmapPullBlocked, "local_worktree_dirty_non_generated:.*roadmap.sqlite"):
            roadmap_pull.guarded_pull(self.local)

        self.assertEqual(local_db, (self.local / "roadmap.sqlite").read_bytes())

    def test_non_generated_dirt_still_blocks(self) -> None:
        (self.local / "README.md").write_text("local edit\n", encoding="utf-8")

        with self.assertRaisesRegex(
            roadmap_pull.RoadmapPullBlocked,
            "local_worktree_dirty_non_generated:README.md",
        ):
            roadmap_pull.guarded_pull(self.local)

    def test_c2_scratch_arguments_survive_guarded_pull(self) -> None:
        scratch = self.local / ".c2-checkpoint-args.json"
        contents = '{"work_item_id":"wi:test"}\n'
        scratch.write_text(contents, encoding="utf-8")
        (self.seed / "README.md").write_text("remote change\n", encoding="utf-8")
        remote_head = self.push_seed("remote change")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(remote_head, git(self.local, "rev-parse", "HEAD").stdout.strip())
        self.assertEqual(contents, scratch.read_text(encoding="utf-8"))

    def test_unrecognized_c2_scratch_still_blocks(self) -> None:
        scratch = self.local / ".c2-checkpoint-args.json"
        scratch.write_text("not JSON", encoding="utf-8")

        with self.assertRaisesRegex(roadmap_pull.RoadmapPullBlocked, "local_worktree_dirty_non_generated"):
            roadmap_pull.guarded_pull(self.local)
        self.assertEqual("not JSON", scratch.read_text(encoding="utf-8"))

    def test_c2_scratch_does_not_relax_main_branch_requirement(self) -> None:
        scratch = self.local / ".c2-checkpoint-args.json"
        scratch.write_text("{}", encoding="utf-8")
        git(self.local, "switch", "-c", "scratch-work")

        with self.assertRaisesRegex(roadmap_pull.RoadmapPullBlocked, "branch_mismatch"):
            roadmap_pull.guarded_pull(self.local)
        self.assertEqual("{}", scratch.read_text(encoding="utf-8"))

    def test_bootstrap_guard_installs_hook_before_merge(self) -> None:
        hooks_path = Path(git(self.local, "config", "--get", "core.hooksPath").stdout.strip())
        git(self.local, "config", "--unset", "core.hooksPath")
        shutil.rmtree(hooks_path)
        (self.seed / "README.md").write_text("remote\n", encoding="utf-8")
        remote_head = self.push_seed("remote bootstrap change")

        result = roadmap_pull.guarded_pull(self.local, bootstrap_guard=True)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(remote_head, git(self.local, "rev-parse", "HEAD").stdout.strip())
        installed = Path(git(self.local, "config", "--get", "core.hooksPath").stdout.strip())
        self.assertTrue((installed / "reference-transaction").is_file())

    def test_guarded_pull_refreshes_hook_after_remote_hook_change(self) -> None:
        tracked_hook = self.seed / ".githooks" / "reference-transaction"
        tracked_hook.write_text(
            tracked_hook.read_text(encoding="utf-8") + "\n# remote-update\n",
            encoding="utf-8",
        )
        self.push_seed("remote hook update")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual("PASS", result["status"])
        installed = Path(git(self.local, "config", "--get", "core.hooksPath").stdout.strip())
        self.assertEqual(
            (self.local / ".githooks" / "reference-transaction").read_bytes(),
            (installed / "reference-transaction").read_bytes(),
        )

    def test_unrelated_ref_update_does_not_consume_pull_authorization(self) -> None:
        head = git(self.local, "rev-parse", "HEAD").stdout.strip()
        auth = roadmap_pull._authorize_merge(self.local, head, head, "main")

        git(self.local, "tag", "unrelated-tag")

        self.assertTrue(auth.is_file())
        auth.unlink()


    def test_authoritative_terminal_request_allows_running_prompt_to_finish(self) -> None:
        conn = db.connect(self.seed)
        db.request_terminal(conn, "123456", "completed", actor="codex", note="explicit PASS")
        conn.commit()
        conn.close()
        db.reconcile_prompt_file_locations(self.seed)
        db.render(self.seed)
        self.push_seed("terminal request confirms finish")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual(["123456"], result["terminal_confirmed"])
        conn = sqlite3.connect(self.local / "roadmap.sqlite")
        self.assertEqual("completed", conn.execute("SELECT status FROM prompts WHERE prompt_id='123456'").fetchone()[0])
        conn.close()
        self.assertFalse((self.local / "prompts" / "one.md").exists())
        self.assertTrue((self.local / "completed" / "one.md").exists())


    def test_terminal_codex_usage_does_not_finish_running_prompt(self) -> None:
        conn = db.connect(self.seed)
        db.record_execution(
            conn,
            "123456",
            cycle_key="terminal-cycle",
            started_at="2026-09-19T00:00:00Z",
            ended_at="2026-09-19T00:01:00Z",
            outcome="PASS",
            source="codex-usage",
            allow_running_terminal=True,
        )
        conn.commit()
        conn.close()
        db.render(self.seed)
        self.push_seed("terminal usage is telemetry only")

        result = roadmap_pull.guarded_pull(self.local)

        self.assertEqual([], result["terminal_confirmed"])
        self.assertEqual(["123456"], result["preserved_running"])
        conn = sqlite3.connect(self.local / "roadmap.sqlite")
        self.assertEqual("running", conn.execute("SELECT status FROM prompts WHERE prompt_id='123456'").fetchone()[0])
        self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM executions WHERE prompt_id='123456'").fetchone()[0])
        conn.close()
        self.assertTrue((self.local / "prompts" / "one.md").exists())
        self.assertFalse((self.local / "completed" / "one.md").exists())


if __name__ == "__main__":
    unittest.main()
