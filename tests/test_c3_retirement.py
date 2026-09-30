from contextlib import closing
import importlib
import json
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
    def test_retirement_masks_units_writes_audit_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker, audit = root / "c2-retired.json", root / "audit.json"
            units = root / "units"
            units.mkdir()
            (units / "c2-runtime.service").write_text("[Unit]\n")
            state = {unit: {"ActiveState": "active", "UnitFileState": "enabled",
                            "LoadState": "loaded"} for unit in retirement.LEGACY_UNITS}
            for unit in retirement.C3_REQUIRED:
                state[unit] = {"ActiveState": "inactive", "UnitFileState": "enabled",
                               "LoadState": "loaded"}
            calls = []

            def run(*args):
                calls.append(args)
                if args[0] == "show":
                    unit, name = args[1], args[2].removeprefix("--property=")
                    return type("Result", (), {"stdout": state[unit][name] + "\n"})()
                if args[0] == "list-units":
                    return type("Result", (), {"stdout": ""})()
                if args[0] == "stop":
                    for unit in args[1:]:
                        state[unit]["ActiveState"] = "inactive"
                if args[0] == "mask":
                    for unit in args[1:]:
                        state[unit]["UnitFileState"] = "masked"
                return type("Result", (), {"stdout": ""})()

            with patch.object(retirement, "_run", side_effect=run), \
                 patch.object(retirement, "_preflight", return_value={"artifact_sha256": "abc"}), \
                 patch.object(retirement, "_active_runs", return_value=0), \
                 patch.object(c2_snapshot_sync, "sync", return_value={"state": "current"}), \
                 patch.object(retirement, "USER_UNIT_DIR", units):
                result = retirement.retire(marker=marker, audit=audit)
                self.assertEqual(result["status"], "retired")
                self.assertEqual(retirement.retire(marker=marker, audit=audit)["status"],
                                 "already_retired")
            self.assertTrue((root / "retired-unit-files/c2-runtime.service").is_file())
            manifest = json.loads(audit.read_text())
            self.assertEqual(manifest["after"]["c2-runtime.service"]["unit_file"], "masked")
            self.assertEqual(manifest["c3_evidence"]["artifact_sha256"], "abc")
            self.assertEqual(sum(c[0] == "mask" for c in calls), 1)
            with self.assertRaises(retirement.RetirementError):
                retirement.require_not_retired(marker)

    def test_preflight_refuses_active_runs_and_requires_replacement_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker.json"
            with patch.object(retirement, "_preflight",
                              side_effect=retirement.RetirementError("active_roadmap_runs")):
                with self.assertRaisesRegex(retirement.RetirementError, "active_roadmap_runs"):
                    retirement.retire(marker=marker, audit=Path(tmp) / "audit.json")
            self.assertFalse(marker.exists())
        self.assertTrue({"c2-runtime.service", "c2-runtime.timer", "c2-runtime.path",
                         "c2-inbox-maintenance.timer", "c2-supervisor-recovery.timer"}
                        <= set(retirement.LEGACY_UNITS))
        self.assertNotIn("chatgpt-rdc-supervisor.service", retirement.LEGACY_UNITS)
        self.assertTrue({"c3-runtime.service", "c3-runtime.timer", "c3-runtime.path",
                         "c3-inbox-maintenance.service", "c3-inbox-maintenance.timer"}
                        <= set(retirement.C3_REQUIRED))

    def test_preflight_checks_live_backend_artifact_tracker_and_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend_module = importlib.import_module("c3_symphony_backend")
            bridge_module = importlib.import_module("c3_symphony_bridge")
            route_module = importlib.import_module("c3_symphony_route")
            root = Path(tmp)
            workflow = root / "WORKFLOW.md"
            workflow.write_text('---\n{"tracker":{"provider":{"repo":"gernalix/c3-symphony"}},'
                                '"server":{"host":"127.0.0.1"}}\n---\n')
            binary = root / "symphony"
            binary.write_bytes(b"pinned-artifact")
            config = bridge_module.HostConfig(
                "production", "gernalix/c3-symphony", frozenset({"gernalix/codex-roadmap"}))
            healthy = {"active_state": "active", "api_healthy": True,
                       "counts": {"running": 0, "retrying": 0}}
            with patch.object(bridge_module, "load_config", return_value=config), \
                 patch.object(route_module, "WORKFLOW", workflow), \
                 patch.object(backend_module, "PRODUCTION_BINARY", binary), \
                 patch.object(backend_module, "verify_artifact") as verify, \
                 patch.object(backend_module, "status", return_value=healthy), \
                 patch.object(c2_snapshot_sync, "sync"), \
                 patch.object(retirement, "_active_runs", return_value=0), \
                 patch.object(retirement, "_stale_triage", return_value=False), \
                 patch.object(retirement, "_property", return_value="loaded"):
                evidence = retirement._preflight(root / "snapshot")
                verify.assert_called_once_with(binary)
                self.assertEqual(evidence["tracker_repo"], "gernalix/c3-symphony")
                with patch.object(backend_module, "status",
                                  return_value={"active_state": "inactive", "api_healthy": False}):
                    with self.assertRaisesRegex(retirement.RetirementError,
                                                "c3_symphony_unhealthy"):
                        retirement._preflight(root / "snapshot")
                with patch.object(retirement, "_property", return_value="not-found"):
                    with self.assertRaisesRegex(retirement.RetirementError,
                                                "c3_unit_not_installed"):
                        retirement._preflight(root / "snapshot")

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
            self.assertTrue((Path(tmp) / "c3-inbox-maintenance.timer").is_file())
            run.assert_called_once_with(["systemctl", "--user", "daemon-reload"], check=True)

    def test_service_marker_gives_exclusive_c3_or_c2_ownership(self):
        units = Path(__file__).resolve().parents[1] / "systemd"
        for name in retirement.LEGACY_UNITS:
            source = units / name
            if source.is_file():
                self.assertIn("ConditionPathExists=!%h/.local/state/c3-control/c2-retired.json",
                              source.read_text(), name)
        for name in ("c3-roadmap-snapshot.service", "c3-runtime.service",
                     "c3-inbox-maintenance.service"):
            self.assertIn("ConditionPathExists=%h/.local/state/c3-control/c2-retired.json",
                          (units / name).read_text(), name)

    def test_c3_snapshot_uses_existing_read_only_sync(self):
        with patch.object(c3_control.c2_snapshot_sync, "sync",
                          return_value={"state": "current"}) as sync:
            self.assertEqual(c3_control.main(["snapshot", "--repo", "/tmp/repo",
                                              "--output", "/tmp/snapshot"]), 0)
            sync.assert_called_once_with(Path("/tmp/repo"), Path("/tmp/snapshot"))

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
            self.assertEqual(submitted[0][0], "ensure_issue_triage")
            self.assertEqual(submitted[0][1]["batch_limit"], 25)
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
