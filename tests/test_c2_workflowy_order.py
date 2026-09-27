from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import c2_control
import c2_workflowy_order as cli


class WorkflowyOrderCliTests(unittest.TestCase):
    def write_env(self, root: str, text: str) -> Path:
        path = Path(root) / "runtime.env"
        path.write_text(text, encoding="utf-8")
        return path

    def test_runtime_env_parsing_and_invalid_authority_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid = self.write_env(
                tmp, "C2_SUPERVISOR_ID=supervisor:one\nC2_FENCING_TOKEN=7\n"
            )
            self.assertEqual(("supervisor:one", 7), cli.load_runtime_identity(valid))
            for text, error in (
                ("C2_SUPERVISOR_ID=only\n", "invalid_fencing_token"),
                ("C2_SUPERVISOR_ID=bad value\nC2_FENCING_TOKEN=1\n", "invalid_supervisor_id"),
                ("C2_SUPERVISOR_ID=ok\nC2_FENCING_TOKEN=zero\n", "invalid_fencing_token"),
                ("UNKNOWN=value\nC2_SUPERVISOR_ID=ok\nC2_FENCING_TOKEN=1\n", "invalid_supervisor_runtime_env"),
            ):
                path = self.write_env(tmp, text)
                with self.subTest(text=text), self.assertRaisesRegex(
                    cli.WorkflowyOrderError, error
                ):
                    cli.load_runtime_identity(path)
            with self.assertRaisesRegex(
                cli.WorkflowyOrderError, "supervisor_runtime_env_missing"
            ):
                cli.load_runtime_identity(Path(tmp) / "missing.env")

    def test_set_and_clear_use_control_path_without_authority_in_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime_env = self.write_env(
                tmp, "C2_SUPERVISOR_ID=supervisor-one\nC2_FENCING_TOKEN=9\n"
            )
            with patch.object(
                cli.c2_control, "submit_control", return_value={"issue_number": 12}
            ) as submit, redirect_stdout(StringIO()) as output:
                self.assertEqual(0, cli.main([
                    "set", "--scope", "roadmap", "--source-modified-at", "wf:123",
                    "wi:b", "wi:a",
                ], runtime_env=runtime_env))
                call = submit.call_args.kwargs
                self.assertEqual("set_manual_order", call["operation"])
                self.assertEqual(["wi:b", "wi:a"], call["arguments"]["ordered_ids"])
                self.assertEqual("workflowy", call["arguments"]["source"])
                self.assertNotIn("supervisor_authority", call["arguments"])
                self.assertEqual("supervisor-one", call["supervisor_id"])
                self.assertEqual(9, call["fencing_token"])
                self.assertEqual("queued", json.loads(output.getvalue())["status"])

                self.assertEqual(0, cli.main([
                    "clear", "--scope", "inbox", "issue:b", "issue:a",
                ], runtime_env=runtime_env))
                call = submit.call_args.kwargs
                self.assertEqual("clear_manual_order", call["operation"])
                self.assertEqual(
                    {"scope": "inbox", "ids": ["issue:a", "issue:b"]},
                    call["arguments"],
                )

    def test_request_identity_is_stable_and_covers_semantic_inputs(self):
        first = cli.request_key("set", "roadmap", ["wi:b", "wi:a"], "wf:1")
        self.assertEqual(
            first, cli.request_key("set", "roadmap", ["wi:b", "wi:a"], "wf:1")
        )
        self.assertNotEqual(
            first, cli.request_key("set", "roadmap", ["wi:a", "wi:b"], "wf:1")
        )
        self.assertNotEqual(
            first, cli.request_key("set", "roadmap", ["wi:b", "wi:a"], "wf:2")
        )
        self.assertNotEqual(
            first, cli.request_key("set", "inbox", ["wi:b", "wi:a"], "wf:1")
        )
        self.assertEqual(
            cli.request_key("clear", "roadmap", ["wi:b", "wi:a"]),
            cli.request_key("clear", "roadmap", ["wi:a", "wi:b"]),
        )

    def test_missing_runtime_env_stops_before_control_submission(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            cli.c2_control, "submit_control"
        ) as submit:
            with self.assertRaisesRegex(
                cli.WorkflowyOrderError, "supervisor_runtime_env_missing"
            ):
                cli.main([
                    "set", "--scope", "roadmap", "--source-modified-at", "wf:1",
                    "wi:a",
                ], runtime_env=Path(tmp) / "missing.env")
            submit.assert_not_called()

    def test_shared_control_path_injects_validated_authority(self):
        lease = MagicMock()
        lease.__enter__.return_value = lease
        lease.__exit__.return_value = False
        row = {
            "supervisor_id": "supervisor-one",
            "fencing_token": 9,
            "lease_expires_at": 9999999999.0,
        }
        arguments = {"scope": "roadmap", "ids": ["wi:a"]}
        with patch.object(c2_control, "connect", return_value=lease), \
             patch.object(c2_control, "_require", return_value=row) as require, \
             patch.object(c2_control, "record_activity", return_value=row), \
             patch.object(c2_control, "submit_document", return_value={"issue_number": 1}) as submit:
            c2_control.submit_control(
                operation="clear_manual_order", arguments=arguments,
                request_key="stable-key", supervisor_id="supervisor-one",
                fencing_token=9, actor="c2-workflowy-order",
            )
        require.assert_called_once()
        operation = submit.call_args.args[0]["operations"][0]
        self.assertEqual("c2_clear_manual_order", operation["op"])
        self.assertEqual(row, operation["arguments"]["supervisor_authority"])
        self.assertNotIn("supervisor_authority", arguments)
        self.assertEqual("stable-key", submit.call_args.kwargs["request_key"])


if __name__ == "__main__":
    unittest.main()
