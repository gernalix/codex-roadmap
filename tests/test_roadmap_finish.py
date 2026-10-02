from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_finish
import c2_repository_integration as integration
import roadmap_repo_integration as dedicated


class FinishWrapperTests(unittest.TestCase):
    def test_dedicated_writer_is_permanently_fail_closed(self):
        with patch("subprocess.run") as process:
            for entry in (dedicated.queue, dedicated.status, dedicated.integrate):
                with self.assertRaisesRegex(dedicated.IntegrationError,"retired"):
                    entry("123456")
            self.assertEqual(2,dedicated.main())
            process.assert_not_called()

    @patch("roadmap_finish.prompt_repository", return_value="gernalix/codex-roadmap")
    @patch("roadmap_finish.queue_integration", return_value=("queued", False))
    def test_self_repo_uses_generic_task_record(self, queue, repository):
        out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        repository.assert_called_once_with(roadmap_finish.ROADMAP_DB,"123456")
        queue.assert_called_once_with("123456","gernalix/codex-roadmap",Path("/tmp/r"))
        self.assertEqual("queued",out["status"])

    @patch("roadmap_finish.prompt_repository", return_value="owner/other")
    @patch("roadmap_finish.queue_integration", return_value=("queued", False))
    def test_external_worktree_reads_routing_from_roadmap_db(self, queue, repository):
        out=roadmap_finish.finish(Path("/tmp/external"),"123456",confirm_executed=True)
        repository.assert_called_once_with(roadmap_finish.ROADMAP_DB,"123456")
        queue.assert_called_once_with("123456","owner/other",Path("/tmp/external"))
        self.assertEqual("queued",out["status"])

    @patch("c2_repository_integration._external", return_value={"status":"queued"})
    def test_external_path_unchanged(self, external):
        self.assertEqual(("queued",False),integration.queue_integration(
            "123456","owner/other",Path("/tmp/r")))
        external.assert_called_once_with("123456","finish-any","owner/other")

    @patch("c2_repository_integration._external", return_value={"status":"merged","integration_state":"merged"})
    def test_external_status_path_unchanged(self, external):
        self.assertEqual("merged",integration.integration_status("123456","owner/other")["status"])
        external.assert_called_once_with("123456","status-any","owner/other")

    @patch("c2_repository_integration._external", return_value={"status":"queued","head_sha":"a"*40})
    def test_own_queued(self, own):
        self.assertEqual(("queued",False),integration.queue_integration(
            "123456",dedicated.REPOSITORY,Path("/tmp/r")))
        own.assert_called_once_with("123456","finish-any",dedicated.REPOSITORY)

    @patch("c2_repository_integration._external", return_value={"status":"merged","integration_state":"merged","merge_sha":"b"*40})
    def test_own_merged(self, own):
        result=integration.integration_status("123456",dedicated.REPOSITORY)
        self.assertEqual("merged",result["status"])
        self.assertEqual("b"*40,result["merge_sha"])

    @patch("roadmap_finish._queue_repo_integration", return_value=("merged", True))
    @patch("roadmap_finish.finish_result", return_value={"status":"queued"})
    def test_pass_terminal_only_after_merge(self, result, queue):
        out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        self.assertEqual("merged",out["repo_integration"])
        result.assert_called_once()

    @patch("roadmap_finish._queue_repo_integration", return_value=("queued", False))
    @patch("roadmap_finish.finish_result")
    def test_queued_does_not_terminalize(self, result, queue):
        out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        self.assertEqual("QUEUED",out["result"])
        result.assert_not_called()

    @patch("roadmap_finish._queue_repo_integration")
    @patch("roadmap_finish.finish_result", return_value={"status":"queued"})
    def test_non_pass_skips_integration(self, result, queue):
        roadmap_finish.finish(Path("/tmp/r"),"123456",result="BLOCKED",confirm_executed=True)
        queue.assert_not_called()

if __name__=="__main__": unittest.main()
