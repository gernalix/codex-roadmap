import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c3_remote_ingress as ingress


class RemoteIngressTests(unittest.TestCase):
    def test_priority_and_rejection_do_not_write_in_remote_checkout(self):
        rows = [
            {'number': 1, 'title': '[roadmap-mutation] ordinary', 'body': '{}'},
            {'number': 2, 'title': '[roadmap-mutation] start-123456', 'body': '{}'},
            {'number': 3, 'title': '[roadmap-mutation] invalid', 'body': 'invalid'},
        ]
        with patch.object(ingress, 'gh', side_effect=[rows, {}, {}, {}]) as gh, patch.object(ingress, 'submit_local', return_value={'submission': 'applied'}) as submit:
            result = ingress.drain()
            self.assertEqual(result, {'applied': 2, 'rejected': 1})
            self.assertEqual(submit.call_args_list[0].kwargs['issue_number'], 2)
            self.assertEqual(gh.call_args_list[-1].args[-1], 'state_reason=not_planned')

    def test_socket_failure_preserves_pending_issue(self):
        rows = [{'number': 1, 'title': '[roadmap-mutation] ordinary', 'body': '{}'}]
        with patch.object(ingress, 'gh', return_value=rows) as gh, patch.object(ingress, 'submit_local', side_effect=ConnectionRefusedError):
            with self.assertRaises(ConnectionRefusedError):
                ingress.drain()
            self.assertEqual(gh.call_count, 1)
