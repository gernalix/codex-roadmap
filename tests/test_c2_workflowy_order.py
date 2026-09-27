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
import submit_mutation


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
                    "clear", "--scope", "inbox", "--source-modified-at", "wf:reset:1",
                    "issue:b", "issue:a",
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
            cli.request_key("clear", "roadmap", ["wi:b", "wi:a"], "wf:reset:1"),
            cli.request_key("clear", "roadmap", ["wi:a", "wi:b"], "wf:reset:1"),
        )
        self.assertNotEqual(
            cli.request_key("clear", "roadmap", ["wi:a"], "wf:reset:1"),
            cli.request_key("clear", "roadmap", ["wi:a"], "wf:reset:2"),
        )

    def test_clear_reset_events_are_idempotent_but_distinct(self):
        clear_one = cli.request_key(
            "clear", "roadmap", ["wi:b", "wi:a"], "wf:reset:1"
        )
        set_key = cli.request_key(
            "set", "roadmap", ["wi:a", "wi:b"], "wf:reorder:2"
        )
        clear_two = cli.request_key(
            "clear", "roadmap", ["wi:a", "wi:b"], "wf:reset:3"
        )
        self.assertEqual(
            clear_one,
            cli.request_key(
                "clear", "roadmap", ["wi:a", "wi:b"], "wf:reset:1"
            ),
        )
        self.assertNotEqual(clear_one, set_key)
        self.assertNotEqual(clear_one, clear_two)

    def test_clear_requires_valid_reset_event_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime_env = self.write_env(
                tmp, "C2_SUPERVISOR_ID=supervisor-one\nC2_FENCING_TOKEN=9\n"
            )
            with patch.object(cli.c2_control, "submit_control") as submit:
                with self.assertRaises(SystemExit):
                    cli.main(
                        ["clear", "--scope", "roadmap"],
                        runtime_env=runtime_env,
                    )
                with self.assertRaisesRegex(
                    cli.WorkflowyOrderError, "source_modified_at_required"
                ):
                    cli.main(
                        [
                            "clear", "--scope", "roadmap",
                            "--source-modified-at", "",
                        ],
                        runtime_env=runtime_env,
                    )
                with self.assertRaisesRegex(
                    cli.WorkflowyOrderError, "invalid_source_modified_at"
                ):
                    cli.main(
                        [
                            "clear", "--scope", "roadmap",
                            "--source-modified-at", " wf:reset:1 ",
                        ],
                        runtime_env=runtime_env,
                    )
            submit.assert_not_called()

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

    def test_set_control_path_keeps_full_validated_authority(self):
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
                operation="set_manual_order", arguments=arguments,
                request_key="stable-key", supervisor_id="supervisor-one",
                fencing_token=9, actor="c2-workflowy-order",
            )
        require.assert_called_once()
        operation = submit.call_args.args[0]["operations"][0]
        self.assertEqual("c2_set_manual_order", operation["op"])
        self.assertEqual(row, operation["arguments"]["supervisor_authority"])
        self.assertNotIn("supervisor_authority", arguments)
        self.assertEqual("stable-key", submit.call_args.kwargs["request_key"])

    def test_workflowy_canonical_renew_is_atomic_with_manual_order(self):
        lease = MagicMock()
        lease.__enter__.return_value = lease
        lease.__exit__.return_value = False
        row = {
            "supervisor_id": "supervisor-one",
            "fencing_token": 9,
            "lease_expires_at": 9999999999.0,
        }
        with patch.object(c2_control, "connect", return_value=lease), \
             patch.object(c2_control, "_require", return_value=row), \
             patch.object(c2_control, "record_activity", return_value=row), \
             patch.object(c2_control, "submit_document", return_value={}) as submit:
            c2_control.submit_control(
                operation="clear_manual_order",
                arguments={"scope": "roadmap", "ids": ["wi:a"]},
                request_key="fresh-transport-key",
                supervisor_id="supervisor-one",
                fencing_token=9,
                actor="c2-workflowy-order",
                canonical_renew=True,
            )
        document = submit.call_args.args[0]
        self.assertEqual(
            ["c2_renew_supervisor", "c2_clear_manual_order"],
            [operation["op"] for operation in document["operations"]],
        )
        for operation in document["operations"]:
            self.assertEqual(row, operation["arguments"]["supervisor_authority"])

    def test_authority_renewal_does_not_change_same_event_document(self):
        lease = MagicMock()
        lease.__enter__.return_value = lease
        lease.__exit__.return_value = False
        rows = [
            {
                "supervisor_id": "supervisor-one",
                "fencing_token": 9,
                "lease_expires_at": 1000.0,
            },
            {
                "supervisor_id": "supervisor-one",
                "fencing_token": 9,
                "lease_expires_at": 2000.0,
            },
        ]
        key = cli.request_key(
            "clear", "roadmap", ["wi:a"], "wf:reset:1"
        )
        with patch.object(c2_control, "connect", return_value=lease), \
             patch.object(c2_control, "_require", side_effect=rows), \
             patch.object(c2_control, "record_activity", side_effect=rows), \
             patch.object(c2_control, "submit_document", return_value={}) as submit:
            for _ in rows:
                c2_control.submit_control(
                    operation="clear_manual_order",
                    arguments={"scope": "roadmap", "ids": ["wi:a"]},
                    request_key=key,
                    supervisor_id="supervisor-one",
                    fencing_token=9,
                    actor="c2-workflowy-order",
                )
        first, second = [call.args[0] for call in submit.call_args_list]
        self.assertEqual(first, second)
        self.assertEqual(
            {"supervisor_id": "supervisor-one", "fencing_token": 9},
            first["operations"][0]["arguments"]["supervisor_authority"],
        )
        self.assertEqual(
            [key, key],
            [call.kwargs["request_key"] for call in submit.call_args_list],
        )

    def test_same_key_different_manual_order_operation_fails_closed(self):
        authority = {"supervisor_id": "supervisor-one", "fencing_token": 9}
        clear = {
            "schema": submit_mutation.SCHEMA,
            "actor": "c2-workflowy-order",
            "operations": [{
                "op": "c2_clear_manual_order",
                "arguments": {
                    "scope": "roadmap",
                    "ids": ["wi:a"],
                    "supervisor_authority": authority,
                },
            }],
        }
        issue = {
            "number": 23,
            "state": "OPEN",
            "body": json.dumps(clear),
            "url": "https://example.invalid/issues/23",
        }
        with patch.object(submit_mutation, "_matching_issues", return_value=[issue]):
            replay = submit_mutation.submit_document(clear, request_key="same-event")
            self.assertEqual("pending", replay["submission"])
            changed = json.loads(json.dumps(clear))
            changed["operations"][0]["op"] = "c2_set_manual_order"
            with self.assertRaisesRegex(
                submit_mutation.MutationSubmitError,
                "request_key_conflict:same-event",
            ):
                submit_mutation.submit_document(changed, request_key="same-event")


if __name__ == "__main__":
    unittest.main()
