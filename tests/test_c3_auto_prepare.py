import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c3_auto_prepare


class AutoPreparationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE projects(project_id TEXT PRIMARY KEY,slug TEXT,name TEXT,status TEXT,archived INTEGER,created_source TEXT,notes TEXT);
          CREATE TABLE repositories(repository_id TEXT,project_id TEXT,location TEXT,kind TEXT,branch TEXT,head TEXT,status TEXT,canonical INTEGER,repository_kind TEXT,host_id TEXT,worktree_path TEXT,remote_url TEXT,runtime_path TEXT);
          CREATE TABLE work_items(work_item_id TEXT PRIMARY KEY,title TEXT,objective TEXT,acceptance_json TEXT,current_action TEXT,next_action TEXT,repo TEXT,project_id TEXT,project_name TEXT,prompt_id TEXT,executor_policy TEXT,sort_order INTEGER,created_at TEXT,status TEXT);
          CREATE VIEW v_work_item_runnable AS SELECT * FROM work_items WHERE status='pending';
          CREATE TABLE work_item_execution_specs(work_item_id TEXT PRIMARY KEY,activity TEXT);
          CREATE TABLE executions(prompt_id TEXT,outcome TEXT,model TEXT,reasoning TEXT);
        """)
        self.db.execute("INSERT INTO projects VALUES('51','roadmap','codex-roadmap','active',0,'test','')")
        self.db.execute("INSERT INTO repositories VALUES('R0051','51','','','','','',1,'','','','https://github.com/gernalix/codex-roadmap','')")
        self.db.execute("INSERT INTO work_items VALUES('old','old','old','[]',NULL,NULL,'gernalix/codex-roadmap','51','codex-roadmap','old','codex',0,'1','completed')")
        self.db.execute("INSERT INTO work_item_execution_specs VALUES('old','coding')")
        self.db.execute("INSERT INTO executions VALUES('old','PASS','gpt-5.6-sol','medium')")

    def tearDown(self):
        self.db.close()

    def add(self, wid, repo='gernalix/codex-roadmap', objective='Do the scoped change.', acceptance='["Verify the scoped result."]'):
        self.db.execute("INSERT INTO work_items VALUES(?,?,?, ?,NULL,NULL,?,NULL,NULL,NULL,'auto',1,'2','pending')", (wid,wid,objective,acceptance,repo))

    def test_prepares_only_uniquely_proven_canonical_candidate(self):
        self.add('ready')
        self.add('ambiguous', repo='not-a-canonical-repository')
        plan = c3_auto_prepare.plan(self.db)
        self.assertEqual(2, plan['dependency_ready'])
        candidate = plan['prepared_candidates'][0]
        self.assertEqual('ready', candidate['item']['work_item_id'])
        self.assertEqual({'activity':'coding','model':'gpt-5.6-sol','reasoning':'medium'}, candidate['profile'])
        self.assertEqual('canonical_repository_identity_missing', plan['waiting'][0]['reason'])

    def test_prompt_preserves_canonical_text_without_invented_acceptance(self):
        self.add('ready', objective='Keep this exact objective.')
        candidate = c3_auto_prepare.plan(self.db)['prepared_candidates'][0]
        body = c3_auto_prepare.prompt_body(candidate['item'])
        self.assertIn('Keep this exact objective.', body)
        self.assertIn('Acceptance criteria', body)

    def test_missing_acceptance_fails_closed_before_identity_or_profile(self):
        self.add('incomplete', acceptance='[]')
        plan = c3_auto_prepare.plan(self.db)
        self.assertEqual([], plan['prepared_candidates'])
        self.assertEqual('acceptance_missing', plan['waiting'][0]['reason'])

    def test_existing_spec_is_not_candidate(self):
        self.add('ready')
        self.db.execute("INSERT INTO work_item_execution_specs VALUES('ready','coding')")
        self.assertEqual([], c3_auto_prepare.plan(self.db)['prepared_candidates'])


if __name__ == '__main__':
    unittest.main()
