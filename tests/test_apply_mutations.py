from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_db as db
import apply_mutations

class MutationTests(unittest.TestCase):
    def test_dependency_replace_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            conn=db.connect(repo)
            db.register_prompt(conn,prompt_id="111111",slug="old",title="Old",current_path="prompts/old.md")
            db.register_prompt(conn,prompt_id="222222",slug="fix",title="Fix",current_path="prompts/fix.md")
            db.register_prompt(conn,prompt_id="333333",slug="downstream",title="Downstream",current_path="prompts/downstream.md")
            db.add_dependency(conn,"333333","111111")
            conn.commit(); conn.close()
            inbox=repo/"mutations/inbox"; inbox.mkdir(parents=True)
            (inbox/"replace.json").write_text(json.dumps({
                "schema":"codex-roadmap.mutation.v1","actor":"chatgpt",
                "operations":[{
                    "op":"dependency_replace",
                    "prompt_id":"333333",
                    "old_depends_on_prompt_id":"111111",
                    "new_depends_on_prompt_id":"222222"
                }]
            }),encoding="utf-8")
            out=apply_mutations.apply_inbox(repo, test_only=True)
            self.assertEqual(1,out["operations"])
            conn=db.connect(repo,writable=False)
            deps=conn.execute(
                "select depends_on_prompt_id from dependencies where prompt_id='333333'"
            ).fetchall()
            self.assertEqual(["222222"],[row[0] for row in deps])
            self.assertEqual(
                1,
                conn.execute("select count(*) from audit_events where event_type='dependency_replaced'").fetchone()[0],
            )
            conn.close()

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
            out=apply_mutations.apply_inbox(repo, test_only=True)
            self.assertEqual(2,out["operations"])
            self.assertFalse((inbox/"a.json").exists())
            self.assertTrue((repo/"mutations/applied/a.json").exists())
            conn=db.connect(repo,writable=False)
            self.assertEqual(1,conn.execute("select count(*) from analyses").fetchone()[0])
            self.assertEqual(1,conn.execute("select count(*) from analysis_code_changes").fetchone()[0])
            conn.close()

if __name__=="__main__": unittest.main()
