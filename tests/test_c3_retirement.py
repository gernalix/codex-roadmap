from contextlib import closing
import importlib
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import c2_intake
import c2_issue_inbox
import c2_runtime
import c2_scheduler
import c2_snapshot_sync
import c2_worker
import c3_control
import c3_control_install
import c3_retirement as retirement
import c3_runtime
import c3_worker
import install_c2_inbox_maintenance
import install_c2_master_watchdog
import install_live_status_systemd
from test_c2_intake import C2IntakeTests


class C3RetirementTests(unittest.TestCase):
    def test_retired_cutover_and_snapshot_fail_without_evidence_or_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "absent.json"
            with self.assertRaisesRegex(retirement.RetirementError, "retired_permanently"):
                retirement.require_not_retired(marker)
            with self.assertRaisesRegex(retirement.RetirementError, "cutover_retired"):
                retirement.retire(marker=marker)
            with self.assertRaisesRegex(c2_snapshot_sync.SnapshotError, "transport_retired"):
                c2_snapshot_sync.sync(Path(tmp), Path(tmp) / "copy.sqlite")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_legacy_installers_fail_before_writing_after_retirement(self):
        for module in (install_c2_inbox_maintenance, install_c2_master_watchdog):
            with patch.object(module, "require_not_retired",
                              side_effect=retirement.RetirementError("c2_retired")), \
                 patch.object(module, "shutil") as copy:
                with self.assertRaises(retirement.RetirementError):
                    module.main()
                copy.copyfile.assert_not_called()
                copy.copy2.assert_not_called()
        with patch.object(install_live_status_systemd, "require_not_retired",
                          side_effect=retirement.RetirementError("c2_retired")), \
             patch.object(install_live_status_systemd, "shutil") as copy:
            with self.assertRaises(retirement.RetirementError):
                install_live_status_systemd.install(Path("/tmp/repo"), Path("/tmp/units"))
            copy.copy2.assert_not_called()

    def test_c3_unit_install_stages_without_starting(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(c3_control_install.subprocess, "run") as run:
            installed = c3_control_install.install(Path(tmp))
            self.assertEqual(set(installed), set(c3_control_install.UNITS))
            self.assertTrue((Path(tmp) / "c3-runtime.service").is_file())
            self.assertTrue((Path(tmp) / "c3-runtime.path").is_file())
            run.assert_called_once_with(["systemctl", "--user", "daemon-reload"], check=True)

    def test_control_has_no_snapshot_transport(self):
        with self.assertRaises(SystemExit):
            c3_control.main(["snapshot"])
        self.assertNotIn("c3-roadmap-snapshot.service", c3_control_install.UNITS)
        self.assertNotIn("c3-inbox-maintenance.timer", c3_control_install.UNITS)

    def test_c3_route_never_selects_legacy_codex(self):
        route = {"mode": "production", "healthy": True,
                 "source_repos": ["gernalix/codex-roadmap"],
                 "tracker_repo": "gernalix/c3-symphony", "no_legacy_codex": True}
        self.assertEqual("symphony", c2_scheduler.routed_executor(
            "auto", "coding", "gernalix/codex-roadmap", route))
        self.assertEqual("symphony-unhealthy", c2_scheduler.routed_executor(
            "auto", "coding", "other/repo", route))
        self.assertEqual("symphony-unhealthy", c2_scheduler.routed_executor(
            "auto", "diagnostic", "gernalix/codex-roadmap", route))
        self.assertEqual("chatgpt", c2_scheduler.routed_executor(
            "auto", "semantic", None, route))
        self.assertEqual("rdc", c2_scheduler.routed_executor(
            "auto", "native", None, route))
        unhealthy = {**route, "healthy": False}
        self.assertEqual("symphony-unhealthy", c2_scheduler.routed_executor(
            "auto", "coding", "gernalix/codex-roadmap", unhealthy))
        self.assertEqual("chatgpt", c2_scheduler.routed_executor(
            "auto", "semantic", None, unhealthy))

    def test_dependency_chain_stays_ordered_under_c3_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as db:
                db.execute("BEGIN IMMEDIATE")
                first = c2_intake.add_work_item(db, title="wi:5eb4", repo="r1")
                second = c2_intake.add_work_item(db, title="wi:8a0d", repo="r2",
                                                 depends_on=[first["work_item_id"]])
                third = c2_intake.add_work_item(db, title="wi:8a803", repo="r3",
                                                depends_on=[second["work_item_id"]])
                for item in (first, second, third):
                    c2_scheduler.configure(db, item["work_item_id"], activity="native",
                                           command=["true"])
                db.commit()
            route = {"mode": "production", "healthy": True, "source_repos": ["r1"],
                     "tracker_repo": "gernalix/c3-symphony", "no_legacy_codex": True}
            submitted = []
            with closing(c2_runtime._open_snapshot(path)) as db:
                c2_runtime.advance(db, submit=lambda op, args, key: submitted.append((op, args)),
                                   launch=lambda _: None, launch_notify=lambda _: None,
                                   worker_prefix="c3-run:", coding_route_override=route, now=10)
            schedule = [args for op, args in submitted if op == "schedule"][0]
            with closing(c2_intake._connect(path)) as db:
                db.execute("BEGIN IMMEDIATE")
                claimed = c2_scheduler.schedule(db, now=10, **schedule)
                self.assertEqual([first["work_item_id"]],
                                 [run["work_item_id"] for run in claimed])
                db.rollback()

    def test_c3_worker_disables_codex_adapter(self):
        with patch.object(c3_worker, "run_once", return_value={"phase": "ok"}) as run:
            self.assertEqual(c3_worker.main.__name__, "main")
            with patch("sys.argv", ["c3_worker.py", "--db", "/tmp/db", "--run-id", "r"]):
                self.assertEqual(c3_worker.main(), 0)
            self.assertFalse(run.call_args.kwargs["legacy_codex_allowed"])
            self.assertEqual(run.call_args.kwargs["worker_prefix"], "c3-run:")

    def test_c3_runtime_handoff_retains_fence_and_requests_bounded_inbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_path = C2IntakeTests().make_cutover_db(root)
            with closing(c2_intake._connect(snapshot_path)) as db:
                db.execute("BEGIN IMMEDIATE")
                c2_issue_inbox.capture(db, description="One observation")
                db.commit()
            marker = root / "retired.json"
            marker.write_text("{}")
            submitted = []
            route = {"mode": "production", "healthy": True,
                     "source_repos": ["gernalix/codex-roadmap"],
                     "tracker_repo": "gernalix/c3-symphony"}
            with patch.object(c3_runtime, "LOCK", root / "runtime.lock"), \
                 patch.object(c3_runtime, "DEFAULT_DB", root / "lease.sqlite3"), \
                 patch.object(c3_runtime, "MARKER", marker), \
                 patch.object(c3_runtime, "publish_runtime_identity"), \
                 patch.object(c3_runtime.core, "_coding_route", return_value=route), \
                 patch.object(c3_runtime.core, "_writer_submit",
                              side_effect=lambda op, args, key: submitted.append((op, args, key))), \
                 patch.object(c3_runtime.core, "advance", return_value={"ready": 0}) as advance:
                result = c3_runtime.run(snapshot_path)
            self.assertEqual(result, {"ready": 0, "inbox_pending": 1})
            self.assertEqual(submitted, [])
            self.assertEqual(advance.call_args.kwargs["worker_prefix"], "c3-run:")
            self.assertTrue(advance.call_args.kwargs["coding_route_override"]["no_legacy_codex"])

    def test_bounded_triage_objective_preserves_observation_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = C2IntakeTests().make_cutover_db(Path(tmp))
            with closing(c2_intake._connect(path)) as db:
                db.execute("BEGIN IMMEDIATE")
                issue = c2_issue_inbox.capture(db, description="Need a decision")
                result = c2_issue_inbox.ensure_triage(
                    db, project_url=c2_runtime.C2_TRIAGE_PROJECT_URL, batch_limit=25)
                objective = db.execute("SELECT objective FROM work_items WHERE work_item_id=?",
                                       (result["work_item_id"],)).fetchone()[0]
                self.assertIn("at most 25 rows", objective)
                self.assertEqual("pending", db.execute(
                    "SELECT state FROM issue_inbox WHERE issue_id=?",
                    (issue["issue_id"],)).fetchone()[0])
                db.rollback()

    def test_c3_worker_rejects_codex_and_never_uses_inbox_codex_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = C2IntakeTests().make_cutover_db(root)
            with closing(c2_intake._connect(path)) as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE work_items SET status='running' WHERE prompt_id='123456'")
                db.execute("""INSERT INTO work_item_runs VALUES(
                    'legacy','prompt:123456','event',1,'codex','running',100,
                    'c3-run:legacy',NULL,'{}',1)""")
                c2_scheduler.executor_started(db, run_id="legacy", now=2)
                triage = c2_intake.add_work_item(db, title="Triage")
                db.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",
                           (triage["work_item_id"],))
                db.execute("INSERT INTO work_item_tags VALUES(?,'c2:issue-triage')",
                           (triage["work_item_id"],))
                metadata = {"activity": "semantic", "project_url": c2_runtime.C2_TRIAGE_PROJECT_URL}
                db.execute("""INSERT INTO work_item_runs VALUES(
                    'triage',?,'event',1,'chatgpt','running',100,
                    'c3-run:triage',NULL,?,1)""",
                    (triage["work_item_id"], json.dumps(metadata)))
                c2_scheduler.executor_started(db, run_id="triage", now=2)
                db.commit()
            with self.assertRaisesRegex(c2_worker.WorkerError, "legacy_codex_retired"):
                c2_worker.run_once(path, "legacy", worker_prefix="c3-run:",
                                   legacy_codex_allowed=False)
            kill_switch = root / "disable-browser"
            kill_switch.write_text("")
            with patch.object(c2_worker, "KILL_SWITCH", kill_switch), \
                 patch.object(c2_worker, "lane_degraded", return_value=False), \
                 patch.object(c2_worker, "execute_inbox_codex") as fallback:
                result = c2_worker.run_once(path, "triage", worker_prefix="c3-run:",
                                            legacy_codex_allowed=False)
            self.assertEqual(result["phase"], "suspended")
            fallback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
