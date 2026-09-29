from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_watchdog as watchdog


def db_state(*, inbox=1, pending=1, waiting=0, blocked=0, runnable=None, runs=None):
    return {
        "available": True,
        "counts": {
            "pending": pending,
            "waiting": waiting,
            "blocked": blocked,
        },
        "inbox_pending": inbox,
        "runnable_ids": list(runnable or []),
        "active_runs": list(runs or []),
        "authority": {"supervisor_id": "sup-a", "lease_valid": True},
        "last_triaged_at_ms": 123,
    }


def snap(db, *, active="inactive", result="success", worker=False):
    return {
        "db": db,
        "service": {"active": active, "result": result},
        "master_worker_alive": worker,
    }


class MasterWatchdogDecisionTests(unittest.TestCase):
    def test_quiescent_when_no_work_remains(self):
        db = db_state(inbox=0, pending=0)
        result = watchdog.decide(snap(db), {}, now=1000)
        self.assertEqual(result["status"], "globally_quiescent")
        self.assertFalse(result["should_start_goal"])

    def test_active_goal_is_working(self):
        db = db_state()
        result = watchdog.decide(snap(db, active="active"), {}, now=1000)
        self.assertEqual(result["status"], "working")
        self.assertFalse(result["should_start_goal"])

    def test_changed_state_wakes_goal_once(self):
        db = db_state(inbox=25)
        result = watchdog.decide(snap(db), {}, now=1000)
        self.assertEqual(result["status"], "recovering")
        self.assertTrue(result["should_start_goal"])
        fp = watchdog.state_fingerprint(db)
        again = watchdog.decide(
            snap(db), {"last_wake_fingerprint": fp, "last_wake_at": 1000}, now=1010
        )
        self.assertEqual(again["status"], "waiting_external")
        self.assertFalse(again["should_start_goal"])

    def test_failed_service_has_bounded_retries(self):
        db = db_state()
        fp = watchdog.state_fingerprint(db)
        retry = watchdog.decide(
            snap(db, result="exit-code"),
            {"last_wake_fingerprint": fp, "last_wake_at": 900, "start_failures": 2},
            now=1000,
        )
        self.assertTrue(retry["should_start_goal"])
        exhausted = watchdog.decide(
            snap(db, result="exit-code"),
            {"last_wake_fingerprint": fp, "last_wake_at": 900, "start_failures": 3},
            now=1000,
        )
        self.assertEqual(exhausted["status"], "needs_user")
        self.assertEqual(exhausted["attention_key"], "master_goal_recovery_failed")

    def test_attention_dedup_and_resolution(self):
        problem = {
            "status": "needs_user",
            "attention_key": "manual_fix",
            "headline": "Serve attenzione",
            "intervention": "Apri ChatGPT",
        }
        event, alert = watchdog.attention_transition(problem, {}, False)
        self.assertEqual(event, "attention")
        duplicate, same = watchdog.attention_transition(problem, alert, False)
        self.assertIsNone(duplicate)
        self.assertEqual(same, alert)
        resolved, cleared = watchdog.attention_transition(
            {"status": "working", "attention_key": "", "headline": "Ripartito"},
            alert,
            True,
        )
        self.assertEqual(resolved, "resolved")
        self.assertFalse(cleared["active"])


if __name__ == "__main__":
    unittest.main()
