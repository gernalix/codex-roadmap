from __future__ import annotations
import hashlib, sys, tempfile, unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_db as db

class RoadmapDBTests(unittest.TestCase):
    def test_render_reads_canonical_database_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            conn = db.connect(repo)
            db.register_prompt(conn, prompt_id="123456", slug="one", title="One", current_path="prompts/one.md")
            conn.commit()
            conn.close()
            (repo / "prompts").mkdir()
            (repo / "prompts" / "one.md").write_text("one\n", encoding="utf-8")
            database = repo / "roadmap.sqlite"
            before = hashlib.sha256(database.read_bytes()).hexdigest()
            database.chmod(0o400)
            try:
                db.render(repo)
            finally:
                database.chmod(0o600)
            self.assertEqual(before, hashlib.sha256(database.read_bytes()).hexdigest())

    def test_reopening_stable_database_does_not_rewrite_view_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            conn.commit(); conn.close()
            database=repo/"roadmap.sqlite"
            before=hashlib.sha256(database.read_bytes()).hexdigest()
            conn=db.connect(repo)
            conn.close()
            after=hashlib.sha256(database.read_bytes()).hexdigest()
            self.assertEqual(before,after)

    def test_prompt_body_is_canonical_sqlite_materialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            body="PROMPT_ID=123456\nGoal: test\n"
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                prompt_text=body,
            )
            conn.commit()
            self.assertEqual(body, db.canonical_prompt_text(conn, "123456"))
            row=conn.execute(
                "SELECT sha256 FROM prompt_materializations WHERE prompt_id='123456'"
            ).fetchone()
            self.assertEqual(db.materialization_hash(body), row["sha256"])
            self.assertEqual(row["sha256"], db.prompt_row(conn, "123456")["materialization_sha256"])
            conn.close()

    def test_register_dependencies_execution_analysis_and_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"schema").mkdir()
            (repo/"tools").mkdir()
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",explanation="Uno",queue_position=1)
            db.register_prompt(conn,prompt_id="654321",slug="two",title="Two",current_path="prompts/two.md",explanation="Due",queue_position=2)
            db.add_dependency(conn,"654321","123456")
            conn.commit()
            self.assertEqual("123456",db.next_runnable(conn)["prompt_id"])
            db.record_execution(conn,"123456",cycle_key="c1",started_at="2026-09-18T10:00:00Z",ended_at="2026-09-18T10:01:00Z",outcome="PASS",source="test")
            db.record_analysis(conn,"123456",bottlenecks_found=True,summary="x",fix_prompt_id=None)
            conn.commit()
            self.assertEqual("654321",db.next_runnable(conn)["prompt_id"])
            conn.close()
            (repo/"prompts").mkdir()
            (repo/"prompts/one.md").write_text("x",encoding="utf-8")
            (repo/"prompts/two.md").write_text("x",encoding="utf-8")
            conn=db.connect(repo)
            db.refresh_materialization_hashes(conn,repo)
            conn.commit(); conn.close()
            db.render(repo)
            self.assertIn("prompts/two", (repo/"roadmap.md").read_text())
            self.assertIn("123456", (repo/"prompt-registry.md").read_text())
            self.assertTrue((repo/"obsidian/Prompts/123456 one.md").is_file())
            spieg=(repo/"spiegazioni.md").read_text(encoding="utf-8")
            self.assertNotIn("[[obsidian/Prompts/123456 one\\|123456]]",spieg)
            self.assertTrue(db.verify(repo)["ok"])

    def test_summary_rows_prioritizes_running_over_pending_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="pending",title="Pending",current_path="prompts/pending.md",queue_position=1)
            db.register_prompt(conn,prompt_id="654321",slug="running",title="Running",current_path="prompts/running.md",queue_position=99)
            db.set_status(conn,"654321","running",actor="codex",note="launch")
            conn.commit()
            rows=db.summary_rows(conn)
            self.assertEqual(["654321","123456"], [row["prompt_id"] for row in rows[:2]])
            conn.close()

    def test_terminal_request_finalizes_immediately_and_usage_stays_passive(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"prompts").mkdir()
            (repo/"prompts/one.md").write_text("PROMPT_ID=123456",encoding="utf-8")
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            db.refresh_materialization_hashes(conn,repo)
            db.set_status(conn,"123456","running",actor="codex",note="launch")
            db.record_terminal(conn,"123456","PASS",source="roadmap_result")
            conn.commit()
            self.assertEqual("completed",db.prompt_row(conn,"123456")["status"])
            self.assertEqual(1,conn.execute("select count(*) from terminal_requests").fetchone()[0])
            conn.close()

            db.reconcile_prompt_file_locations(repo)
            db.render(repo)
            spieg=(repo/"spiegazioni.md").read_text(encoding="utf-8")
            self.assertNotIn("| 123456 | running |",spieg)
            self.assertTrue((repo/"completed/one.md").is_file())

            conn=db.connect(repo)
            db.record_execution(
                conn,"123456",cycle_key="real-cycle",started_at="2026-09-18T10:00:00Z",
                ended_at="2026-09-18T10:01:00Z",outcome="PASS",source="codex-usage",
                allow_running_terminal=True,
            )
            conn.commit()
            self.assertEqual("completed",db.prompt_row(conn,"123456")["status"])
            self.assertEqual(1,conn.execute("select count(*) from terminal_requests").fetchone()[0])
            self.assertEqual(1,conn.execute("select count(*) from executions").fetchone()[0])
            conn.close()

    def test_analysis_code_changes_attach_to_latest_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"prompts").mkdir()
            (repo/"prompts/one.md").write_text("PROMPT_ID=123456",encoding="utf-8")
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            db.refresh_materialization_hashes(conn,repo)
            db.record_analysis(conn,"123456",bottlenecks_found=True,summary="Found one")
            change_id=db.record_code_change(
                conn,"123456",repository="gernalix/example",change_type="fix",
                commit_sha="abc123",summary="Fixed the bottleneck"
            )
            conn.commit()
            self.assertGreater(change_id,0)
            row=conn.execute("select * from v_prompt_summary where prompt_id='123456'").fetchone()
            self.assertEqual(1,row["chatgpt_code_changed"])
            self.assertEqual(1,row["chatgpt_code_change_count"])
            conn.close()
            db.render(repo)
            note=(repo/"obsidian/Prompts/123456 one.md").read_text(encoding="utf-8")
            self.assertIn("gernalix/example",note)
            self.assertIn("abc123",note)

    def test_prompt_text_mutation_updates_canonical_materialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            original="PROMPT_ID=123456\nOriginal\n"
            updated="PROMPT_ID=123456\nUpdated\n"
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                model="GPT-5.6 Terra",
                reasoning="medium",
                queue_position=1,
                prompt_text=original,
            )
            db.apply_mutation(
                conn,
                {
                    "op":"prompt_text",
                    "prompt_id":"123456",
                    "prompt_text":updated,
                    "note":"expand scope",
                },
            )
            conn.commit()
            row=db.prompt_row(conn,"123456")
            self.assertEqual(updated,db.canonical_prompt_text(conn,"123456"))
            self.assertEqual(db.materialization_hash(updated),row["materialization_sha256"])
            self.assertEqual("GPT-5.6 Terra",row["model"])
            self.assertEqual("medium",row["reasoning"])
            self.assertEqual(1,row["queue_position"])
            self.assertEqual("pending",row["status"])
            self.assertEqual(
                1,
                conn.execute("select count(*) from audit_events where event_type='prompt_text_updated'").fetchone()[0],
            )
            conn.close()
            (repo/"prompts").mkdir(exist_ok=True)
            (repo/"prompts/one.md").write_text(original,encoding="utf-8")
            db.render(repo)
            self.assertEqual(updated,(repo/"prompts/one.md").read_text(encoding="utf-8"))

    def test_model_mutation_updates_only_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                model="GPT-5.5",
                reasoning="medium",
                queue_position=1,
            )
            db.apply_mutation(
                conn,
                {"op":"model","prompt_id":"123456","model":"GPT-5.6 Terra","note":"model-only update"},
            )
            conn.commit()
            row=db.prompt_row(conn,"123456")
            self.assertEqual("GPT-5.6 Terra",row["model"])
            self.assertEqual("medium",row["reasoning"])
            self.assertEqual(1,row["queue_position"])
            self.assertEqual("pending",row["status"])
            self.assertEqual(
                1,
                conn.execute("select count(*) from audit_events where event_type='prompt_model_updated'").fetchone()[0],
            )
            conn.close()

    def test_reasoning_mutation_updates_only_reasoning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                model="GPT-6 Luna",
                reasoning="medium",
                queue_position=1,
            )
            db.apply_mutation(
                conn,
                {"op":"reasoning","prompt_id":"123456","reasoning":"low","note":"reasoning-only update"},
            )
            conn.commit()
            row=db.prompt_row(conn,"123456")
            self.assertEqual("GPT-6 Luna",row["model"])
            self.assertEqual("low",row["reasoning"])
            self.assertEqual(1,row["queue_position"])
            self.assertEqual("pending",row["status"])
            self.assertEqual(
                1,
                conn.execute("select count(*) from audit_events where event_type='prompt_reasoning_updated'").fetchone()[0],
            )
            conn.close()

    def test_prompt_materialization_rejects_execution_metadata_in_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            for body in (
                "PROMPT_ID=123456\nMODEL=GPT-6 Luna\n# Goal\nTest\n",
                "PROMPT_ID=123456 | model=GPT-6 Luna | reasoning=low\n# Goal\nTest\n",
            ):
                with self.assertRaisesRegex(
                    db.RoadmapDBError,
                    "prompt_text_contains_execution_metadata:123456",
                ):
                    db.register_prompt(
                        conn,
                        prompt_id="123456",
                        slug="one",
                        title="One",
                        current_path="prompts/one.md",
                        prompt_text=body,
                    )
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                model="GPT-6 Luna",
                reasoning="low",
                prompt_text="PROMPT_ID=123456\n# Goal\nTest\n",
            )
            self.assertEqual("GPT-6 Luna", db.prompt_row(conn,"123456")["model"])
            self.assertEqual("low", db.prompt_row(conn,"123456")["reasoning"])
            conn.close()

    def test_explanation_mutation_updates_only_explanation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                explanation="Old",
                model="GPT-5.6 Luna",
                reasoning="low",
                queue_position=1,
            )
            db.apply_mutation(
                conn,
                {"op":"explanation","prompt_id":"123456","explanation":"New simple explanation","note":"clarify"},
            )
            conn.commit()
            row=db.prompt_row(conn,"123456")
            self.assertEqual("New simple explanation",row["explanation"])
            self.assertEqual("GPT-5.6 Luna",row["model"])
            self.assertEqual("low",row["reasoning"])
            self.assertEqual(1,row["queue_position"])
            self.assertEqual(
                1,
                conn.execute("select count(*) from audit_events where event_type='prompt_explanation_updated'").fetchone()[0],
            )
            conn.close()

    def test_spiegazioni_marks_dependency_and_manual_prerequisite_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"prompts").mkdir()
            for prompt_id, slug in (("123456","one"),("654321","two"),("777777","three")):
                (repo/f"prompts/{slug}.md").write_text(f"PROMPT_ID={prompt_id}",encoding="utf-8")
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",queue_position=1)
            db.register_prompt(conn,prompt_id="654321",slug="two",title="Two",current_path="prompts/two.md",queue_position=2)
            db.register_prompt(conn,prompt_id="777777",slug="three",title="Three",current_path="prompts/three.md",queue_position=3)
            db.add_dependency(conn,"654321","123456")
            db.add_tag(conn,"777777","manual-prerequisite:kuma-login")
            db.refresh_materialization_hashes(conn,repo)
            conn.commit()
            runnable=[
                row["prompt_id"]
                for row in conn.execute(
                    "SELECT prompt_id FROM v_runnable_prompts ORDER BY queue_position"
                )
            ]
            self.assertEqual(["123456"],runnable)
            conn.close()
            db.render(repo)
            spieg=(repo/"spiegazioni.md").read_text(encoding="utf-8")
            self.assertIn("| Eseguibile ora? |",spieg)
            self.assertIn("✅ Sì",spieg)
            self.assertIn("⏳ No — prima: 123456",spieg)
            self.assertIn("⛔ No — prima: rifai il login a Kuma",spieg)

    def test_untag_removes_manual_prerequisite_and_makes_prompt_runnable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="123456",
                slug="one",
                title="One",
                current_path="prompts/one.md",
                queue_position=1,
            )
            db.add_tag(conn,"123456","manual-prerequisite:open-codex-desktop")
            conn.commit()
            self.assertEqual(
                [],
                [row["prompt_id"] for row in conn.execute("SELECT prompt_id FROM v_runnable_prompts")],
            )
            db.remove_tag(
                conn,
                "123456",
                "manual-prerequisite:open-codex-desktop",
                actor="chatgpt",
                note="prerequisite satisfied",
            )
            conn.commit()
            self.assertEqual(
                ["123456"],
                [row["prompt_id"] for row in conn.execute("SELECT prompt_id FROM v_runnable_prompts")],
            )
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE prompt_id='123456' AND event_type='prompt_tag_removed'"
                ).fetchone()[0],
            )
            conn.close()

    def test_attention_contains_only_unresolved_exceptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="111111",slug="done",title="Done",current_path="prompts/done.md",status="completed")
            db.register_prompt(conn,prompt_id="222222",slug="blocked",title="Blocked",current_path="prompts/blocked.md",status="blocked")
            db.register_prompt(conn,prompt_id="333333",slug="fix",title="Fix",current_path="prompts/fix.md",status="completed")
            db.register_prompt(conn,prompt_id="444444",slug="unresolved",title="Unresolved",current_path="prompts/unresolved.md",status="blocked")
            db.ensure_historical_stub(conn,"555555",title="Historical",status="unknown")
            db.add_relation(conn,"222222","333333","fix",actor="chatgpt")
            conn.commit()
            attention=[
                row["prompt_id"]
                for row in conn.execute("SELECT prompt_id FROM v_attention ORDER BY prompt_id")
            ]
            self.assertEqual(["444444"],attention)
            conn.close()

    def test_pbf_dispositions_are_recursive_cycle_safe_and_preserve_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)

            def add(prompt_id, status="pending", path=None):
                db.register_prompt(
                    conn,
                    prompt_id=prompt_id,
                    slug=f"p-{prompt_id}",
                    title=f"P {prompt_id}",
                    current_path=path or f"prompts/{prompt_id}.md",
                    project_name="Example",
                    repo="gernalix/example",
                    status=status,
                )

            # A real leaf PBF remains actionable.
            add("100001", status="blocked")

            # Explicit successors in every live phase make the parent covered.
            add("100002", status="blocked"); add("200002", status="pending")
            db.add_relation(conn,"100002","200002","fix",actor="chatgpt")
            add("100003", status="blocked"); add("200003", status="pending")
            db.set_status(conn,"200003","running",actor="codex",note="launch")
            db.add_relation(conn,"100003","200003","followup",actor="chatgpt")
            add("100004", status="blocked"); add("200004", status="completed")
            db.add_relation(conn,"100004","200004","fix",actor="chatgpt")

            # Multi-hop paths are followed without requiring the intermediate
            # failure itself to become active.
            add("100005", status="blocked"); add("200005", status="blocked"); add("300005", status="pending")
            db.add_relation(conn,"100005","200005","fix",actor="chatgpt")
            db.add_relation(conn,"200005","300005","followup",actor="chatgpt")

            # resolved_by to a completed successor is stronger than covered.
            add("100006", status="blocked"); add("200006", status="completed")
            db.add_relation(conn,"100006","200006","resolved_by",actor="chatgpt")

            # A completed prompt with a historical non-PASS execution is a
            # resolved PBF; the historical execution outcome remains unchanged.
            add("100007", status="completed")
            db.record_execution(
                conn,
                "100007",
                cycle_key="historical-blocked-100007",
                outcome="BLOCKED",
                source="codex-usage",
            )

            # A cycle with no active/completed successor must terminate safely
            # and remain actionable rather than disappearing.
            add("100008", status="blocked"); add("200008", status="blocked")
            db.add_relation(conn,"100008","200008","followup",actor="chatgpt")
            db.add_relation(conn,"200008","100008","followup",actor="chatgpt")

            # Intentional terminal states are waived only with evidence.
            add("100009")
            db.set_status(conn,"100009","cancelled",actor="chatgpt",note="user intentionally closed")
            add("100010", status="cancelled")
            add("100011"); add("200011", status="blocked")
            db.add_relation(conn,"100011","200011","replacement",actor="chatgpt",note="intentional replacement")

            # Historical stubs do not create invented repair work.
            db.ensure_historical_stub(conn,"100012",title="Historical",status="unknown")

            conn.commit()
            dispositions={
                row["prompt_id"]: row["pbf_disposition"]
                for row in conn.execute(
                    "SELECT prompt_id,pbf_disposition FROM v_pbf_dispositions"
                )
            }
            self.assertEqual("needs_fix",dispositions["100001"])
            self.assertEqual("covered",dispositions["100002"])
            self.assertEqual("covered",dispositions["100003"])
            self.assertEqual("covered",dispositions["100004"])
            self.assertEqual("covered",dispositions["100005"])
            self.assertEqual("resolved",dispositions["100006"])
            self.assertEqual("resolved",dispositions["100007"])
            self.assertEqual("needs_fix",dispositions["100008"])
            self.assertEqual("needs_fix",dispositions["200008"])
            self.assertEqual("waived",dispositions["100009"])
            self.assertEqual("needs_fix",dispositions["100010"])
            self.assertEqual("waived",dispositions["100011"])
            self.assertEqual("historical_unclassified",dispositions["100012"])

            self.assertEqual(
                "BLOCKED",
                conn.execute(
                    "SELECT outcome FROM executions WHERE cycle_key='historical-blocked-100007'"
                ).fetchone()[0],
            )
            attention={
                row["prompt_id"]
                for row in conn.execute("SELECT prompt_id FROM v_attention")
            }
            self.assertIn("100001",attention)
            self.assertIn("100008",attention)
            self.assertIn("200008",attention)
            self.assertIn("100010",attention)
            self.assertNotIn("100002",attention)
            self.assertNotIn("100006",attention)
            self.assertNotIn("100012",attention)
            conn.close()

    def test_running_prompt_is_immutable_to_roadmap_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(
                conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",
                explanation="original",model="GPT-5.6 Terra",queue_position=1
            )
            db.register_prompt(conn,prompt_id="654321",slug="two",title="Two",current_path="prompts/two.md")
            db.set_status(conn,"123456","running",actor="codex",note="launch")
            actions=[
                lambda: db.set_status(conn,"123456","superseded",actor="chatgpt"),
                lambda: db.set_model(conn,"123456","GPT-5.6 Sol"),
                lambda: db.set_reasoning(conn,"123456","low"),
                lambda: db.set_prompt_text(conn,"123456","changed"),
                lambda: db.reorder_prompt(conn,"123456",9),
                lambda: db.add_dependency(conn,"123456","654321"),
                lambda: db.add_relation(conn,"123456","654321","replacement",actor="chatgpt"),
                lambda: db.add_tag(conn,"123456","x"),
                lambda: db.remove_tag(conn,"123456","x",actor="chatgpt"),
                lambda: db.record_analysis(conn,"123456",summary="x"),
            ]
            for action in actions:
                with self.assertRaisesRegex(db.RoadmapDBError,"running_prompt_locked"):
                    action()
            db.set_explanation(
                conn,
                "123456",
                "Simple explanation for the dashboard",
                actor="chatgpt",
                note="presentation-only",
            )
            row=db.prompt_row(conn,"123456")
            self.assertEqual("running",row["status"])
            self.assertEqual("Simple explanation for the dashboard",row["explanation"])
            self.assertEqual("GPT-5.6 Terra",row["model"])
            self.assertEqual(1,row["queue_position"])
            self.assertEqual(
                1,
                conn.execute(
                    "select count(*) from audit_events where event_type='prompt_explanation_updated'"
                ).fetchone()[0],
            )
            conn.close()

    def test_fix_relation_auto_forwards_pending_children(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="parent",title="Parent",current_path="prompts/parent.md",status="blocked")
            db.register_prompt(conn,prompt_id="234567",slug="fix",title="Fix",current_path="prompts/fix.md")
            db.register_prompt(conn,prompt_id="345678",slug="child",title="Child",current_path="prompts/child.md")
            db.add_dependency(conn,"345678","123456")

            db.add_relation(conn,"123456","234567","fix",actor="chatgpt")

            deps=[
                row[0]
                for row in conn.execute(
                    "SELECT depends_on_prompt_id FROM dependencies WHERE prompt_id='345678' ORDER BY 1"
                )
            ]
            self.assertEqual(["234567"],deps)
            # Explicit legacy dependency_replace after auto-forwarding is idempotent.
            db.replace_dependency(conn,"345678","123456","234567")
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE prompt_id='345678' AND event_type='dependency_auto_forwarded'"
                ).fetchone()[0],
            )
            conn.close()

    def test_replacement_relation_auto_supersedes_pending_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="old",title="Old",current_path="prompts/old.md")
            db.register_prompt(conn,prompt_id="234567",slug="new",title="New",current_path="prompts/new.md")
            db.add_relation(conn,"123456","234567","replacement",actor="chatgpt")
            self.assertEqual("superseded",db.prompt_row(conn,"123456")["status"])
            conn.close()

    def test_pending_prompt_cannot_start_until_dependencies_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="parent",title="Parent",current_path="prompts/parent.md")
            db.register_prompt(conn,prompt_id="654321",slug="child",title="Child",current_path="prompts/child.md")
            db.add_dependency(conn,"654321","123456")
            with self.assertRaisesRegex(
                db.RoadmapDBError,
                "prompt_dependencies_incomplete:654321:123456",
            ):
                db.set_status(conn,"654321","running",actor="codex",note="launch")
            self.assertEqual("pending",db.prompt_row(conn,"654321")["status"])
            db.set_status(conn,"123456","completed",actor="test")
            db.set_status(conn,"654321","running",actor="codex",note="launch")
            self.assertEqual("running",db.prompt_row(conn,"654321")["status"])
            conn.close()

    def test_superseded_prompt_cannot_be_reactivated(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            db.set_status(conn,"123456","superseded",actor="chatgpt")
            with self.assertRaisesRegex(db.RoadmapDBError,"terminal_prompt_cannot_reactivate"):
                db.set_status(conn,"123456","running",actor="codex",note="late launch")
            self.assertEqual("superseded",db.prompt_row(conn,"123456")["status"])
            conn.close()

    def test_reorder_prompt_updates_queue_without_changing_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",queue_position=2)
            db.register_prompt(conn,prompt_id="654321",slug="two",title="Two",current_path="prompts/two.md",queue_position=1)
            db.reorder_prompt(conn,"123456",1,actor="chatgpt",note="optimize queue")
            db.reorder_prompt(conn,"654321",2,actor="chatgpt")
            conn.commit()
            self.assertEqual(1,db.prompt_row(conn,"123456")["queue_position"])
            self.assertEqual("123456",db.next_runnable(conn)["prompt_id"])
            self.assertEqual(2,conn.execute("select count(*) from audit_events where event_type='prompt_reordered'").fetchone()[0])
            with self.assertRaises(db.RoadmapDBError):
                db.reorder_prompt(conn,"123456",0)
            conn.close()
    def test_render_escapes_wikilink_alias_pipes_in_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"prompts").mkdir()
            (repo/"prompts/one.md").write_text("PROMPT_ID=123456",encoding="utf-8")
            (repo/"prompts/two.md").write_text("PROMPT_ID=654321",encoding="utf-8")
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",queue_position=1)
            db.register_prompt(conn,prompt_id="654321",slug="two",title="Two",current_path="prompts/two.md",queue_position=2)
            db.add_dependency(conn,"654321","123456")
            db.refresh_materialization_hashes(conn,repo)
            conn.commit(); conn.close()
            db.render(repo)
            spieg=(repo/"spiegazioni.md").read_text(encoding="utf-8")
            registry=(repo/"prompt-registry.md").read_text(encoding="utf-8")
            self.assertIn("[[prompts/one\\|One]]",spieg)
            self.assertIn("[[obsidian/Prompts/123456 one\\|123456]]",spieg)
            self.assertIn("[[obsidian/Prompts/123456 one\\|123456 · One]]",registry)
            self.assertNotIn("[[prompts/one|One]]",spieg)
    def test_prompt_id_is_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            with self.assertRaises(db.RoadmapDBError):
                db.register_prompt(conn,prompt_id="123456",slug="two",title="Two",current_path="prompts/two.md")
            conn.close()

if __name__=="__main__": unittest.main()
