from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_goal_start as goal_start


class MasterGoalWakeHandoffTests(unittest.TestCase):
    def test_wake_event_carries_changed_control_plane_facts(self):
        db = {
            "inbox_pending": 283,
            "counts": {"pending": 40, "waiting": 48, "blocked": 36, "running": 2},
            "runnable_ids": ["wi:a", "wi:b"],
            "authority": {"supervisor_id": "sup-a", "lease_valid": False},
            "active_runs": [{
                "run_id": "run-a", "work_item_id": "wi:triage",
                "state": "recovering", "lease_expired": True,
            }],
        }
        with mock.patch.object(goal_start.master_watchdog, "read_json", return_value={
            "state_key": "abc123", "status": "waiting_external"
        }), mock.patch.object(goal_start.master_watchdog, "db_snapshot", return_value=db):
            event = goal_start.wake_event()
        self.assertEqual(event["watchdog_state_key"], "abc123")
        self.assertFalse(event["authority_lease_valid"])
        self.assertEqual(event["inbox_pending"], 283)
        self.assertTrue(event["active_runs"][0]["lease_expired"])

    def test_prompt_forces_fresh_canonical_read(self):
        event = {
            "watchdog_state_key": "abc123",
            "watchdog_status": "waiting_external",
            "inbox_pending": 283,
            "counts": {}, "runnable_count": 2,
            "authority_lease_valid": False, "active_runs": [],
        }
        prompt = goal_start.build_prompt(event)
        self.assertIn("MUST perform one fresh read of canonical C2 state", prompt)
        self.assertIn('"authority_lease_valid":false', prompt)
        self.assertIn("do not rely on the last verified state", prompt)
        self.assertEqual(goal_start.client_message_id(event), "c2-master-goal-watchdog-abc123")


if __name__ == "__main__":
    unittest.main()
