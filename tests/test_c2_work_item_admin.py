from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_intake
import c2_scheduler
import c2_work_item_admin as admin
import test_c2_intake


class WorkItemAdminTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        path = test_c2_intake.C2IntakeTests().make_cutover_db(Path(self.tmp.name))
        self.conn = c2_intake._connect(path)
        c2_scheduler.install_schema(self.conn)
        self.conn.execute("BEGIN IMMEDIATE")
        self.root = c2_intake.add_work_item(self.conn, title="Old task", repo="gernalix/example")
        self.root_id = self.root["work_item_id"]

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_supersede_tree_preserves_completed_descendants_and_records_evidence(self):
        child = c2_intake.add_work_item(self.conn, title="Residual", parent_id=self.root_id)
        done = c2_intake.add_work_item(self.conn, title="Done", parent_id=self.root_id)
        self.conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?", (done["work_item_id"],))
        successor = c2_intake.add_work_item(self.conn, title="Successor")
        fact = "gernalix/example main abc123 src/feature.py absorbs old task"
        admin.reconcile(self.conn, self.root_id, classification="DUPLICATE_MERGE",
                        status="superseded", evidence=[fact],
                        superseded_by=successor["work_item_id"], include_descendants=True)
        states = dict(self.conn.execute("SELECT work_item_id,status FROM work_items"))
        self.assertEqual("superseded", states[self.root_id])
        self.assertEqual("superseded", states[child["work_item_id"]])
        self.assertEqual("completed", states[done["work_item_id"]])
        self.assertEqual(1, self.conn.execute("SELECT count(*) FROM work_item_relations WHERE from_work_item_id=? AND to_work_item_id=? AND relation_type='superseded_by'", (self.root_id, successor["work_item_id"])).fetchone()[0])
        self.assertEqual(1, self.conn.execute("SELECT count(*) FROM work_item_evidence WHERE work_item_id=? AND evidence_kind='classification'", (self.root_id,)).fetchone()[0])

    def test_supersede_tree_rejects_unfinished_required_nested_gate(self):
        child = c2_intake.add_work_item(self.conn, title="Implementation", parent_id=self.root_id)
        gate = c2_intake.add_work_item(self.conn, title="Physical QA gate",
                                      kind="gate", parent_id=child["work_item_id"],
                                      acceptance=["QA01", "QA02"])
        successor = c2_intake.add_work_item(self.conn, title="Active successor")
        with self.assertRaisesRegex(ValueError, "required_descendant_gate_requires_separate_resolution"):
            admin.reconcile(self.conn, self.root_id, classification="DUPLICATE_MERGE",
                            status="superseded", evidence=["Successor covers implementation"],
                            superseded_by=successor["work_item_id"], include_descendants=True)
        states = dict(self.conn.execute("SELECT work_item_id,status FROM work_items"))
        self.assertEqual("pending", states[self.root_id])
        self.assertEqual("pending", states[child["work_item_id"]])
        self.assertEqual("pending", states[gate["work_item_id"]])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM work_item_relations").fetchone()[0])

    def test_waiting_requires_blocker_and_removes_only_named_dependency(self):
        dep = c2_intake.add_work_item(self.conn, title="Old dependency")
        self.conn.execute("INSERT INTO work_item_dependencies(work_item_id,depends_on_work_item_id,required) VALUES(?,?,1)", (self.root_id, dep["work_item_id"]))
        with self.assertRaisesRegex(ValueError, "waiting_blocker_required"):
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_WAITING",
                            status="waiting", evidence=["repo main abc123 path"])
        admin.reconcile(self.conn, self.root_id, classification="CURRENT_WAITING",
                        status="waiting", evidence=["repo main abc123 path"],
                        fields={"blocker": "Login required", "sort_order": 99},
                        remove_dependencies=[dep["work_item_id"]])
        row = self.conn.execute("SELECT status,blocker,sort_order FROM work_items WHERE work_item_id=?", (self.root_id,)).fetchone()
        self.assertEqual(("waiting", "Login required", 99), tuple(row))
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM work_item_dependencies WHERE work_item_id=?", (self.root_id,)).fetchone()[0])

    def test_rejects_prompt_and_active_run(self):
        with self.assertRaisesRegex(ValueError, "nonprompt_root_required"):
            admin.reconcile(self.conn, "prompt:111111", classification="OBSOLETE",
                            status="cancelled", evidence=["repo main abc123 path"])
        c2_scheduler.configure(self.conn, self.root_id, activity="native", command=["true"])
        run = c2_scheduler.schedule(self.conn, event_key="test", now=1)[0]
        with self.assertRaisesRegex(ValueError, "work_item_state_changed|active_run_requires_normal_lifecycle"):
            admin.reconcile(self.conn, self.root_id, classification="OBSOLETE",
                            status="cancelled", evidence=["repo main abc123 path"])
        self.assertEqual(self.root_id, run["work_item_id"])

    def test_invalid_fields_and_evidence_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "invalid_work_item_fields"):
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_READY",
                            status="pending", evidence=["repo main abc123 path"], fields={"prompt_id": "123456"})
        with self.assertRaisesRegex(ValueError, "repository_evidence_required"):
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_READY",
                            status="pending", evidence=[])

    def test_updates_acceptance_and_adds_or_replaces_dependencies_and_tags(self):
        old_dep = c2_intake.add_work_item(self.conn, title="Old dependency")
        new_dep = c2_intake.add_work_item(self.conn, title="New dependency")
        extra_dep = c2_intake.add_work_item(self.conn, title="Extra dependency")
        self.conn.execute("INSERT INTO work_item_dependencies(work_item_id,depends_on_work_item_id,required,note) VALUES(?,?,0,'old')",
                          (self.root_id, old_dep["work_item_id"]))
        self.conn.execute("INSERT INTO work_item_tags(work_item_id,tag) VALUES(?, 'old-tag')", (self.root_id,))

        admin.reconcile(
            self.conn, self.root_id, classification="CURRENT_READY", status="pending",
            evidence=["repo main abc123 acceptance reviewed"],
            fields={"acceptance_json": ["First criterion", "Second criterion"]},
            add_dependencies=[new_dep["work_item_id"]], add_tags=["new-tag"],
        )
        self.assertEqual(["First criterion", "Second criterion"], json.loads(self.conn.execute(
            "SELECT acceptance_json FROM work_items WHERE work_item_id=?", (self.root_id,)
        ).fetchone()[0]))
        self.assertEqual({old_dep["work_item_id"], new_dep["work_item_id"]}, {
            row[0] for row in self.conn.execute(
                "SELECT depends_on_work_item_id FROM work_item_dependencies WHERE work_item_id=?", (self.root_id,)
            )
        })
        self.assertEqual({"old-tag", "new-tag"}, {
            row[0] for row in self.conn.execute("SELECT tag FROM work_item_tags WHERE work_item_id=?", (self.root_id,))
        })

        admin.reconcile(
            self.conn, self.root_id, classification="CURRENT_READY", status="pending",
            evidence=["repo main abc123 dependencies and tags replaced"],
            replace_dependencies=[extra_dep["work_item_id"]], replace_tags=["replacement"],
        )
        self.assertEqual({extra_dep["work_item_id"]}, {
            row[0] for row in self.conn.execute(
                "SELECT depends_on_work_item_id FROM work_item_dependencies WHERE work_item_id=?", (self.root_id,)
            )
        })
        self.assertEqual({"replacement"}, {
            row[0] for row in self.conn.execute("SELECT tag FROM work_item_tags WHERE work_item_id=?", (self.root_id,))
        })

    def test_acceptance_dependencies_and_tags_validation_fail_closed(self):
        dep = c2_intake.add_work_item(self.conn, title="Dependency")
        with self.assertRaisesRegex(ValueError, "invalid_acceptance"):
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_READY", status="pending",
                            evidence=["repo main abc123"], fields={"acceptance_json": [" "]})
        with self.assertRaisesRegex(ValueError, "dependency_cycle"):
            self.conn.execute("INSERT INTO work_item_dependencies(work_item_id,depends_on_work_item_id,required) VALUES(?,?,1)",
                              (dep["work_item_id"], self.root_id))
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_READY", status="pending",
                            evidence=["repo main abc123"], add_dependencies=[dep["work_item_id"]])
        with self.assertRaisesRegex(ValueError, "invalid_tags"):
            admin.reconcile(self.conn, self.root_id, classification="CURRENT_READY", status="pending",
                            evidence=["repo main abc123"], replace_tags=[""])


if __name__ == "__main__":
    unittest.main()
