from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))

import roadmap_start as start


class RoadmapStartTests(unittest.TestCase):
    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._remote_prompt_status", return_value="running")
    @patch("roadmap_start._remote_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_claim_waits_for_writer_and_requires_running(self, submit, wait, record, status, task):
        submit.return_value={
            "submission":"queued",
            "issue_number":"42",
            "issue_url":"https://example.invalid/42",
        }
        result=start.claim_start(Path("."),"123456",timeout=1)
        self.assertEqual("ok",result["status"])
        self.assertEqual("running",result["roadmap_status"])
        wait.assert_called_once_with("gernalix/codex-roadmap","42",1)
        record.assert_called_once_with("gernalix/codex-roadmap","main","123456")
        status.assert_called_once_with("gernalix/codex-roadmap","main","123456")
        task.assert_called_once()

    @patch("roadmap_start._remote_prompt_record", side_effect=start.RoadmapStartError("prompt_not_found:123456"))
    @patch("roadmap_start.submit_document")
    def test_missing_prompt_is_rejected_before_submitting_a_mutation(self, submit, record):
        with self.assertRaisesRegex(start.RoadmapStartError, "prompt_not_registered:123456"):
            start.claim_start(Path("."), "123456", timeout=1)
        record.assert_called_once_with("gernalix/codex-roadmap", "main", "123456")
        submit.assert_not_called()

    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._remote_prompt_status", return_value="superseded")
    @patch("roadmap_start._remote_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_claim_fails_closed_if_prompt_is_no_longer_running(self, submit, wait, record, status, task):
        submit.return_value={"submission":"applied","issue_number":"42","issue_url":""}
        with self.assertRaisesRegex(start.RoadmapStartError,"prompt_not_claimed"):
            start.claim_start(Path("."),"123456",timeout=1)
        task.assert_not_called()

    @patch("roadmap_start._repo_task_worktree", return_value="/tmp/task-worktree")
    @patch("roadmap_start._remote_prompt_status", return_value="running")
    @patch("roadmap_start._remote_prompt_record", return_value={"status":"pending","repo":"gernalix/example","project_id":"1"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_git_prompt_returns_isolated_worktree(self, submit, wait, record, status, task):
        submit.return_value={"submission":"queued","issue_number":"42","issue_url":""}
        result=start.claim_start(Path("."),"123456",timeout=1)
        self.assertEqual("/tmp/task-worktree",result["worktree_path"])
        self.assertEqual("task/123456",result["task_branch"])
        self.assertEqual("enabled",result["repo_single_writer"])


if __name__=="__main__":
    unittest.main()
