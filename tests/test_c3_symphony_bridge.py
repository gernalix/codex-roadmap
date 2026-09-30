import importlib.util
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / "tools/c3_symphony_bridge.py"
spec = importlib.util.spec_from_file_location("c3_symphony_bridge", MODULE)
bridge = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)


ITEM_ID = "wi:" + "a" * 32
CONFIG = bridge.HostConfig("canary", bridge.CANARY_TRACKER,
                           frozenset({"gernalix/codex-roadmap"}))


class FakeGitHub(bridge.GitHubIssues):
    def __init__(self):
        self.repo = CONFIG.tracker_repo
        self.rows = []

    def matching(self, title):
        return [row for row in self.rows if row["title"] == title]

    def create(self, title, body):
        row = {"number": len(self.rows) + 1, "title": title, "body": body,
               "state": "open", "labels": [{"name": bridge.LABEL}]}
        self.rows.append(row)
        return row

    def api(self, method, path, payload=None):
        if method == "GET" and path == f"repos/{self.repo}/issues/1/comments?per_page=100":
            return [{"body": 'C3_RESULT={"outcome":"PASS","completed":[],"remaining":[],"evidence":["tested"],"blocker":null,"next_action":null}'}]
        raise AssertionError(path)


class BridgeTests(unittest.TestCase):
    def item(self):
        return bridge.CodingItem(ITEM_ID, "Tiny fix", "Create a marker", "[]",
                                 "gernalix/codex-roadmap", "gpt-6-sol", "medium")

    def test_publish_replay_uses_same_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            github = FakeGitHub()
            lock = Path(directory) / "publish.lock"
            self.assertEqual(bridge.publish(self.item(), github, lock),
                             {"issue_number": 1, "created": True})
            self.assertEqual(bridge.publish(self.item(), github, lock),
                             {"issue_number": 1, "created": False})
            self.assertEqual(len(github.rows), 1)

    def test_delayed_create_readback_does_not_create_twice(self):
        class DelayedGitHub(FakeGitHub):
            def __init__(self):
                super().__init__()
                self.delay = False
            def matching(self, title):
                if self.delay:
                    self.delay = False
                    return []
                return super().matching(title)
            def create(self, title, body):
                row = super().create(title, body)
                self.delay = True
                return row
        with tempfile.TemporaryDirectory() as directory:
            github = DelayedGitHub()
            with patch.object(bridge.time, "sleep"):
                result = bridge.publish(self.item(), github, Path(directory) / "lock")
            self.assertEqual(result, {"issue_number": 1, "created": True})
            self.assertEqual(len(github.rows), 1)

    def test_conflicting_or_duplicate_tracker_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            github = FakeGitHub()
            lock = Path(directory) / "publish.lock"
            github.create(bridge.issue_title(self.item()), "wrong body")
            with self.assertRaisesRegex(bridge.BridgeError, "tracker_identity_conflict"):
                bridge.publish(self.item(), github, lock)
            github.rows.append(dict(github.rows[0], number=2))
            with self.assertRaisesRegex(bridge.BridgeError, "duplicate_tracker_identity"):
                bridge.publish(self.item(), github, lock)

    def test_closed_issue_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            github = FakeGitHub()
            github.create(bridge.issue_title(self.item()), bridge.issue_body(self.item()))
            github.rows[0]["state"] = "closed"
            github.rows[0]["labels"] = []
            self.assertEqual(bridge.publish(self.item(), github, Path(directory) / "lock"),
                             {"issue_number": 1, "created": False})
            self.assertEqual(len(github.rows), 1)

    def test_exact_closed_tracker_terminal_readback(self):
        github = FakeGitHub()
        github.create(bridge.issue_title(self.item()), bridge.issue_body(self.item()))
        github.rows[0]["state"] = "closed"
        result = bridge.inspect(self.item(), github)
        self.assertEqual(result["terminal"]["evidence"], ["tested"])
        github.rows.append(dict(github.rows[0], number=2))
        with self.assertRaisesRegex(bridge.BridgeError, "tracker_identity_missing_or_conflicted"):
            bridge.inspect(self.item(), github)

    def test_workflow_has_host_token_reference_and_appserver_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspaces"
            output = root / "host" / "WORKFLOW.md"
            bridge.write_workflow(self.item(), workspace, output, CONFIG)
            data = output.read_text()
            config = json.loads(data.split("---", 2)[1])
            self.assertEqual(config["tracker"]["provider"]["token"], "$GITHUB_TOKEN")
            self.assertEqual(config["tracker"]["required_labels"], [bridge.LABEL])
            self.assertIn(" source -- --depth 1", config["hooks"]["after_create"])
            self.assertIn("-c model=gpt-6-sol", config["codex"]["command"])
            self.assertIn("-c model_reasoning_effort=medium", config["codex"]["command"])
            self.assertNotIn(" -m ", config["codex"]["command"])
            self.assertIn("Do not call roadmap_start.py", data)
            self.assertIn("canonical tracker repository is gernalix/symphony-canary", data)
            self.assertIn("the tracker issue is {{ issue.identifier }}", data)
            self.assertIn("Source repository in the issue body is never the tracker target", data)
            self.assertIn("read back that same tracker repository/issue and require state=closed", data)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(bridge.BridgeError, "workflow_inside_codex_workspace"):
                bridge.write_workflow(self.item(), workspace, workspace / "WORKFLOW.md", CONFIG)

    def test_loader_requires_runnable_coding_spec_and_exact_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "roadmap.sqlite"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript("""
                    CREATE TABLE work_items(work_item_id TEXT,title TEXT,objective TEXT,prompt_id TEXT,
                      acceptance_json TEXT,repo TEXT,status TEXT,actionable INTEGER,
                      executor_policy TEXT);
                    CREATE TABLE work_item_execution_specs(work_item_id TEXT,activity TEXT,
                      model TEXT,reasoning TEXT,worktree TEXT);
                    CREATE TABLE work_item_runs(run_id TEXT,work_item_id TEXT,executor TEXT,state TEXT,worker_ref TEXT);
                    CREATE VIEW v_work_item_runnable AS SELECT * FROM work_items
                      WHERE status='pending' AND actionable=1;
                """)
                conn.execute("INSERT INTO work_items VALUES(?,?,?,?,?,?,?,?,?)",
                             (ITEM_ID, "Tiny fix", "Create marker", None, "[]", "gernalix/codex-roadmap",
                              "pending", 1, "codex"))
                conn.execute("INSERT INTO work_item_execution_specs VALUES(?,?,?,?,?)",
                             (ITEM_ID, "coding", "gpt-6-sol", "medium", None))
                conn.commit()
            self.assertEqual(bridge.load_item(db, ITEM_ID, CONFIG).model, "gpt-6-sol")
            with closing(sqlite3.connect(db)) as conn:
                conn.execute("UPDATE work_item_execution_specs SET activity='native'")
                conn.commit()
            with self.assertRaisesRegex(bridge.BridgeError, "item_not_autonomous_coding"):
                bridge.load_item(db, ITEM_ID, CONFIG)

    def test_auto_coding_and_human_model_label_resolve_for_appserver(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "roadmap.sqlite"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript("""
                    CREATE TABLE work_items(work_item_id TEXT,title TEXT,objective TEXT,prompt_id TEXT,
                      acceptance_json TEXT,repo TEXT,status TEXT,actionable INTEGER,
                      executor_policy TEXT);
                    CREATE TABLE work_item_execution_specs(work_item_id TEXT,activity TEXT,
                      model TEXT,reasoning TEXT,worktree TEXT);
                    CREATE TABLE work_item_runs(run_id TEXT,work_item_id TEXT,executor TEXT,state TEXT,worker_ref TEXT);
                    CREATE VIEW v_work_item_runnable AS SELECT * FROM work_items
                      WHERE status='pending' AND actionable=1;
                """)
                conn.execute("INSERT INTO work_items VALUES(?,?,?,?,?,?,?,?,?)",
                             (ITEM_ID, "Tiny fix", "Create marker", None, "[]", "gernalix/codex-roadmap",
                              "pending", 1, "auto"))
                conn.execute("INSERT INTO work_item_execution_specs VALUES(?,?,?,?,?)",
                             (ITEM_ID, "coding", "GPT-6 Sol", "Medium", None))
                conn.commit()
            item = bridge.load_item(db, ITEM_ID, CONFIG)
            self.assertEqual((item.model, item.reasoning), ("gpt-6-sol", "medium"))
            self.assertIn("-c model=gpt-6-sol", bridge.workflow_text(item, Path(directory) / "workspaces", CONFIG))

    def test_production_requires_explicit_non_canary_tracker_and_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"config.json"
            path.write_text(json.dumps({"mode": "production", "tracker_repo": bridge.CANARY_TRACKER,
                                        "source_repos": ["gernalix/codex-roadmap"]}))
            with self.assertRaisesRegex(bridge.BridgeError, "production_tracker_is_canary"):
                bridge.load_config(path)
            path.write_text(json.dumps({"mode": "production", "tracker_repo": "gernalix/c3-symphony",
                                        "source_repos": ["gernalix/codex-roadmap", "gernalix/other"]}))
            config = bridge.load_config(path)
            self.assertEqual(config.tracker_repo, "gernalix/c3-symphony")
            self.assertIn("gernalix/other", config.source_repos)
            foreign = bridge.CodingItem(ITEM_ID, "x", "x", "[]", "gernalix/not-allowed", "gpt-6-sol", "medium")
            with self.assertRaisesRegex(bridge.BridgeError, "source_or_tracker_not_configured"):
                bridge.workflow_text(foreign, Path(directory), config)


if __name__ == "__main__":
    unittest.main()
