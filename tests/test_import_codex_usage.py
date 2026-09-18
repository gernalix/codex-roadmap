from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_db as db
import import_codex_usage as importer

class ImportTests(unittest.TestCase):
    def test_import_is_idempotent_and_updates_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); repo=base/"repo"; src=base/"usage"; repo.mkdir()
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            conn.commit(); conn.close()
            p=src/"prompts/123456"; p.mkdir(parents=True)
            (p/"metrics.json").write_text(json.dumps({
                "prompt_id":"123456","cycle_key":"abc","status":"PASS",
                "timestamp_start_utc":"2026-09-18T10:00:00Z","timestamp_end_utc":"2026-09-18T10:01:00Z",
                "duration_seconds":60,"total_tokens":100,"tool_call_count":2
            }),encoding="utf-8")
            s1=importer.import_metrics(repo,src,render_after=False)
            db_bytes=(repo/"roadmap.sqlite").read_bytes()
            s2=importer.import_metrics(repo,src,render_after=False)
            self.assertEqual(1,s1["inserted"]); self.assertEqual(1,s2["existing"])
            self.assertEqual(db_bytes,(repo/"roadmap.sqlite").read_bytes())
            conn=db.connect(repo,writable=False)
            self.assertEqual("completed",db.prompt_row(conn,"123456")["status"])
            self.assertEqual(1,conn.execute("select count(*) from executions").fetchone()[0])
            conn.close()

    def test_conflict_reimport_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); repo=base/"repo"; src=base/"usage"; repo.mkdir()
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md",prompt_text="expected")
            conn.commit(); conn.close()
            p=src/"prompts/123456"; p.mkdir(parents=True)
            (p/"metrics.json").write_text(json.dumps({
                "prompt_id":"123456","cycle_key":"abc","status":"PASS","prompt_text_redacted":"observed"
            }),encoding="utf-8")
            self.assertEqual(1,importer.import_metrics(repo,src,render_after=False)["conflicts"])
            db_bytes=(repo/"roadmap.sqlite").read_bytes()
            self.assertEqual(1,importer.import_metrics(repo,src,render_after=False)["conflicts"])
            self.assertEqual(db_bytes,(repo/"roadmap.sqlite").read_bytes())

if __name__=="__main__": unittest.main()
