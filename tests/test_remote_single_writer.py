from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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
                "path": "mutations/inbox/terminal-123456.json",
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
        document = submit.call_args.args[0]
        self.assertEqual("status", document["operations"][0]["op"])
        self.assertEqual("completed", document["operations"][0]["status"])

    def test_terminal_request_key_is_one_per_prompt(self) -> None:
        captured: list[tuple[str, str]] = []

        def fake_submit(document, *, request_key, **_kwargs):
            captured.append((request_key, document["operations"][0]["status"]))
            return {"submission": "queued", "path": "x", "request_key": request_key}

        with patch.object(roadmap_result, "submit_document", side_effect=fake_submit):
            roadmap_result.finish_result(Path("."), "654321", "PASS", confirm_executed=True)
            roadmap_result.finish_result(Path("."), "654321", "FAIL", confirm_executed=True)

        self.assertEqual(
            [("terminal-654321", "completed"), ("terminal-654321", "failed")],
            captured,
        )

    def test_existing_same_request_is_idempotent(self) -> None:
        document = {
            "schema": submit_mutation.SCHEMA,
            "actor": "codex",
            "operations": [{"op": "status", "prompt_id": "123456", "status": "completed"}],
        }
        with patch.object(
            submit_mutation,
            "_read_remote_document",
            side_effect=[document],
        ), patch.object(submit_mutation, "_gh") as gh:
            out = submit_mutation.submit_document(document, request_key="terminal-123456")
        self.assertEqual("applied", out["submission"])
        gh.assert_not_called()

    def test_existing_different_request_is_rejected(self) -> None:
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
        with patch.object(submit_mutation, "_read_remote_document", side_effect=[existing]):
            with self.assertRaises(submit_mutation.MutationSubmitError):
                submit_mutation.submit_document(wanted, request_key="terminal-123456")


if __name__ == "__main__":
    unittest.main()
