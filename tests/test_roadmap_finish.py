from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_finish


class FinishWrapperTests(unittest.TestCase):
    @patch("roadmap_finish._queue_repo_integration", return_value=("merged", True))
    def test_finish_terminalizes_only_after_repo_is_already_merged(self, queue):
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
        queue.assert_called_once_with("123456")
        self.assertEqual("PASS",calls[0][2])
        self.assertEqual("remote_single_writer",out["finish_mode"])
        self.assertEqual("merged",out["repo_integration"])

    @patch("roadmap_finish._queue_repo_integration", return_value=("queued", False))
    def test_queued_repo_work_returns_without_terminalizing_or_waiting(self, queue):
        original=roadmap_finish.finish_result
        calls=[]
        roadmap_finish.finish_result=lambda *args,**kwargs: calls.append((args,kwargs))
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        finally:
            roadmap_finish.finish_result=original
        self.assertEqual([], calls)
        self.assertEqual("queued",out["status"])
        self.assertEqual("QUEUED",out["result"])
        self.assertEqual("async_integration_queue",out["finish_mode"])
        self.assertEqual("none",out["user_action"])

    @patch("roadmap_finish.subprocess.run")
    @patch.object(Path, "is_file", return_value=True)
    def test_queue_helper_accepts_queued_payload(self, _is_file, run):
        run.return_value=subprocess.CompletedProcess([],0,stdout=json.dumps({"status":"queued"}),stderr="")
        state, integrated=roadmap_finish._queue_repo_integration("123456")
        self.assertEqual("queued",state)
        self.assertFalse(integrated)
        self.assertIn("finish-any",run.call_args.args[0])

    @patch("roadmap_finish._queue_repo_integration")
    def test_dry_run_does_not_touch_repo_queue(self, queue):
        original=roadmap_finish.finish_result
        roadmap_finish.finish_result=lambda *args,**kwargs: {"status":"dry-run"}
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",dry_run=True)
        finally:
            roadmap_finish.finish_result=original
        queue.assert_not_called()
        self.assertEqual("dry-run",out["repo_integration"])


if __name__=="__main__": unittest.main()
