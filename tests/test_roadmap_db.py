from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_db as db

class RoadmapDBTests(unittest.TestCase):
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

    def test_terminal_status_waits_for_exact_usage_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            (repo/"prompts").mkdir()
            (repo/"prompts/one.md").write_text("PROMPT_ID=123456",encoding="utf-8")
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            db.refresh_materialization_hashes(conn,repo)
            db.record_terminal(conn,"123456","PASS",source="roadmap_result")
            conn.commit()
            self.assertEqual("completed",db.prompt_row(conn,"123456")["status"])
            self.assertEqual(0,conn.execute("select count(*) from executions").fetchone()[0])
            self.assertEqual(1,conn.execute("select count(*) from audit_events where event_type='terminal_result'").fetchone()[0])
            db.record_execution(
                conn,"123456",cycle_key="real-cycle",started_at="2026-09-18T10:00:00Z",
                ended_at="2026-09-18T10:01:00Z",outcome="PASS",source="codex-usage"
            )
            conn.commit()
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
