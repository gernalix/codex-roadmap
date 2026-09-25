from contextlib import closing
from pathlib import Path
import sqlite3
import json
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_cutover_writer
import apply_issue_mutation
import roadmap_db
from test_c2_identity import C2IdentityTests


class CutoverWriterTests(unittest.TestCase):
    def test_full_cutover_preserves_running_and_replays_without_reimport(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            db=roadmap_db.connect(root)
            for prompt_id in ('175908','707603'):
                roadmap_db.register_prompt(db,prompt_id=prompt_id,slug='p'+prompt_id,
                    title='Running '+prompt_id,current_path='prompts/'+prompt_id+'.md',
                    project_id='51')
                roadmap_db.set_status(db,prompt_id,'running',actor='fixture')
            db.commit();db.close()
            (root/'operations/task-state').mkdir(parents=True)
            vault=C2IdentityTests().make_megavault(root)
            payload=c2_cutover_writer.build_snapshot(vault)
            payload['expected_db_sha256']=c2_cutover_writer._sha256(root/'roadmap.sqlite')
            event=root/'event.json'
            event.write_text(json.dumps({'issue':{'number':77,
                'title':'[roadmap-mutation] c2-cutover-fixture',
                'body':json.dumps({'schema':'codex-roadmap.mutation.v1',
                    'actor':'test','operations':[{'op':'c2_cutover','arguments':payload}]})}}))
            first=apply_issue_mutation.apply_issue(root,event)
            self.assertEqual(1,first['operations'])
            second=apply_issue_mutation.apply_issue(root,event)
            self.assertTrue(second['idempotent'])
            with closing(sqlite3.connect(root/'roadmap.sqlite')) as conn:
                self.assertEqual('ok',conn.execute('PRAGMA integrity_check').fetchone()[0])
                self.assertEqual([],conn.execute('PRAGMA foreign_key_check').fetchall())
                self.assertEqual([('175908','running'),('707603','running')],
                    conn.execute("SELECT prompt_id,status FROM prompts WHERE status='running' ORDER BY prompt_id").fetchall())
