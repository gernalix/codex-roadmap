from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_goal_start as goal_start


class FakeRPC:
    def __init__(self, status="blocked", objective="old"):
        self.status = status
        self.objective = objective
        self.calls = []

    def __call__(self, method, arguments):
        self.calls.append((method, arguments))
        if method == "thread/goal/get":
            return {"goal": {"status": self.status, "objective": self.objective}}
        if method == "thread/goal/set":
            self.status = arguments["status"]
            self.objective = arguments.get("objective", self.objective)
            return {"goal": {"status": self.status, "objective": self.objective}}
        raise AssertionError(method)


class MasterGoalActivationTests(unittest.TestCase):
    def test_activate_goal_uses_native_goal_without_resuming_thread(self):
        rpc = FakeRPC()
        self.assertEqual(goal_start.activate_goal(rpc), "active")
        self.assertEqual(rpc.status, "active")
        self.assertEqual(rpc.objective, goal_start.OBJECTIVE)
        self.assertEqual([method for method, _ in rpc.calls], [
            "thread/goal/set", "thread/goal/get"
        ])


if __name__ == "__main__":
    unittest.main()
