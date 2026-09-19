from __future__ import annotations
import subprocess, sys, unittest
from pathlib import Path
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_finish


class FinishWrapperTests(unittest.TestCase):
    @patch("roadmap_finish._handoff_repo_single_writer", return_value=("merge123", True))
    def test_finish_terminalizes_only_after_repo_writer_merged(self, handoff):
        original=roadmap_finish.finish_result
        calls=[]
        def fake(repo,prompt_id,result,**kwargs):
            calls.append((str(repo),prompt_id,result,kwargs))
            return {"status":"queued","prompt_id":prompt_id}
        roadmap_finish.finish_result=fake
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        finally:
            roadmap_finish.finish_result=original
        handoff.assert_called_once_with("123456", timeout=0.0)
        self.assertEqual("PASS",calls[0][2])
        self.assertEqual("remote_single_writer",out["finish_mode"])
        self.assertEqual("merge123",out["repo_integration"])

    @patch("roadmap_finish._handoff_repo_single_writer", return_value=("pending-integration", False))
    def test_pending_remote_ci_returns_successful_handoff_without_terminalizing(self, handoff):
        original=roadmap_finish.finish_result
        calls=[]
        roadmap_finish.finish_result=lambda *args,**kwargs: calls.append((args,kwargs))
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        finally:
            roadmap_finish.finish_result=original
        self.assertEqual([], calls)
        self.assertEqual("queued",out["status"])
        self.assertEqual("PENDING_INTEGRATION",out["result"])
        self.assertEqual("remote_single_writer_async",out["finish_mode"])

    @patch("roadmap_finish.subprocess.run")
    @patch.object(Path, "is_file", return_value=True)
    def test_handoff_converts_only_integration_timeout_to_pending(self, _is_file, run):
        run.return_value=subprocess.CompletedProcess([],2,stdout="",stderr="repo-task: single-writer integration timeout\n")
        state, integrated=roadmap_finish._handoff_repo_single_writer("123456")
        self.assertEqual("pending-integration",state)
        self.assertFalse(integrated)

    @patch("roadmap_finish._handoff_repo_single_writer")
    def test_dry_run_does_not_touch_repo_writer(self, handoff):
        original=roadmap_finish.finish_result
        roadmap_finish.finish_result=lambda *args,**kwargs: {"status":"dry-run"}
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",dry_run=True)
        finally:
            roadmap_finish.finish_result=original
        handoff.assert_not_called()
        self.assertEqual("dry-run",out["repo_integration"])


if __name__=="__main__": unittest.main()
