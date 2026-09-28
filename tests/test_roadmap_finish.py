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
    def test_c2_work_item_id_uses_guarded_dedicated_branch(self):
        work_item_id = "wi:" + "a" * 32
        repo = Path("/tmp/codex-roadmap-task")
        head = "b" * 40

        def git_result(_repo, *args):
            if args == ("rev-parse", "--show-toplevel"):
                return str(repo)
            if args == ("branch", "--show-current"):
                return "task/wi-" + "a" * 32
            if args == ("remote", "get-url", "origin"):
                return "https://github.com/gernalix/codex-roadmap.git"
            if args == ("status", "--porcelain"):
                return ""
            if args == ("rev-parse", "HEAD"):
                return head
            raise AssertionError(args)

        with patch.object(dedicated, "_git", side_effect=git_result):
            self.assertEqual(head, dedicated._identity(repo, work_item_id))
        self.assertEqual("wi-" + "a" * 32, dedicated._branch_name(work_item_id))

    def test_work_item_pr_lookup_uses_task_branch(self):
        work_item_id = "wi:" + "a" * 32
        row = {"number": 44, "state": "OPEN",
               "headRefName": "task/wi-" + "a" * 32,
               "baseRefName": "main"}
        with patch.object(dedicated, "_run", return_value=json.dumps([row])) as run:
            self.assertEqual(row, dedicated._pr(work_item_id))
        self.assertIn("task/wi-" + "a" * 32, run.call_args.args)

    def test_work_item_queue_uses_single_writer_process_title(self):
        work_item_id = "wi:" + "a" * 32
        head = "b" * 40
        with patch.object(dedicated, "_identity", return_value=head), \
             patch.object(dedicated, "_pr", return_value=None), \
             patch.object(dedicated, "_git", return_value="") as git, \
             patch.object(dedicated, "_run", return_value="https://example.test/pr") as run, \
             patch.object(dedicated, "status", return_value={"status":"queued","head_sha":head}):
            out = dedicated.queue(Path("/tmp/codex-roadmap-task"), work_item_id)
        self.assertEqual("queued", out["status"])
        self.assertTrue(any(call.args[-1] == f"{head}:refs/heads/task/wi-{'a'*32}"
                            for call in git.call_args_list if call.args[1] == "push"))
        self.assertIn("[single-writer] " + work_item_id, run.call_args.args)

    def test_work_item_queue_updates_managed_pr_only_for_exact_new_head(self):
        work_item_id = "wi:" + "a" * 32
        old_head, new_head = "a" * 40, "b" * 40
        with patch.object(dedicated, "_identity", return_value=new_head), \
             patch.object(dedicated, "_pr", return_value={"number": 44}), \
             patch.object(dedicated, "_git", return_value=old_head + "\trefs/heads/task/wi-" + "a" * 32), \
             patch.object(dedicated, "_run", return_value="updated") as run, \
             patch.object(dedicated, "status", side_effect=[
                 {"status":"queued","head_sha":old_head},
                 {"status":"queued","head_sha":new_head},
             ]):
            out = dedicated.queue(Path("/tmp/codex-roadmap-task"), work_item_id,
                                  expected_head=new_head)
        self.assertEqual(new_head, out["head_sha"])
        self.assertIn("edit", run.call_args.args)
        self.assertIn("[single-writer] " + work_item_id, run.call_args.args)

        with patch.object(dedicated, "_identity", return_value=new_head), \
             patch.object(dedicated, "_pr", return_value={"number": 44}), \
             patch.object(dedicated, "status", return_value={"status":"queued","head_sha":old_head}):
            with self.assertRaisesRegex(dedicated.IntegrationError, "task_pr_head_drift"):
                dedicated.queue(Path("/tmp/codex-roadmap-task"), work_item_id)

    def test_exact_new_head_repairs_pushed_managed_pr_marker(self):
        old_head, new_head = "a" * 40, "b" * 40
        existing = {"number": 44, "state": "OPEN", "headRefOid": new_head,
                    "body": "C2-tested-head: " + old_head}
        with patch.object(dedicated, "_identity", return_value=new_head), \
             patch.object(dedicated, "_pr", return_value=existing), \
             patch.object(dedicated, "_git", return_value=new_head + "\trefs/heads/task/123456") as git, \
             patch.object(dedicated, "_run", return_value="updated") as run, \
             patch.object(dedicated, "status", return_value={"status":"queued","head_sha":new_head}):
            out = dedicated.queue(Path("/tmp/r"), "123456", expected_head=new_head)
        self.assertEqual(new_head, out["head_sha"])
        self.assertTrue(any(call.args[1:] == ("merge-base", "--is-ancestor", old_head, new_head)
                            for call in git.call_args_list))
        self.assertIn("edit", run.call_args.args)

        with patch.object(dedicated, "_identity", return_value=new_head), \
             patch.object(dedicated, "_pr", return_value=existing):
            with self.assertRaisesRegex(dedicated.IntegrationError, "tested_head_drift"):
                dedicated.queue(Path("/tmp/r"), "123456")

    @patch("roadmap_finish.prompt_repository", return_value="gernalix/codex-roadmap")
    @patch("roadmap_finish.queue_integration", return_value=("queued", False))
    def test_self_repo_no_generic_task_record_needed(self, queue, repository):
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
    @patch("c2_repository_integration.queue")
    def test_external_path_unchanged(self, own, external):
        self.assertEqual(("queued",False),integration.queue_integration(
            "123456","owner/other",Path("/tmp/r")))
        external.assert_called_once_with("123456","finish-any")
        own.assert_not_called()

    @patch("c2_repository_integration._external", return_value={"status":"merged","integration_state":"merged"})
    def test_external_status_path_unchanged(self, external):
        self.assertEqual("merged",integration.integration_status("123456","owner/other")["status"])
        external.assert_called_once_with("123456","status-any")

    @patch("c2_repository_integration.queue", return_value={"status":"queued","head_sha":"a"*40})
    def test_own_queued(self, own):
        self.assertEqual(("queued",False),integration.queue_integration(
            "123456",dedicated.REPOSITORY,Path("/tmp/r")))
        own.assert_called_once()

    @patch("c2_repository_integration.status", return_value={"status":"merged","integration_state":"merged","merge_sha":"b"*40})
    def test_own_merged(self, own):
        result=integration.integration_status("123456",dedicated.REPOSITORY)
        self.assertEqual("merged",result["status"])
        self.assertEqual("b"*40,result["merge_sha"])

    @patch("roadmap_repo_integration._pr")
    @patch("roadmap_repo_integration._run")
    def test_merged_requires_main_contains_merge(self, run, pr):
        pr.return_value={"state":"MERGED","headRefOid":"a"*40,
                         "mergeCommit":{"oid":"b"*40},"number":42}
        run.return_value=json.dumps({"status":"diverged"})
        with self.assertRaisesRegex(dedicated.IntegrationError,"merge_not_on_main"):
            dedicated.status("123456")

    @patch("roadmap_repo_integration._pr")
    def test_open_pr_fails_on_tested_head_drift(self, pr):
        pr.return_value={"state":"OPEN","headRefOid":"a"*40,
            "body":"C2-tested-head: "+"b"*40,"number":42}
        with self.assertRaisesRegex(dedicated.IntegrationError,"tested_head_drift"):
            dedicated.status("123456")

    @patch("roadmap_repo_integration._run")
    def test_new_open_pr_supersedes_prior_merged_pr(self, run):
        run.return_value=json.dumps([
            {"number":1,"state":"MERGED","headRefName":"task/123456","baseRefName":"main"},
            {"number":2,"state":"OPEN","headRefName":"task/123456","baseRefName":"main"},
        ])
        self.assertEqual(2,dedicated._pr("123456")["number"])

    @patch("roadmap_repo_integration._identity", return_value="b"*40)
    @patch("roadmap_repo_integration._git")
    @patch("roadmap_repo_integration.status", return_value={"status":"merged","head_sha":"a"*40})
    @patch("roadmap_repo_integration._pr", return_value={"state":"MERGED"})
    def test_merged_tested_head_accepts_only_later_operational_checkpoint(self, pr, status, git, identity):
        git.side_effect=lambda repo,*args: "operations/task-state/123456.md" if args[0]=="diff" else ""
        out=dedicated.queue(Path("/tmp/r"),"123456")
        self.assertEqual("merged",out["status"])
        self.assertFalse(any(call.args[1]=="push" for call in git.call_args_list))

    @patch("roadmap_repo_integration._identity", return_value="b"*40)
    @patch("roadmap_repo_integration._run", return_value="https://example.test/pr")
    @patch("roadmap_repo_integration._git")
    @patch("roadmap_repo_integration.status", side_effect=[{"status":"merged","head_sha":"a"*40},
                                                           {"status":"queued","head_sha":"b"*40}])
    @patch("roadmap_repo_integration._pr", return_value={"state":"MERGED"})
    def test_code_after_merge_queues_new_exact_head(self, pr, status, git, run, identity):
        def git_result(repo,*args):
            if args[0]=="diff": return "tools/roadmap_repo_integration.py"
            if args[0]=="ls-remote": return "a"*40+"\trefs/heads/task/123456"
            return ""
        git.side_effect=git_result
        out=dedicated.queue(Path("/tmp/r"),"123456",expected_head="b"*40)
        self.assertEqual("queued",out["status"])
        self.assertTrue(any(call.args[1]=="push" for call in git.call_args_list))

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
