from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_watchdog as watchdog


def db_state(*, inbox=1, pending=1, waiting=0, blocked=0, runnable=None, runs=None, triage_run=None):
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
        "authority": {"supervisor_id": "sup-a", "lease_valid": True, "lease_stale": False},
        "triage_run": triage_run,
        "last_triaged_at_ms": 123,
    }


def snap(db, *, active="inactive", result="success", worker=False, delegated=None,
         run_workers=None, goal_status="paused"):
    return {
        "db": db,
        "service": {"active": active, "result": result},
        "master_worker_alive": worker,
        "delegated_worker": delegated or {},
        "run_workers": run_workers or [],
        "goal_status": goal_status,
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

    def test_live_delegated_worker_is_working_even_with_expired_lease(self):
        triage = {
            "run_id": "triage-1", "state": "recovering",
            "worker_ref": "c2-run:triage-1", "lease_expired": True,
        }
        db = db_state(inbox=25, triage_run=triage)
        result = watchdog.decide(snap(db, delegated={
            "run_id": "triage-1", "alive": True,
            "progressing": True, "progress_age_s": 30,
        }), {}, now=1000)
        self.assertEqual(result["status"], "working")
        self.assertEqual(result["phase"], "delegated")
        self.assertFalse(result["should_start_goal"])

    def test_delegated_worker_health_changes_fingerprint(self):
        triage = {
            "run_id": "triage-1", "state": "running",
            "worker_ref": "c2-run:triage-1", "lease_expired": True,
        }
        db = db_state(inbox=25, triage_run=triage)
        healthy = watchdog.state_fingerprint(
            db, {"alive": True, "progressing": True}
        )
        stalled = watchdog.state_fingerprint(
            db, {"alive": True, "progressing": False}
        )
        dead = watchdog.state_fingerprint(
            db, {"alive": False, "progressing": False}
        )
        self.assertNotEqual(healthy, stalled)
        self.assertNotEqual(healthy, dead)

    def test_stalled_delegated_worker_never_wakes_goal(self):
        triage = {
            "run_id": "triage-1", "state": "running",
            "worker_ref": "c2-run:triage-1", "lease_expired": True,
        }
        db = db_state(inbox=25, triage_run=triage)
        healthy_fp = watchdog.state_fingerprint(
            db, {"alive": True, "progressing": True}
        )
        result = watchdog.decide(
            snap(db, delegated={
                "run_id": "triage-1", "alive": True,
                "progressing": False, "progress_age_s": 4000,
            }),
            {"last_wake_fingerprint": healthy_fp, "last_wake_at": 900},
            now=1000,
        )
        self.assertEqual(result["status"], "working")
        self.assertFalse(result["should_start_goal"])

    def test_dead_delegated_worker_recovers_run_after_healthy_state(self):
        triage = {
            "run_id": "triage-1", "state": "running",
            "worker_ref": "c2-run:triage-1", "lease_expired": True,
        }
        db = db_state(inbox=25, triage_run=triage, runs=[triage])
        healthy_fp = watchdog.state_fingerprint(
            db, {"alive": True, "progressing": True}
        )
        result = watchdog.decide(
            snap(db, run_workers=[{"active": "inactive", "lease_expired": True}], delegated={
                "run_id": "triage-1", "alive": False,
                "progressing": False, "progress_age_s": 4000,
            }),
            {"last_wake_fingerprint": healthy_fp, "last_wake_at": 900},
            now=1000,
        )
        self.assertEqual(result["status"], "recovering")
        self.assertTrue(result["should_recover_runs"])
        self.assertFalse(result["should_start_goal"])

    def test_live_run_blocks_restart_with_expired_lease(self):
        db = db_state(runs=[{"run_id": "r1", "state": "running", "lease_expired": True}])
        result = watchdog.decide(snap(db, run_workers=[{
            "run_id": "r1", "active": "active", "lease_expired": True,
        }], goal_status="active"), {}, now=1000)
        self.assertEqual(result["status"], "working")
        self.assertFalse(result["should_start_goal"])

    def test_ambiguous_worker_state_escalates(self):
        db = db_state(runs=[{"run_id": "r1", "state": "running", "lease_expired": True}])
        result = watchdog.decide(snap(db, run_workers=[{
            "run_id": "r1", "active": "unknown", "lease_expired": True,
        }]), {}, now=1000)
        self.assertEqual(result["status"], "needs_user")
        self.assertFalse(result["should_start_goal"])

    def test_active_orphaned_goal_restarts_even_with_unchanged_fingerprint(self):
        db = db_state()
        fp = watchdog.state_fingerprint(db)
        result = watchdog.decide(snap(db, goal_status="active"), {
            "last_wake_fingerprint": fp, "last_wake_at": 999,
        }, now=1000)
        self.assertTrue(result["should_start_goal"])

    def test_recovery_deduplicated(self):
        db = db_state(runs=[{"run_id": "r1", "state": "running", "lease_expired": True}])
        workers = [{"run_id": "r1", "active": "inactive", "lease_expired": True}]
        recovery = watchdog.decide(snap(db, run_workers=workers), {}, now=1000)
        result = watchdog.decide(snap(db, run_workers=[{
            "run_id": "r1", "active": "inactive", "lease_expired": True,
        }]), {"last_recovery_fingerprint": recovery["recovery_key"]}, now=1000)
        self.assertEqual(result["status"], "waiting_external")
        self.assertFalse(result.get("should_recover_runs", False))

    def test_recover_dead_run_while_other_worker_is_live(self):
        db = db_state(runs=[{"run_id": "r1"}, {"run_id": "r2"}])
        result = watchdog.decide(snap(db, run_workers=[
            {"run_id": "r1", "active": "active", "lease_expired": True},
            {"run_id": "r2", "active": "inactive", "lease_expired": True},
        ]), {}, now=1000)
        self.assertTrue(result["should_recover_runs"])
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

    def test_triage_gate_ignores_inbox_growth_and_unrelated_counts(self):
        triage = {
            "run_id": "triage-1", "state": "recovering",
            "worker_ref": "c2-run:triage-1", "lease_expired": True,
        }
        first = db_state(inbox=264, pending=80, waiting=10, blocked=5, triage_run=triage)
        second = db_state(inbox=284, pending=120, waiting=18, blocked=9, triage_run=triage)
        self.assertEqual(watchdog.state_fingerprint(first), watchdog.state_fingerprint(second))
        second["authority"]["lease_stale"] = True
        self.assertNotEqual(watchdog.state_fingerprint(first), watchdog.state_fingerprint(second))

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
