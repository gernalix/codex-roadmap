import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
          CREATE TABLE work_item_dependencies(work_item_id TEXT,depends_on_work_item_id TEXT,required INTEGER);
          CREATE VIEW v_work_item_runnable AS SELECT w.* FROM work_items w WHERE w.status='pending' AND NOT EXISTS (
            SELECT 1 FROM work_item_dependencies d JOIN work_items dep ON dep.work_item_id=d.depends_on_work_item_id
            WHERE d.work_item_id=w.work_item_id AND d.required=1 AND dep.status NOT IN ('completed','waived','cancelled','superseded')
          );
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

    def test_missing_title_fails_closed(self):
        self.add('incomplete')
        self.db.execute("UPDATE work_items SET title='' WHERE work_item_id='incomplete'")
        plan = c3_auto_prepare.plan(self.db)
        self.assertEqual([], plan['prepared_candidates'])
        self.assertEqual('title_missing', plan['waiting'][0]['reason'])

    def test_existing_spec_is_not_candidate(self):
        self.add('ready')
        self.db.execute("INSERT INTO work_item_execution_specs VALUES('ready','coding')")
        self.assertEqual([], c3_auto_prepare.plan(self.db)['prepared_candidates'])

    def test_ambiguous_execution_profile_fails_closed(self):
        self.add('ready')
        self.db.execute("INSERT INTO work_items VALUES('old2','old2','old2','[]',NULL,NULL,'gernalix/codex-roadmap','51','codex-roadmap','old2','codex',0,'1','completed')")
        self.db.execute("INSERT INTO work_item_execution_specs VALUES('old2','diagnostic')")
        self.db.execute("INSERT INTO executions VALUES('old2','PASS','gpt-5.6-sol','medium')")
        plan = c3_auto_prepare.plan(self.db)
        self.assertEqual([], plan['prepared_candidates'])
        self.assertEqual('unique_proven_execution_profile_missing', plan['waiting'][0]['reason'])

    def test_unsatisfied_dependency_is_not_dependency_ready(self):
        self.add('blocked')
        self.add('dependency')
        self.db.execute("UPDATE work_items SET status='blocked' WHERE work_item_id='dependency'")
        self.db.execute("INSERT INTO work_item_dependencies VALUES('blocked','dependency',1)")
        plan = c3_auto_prepare.plan(self.db)
        self.assertEqual(0, plan['dependency_ready'])
        self.assertEqual([], plan['prepared_candidates'])

    def test_apply_uses_prepare_once_and_replay_creates_no_second_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.add('ready')
            path = Path(tmp) / 'state.sqlite'
            self.db.commit()
            disk = sqlite3.connect(path)
            self.db.backup(disk); disk.close()
            calls=[]
            def fake_prepare(spec):
                calls.append(spec)
                with sqlite3.connect(path) as writable:
                    writable.execute("INSERT INTO work_item_execution_specs VALUES(?,?)", (spec['work_item_id'], spec['activity']))
                return {'status':'prepared','work_item_id':spec['work_item_id'],'dispatched':False}
            with patch.object(c3_auto_prepare.c2_prepare_codex, 'prepare', side_effect=fake_prepare):
                first=c3_auto_prepare.apply(path, 1)
                second=c3_auto_prepare.apply(path, 1)
            self.assertEqual(1, len(calls))
            self.assertEqual('prepared', first['results'][0]['status'])
            self.assertEqual([], second['results'])

    def test_dry_run_has_no_prepare_side_effect(self):
        self.add('ready')
        with patch.object(c3_auto_prepare.c2_prepare_codex, 'prepare') as prepare:
            result=c3_auto_prepare.plan(self.db, 1)
        self.assertEqual('ready', result['prepared_candidates'][0]['item']['work_item_id'])
        prepare.assert_not_called()

    def test_planning_preserves_priority_and_tags_outside_preparation(self):
        self.add('ready')
        self.db.execute("ALTER TABLE work_items ADD COLUMN priority TEXT")
        self.db.execute("ALTER TABLE work_items ADD COLUMN tags_json TEXT")
        self.db.execute("UPDATE work_items SET priority='P0',tags_json='[\\\"critical\\\"]' WHERE work_item_id='ready'")
        before=self.db.execute("SELECT priority,tags_json FROM work_items WHERE work_item_id='ready'").fetchone()
        c3_auto_prepare.plan(self.db)
        after=self.db.execute("SELECT priority,tags_json FROM work_items WHERE work_item_id='ready'").fetchone()
        self.assertEqual(tuple(before),tuple(after))


if __name__ == '__main__':
    unittest.main()
