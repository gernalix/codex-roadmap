import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools"))
import c3_symphony_route as route
from c3_symphony_bridge import CodingItem, HostConfig


ITEM = "wi:"+"a"*32
RUN = "b"*32
CONFIG = HostConfig("production", "gernalix/c3-symphony", frozenset({"gernalix/codex-roadmap"}))


class RouteTests(unittest.TestCase):
    def test_routing_preserves_non_coding_and_legacy(self):
        for activity in ("diagnostic", "gui", "native", "semantic"):
            self.assertFalse(route.eligible(CONFIG, activity=activity, policy="auto",
                                            repo="gernalix/codex-roadmap"))
        self.assertFalse(route.eligible(CONFIG, activity="coding", policy="auto",
                                        repo="gernalix/foreign"))
        self.assertFalse(route.eligible(HostConfig("legacy", None, frozenset()),
                                        activity="coding", policy="auto",
                                        repo="gernalix/codex-roadmap"))
        self.assertTrue(route.eligible(CONFIG, activity="coding", policy="codex",
                                       repo="gernalix/codex-roadmap"))

    def test_ownership_prevents_second_run_or_tracker(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(route, "OWNERS", Path(directory)):
            route.reserve_ownership(ITEM, RUN, CONFIG)
            route.reserve_ownership(ITEM, RUN, CONFIG)
            with self.assertRaisesRegex(route.RouteError, "ownership_conflict"):
                route.reserve_ownership(ITEM, "c"*32, CONFIG)
            with self.assertRaisesRegex(route.RouteError, "ownership_conflict"):
                route.reserve_ownership(ITEM, RUN, HostConfig("canary", "gernalix/symphony-canary",
                                                               CONFIG.source_repos))

    def test_terminal_contract_fails_closed(self):
        good = {"outcome": "PASS", "completed": ["tested"], "remaining": [],
                "evidence": ["commit abc"], "blocker": None, "next_action": None}
        self.assertEqual(route.validate_terminal(good)["strict_contract"], True)
        with self.assertRaisesRegex(route.RouteError, "terminal_contract_invalid"):
            route.validate_terminal({**good, "evidence": []})

    def test_import_workspace_commit_fast_forwards_canonical_task_worktree(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/"target"
            subprocess.run(["git","init",str(target)],check=True,capture_output=True)
            subprocess.run(["git","-C",str(target),"config","user.name","Test"],check=True)
            subprocess.run(["git","-C",str(target),"config","user.email","test@example.com"],check=True)
            (target/"base.txt").write_text("base\n")
            subprocess.run(["git","-C",str(target),"add","."],check=True)
            subprocess.run(["git","-C",str(target),"commit","-m","base"],check=True,capture_output=True)
            subprocess.run(["git","-C",str(target),"branch","-M","task/123456"],check=True)
            base = subprocess.check_output(["git","-C",str(target),"rev-parse","HEAD"],text=True).strip()
            workspace = root/"workspaces"/"GH-7"
            workspace.mkdir(parents=True)
            source = workspace/"source"
            subprocess.run(["git","clone","--no-hardlinks","--branch","task/123456",
                            str(target),str(source)],check=True,capture_output=True)
            subprocess.run(["git","-C",str(source),"config","user.name","Test"],check=True)
            subprocess.run(["git","-C",str(source),"config","user.email","test@example.com"],check=True)
            (workspace/".c3-source-base").write_text(base+"\n")
            (source/"change.txt").write_text("done\n")
            subprocess.run(["git","-C",str(source),"add","."],check=True)
            subprocess.run(["git","-C",str(source),"commit","-m","change"],check=True,capture_output=True)
            source_head = subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
            item = CodingItem(ITEM,"Tiny","Fix","[]","gernalix/codex-roadmap",
                              "gpt-6-sol","medium",str(target),"123456")
            self.assertEqual(source_head, route.import_workspace_commit(item,7,root/"workspaces"))
            target_head = subprocess.check_output(["git","-C",str(target),"rev-parse","HEAD"],text=True).strip()
            self.assertEqual(source_head,target_head)
            self.assertEqual("done\n",(target/"change.txt").read_text())

    def test_closed_exact_tracker_queues_one_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            workflow = Path(directory)/"WORKFLOW.md"
            workflow.write_text('---\n{"workspace":{"root":"/tmp/c3-workspaces"}}\n---\n')
            item = CodingItem(ITEM, "Tiny", "Fix", "[]", "gernalix/codex-roadmap",
                              "gpt-6-sol", "medium", "/tmp/task-worktree", "123456")
            terminal = {"outcome": "PASS", "completed": [], "remaining": [],
                        "evidence": ["tested head"], "blocker": None, "next_action": None}
            calls = []
            def bridge(action, *_):
                calls.append(action)
                return ({"issue_number": 7, "created": False} if action == "publish" else
                        {"issue_number": 7, "state": "closed", "terminal": terminal})
            with patch.object(route, "load_item", return_value=item), \
                 patch.object(route.backend, "status", return_value={"active_state":"active", "api_healthy":True}), \
                 patch.object(route, "workflow_text", return_value=workflow.read_text()), \
                 patch.object(route, "reserve_ownership"), \
                 patch.object(route, "import_workspace_commit", return_value="abc123") as importer, \
                 patch.object(route, "_queue_repo_integration", return_value=("queued", False)) as integration:
                result = route.dispatch(Path(directory)/"roadmap.sqlite", RUN, ITEM, CONFIG,
                                        submit=lambda *args: calls.append(args),
                                        workflow=workflow, bridge=bridge)
            self.assertEqual(result["phase"], "queued")
            self.assertEqual(calls[:2], ["publish", "inspect"])
            self.assertEqual(len([call for call in calls if isinstance(call, tuple)]), 1)
            importer.assert_called_once_with(item, 7, Path("/tmp/c3-workspaces"))
            integration.assert_called_once_with("123456", Path("/tmp/task-worktree"))


if __name__ == "__main__":
    unittest.main()
