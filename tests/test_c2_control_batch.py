from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_control


class C2ControlBatchTests(unittest.TestCase):
    def test_submit_controls_uses_one_transactional_document(self):
        authority = {
            "supervisor_id": "sup-a",
            "fencing_token": 7,
            "lease_expires_at": 1234.0,
        }
        lease = mock.MagicMock()
        with mock.patch.object(c2_control, "connect") as connect, \
             mock.patch.object(c2_control, "_require", return_value=authority), \
             mock.patch.object(c2_control, "record_activity", return_value=authority), \
             mock.patch.object(c2_control, "submit_document", return_value={"submission": "queued"}) as submit:
            connect.return_value.__enter__.return_value = lease
            result = c2_control.submit_controls(
                operations=[
                    {"operation": "promote_issue", "arguments": {"issue_id": "issue:1"}},
                    {"operation": "discard_issue", "arguments": {"issue_id": "issue:2"}},
                ],
                request_key="batch-1", supervisor_id="sup-a", fencing_token=7,
                canonical_renew=True,
            )
        self.assertEqual({"submission": "queued"}, result)
        document = submit.call_args.args[0]
        self.assertEqual(
            ["c2_renew_supervisor", "c2_promote_issue", "c2_discard_issue"],
            [op["op"] for op in document["operations"]],
        )
        self.assertEqual("batch-1", submit.call_args.kwargs["request_key"])
        for operation in document["operations"]:
            self.assertEqual(
                authority,
                operation["arguments"]["supervisor_authority"],
            )

    def test_submit_controls_rejects_unbounded_batch(self):
        with self.assertRaisesRegex(ValueError, "bounded"):
            c2_control.submit_controls(
                operations=[{"operation": "discard_issue", "arguments": {}}] * 51,
                request_key="too-many", supervisor_id="sup-a", fencing_token=7,
            )


if __name__ == "__main__":
    unittest.main()
