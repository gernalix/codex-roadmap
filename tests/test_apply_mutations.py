from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_db as db
import apply_mutations

class MutationTests(unittest.TestCase):
    def test_chatgpt_analysis_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="123456",slug="one",title="One",current_path="prompts/one.md")
            conn.commit(); conn.close()
            inbox=repo/"mutations/inbox"; inbox.mkdir(parents=True)
            (inbox/"a.json").write_text(json.dumps({
                "schema":"codex-roadmap.mutation.v1","actor":"chatgpt",
                "operations":[
                    {"op":"analysis","prompt_id":"123456","bottlenecks_found":True,"summary":"Found"},
                    {"op":"code_change","prompt_id":"123456","repository":"gernalix/example","change_type":"fix","commit_sha":"abc123"}
                ]
            }),encoding="utf-8")
            out=apply_mutations.apply_inbox(repo)
            self.assertEqual(2,out["operations"])
            self.assertFalse((inbox/"a.json").exists())
            self.assertTrue((repo/"mutations/applied/a.json").exists())
            conn=db.connect(repo,writable=False)
            self.assertEqual(1,conn.execute("select count(*) from analyses").fetchone()[0])
            self.assertEqual(1,conn.execute("select count(*) from analysis_code_changes").fetchone()[0])
            conn.close()

if __name__=="__main__": unittest.main()
