from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_goal_start as goal_start


class FakeRPC:
    def __init__(self, status):
        self.status = status
        self.calls = []

    def __call__(self, method, arguments):
        self.calls.append((method, arguments))
        if method == "thread/goal/get":
            return {"goal": {"status": self.status}}
        if method == "thread/goal/set":
            self.status = arguments["status"]
            return {"goal": {"status": self.status}}
        raise AssertionError(method)


class MasterGoalBoundedTurnTests(unittest.TestCase):
    def test_pause_if_active_pauses_goal(self):
        rpc = FakeRPC("active")
        self.assertEqual(goal_start.pause_if_active(rpc), "paused")
        self.assertEqual(rpc.status, "paused")

    def test_pause_if_active_preserves_terminal_status(self):
        rpc = FakeRPC("blocked")
        self.assertEqual(goal_start.pause_if_active(rpc), "blocked")
        self.assertEqual(rpc.status, "blocked")
        self.assertEqual(len([c for c in rpc.calls if c[0] == "thread/goal/set"]), 0)


if __name__ == "__main__":
    unittest.main()
