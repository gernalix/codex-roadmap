from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_roadmap_status as status


class Result:
    def __init__(self, stdout=""):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


class GoalRuntimeTests(unittest.TestCase):
    def test_master_goal_start_process_counts_as_live_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(status, "RPC_PIDFILE", Path(tmp) / "missing.pid"), \
                 mock.patch.object(status, "SESSION_ROOT", Path(tmp) / "sessions"), \
                 mock.patch.object(status, "sh", return_value=Result(
                     "123 python3 /home/daniele/.local/bin/c2-master-goal-start\n"
                 )):
                runtime = status.goal_runtime(1000)
        self.assertTrue(runtime["worker_alive"])
        self.assertTrue(runtime["helper_alive"])


if __name__ == "__main__":
    unittest.main()
