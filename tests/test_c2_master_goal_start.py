from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_goal_start as goal_start


class FakeRPC:
    def __init__(self, status="blocked", objective="old", thread_status="notLoaded"):
        self.status = status
        self.objective = objective
        self.thread_status = thread_status
        self.calls = []

    def __call__(self, method, arguments):
        self.calls.append((method, arguments))
        if method == "thread/goal/get":
            return {"goal": {"status": self.status, "objective": self.objective}}
        if method == "thread/goal/set":
            self.status = arguments["status"]
            self.objective = arguments.get("objective", self.objective)
            return {"goal": {"status": self.status, "objective": self.objective}}
        if method == "thread/read":
            return {"thread": {"id": goal_start.THREAD,
                               "status": {"type": self.thread_status}, "turns": []}}
        if method == "model/list":
            return {"data": [{"id": "gpt-6-luna", "model": "gpt-6-luna",
                              "displayName": "GPT-6 Luna",
                              "supportedReasoningEfforts": [{"reasoningEffort": "medium"}]}],
                    "nextCursor": None}
        if method == "thread/resume":
            self.thread_status = "idle"
            return {"thread": {"id": goal_start.THREAD}}
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
        self.assertNotIn("execute exactly one batch", goal_start.OBJECTIVE)
        self.assertIn("backfill completed slots", goal_start.OBJECTIVE)

    def test_rehydrate_unloaded_thread_resumes_without_starting_turn(self):
        rpc = FakeRPC(thread_status="notLoaded")
        self.assertEqual(goal_start.rehydrate_thread(rpc), "resumed")
        methods = [method for method, _ in rpc.calls]
        self.assertEqual(methods, ["thread/read", "model/list", "thread/resume"])
        self.assertNotIn("turn/start", methods)
        resume = rpc.calls[-1][1]
        self.assertEqual(resume["threadId"], goal_start.THREAD)
        self.assertEqual(resume["cwd"], str(goal_start.RUNTIME_WORKTREE))
        self.assertEqual(resume["config"]["model_reasoning_effort"], "medium")

    def test_rehydrate_loaded_thread_does_not_create_second_owner(self):
        rpc = FakeRPC(thread_status="active")
        self.assertEqual(goal_start.rehydrate_thread(rpc), "active")
        self.assertEqual([method for method, _ in rpc.calls], ["thread/read"])


if __name__ == "__main__":
    unittest.main()
