from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
MODULE = TOOLS / "roadmap_finish.py"
spec = importlib.util.spec_from_file_location("roadmap_finish", MODULE)
finish_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(finish_module)


class RoadmapFinishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_complete = finish_module.complete
        self.original_reconcile = finish_module.reconcile

    def tearDown(self) -> None:
        finish_module.complete = self.original_complete
        finish_module.reconcile = self.original_reconcile

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

    def test_non_identity_guard_error_is_not_hidden(self) -> None:
        def fake_complete(*args, **kwargs):
            raise finish_module.RoadmapError("push_blocked:test")

        finish_module.complete = fake_complete
        with self.assertRaisesRegex(finish_module.RoadmapError, "push_blocked:test"):
            finish_module.finish(Path("/tmp/repo"), "123456", confirm_executed=True)


if __name__ == "__main__":
    unittest.main()
