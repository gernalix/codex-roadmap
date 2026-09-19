from __future__ import annotations

import json
import sys
import tempfile
import unittest
import base64
import subprocess
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import apply_mutations
import roadmap_db as db
import roadmap_sync


class UsageExecutionMutationTests(unittest.TestCase):
    def test_download_remote_db_uses_git_blob_for_large_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                prompt_text="expected prompt",
            )
            conn.commit()
            conn.close()
            raw_db = (repo / "roadmap.sqlite").read_bytes()

            tree = {"tree": [{"path": "roadmap.sqlite", "type": "blob", "sha": "blob-sha"}]}
            blob = {"content": base64.b64encode(raw_db).decode("ascii")}
            with patch.object(
                roadmap_sync.subprocess,
                "run",
                side_effect=[
                    subprocess.CompletedProcess([], 0, json.dumps(tree).encode(), b""),
                    subprocess.CompletedProcess([], 0, json.dumps(blob).encode(), b""),
                ],
            ) as run:
                prompt_ids, cycle_keys = roadmap_sync._download_remote_db("owner/repo", "main")

            self.assertEqual({"123456"}, prompt_ids)
            self.assertEqual(set(), cycle_keys)
            self.assertEqual(
                [
                    "gh", "api", "repos/owner/repo/git/trees/main?recursive=1",
                ],
                run.call_args_list[0].args[0],
            )
            self.assertEqual(
                ["gh", "api", "repos/owner/repo/git/blobs/blob-sha"],
                run.call_args_list[1].args[0],
            )

    def test_matching_usage_execution_updates_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                prompt_text="expected prompt",
            )
            conn.commit()
            expected = db.prompt_row(conn, "123456")["materialization_sha256"]
            conn.close()

            inbox = repo / "mutations" / "inbox"
            inbox.mkdir(parents=True)
            (inbox / "usage.json").write_text(
                json.dumps(
                    {
                        "schema": "codex-roadmap.mutation.v1",
                        "actor": "codex-usage",
                        "operations": [
                            {
                                "op": "usage_execution",
                                "prompt_id": "123456",
                                "cycle_key": "cycle-1",
                                "materialization_sha256": expected,
                                "outcome": "PASS",
                                "source": "codex-usage",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            apply_mutations.apply_inbox(repo, test_only=True)
            conn = db.connect(repo, writable=False)
            self.assertEqual("completed", db.prompt_row(conn, "123456")["status"])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0])
            self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM identity_conflicts").fetchone()[0])
            conn.close()

    def test_mismatched_usage_execution_records_conflict_without_status_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                prompt_text="expected prompt",
            )
            conn.commit()
            conn.close()

            inbox = repo / "mutations" / "inbox"
            inbox.mkdir(parents=True)
            (inbox / "usage.json").write_text(
                json.dumps(
                    {
                        "schema": "codex-roadmap.mutation.v1",
                        "actor": "codex-usage",
                        "operations": [
                            {
                                "op": "usage_execution",
                                "prompt_id": "123456",
                                "cycle_key": "cycle-2",
                                "materialization_sha256": "0" * 64,
                                "outcome": "PASS",
                                "source": "codex-usage",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            apply_mutations.apply_inbox(repo, test_only=True)
            conn = db.connect(repo, writable=False)
            self.assertEqual("pending", db.prompt_row(conn, "123456")["status"])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0])
            self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM identity_conflicts").fetchone()[0])
            conn.close()

    def test_sync_skips_nonterminal_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            metrics = source / "prompts" / "123456"
            metrics.mkdir(parents=True)
            (metrics / "metrics.json").write_text(
                json.dumps(
                    {
                        "prompt_id": "123456",
                        "cycle_key": "cycle-running",
                        "status": "RUNNING",
                        "prompt_text_redacted": "expected prompt",
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(
                roadmap_sync,
                "_download_remote_db",
                return_value=({"123456"}, set()),
            ), patch.object(roadmap_sync, "submit_document") as submit:
                out = roadmap_sync.sync(Path("/not/a/git/repo"), source)

            self.assertEqual(1, out["skipped_nonterminal"])
            self.assertEqual(0, out["queued"])
            submit.assert_not_called()

    def test_sync_queues_only_new_registered_cycle_without_touching_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            metrics = source / "prompts" / "123456"
            metrics.mkdir(parents=True)
            (metrics / "metrics.json").write_text(
                json.dumps(
                    {
                        "prompt_id": "123456",
                        "cycle_key": "cycle-new",
                        "status": "PASS",
                        "prompt_text_redacted": "expected prompt",
                        "total_tokens": 42,
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(
                roadmap_sync,
                "_download_remote_db",
                return_value=({"123456"}, {"cycle-old"}),
            ), patch.object(
                roadmap_sync,
                "submit_document",
                return_value={
                    "submission": "queued",
                    "path": "mutations/inbox/x.json",
                    "request_key": "x",
                },
            ) as submit:
                out = roadmap_sync.sync(Path("/not/a/git/repo"), source)

            self.assertEqual(1, out["queued"])
            self.assertEqual(1, submit.call_count)
            operation = submit.call_args.args[0]["operations"][0]
            self.assertEqual("usage_execution", operation["op"])
            self.assertEqual("cycle-new", operation["cycle_key"])
            self.assertEqual("PASS", operation["outcome"])


if __name__ == "__main__":
    unittest.main()
