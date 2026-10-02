import sqlite3
import tempfile
import unittest
from pathlib import Path

from roadmap_db import connect
from c3_projects import synchronize, validate_references
from c3_local_writer import LocalWriter
from work_items_migration import migrate_database
from work_items_cutover import cutover_database


class ProjectAuthorityTests(unittest.TestCase):
    def fixture(self, root):
        source_dir = root / 'megavault'
        source_dir.mkdir()
        connect(source_dir).close()
        migrate_database(source_dir / 'roadmap.sqlite')
        cutover_database(source_dir / 'roadmap.sqlite')
        source = connect(source_dir)
        for pid, slug in ((104, 'favorites'), (105, 'supervisor')):
            source.execute('INSERT INTO projects VALUES(?,?,?,\'active\',0,\'test\',NULL)', (pid, slug, slug))
        source.execute("INSERT INTO project_aliases VALUES('rdc',105)")
        source.commit()
        source.close()
        target_dir = root / 'c3'
        target_dir.mkdir()
        connect(target_dir).close()
        migrate_database(target_dir / 'roadmap.sqlite')
        cutover_database(target_dir / 'roadmap.sqlite')
        conn = connect(target_dir)
        conn.execute("INSERT INTO projects VALUES(104,'supervisor','supervisor','active',0,'old',NULL)")
        conn.execute("INSERT INTO project_aliases VALUES('rdc',104)")
        conn.execute("INSERT INTO work_items(work_item_id,kind,title,status,project_id,created_at,updated_at) VALUES('wi:old','task','old','completed','104','2026','2026')")
        conn.execute("INSERT INTO prompt_id_registry(prompt_id,project_id,source,status,created_at_utc) VALUES(123456,104,'old','allocated','2026')")
        conn.execute("INSERT INTO prompt_id_allocation_requests(request_id,prompt_id,project_id,source) VALUES('old-allocation',123456,104,'old')")
        conn.commit()
        conn.close()
        return target_dir, source_dir / 'roadmap.sqlite'

    def test_historical_references_remap_by_slug_and_alias_cache_refreshes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = self.fixture(Path(tmp))
            conn = connect(repo)
            conn.execute('BEGIN IMMEDIATE')
            self.assertEqual({104: 105}, synchronize(conn, source)['remapped_ids'])
            validate_references(conn)
            conn.commit()
            self.assertEqual('105', conn.execute('SELECT project_id FROM work_items').fetchone()[0])
            self.assertEqual(105, conn.execute('SELECT project_id FROM prompt_id_registry').fetchone()[0])
            self.assertEqual(105, conn.execute('SELECT project_id FROM prompt_id_allocation_requests').fetchone()[0])
            self.assertEqual('favorites', conn.execute('SELECT slug FROM projects WHERE project_id=104').fetchone()[0])
            conn.execute('BEGIN IMMEDIATE')
            self.assertFalse(synchronize(conn, source)['changed'])
            conn.rollback()
            with sqlite3.connect(source) as mv:
                mv.execute("INSERT INTO project_aliases VALUES('new-alias',104)")
            conn.execute('BEGIN IMMEDIATE')
            self.assertTrue(synchronize(conn, source)['changed'])
            self.assertEqual(104, conn.execute("SELECT project_id FROM project_aliases WHERE alias='new-alias'").fetchone()[0])
            conn.rollback()
            conn.close()

    def test_writer_rejects_local_identity_writes_and_invalid_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = self.fixture(Path(tmp))
            writer = LocalWriter(repo, projects_source=source)
            try:
                document = {'schema': 'codex-roadmap.mutation.v1', 'operations': [{
                    'op': 'register', 'prompt_id': '654321', 'slug': 'new', 'title': 'new',
                    'current_path': 'prompts/new.md', 'prompt_text': 'new', 'project_id': '999'}]}
                with self.assertRaisesRegex(ValueError, 'noncanonical_project_reference'):
                    writer.apply(document, 'invalid-project')
                self.assertIsNone(writer.conn.execute("SELECT 1 FROM mutation_receipts WHERE request_key='invalid-project'").fetchone())
                with self.assertRaises(sqlite3.DatabaseError):
                    writer.conn.execute("INSERT INTO projects VALUES(999,'illegal','illegal','active',0,'local',NULL)")
                self.assertEqual(104, writer.conn.execute("SELECT project_id FROM projects WHERE slug='supervisor'").fetchone()[0])
            finally:
                writer.close()

    def test_missing_source_rolls_back_without_guessing_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = self.fixture(Path(tmp))
            with sqlite3.connect(source) as mv:
                mv.execute("DELETE FROM project_aliases WHERE project_id=105")
                mv.execute('DELETE FROM projects WHERE project_id=105')
            conn = connect(repo)
            conn.execute('BEGIN IMMEDIATE')
            with self.assertRaisesRegex(ValueError, 'project_identity_missing_in_megavault'):
                synchronize(conn, source)
            conn.rollback()
            self.assertEqual(104, conn.execute('SELECT project_id FROM projects').fetchone()[0])
            conn.close()
