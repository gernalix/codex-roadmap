from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_result
import submit_mutation


class RemoteSingleWriterTests(unittest.TestCase):
    def test_result_submission_does_not_require_local_repo(self) -> None:
        with patch.object(
            roadmap_result,
            "submit_document",
            return_value={
                "submission": "queued",
                "issue_number": "42",
                "issue_url": "https://github.example/issues/42",
                "request_key": "terminal-123456",
            },
        ) as submit:
            out = roadmap_result.finish_result(
                Path("/definitely/not/a/git/repo"),
                "123456",
                "PASS",
                confirm_executed=True,
            )
        self.assertEqual("queued", out["status"])
        self.assertEqual("completed", out["target_status"])
        self.assertEqual("terminal-123456", out["request_key"])
        self.assertEqual("42", out["issue_number"])
        document = submit.call_args.args[0]
        self.assertEqual("terminal_request", document["operations"][0]["op"])
        self.assertEqual("completed", document["operations"][0]["status"])

    def test_terminal_request_key_is_one_per_prompt(self) -> None:
        captured: list[tuple[str, str]] = []

        def fake_submit(document, *, request_key, **_kwargs):
            captured.append((request_key, document["operations"][0]["status"]))
            return {
                "submission": "queued",
                "issue_number": "1",
                "issue_url": "x",
                "request_key": request_key,
            }

        with patch.object(roadmap_result, "submit_document", side_effect=fake_submit):
            roadmap_result.finish_result(Path("."), "654321", "PASS", confirm_executed=True)
            roadmap_result.finish_result(Path("."), "654321", "FAIL", confirm_executed=True)

        self.assertEqual(
            [("terminal-654321", "completed"), ("terminal-654321", "failed")],
            captured,
        )

    def test_existing_same_open_issue_is_idempotent(self) -> None:
        document = {
            "schema": submit_mutation.SCHEMA,
            "actor": "codex",
            "operations": [{"op": "status", "prompt_id": "123456", "status": "completed"}],
        }
        issue = {
            "number": 7,
            "title": "[roadmap-mutation] terminal-123456",
            "state": "OPEN",
            "body": submit_mutation._canonical_bytes(document).decode("utf-8"),
            "url": "https://github.example/issues/7",
        }
        with patch.object(submit_mutation, "_matching_issues", return_value=[issue]), patch.object(
            submit_mutation, "_gh"
        ) as gh:
            out = submit_mutation.submit_document(document, request_key="terminal-123456")
        self.assertEqual("pending", out["submission"])
        self.assertEqual("7", out["issue_number"])
        gh.assert_not_called()

    def test_existing_same_closed_issue_is_applied(self) -> None:
        document = {
            "schema": submit_mutation.SCHEMA,
            "actor": "codex",
            "operations": [{"op": "status", "prompt_id": "123456", "status": "completed"}],
        }
        issue = {
            "number": 8,
            "title": "[roadmap-mutation] terminal-123456",
            "state": "CLOSED",
            "body": submit_mutation._canonical_bytes(document).decode("utf-8"),
            "url": "https://github.example/issues/8",
        }
        with patch.object(submit_mutation, "_matching_issues", return_value=[issue]):
            out = submit_mutation.submit_document(document, request_key="terminal-123456")
        self.assertEqual("applied", out["submission"])

    def test_existing_different_issue_payload_is_rejected(self) -> None:
        wanted = {
            "schema": submit_mutation.SCHEMA,
            "actor": "codex",
            "operations": [{"op": "status", "prompt_id": "123456", "status": "completed"}],
        }
        existing = {
            "schema": submit_mutation.SCHEMA,
            "actor": "codex",
            "operations": [{"op": "status", "prompt_id": "123456", "status": "failed"}],
        }
        issue = {
            "number": 9,
            "title": "[roadmap-mutation] terminal-123456",
            "state": "OPEN",
            "body": json.dumps(existing),
            "url": "x",
        }
        with patch.object(submit_mutation, "_matching_issues", return_value=[issue]):
            with self.assertRaises(submit_mutation.MutationSubmitError):
                submit_mutation.submit_document(wanted, request_key="terminal-123456")

    def test_new_submission_creates_issue_not_git_file(self) -> None:
        document = {
            "schema": submit_mutation.SCHEMA,
            "actor": "chatgpt",
            "operations": [{"op": "tag", "prompt_id": "123456", "tag": "smoke"}],
        }
        response = Mock(returncode=0, stdout=json.dumps({"number": 10, "html_url": "https://x/10"}), stderr="")
        with patch.object(submit_mutation, "_matching_issues", return_value=[]), patch.object(
            submit_mutation, "_gh", return_value=response
        ) as gh:
            out = submit_mutation.submit_document(document, request_key="smoke-123456")
        self.assertEqual("queued", out["submission"])
        args = gh.call_args.args
        self.assertIn("repos/gernalix/codex-roadmap/issues", args)
        self.assertNotIn("contents", " ".join(args))


if __name__ == "__main__":
    unittest.main()
