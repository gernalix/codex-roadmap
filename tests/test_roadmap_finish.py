from __future__ import annotations
import sys, unittest
from pathlib import Path
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_finish


class FinishWrapperTests(unittest.TestCase):
    @patch("roadmap_finish._wait_repo_single_writer", return_value="merge123")
    def test_finish_waits_for_repo_writer_then_delegates_pass(self, wait):
        original=roadmap_finish.finish_result
        calls=[]
        def fake(repo,prompt_id,result,**kwargs):
            calls.append((str(repo),prompt_id,result,kwargs))
            return {"status":"completed","prompt_id":prompt_id}
        roadmap_finish.finish_result=fake
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        finally:
            roadmap_finish.finish_result=original
        wait.assert_called_once_with("123456", timeout=900.0)
        self.assertEqual("PASS",calls[0][2])
        self.assertTrue(calls[0][3]["confirm_executed"])
        self.assertEqual("remote_single_writer",out["finish_mode"])
        self.assertEqual("merge123",out["repo_integration"])

    @patch("roadmap_finish._wait_repo_single_writer")
    def test_dry_run_does_not_touch_repo_writer(self, wait):
        original=roadmap_finish.finish_result
        roadmap_finish.finish_result=lambda *args,**kwargs: {"status":"dry-run"}
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",dry_run=True)
        finally:
            roadmap_finish.finish_result=original
        wait.assert_not_called()
        self.assertEqual("dry-run",out["repo_integration"])


if __name__=="__main__": unittest.main()
