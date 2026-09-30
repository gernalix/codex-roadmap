from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_inbox_codex_executor as executor


class InboxCodexExecutorTests(unittest.TestCase):
    def test_uses_luna_medium_and_batched_triage_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "triage.log"
            with mock.patch.object(executor, "LOG", log), \
                 mock.patch.object(executor, "_env", return_value={}), \
                 mock.patch.object(executor, "_sync"), \
                 mock.patch.object(executor, "_pending", side_effect=[30, 20]), \
                 mock.patch.object(executor.subprocess, "run",
                                   return_value=SimpleNamespace(returncode=0)) as run:
                result = executor.execute(
                    run_id="run-1", work_item_id="wi:test",
                    db_path=Path(tmp) / "roadmap.sqlite3",
                )
        self.assertEqual("progress", result["state"])
        args = run.call_args.args[0]
        self.assertIn("gpt-6-luna", args)
        self.assertIn('model_reasoning_effort="medium"', args)
        prompt = run.call_args.kwargs["input"]
        self.assertIn("Process up to 25 rows", prompt)
        self.assertIn("submit_controls", prompt)


if __name__ == "__main__":
    unittest.main()
