from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
MODULE = TOOLS / "roadmap_finish.py"
spec = importlib.util.spec_from_file_location("roadmap_finish", MODULE)
finish_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(finish_module)


def git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class RoadmapFinishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_complete = finish_module.complete
        self.original_reconcile = finish_module.reconcile
        self.original_cleanup = finish_module._cleanup_failed_race_worktree

    def tearDown(self) -> None:
        finish_module.complete = self.original_complete
        finish_module.reconcile = self.original_reconcile
        finish_module._cleanup_failed_race_worktree = self.original_cleanup

    def test_selected_prompt_completes_directly(self) -> None:
        calls: list[str] = []

        def fake_complete(repo, prompt_id, *, dry_run=False, result=None):
            calls.append("complete")
            self.assertEqual("PASS", result)
            return {"status": "completed", "prompt_id": prompt_id}

        def fake_reconcile(*args, **kwargs):
            calls.append("reconcile")
            raise AssertionError("reconcile must not run")

        finish_module.complete = fake_complete
        finish_module.reconcile = fake_reconcile
        result = finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)
        self.assertEqual(["complete"], calls)
        self.assertEqual("complete", result["finish_mode"])
        self.assertEqual("0", result["push_race_retries"])

    def test_advanced_roadmap_reconciles_in_same_invocation(self) -> None:
        calls: list[str] = []

        def fake_complete(*args, **kwargs):
            calls.append("complete")
            raise finish_module.RoadmapError(
                "prompt_identity_mismatch:selected=654321:requested=123456:"
                "if_requested_task_is_already_executed_use_reconcile"
            )

        def fake_reconcile(repo, prompt_id, *, dry_run=False, confirm_executed=False, result=None):
            calls.append("reconcile")
            self.assertTrue(confirm_executed)
            self.assertEqual("PASS", result)
            return {"status": "completed", "prompt_id": prompt_id, "mode": "reconcile"}

        finish_module.complete = fake_complete
        finish_module.reconcile = fake_reconcile
        result = finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)
        self.assertEqual(["complete", "reconcile"], calls)
        self.assertEqual("reconcile", result["finish_mode"])

    def test_mutating_reconcile_requires_explicit_execution_confirmation(self) -> None:
        def fake_complete(*args, **kwargs):
            raise finish_module.RoadmapError(
                "prompt_identity_mismatch:selected=654321:requested=123456:"
                "if_requested_task_is_already_executed_use_reconcile"
            )

        finish_module.complete = fake_complete
        with self.assertRaisesRegex(
            finish_module.RoadmapError,
            "finish_requires_confirm_executed_after_roadmap_advance",
        ):
            finish_module.finish(Path("/tmp/repo"), "123456")

    def test_dry_run_can_preview_reconcile_without_confirmation(self) -> None:
        def fake_complete(*args, **kwargs):
            raise finish_module.RoadmapError(
                "prompt_identity_mismatch:selected=654321:requested=123456:"
                "if_requested_task_is_already_executed_use_reconcile"
            )

        def fake_reconcile(repo, prompt_id, *, dry_run=False, confirm_executed=False, result=None):
            self.assertTrue(dry_run)
            self.assertFalse(confirm_executed)
            return {"status": "reconcile_ready", "prompt_id": prompt_id}

        finish_module.complete = fake_complete
        finish_module.reconcile = fake_reconcile
        result = finish_module.finish(Path("/tmp/repo"), "123456", dry_run=True)
        self.assertEqual("reconcile", result["finish_mode"])

    def test_concurrent_non_fast_forward_push_is_retried_from_fresh_state(self) -> None:
        calls: list[str] = []
        cleanups: list[str] = []

        def fake_complete(repo, prompt_id, *, dry_run=False, result=None):
            calls.append("complete")
            if len(calls) == 1:
                raise finish_module.RoadmapError(
                    "push_blocked:! [rejected] HEAD -> main (fetch first) "
                    "failed to push some refs:isolated_worktree=/tmp/codex-roadmap-a/worktree"
                )
            raise finish_module.RoadmapError(
                "prompt_identity_mismatch:selected=654321:requested=123456:"
                "if_requested_task_is_already_executed_use_reconcile"
            )

        def fake_reconcile(repo, prompt_id, *, dry_run=False, confirm_executed=False, result=None):
            calls.append("reconcile")
            return {"status": "completed", "prompt_id": prompt_id, "mode": "reconcile"}

        finish_module.complete = fake_complete
        finish_module.reconcile = fake_reconcile
        finish_module._cleanup_failed_race_worktree = lambda repo, exc: cleanups.append(str(exc))

        result = finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)
        self.assertEqual(["complete", "complete", "reconcile"], calls)
        self.assertEqual(1, len(cleanups))
        self.assertEqual("1", result["push_race_retries"])
        self.assertEqual("reconcile", result["finish_mode"])

    def test_auth_or_network_push_failure_is_not_retried(self) -> None:
        calls = 0

        def fake_complete(*args, **kwargs):
            nonlocal calls
            calls += 1
            raise finish_module.RoadmapError("push_blocked:fatal: authentication failed")

        finish_module.complete = fake_complete
        with self.assertRaisesRegex(finish_module.RoadmapError, "authentication failed"):
            finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)
        self.assertEqual(1, calls)

    def test_retryable_push_race_is_bounded(self) -> None:
        calls = 0

        def fake_complete(*args, **kwargs):
            nonlocal calls
            calls += 1
            raise finish_module.RoadmapError(
                "push_blocked:! [rejected] HEAD -> main (non-fast-forward):"
                "isolated_worktree=/tmp/codex-roadmap-race/worktree"
            )

        finish_module.complete = fake_complete
        finish_module._cleanup_failed_race_worktree = lambda repo, exc: None
        with self.assertRaisesRegex(finish_module.RoadmapError, "non-fast-forward"):
            finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)
        self.assertEqual(finish_module.MAX_PUSH_RACE_RETRIES + 1, calls)

    def test_real_concurrent_reconcile_pushes_both_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bare = root / "remote.git"
            seed = root / "seed"
            local_a = root / "local-a"
            local_b = root / "local-b"

            self.assertEqual(0, git(["init", "--bare", str(bare)]).returncode)
            self.assertEqual(0, git(["clone", str(bare), str(seed)]).returncode)
            git(["config", "user.email", "test@example.invalid"], seed)
            git(["config", "user.name", "Test"], seed)
            (seed / "prompts").mkdir()
            (seed / "completed").mkdir()
            names = (("first", "123456"), ("second", "654321"), ("third", "777777"))
            (seed / "roadmap.md").write_text(
                "".join(f"{idx}. [[prompts/{name}|{name}]]\n" for idx, (name, _) in enumerate(names, 1)),
                encoding="utf-8",
            )
            (seed / "spiegazioni.md").write_text(
                "| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |\n"
                "|---|---|---|---|---|\n"
                + "".join(
                    f"| {idx} | [[prompts/{name}|{name}]] | {name} | low | Prompt |\n"
                    for idx, (name, _) in enumerate(names, 1)
                ),
                encoding="utf-8",
            )
            for name, prompt_id in names:
                (seed / "prompts" / f"{name}.md").write_text(
                    f"PROMPT_ID={prompt_id} | reasoning=low\n",
                    encoding="utf-8",
                )
            git(["add", "."], seed)
            self.assertEqual(0, git(["commit", "-m", "seed"], seed).returncode)
            self.assertEqual(0, git(["branch", "-M", "main"], seed).returncode)
            self.assertEqual(0, git(["push", "-u", "origin", "main"], seed).returncode)

            for local in (local_a, local_b):
                self.assertEqual(0, git(["clone", "--branch", "main", str(bare), str(local)]).returncode)
                git(["config", "user.email", "test@example.invalid"], local)
                git(["config", "user.name", "Test"], local)

            guard_globals = self.original_reconcile.__globals__
            original_guard_run = guard_globals["run"]
            first_push_barrier = threading.Barrier(2)
            counter_lock = threading.Lock()
            first_push_count = 0

            def gated_run(repo: Path, *args: str, check: bool = True):
                nonlocal first_push_count
                should_wait = False
                if args and args[0] == "push":
                    with counter_lock:
                        if first_push_count < 2:
                            first_push_count += 1
                            should_wait = True
                if should_wait:
                    first_push_barrier.wait(timeout=10)
                return original_guard_run(repo, *args, check=check)

            guard_globals["run"] = gated_run
            results: dict[str, dict[str, str]] = {}
            errors: list[BaseException] = []

            def worker(label: str, repo: Path, prompt_id: str) -> None:
                try:
                    results[label] = finish_module.finish(repo, prompt_id, confirm_executed=True)
                except BaseException as exc:  # captured for assertion in the main test thread
                    errors.append(exc)

            try:
                threads = [
                    threading.Thread(target=worker, args=("second", local_a, "654321")),
                    threading.Thread(target=worker, args=("third", local_b, "777777")),
                ]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=20)
                self.assertTrue(all(not thread.is_alive() for thread in threads))
            finally:
                guard_globals["run"] = original_guard_run

            self.assertEqual([], errors)
            self.assertEqual({"second", "third"}, set(results))
            self.assertTrue(any(int(result["push_race_retries"]) >= 1 for result in results.values()))

            verify = root / "verify"
            self.assertEqual(0, git(["clone", "--branch", "main", str(bare), str(verify)]).returncode)
            self.assertTrue((verify / "prompts" / "first.md").is_file())
            self.assertTrue((verify / "completed" / "second.md").is_file())
            self.assertTrue((verify / "completed" / "third.md").is_file())
            roadmap = (verify / "roadmap.md").read_text(encoding="utf-8")
            self.assertEqual("1. [[prompts/first|first]]\n", roadmap)


if __name__ == "__main__":
    unittest.main()
