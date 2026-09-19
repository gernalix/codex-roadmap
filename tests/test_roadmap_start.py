from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))

import roadmap_start as start


class RoadmapStartTests(unittest.TestCase):
    def test_gh_json_forces_canonical_github_host(self) -> None:
        response = Mock(returncode=0, stdout="{}", stderr="")
        with patch.object(start.subprocess, "run", return_value=response) as run:
            self.assertEqual({}, start._gh_json("api", "user"))
        self.assertEqual("github.com", run.call_args.kwargs["env"]["GH_HOST"])

    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._local_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_start_claim_skips_fragile_issue_lookup(self, submit, wait, pull, record, task):
        submit.return_value={"submission":"queued","issue_number":"42","issue_url":""}
        start.claim_start(Path("."),"123456",timeout=1)
        self.assertFalse(submit.call_args.kwargs["lookup_existing"])

    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._local_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_target_repository_cannot_redirect_mutation_queue(self, submit, wait, pull, record, task):
        submit.return_value={"submission":"queued","issue_number":"42","issue_url":""}
        start.claim_start(
            Path("."),
            "123456",
            repository="livinggaul-x-downloader",
            timeout=1,
        )
        self.assertEqual(
            "gernalix/codex-roadmap",
            submit.call_args.kwargs["repository"],
        )
        wait.assert_called_once_with("gernalix/codex-roadmap","42",1)

    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._local_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_claim_waits_for_writer_and_requires_running(self, submit, wait, pull, record, task):
        submit.return_value={
            "submission":"queued",
            "issue_number":"42",
            "issue_url":"https://example.invalid/42",
        }
        result=start.claim_start(Path("."),"123456",timeout=1)
        self.assertEqual("ok",result["status"])
        self.assertEqual("running",result["roadmap_status"])
        wait.assert_called_once_with("gernalix/codex-roadmap","42",1)
        pull.assert_called_once_with(Path("."), branch="main")
        record.assert_called_once_with(Path("."), "123456")
        task.assert_called_once()

    @patch("roadmap_start._local_prompt_record", side_effect=start.RoadmapStartError("prompt_not_found:123456"))
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start.submit_document")
    def test_missing_prompt_is_rejected_before_submitting_a_mutation(self, submit, pull, record):
        with self.assertRaisesRegex(start.RoadmapStartError, "prompt_not_registered:123456"):
            start.claim_start(Path("."), "123456", timeout=1)
        pull.assert_called_once_with(Path("."), branch="main")
        record.assert_called_once_with(Path("."), "123456")
        submit.assert_not_called()

    @patch("roadmap_start._repo_task_worktree", return_value=None)
    @patch("roadmap_start._local_prompt_record", return_value={"status":"pending","repo":"","project_id":""})
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_claim_uses_completed_issue_as_authoritative_running_ack(self, submit, wait, pull, record, task):
        submit.return_value={"submission":"applied","issue_number":"42","issue_url":""}
        result=start.claim_start(Path("."),"123456",timeout=1)
        self.assertEqual("running", result["roadmap_status"])
        task.assert_called_once()

    @patch("roadmap_start._repo_task_worktree", return_value="/tmp/task-worktree")
    @patch("roadmap_start._local_prompt_record", return_value={"status":"pending","repo":"gernalix/example","project_id":"1"})
    @patch("roadmap_start.guarded_pull", return_value={"status":"PASS"})
    @patch("roadmap_start._wait_issue_applied")
    @patch("roadmap_start.submit_document")
    def test_git_prompt_returns_isolated_worktree(self, submit, wait, pull, record, task):
        submit.return_value={"submission":"queued","issue_number":"42","issue_url":""}
        result=start.claim_start(Path("."),"123456",timeout=1)
        self.assertEqual("/tmp/task-worktree",result["worktree_path"])
        self.assertEqual("task/123456",result["task_branch"])
        self.assertEqual("enabled",result["repo_single_writer"])


if __name__=="__main__":
    unittest.main()
