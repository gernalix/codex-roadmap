from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import c2_identity
import roadmap_db as db
import work_items_migration as migration


class C2IdentityTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        repo = root / "roadmap"
        repo.mkdir()
        conn = db.connect(repo)
        db.register_prompt(
            conn,
            prompt_id="123456",
            slug="legacy",
            title="Legacy",
            current_path="prompts/legacy.md",
            project_id="51",
        )
        conn.commit()
        conn.close()
        migration.migrate_database(repo / "roadmap.sqlite")
        return repo / "roadmap.sqlite"

    def make_megavault(self, root: Path) -> Path:
        path = root / "megavault.sqlite"
        conn = sqlite3.connect(path)
        conn.executescript(
            """
            PRAGMA foreign_keys=ON;
            CREATE TABLE projects(
              project_id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL, status TEXT NOT NULL,
              archived INTEGER NOT NULL DEFAULT 0,
              created_source TEXT NOT NULL, notes TEXT
            );
            CREATE TABLE project_aliases(
              alias TEXT PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(project_id)
            );
            CREATE TABLE repositories(
              repository_id TEXT PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(project_id),
              location TEXT NOT NULL, kind TEXT NOT NULL, branch TEXT, head TEXT,
              status TEXT, canonical INTEGER NOT NULL DEFAULT 1,
              repository_kind TEXT, host_id TEXT, worktree_path TEXT,
              remote_url TEXT, runtime_path TEXT
            );
            CREATE TABLE project_components(
              component_id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL REFERENCES projects(project_id),
              component TEXT NOT NULL, type TEXT NOT NULL, path TEXT NOT NULL,
              purpose TEXT NOT NULL, UNIQUE(project_id,component)
            );
            CREATE TABLE project_operations(
              operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id INTEGER NOT NULL REFERENCES projects(project_id),
              operation TEXT NOT NULL, command TEXT NOT NULL, scope TEXT NOT NULL,
              host TEXT, workdir TEXT, risk_level TEXT NOT NULL, notes TEXT,
              UNIQUE(project_id,operation)
            );
            CREATE TABLE prompt_id_registry(
              prompt_id INTEGER PRIMARY KEY, parent_prompt_id INTEGER,
              project_id INTEGER REFERENCES projects(project_id),
              source TEXT NOT NULL, status TEXT NOT NULL,
              content_sha256 TEXT, created_at_utc TEXT NOT NULL,
              materialized_at_utc TEXT, used_at_utc TEXT, cancelled_at_utc TEXT
            );
            CREATE TABLE prompt_id_events(
              event_id INTEGER PRIMARY KEY AUTOINCREMENT,
              prompt_id INTEGER NOT NULL REFERENCES prompt_id_registry(prompt_id),
              event_type TEXT NOT NULL, event_at_utc TEXT NOT NULL, detail TEXT
            );
            """
        )
        conn.execute(
            "INSERT INTO projects VALUES(51,'roadmap','Roadmap','active',0,'test',NULL)"
        )
        conn.execute("INSERT INTO project_aliases VALUES('c2',51)")
        conn.execute(
            """INSERT INTO repositories(
                 repository_id,project_id,location,kind,branch,head,status,canonical,
                 repository_kind,host_id,worktree_path,remote_url,runtime_path
               ) VALUES('R1',51,'local','git','main','abc','active',1,
                        'local_worktree',NULL,'/tmp/repo','https://example.test/repo',NULL)"""
        )
        conn.execute(
            "INSERT INTO project_components(project_id,component,type,path,purpose) VALUES(51,'db','database','roadmap.sqlite','state')"
        )
        conn.execute(
            "INSERT INTO project_operations(project_id,operation,command,scope,risk_level) VALUES(51,'verify','python test.py','repo','low')"
        )
        conn.execute(
            """INSERT INTO prompt_id_registry(
                 prompt_id,parent_prompt_id,project_id,source,status,content_sha256,
                 created_at_utc,materialized_at_utc,used_at_utc,cancelled_at_utc
               ) VALUES(654321,NULL,51,'test','allocated',NULL,
                        '2026-01-01T00:00:00Z',NULL,NULL,NULL)"""
        )
        conn.execute(
            "INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail) VALUES(654321,'allocated','2026-01-01T00:00:00Z','test')"
        )
        conn.commit()
        conn.close()
        return path

    def test_import_is_idempotent_and_reserves_existing_roadmap_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.make_target(root)
            source = self.make_megavault(root)
            first = c2_identity.import_megavault_subset(target, source)
            second = c2_identity.import_megavault_subset(target, source)
            self.assertFalse(first["idempotent"])
            self.assertTrue(second["idempotent"])
            self.assertEqual(1, first["historical_roadmap_prompt_ids_reserved"])

            conn = sqlite3.connect(target)
            conn.row_factory = sqlite3.Row
            self.assertEqual(
                "historical-roadmap",
                conn.execute(
                    "SELECT source FROM prompt_id_registry WHERE prompt_id=123456"
                ).fetchone()[0],
            )
            self.assertEqual(
                51,
                conn.execute(
                    "SELECT project_id FROM projects WHERE slug='roadmap'"
                ).fetchone()[0],
            )
            self.assertEqual(
                2,
                conn.execute("SELECT COUNT(*) FROM prompt_id_registry").fetchone()[0],
            )
            self.assertEqual("ok", conn.execute("PRAGMA quick_check").fetchone()[0])
            self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            conn.close()

    def test_allocator_never_reuses_registry_or_roadmap_prompt_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.make_target(root)
            source = self.make_megavault(root)
            c2_identity.import_megavault_subset(target, source)
            conn = c2_identity.connect_db(target)
            try:
                allocated = c2_identity.allocate_prompt_id(
                    conn,
                    source="c2-intake:test",
                    project_id=51,
                )
                conn.commit()
                self.assertNotIn(allocated, {123456, 654321})
                row = conn.execute(
                    "SELECT * FROM prompt_id_registry WHERE prompt_id=?",
                    (allocated,),
                ).fetchone()
                self.assertEqual("allocated", row["status"])
                self.assertEqual(51, row["project_id"])
            finally:
                conn.close()

    def test_prompt_id_lifecycle_and_historical_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.make_target(root)
            source = self.make_megavault(root)
            c2_identity.import_megavault_subset(target, source)
            conn = c2_identity.connect_db(target)
            try:
                prompt_id = c2_identity.allocate_prompt_id(
                    conn,
                    source="c2-intake:test",
                    project_id=51,
                )
                digest = "a" * 64
                c2_identity.materialize_prompt_id(
                    conn, prompt_id, content_sha256=digest
                )
                c2_identity.mark_prompt_id_used(conn, prompt_id)
                conn.commit()
                row = conn.execute(
                    "SELECT status,content_sha256 FROM prompt_id_registry WHERE prompt_id=?",
                    (prompt_id,),
                ).fetchone()
                self.assertEqual(("used", digest), tuple(row))
                with self.assertRaisesRegex(
                    c2_identity.C2IdentityError,
                    "historical_prompt_id_terminal",
                ):
                    c2_identity.materialize_prompt_id(
                        conn, 123456, content_sha256="b" * 64
                    )
            finally:
                conn.close()

    def test_project_resolution_accepts_id_slug_name_and_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.make_target(root)
            source = self.make_megavault(root)
            c2_identity.import_megavault_subset(target, source)
            conn = c2_identity.connect_db(target)
            try:
                for value in (51, "51", "roadmap", "Roadmap", "c2"):
                    self.assertEqual(51, c2_identity.resolve_project_id(conn, value))
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
