import importlib.util
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / "tools/c3_symphony_bridge.py"
spec = importlib.util.spec_from_file_location("c3_symphony_bridge", MODULE)
bridge = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)


ITEM_ID = "wi:" + "a" * 32


class FakeGitHub(bridge.GitHubIssues):
    def __init__(self):
        self.repo = bridge.TRACKER_REPO
        self.rows = []

    def matching(self, title):
        return [row for row in self.rows if row["title"] == title]

    def create(self, title, body):
        row = {"number": len(self.rows) + 1, "title": title, "body": body,
               "state": "open", "labels": [{"name": bridge.LABEL}]}
        self.rows.append(row)
        return row


class BridgeTests(unittest.TestCase):
    def item(self):
        return bridge.CodingItem(ITEM_ID, "Tiny fix", "Create a marker", "[]",
                                 bridge.SOURCE_REPO, "gpt-6-sol", "medium")

    def test_publish_replay_uses_same_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            github = FakeGitHub()
            lock = Path(directory) / "publish.lock"
            self.assertEqual(bridge.publish(self.item(), github, lock),
                             {"issue_number": 1, "created": True})
            self.assertEqual(bridge.publish(self.item(), github, lock),
                             {"issue_number": 1, "created": False})
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

    def test_workflow_has_host_token_reference_and_appserver_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspaces"
            output = root / "host" / "WORKFLOW.md"
            bridge.write_workflow(self.item(), workspace, output)
            data = output.read_text()
            config = json.loads(data.split("---", 2)[1])
            self.assertEqual(config["tracker"]["provider"]["token"], "$GITHUB_TOKEN")
            self.assertEqual(config["tracker"]["required_labels"], [bridge.LABEL])
            self.assertIn("-c model=gpt-6-sol", config["codex"]["command"])
            self.assertIn("-c model_reasoning_effort=medium", config["codex"]["command"])
            self.assertNotIn(" -m ", config["codex"]["command"])
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(bridge.BridgeError, "workflow_inside_codex_workspace"):
                bridge.write_workflow(self.item(), workspace, workspace / "WORKFLOW.md")

    def test_loader_requires_runnable_coding_spec_and_exact_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "roadmap.sqlite"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript("""
                    CREATE TABLE work_items(work_item_id TEXT,title TEXT,objective TEXT,
                      acceptance_json TEXT,repo TEXT,status TEXT,actionable INTEGER,
                      executor_policy TEXT);
                    CREATE TABLE work_item_execution_specs(work_item_id TEXT,activity TEXT,
                      model TEXT,reasoning TEXT);
                    CREATE VIEW v_work_item_runnable AS SELECT * FROM work_items
                      WHERE status='pending' AND actionable=1;
                """)
                conn.execute("INSERT INTO work_items VALUES(?,?,?,?,?,?,?,?)",
                             (ITEM_ID, "Tiny fix", "Create marker", "[]", bridge.SOURCE_REPO,
                              "pending", 1, "codex"))
                conn.execute("INSERT INTO work_item_execution_specs VALUES(?,?,?,?)",
                             (ITEM_ID, "coding", "gpt-6-sol", "medium"))
                conn.commit()
            self.assertEqual(bridge.load_item(db, ITEM_ID).model, "gpt-6-sol")
            with closing(sqlite3.connect(db)) as conn:
                conn.execute("UPDATE work_item_execution_specs SET activity='native'")
                conn.commit()
            with self.assertRaisesRegex(bridge.BridgeError, "item_not_autonomous_coding"):
                bridge.load_item(db, ITEM_ID)


if __name__ == "__main__":
    unittest.main()
