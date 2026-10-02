import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from c3_local_writer import LocalWriter
from c3_prompt_ids import import_registry
from c3_projects import synchronize
from c2_identity import C2IdentityError
import c2_identity
from roadmap_db import register_prompt, add_relation
from test_c3_projects import ProjectAuthorityTests


class PromptAuthorityTests(unittest.TestCase):
    def test_canonical_cli_uses_writer_not_direct_db_or_github(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'canonical.sqlite'
            with patch('c3_storage.CANONICAL_DB', path), patch('c3_local_writer.submit_local', return_value={
                    'allocations': [{'request_id': 'cli', 'prompt_id': 333333}]}) as submit, patch('builtins.print'):
                self.assertEqual(0, c2_identity.main(['allocate', '--request-id', 'cli', '--source', 'new']))
                self.assertEqual('prompt-id-cli', submit.call_args.kwargs['request_key'])
                self.assertFalse(path.exists())

    def fixture(self, root):
        repo, source = ProjectAuthorityTests().fixture(root)
        with sqlite3.connect(repo / 'roadmap.sqlite') as target:
            target.execute("INSERT INTO prompt_id_registry(prompt_id,source,status,created_at_utc) VALUES(111111,'historical-roadmap','allocated','old')")
        with sqlite3.connect(source) as mv:
            mv.execute("INSERT INTO prompt_id_registry(prompt_id,source,status,content_sha256,created_at_utc,materialized_at_utc) VALUES(111111,'original-allocation','materialized',?,'new','new')", ('a'*64,))
            mv.execute("INSERT INTO prompt_id_registry(prompt_id,source,status,created_at_utc) VALUES(222222,'historical-git','allocated','old')")
            mv.execute("INSERT INTO prompt_id_allocation_requests(request_id,prompt_id,source) VALUES('old-mv',111111,'original-allocation')")
        writer = LocalWriter(repo)
        writer.conn.execute('BEGIN IMMEDIATE')
        synchronize(writer.conn, source)
        result = import_registry(writer.conn, source)
        writer.conn.commit()
        return writer, source, result

    def test_import_reserves_union_enriches_placeholder_and_keeps_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            writer, source, result = self.fixture(Path(tmp))
            try:
                self.assertEqual([222222], result['inserted_ids'])
                self.assertEqual(111111, result['enriched_reservations'][0]['prompt_id'])
                self.assertEqual('materialized', writer.conn.execute('SELECT status FROM prompt_id_registry WHERE prompt_id=111111').fetchone()[0])
                self.assertEqual(3, writer.conn.execute('SELECT COUNT(*) FROM prompt_id_registry').fetchone()[0])
                with self.assertRaises(sqlite3.IntegrityError):
                    writer.conn.execute('UPDATE prompt_id_registry SET source=\'changed\' WHERE prompt_id=111111')
                writer.conn.rollback()
                writer.conn.execute('BEGIN IMMEDIATE')
                self.assertEqual('already_imported', import_registry(writer.conn, source)['status'])
                writer.conn.rollback()
            finally:
                writer.close()

    def test_local_allocate_register_materialize_replay_and_no_historical_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            writer, source, _ = self.fixture(Path(tmp))
            try:
                doc = {'schema': 'codex-roadmap.mutation.v1', 'actor': 'test', 'operations': [{
                    'op': 'prompt_id_allocate', 'arguments': {'source': 'new', 'request_id': 'new', 'project_id': 105}}]}
                with patch('c2_identity.secrets.randbelow', side_effect=[111111-100000, 333333-100000]):
                    result = writer.apply(doc, 'new-allocation')
                self.assertEqual(333333, result['allocations'][0]['prompt_id'])
                self.assertEqual(result['allocations'], writer.apply(doc, 'new-allocation')['allocations'])
                registration = {'schema': 'codex-roadmap.mutation.v1', 'operations': [{
                    'op': 'register', 'prompt_id': '333333', 'slug': 'new', 'title': 'new',
                    'project_id': '105', 'current_path': 'prompts/new.md', 'prompt_text': 'new body'}]}
                writer.apply(registration, 'register')
                self.assertEqual('materialized', writer.conn.execute('SELECT status FROM prompt_id_registry WHERE prompt_id=333333').fetchone()[0])
                self.assertTrue(writer.apply(registration, 'register')['idempotent'])
                writer.apply({'schema': 'codex-roadmap.mutation.v1', 'operations': [
                    {'op': 'status', 'prompt_id': '333333', 'status': 'running'}]}, 'start')
                self.assertEqual('used', writer.conn.execute('SELECT status FROM prompt_id_registry WHERE prompt_id=333333').fetchone()[0])
                for forbidden in ('111111', '222222', '555555'):
                    bad = json.loads(json.dumps(registration)); bad['operations'][0]['prompt_id'] = forbidden
                    with self.assertRaises((ValueError, C2IdentityError)):
                        writer.apply(bad, 'illegal-' + forbidden)
                repo = writer.repo
                writer.close()
                writer = LocalWriter(repo)
                self.assertEqual(result['allocations'], writer.apply(doc, 'new-allocation')['allocations'])
            finally:
                writer.close()

    def test_split_request_reconciles_only_with_explicit_retired_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = ProjectAuthorityTests().fixture(Path(tmp))
            writer = LocalWriter(repo)
            try:
                writer.conn.execute('BEGIN IMMEDIATE')
                synchronize(writer.conn, source)
                register_prompt(writer.conn, prompt_id='123456', slug='old', title='old', current_path='falliti/old.md', status='superseded')
                register_prompt(writer.conn, prompt_id='111111', slug='new', title='new', current_path='completed/new.md', status='completed')
                writer.conn.commit()
                with sqlite3.connect(source) as mv:
                    mv.execute("INSERT INTO prompt_id_registry(prompt_id,source,status,created_at_utc) VALUES(111111,'old','allocated','2026')")
                    mv.execute("INSERT INTO prompt_id_allocation_requests(request_id,prompt_id,project_id,source) VALUES('old-allocation',111111,105,'old')")
                writer.conn.execute('BEGIN IMMEDIATE')
                with self.assertRaisesRegex(ValueError, 'prompt_allocation_request_conflict'):
                    import_registry(writer.conn, source)
                writer.conn.rollback()
                writer.conn.execute('BEGIN IMMEDIATE')
                add_relation(writer.conn, '123456', '111111', 'replacement', actor='history')
                result = import_registry(writer.conn, source)
                self.assertEqual(1, len(result['reconciled_requests']))
                self.assertEqual(111111, writer.conn.execute("SELECT prompt_id FROM prompt_id_allocation_requests WHERE request_id='old-allocation'").fetchone()[0])
                self.assertEqual(2, writer.conn.execute('SELECT COUNT(*) FROM prompt_id_registry').fetchone()[0])
                writer.conn.commit()
            finally:
                writer.close()

    def test_real_registry_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = ProjectAuthorityTests().fixture(Path(tmp))
            with sqlite3.connect(source) as mv:
                mv.execute("INSERT INTO prompt_id_registry(prompt_id,source,status,created_at_utc) VALUES(123456,'different','allocated','old')")
            writer = LocalWriter(repo)
            try:
                writer.conn.execute('BEGIN IMMEDIATE')
                with self.assertRaisesRegex(ValueError, 'prompt_registry_conflict:123456'):
                    import_registry(writer.conn, source)
                writer.conn.rollback()
                self.assertEqual('old', writer.conn.execute('SELECT source FROM prompt_id_registry').fetchone()[0])
                with self.assertRaises(sqlite3.IntegrityError):
                    writer.conn.execute("UPDATE prompt_id_registry SET source='broken'")
            finally:
                writer.close()
