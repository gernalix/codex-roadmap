#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from typing import Any

import roadmap_db
from work_items_migration import (
    FEATURE_META_KEY,
    FEATURE_VERSION,
    WorkItemsMigrationError,
    verify_migration,
)

CUTOVER_META_KEY = "work_items_cutover_version"
CUTOVER_VERSION = "1"

EXPECTED_PROMPT_FK_TABLES = {
    "analyses",
    "analysis_code_changes",
    "artifacts",
    "audit_events",
    "dependencies",
    "executions",
    "prompt_materializations",
    "prompt_relations",
    "prompt_tags",
    "status_history",
    "terminal_requests",
}


class WorkItemsCutoverError(RuntimeError):
    pass


def _prompt_fk_tables(conn: sqlite3.Connection) -> set[str]:
    tables = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    hits: set[str] = set()
    for table in tables:
        rows = conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
        if any(str(row[2]) == "prompts" for row in rows):
            hits.add(table)
    return hits


def _assert_ready(conn: sqlite3.Connection) -> None:
    migration = verify_migration(conn)
    if not migration["ok"]:
        raise WorkItemsCutoverError(
            "work_items_migration_invalid:" + ",".join(migration["problems"])
        )
    actual = _prompt_fk_tables(conn)
    if actual != EXPECTED_PROMPT_FK_TABLES:
        raise WorkItemsCutoverError(
            "unexpected_prompt_fk_tables:"
            + json.dumps(
                {
                    "expected": sorted(EXPECTED_PROMPT_FK_TABLES),
                    "actual": sorted(actual),
                },
                sort_keys=True,
            )
        )
    if conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name='prompt_metadata'"
    ).fetchone():
        raise WorkItemsCutoverError("prompt_metadata_already_exists")


PROMPT_METADATA_SQL = """
CREATE TABLE prompt_metadata (
  prompt_id TEXT PRIMARY KEY CHECK (prompt_id GLOB '[0-9][0-9][0-9][0-9][0-9][0-9]'),
  slug TEXT NOT NULL UNIQUE,
  chat_guidance TEXT,
  prompt_type TEXT NOT NULL DEFAULT 'Prompt',
  model TEXT,
  reasoning TEXT,
  megavault_mode TEXT,
  campaign_id TEXT,
  explanation TEXT NOT NULL DEFAULT '',
  current_path TEXT NOT NULL,
  materialization_sha256 TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

REBUILDS: dict[str, tuple[str, str]] = {
    "prompt_materializations": (
        """CREATE TABLE prompt_materializations (
          prompt_id TEXT PRIMARY KEY REFERENCES prompt_metadata(prompt_id) ON UPDATE CASCADE ON DELETE CASCADE,
          body TEXT NOT NULL,
          sha256 TEXT NOT NULL,
          created_at TEXT NOT NULL,
          actor TEXT NOT NULL
        )""",
        "prompt_id,body,sha256,created_at,actor",
    ),
    "executions": (
        """CREATE TABLE executions (
          execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
          prompt_id TEXT NOT NULL REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          cycle_key TEXT UNIQUE,
          materialization_sha256 TEXT,
          started_at TEXT,
          ended_at TEXT,
          outcome TEXT CHECK (outcome IN ('PASS','FAIL','BLOCKED','CANCELLED','UNKNOWN')),
          duration_seconds REAL,
          model TEXT,
          reasoning TEXT,
          codex_project TEXT,
          chat_title TEXT,
          branch TEXT,
          commit_before TEXT,
          commit_after TEXT,
          tool_call_count INTEGER,
          input_tokens INTEGER,
          cached_input_tokens INTEGER,
          uncached_input_tokens INTEGER,
          output_tokens INTEGER,
          reasoning_output_tokens INTEGER,
          total_tokens INTEGER,
          source TEXT NOT NULL DEFAULT 'manual',
          recorded_at TEXT NOT NULL
        )""",
        "execution_id,prompt_id,cycle_key,materialization_sha256,started_at,ended_at,outcome,duration_seconds,model,reasoning,codex_project,chat_title,branch,commit_before,commit_after,tool_call_count,input_tokens,cached_input_tokens,uncached_input_tokens,output_tokens,reasoning_output_tokens,total_tokens,source,recorded_at",
    ),
    "artifacts": (
        """CREATE TABLE artifacts (
          artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
          prompt_id TEXT NOT NULL REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          artifact_type TEXT NOT NULL,
          uri TEXT NOT NULL,
          label TEXT,
          created_at TEXT NOT NULL,
          UNIQUE(prompt_id, artifact_type, uri)
        )""",
        "artifact_id,prompt_id,artifact_type,uri,label,created_at",
    ),
    "status_history": (
        """CREATE TABLE status_history (
          history_id INTEGER PRIMARY KEY AUTOINCREMENT,
          prompt_id TEXT NOT NULL REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          old_status TEXT,
          new_status TEXT NOT NULL,
          changed_at TEXT NOT NULL,
          actor TEXT NOT NULL,
          note TEXT
        )""",
        "history_id,prompt_id,old_status,new_status,changed_at,actor,note",
    ),
    "audit_events": (
        """CREATE TABLE audit_events (
          event_id INTEGER PRIMARY KEY AUTOINCREMENT,
          prompt_id TEXT REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          event_type TEXT NOT NULL,
          event_at TEXT NOT NULL,
          actor TEXT NOT NULL,
          payload_json TEXT
        )""",
        "event_id,prompt_id,event_type,event_at,actor,payload_json",
    ),
    "terminal_requests": (
        """CREATE TABLE terminal_requests (
          prompt_id TEXT PRIMARY KEY REFERENCES prompt_metadata(prompt_id) ON UPDATE CASCADE ON DELETE RESTRICT,
          requested_status TEXT NOT NULL
            CHECK (requested_status IN ('completed','failed','blocked','cancelled','unknown')),
          actor TEXT NOT NULL,
          note TEXT,
          requested_at TEXT NOT NULL
        )""",
        "prompt_id,requested_status,actor,note,requested_at",
    ),
    "analyses": (
        """CREATE TABLE analyses (
          analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
          prompt_id TEXT NOT NULL REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          analyzed_at TEXT NOT NULL,
          actor TEXT NOT NULL DEFAULT 'chatgpt',
          bottlenecks_found INTEGER CHECK (bottlenecks_found IN (0,1) OR bottlenecks_found IS NULL),
          summary TEXT,
          fix_prompt_id TEXT REFERENCES prompt_metadata(prompt_id) ON DELETE SET NULL,
          source_ref TEXT
        )""",
        "analysis_id,prompt_id,analyzed_at,actor,bottlenecks_found,summary,fix_prompt_id,source_ref",
    ),
    "analysis_code_changes": (
        """CREATE TABLE analysis_code_changes (
          code_change_id INTEGER PRIMARY KEY AUTOINCREMENT,
          analysis_id INTEGER NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
          prompt_id TEXT NOT NULL REFERENCES prompt_metadata(prompt_id) ON DELETE CASCADE,
          repository TEXT NOT NULL,
          change_type TEXT NOT NULL,
          commit_sha TEXT,
          summary TEXT,
          created_at TEXT NOT NULL,
          actor TEXT NOT NULL DEFAULT 'chatgpt'
        )""",
        "code_change_id,analysis_id,prompt_id,repository,change_type,commit_sha,summary,created_at,actor",
    ),
}


def _rebuild_table(conn: sqlite3.Connection, table: str, create_sql: str, columns: str) -> None:
    tmp = f"{table}_v2"
    conn.execute(f"ALTER TABLE {table} RENAME TO {tmp}")
    conn.execute(create_sql)
    conn.execute(f"INSERT INTO {table}({columns}) SELECT {columns} FROM {tmp}")
    conn.execute(f"DROP TABLE {tmp}")


def _legacy_counts(conn: sqlite3.Connection) -> dict[str, int]:
    names = (
        "prompts",
        "dependencies",
        "prompt_relations",
        "prompt_tags",
        "prompt_materializations",
        "executions",
        "analyses",
        "analysis_code_changes",
        "artifacts",
        "status_history",
        "audit_events",
        "terminal_requests",
    )
    return {name: int(conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]) for name in names}


def _create_legacy_views(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE VIEW prompts AS
           SELECT
             m.prompt_id,
             m.slug,
             w.title,
             w.project_id,
             w.project_name,
             w.repo,
             m.chat_guidance,
             m.prompt_type,
             m.model,
             m.reasoning,
             m.megavault_mode,
             m.campaign_id,
             m.explanation,
             w.status,
             w.sort_order AS queue_position,
             m.current_path,
             m.materialization_sha256,
             m.created_at,
             CASE WHEN w.updated_at > m.updated_at THEN w.updated_at ELSE m.updated_at END AS updated_at
           FROM prompt_metadata m
           JOIN work_items w ON w.prompt_id=m.prompt_id"""
    )
    conn.execute(
        """CREATE VIEW dependencies AS
           SELECT
             child.prompt_id AS prompt_id,
             parent.prompt_id AS depends_on_prompt_id,
             d.note
           FROM work_item_dependencies d
           JOIN work_items child ON child.work_item_id=d.work_item_id
           JOIN work_items parent ON parent.work_item_id=d.depends_on_work_item_id
           WHERE child.prompt_id IS NOT NULL
             AND parent.prompt_id IS NOT NULL
             AND d.required=1"""
    )
    conn.execute(
        """CREATE VIEW prompt_relations AS
           SELECT
             source.prompt_id AS from_prompt_id,
             target.prompt_id AS to_prompt_id,
             r.relation_type,
             r.created_at,
             r.actor,
             r.note
           FROM work_item_relations r
           JOIN work_items source ON source.work_item_id=r.from_work_item_id
           JOIN work_items target ON target.work_item_id=r.to_work_item_id
           WHERE source.prompt_id IS NOT NULL
             AND target.prompt_id IS NOT NULL"""
    )
    conn.execute(
        """CREATE VIEW prompt_tags AS
           SELECT w.prompt_id AS prompt_id,t.tag
           FROM work_item_tags t
           JOIN work_items w ON w.work_item_id=t.work_item_id
           WHERE w.prompt_id IS NOT NULL"""
    )


def cutover_database(db_path: Path) -> dict[str, Any]:
    path = Path(db_path).expanduser().resolve()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        _assert_ready(conn)
        before = _legacy_counts(conn)
        generated_view_names = (
            "v_prompt_summary",
            "v_runnable_prompts",
            "v_pbf_dispositions",
            "v_attention",
        )
        generated_view_sql = {
            name: str(
                conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
                    (name,),
                ).fetchone()[0]
            )
            for name in generated_view_names
        }
        conn.execute("BEGIN IMMEDIATE")

        for view_name in (
            "v_attention",
            "v_pbf_dispositions",
            "v_runnable_prompts",
            "v_prompt_summary",
        ):
            conn.execute(f"DROP VIEW IF EXISTS {view_name}")

        conn.execute(PROMPT_METADATA_SQL)
        conn.execute(
            """INSERT INTO prompt_metadata(
                 prompt_id,slug,chat_guidance,prompt_type,model,reasoning,
                 megavault_mode,campaign_id,explanation,current_path,
                 materialization_sha256,created_at,updated_at
               )
               SELECT
                 prompt_id,slug,chat_guidance,prompt_type,model,reasoning,
                 megavault_mode,campaign_id,explanation,current_path,
                 materialization_sha256,created_at,updated_at
               FROM prompts"""
        )

        for table in (
            "analyses",
            "analysis_code_changes",
            "artifacts",
            "audit_events",
            "executions",
            "prompt_materializations",
            "status_history",
            "terminal_requests",
        ):
            create_sql, columns = REBUILDS[table]
            _rebuild_table(conn, table, create_sql, columns)

        conn.execute("DROP TABLE dependencies")
        conn.execute("DROP TABLE prompt_relations")
        conn.execute("DROP TABLE prompt_tags")
        conn.execute("DROP TABLE prompts")
        _create_legacy_views(conn)
        for view_name in generated_view_names:
            conn.execute(generated_view_sql[view_name])

        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_executions_prompt_time
               ON executions(prompt_id, started_at, ended_at)"""
        )
        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_analyses_prompt_time
               ON analyses(prompt_id, analyzed_at)"""
        )
        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_code_changes_prompt_time
               ON analysis_code_changes(prompt_id, created_at)"""
        )
        conn.execute(
            """INSERT INTO meta(key,value) VALUES(?,?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (CUTOVER_META_KEY, CUTOVER_VERSION),
        )
        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON")

        quick = str(conn.execute("PRAGMA quick_check").fetchone()[0])
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        after = _legacy_counts(conn)
        prompt_type = conn.execute(
            "SELECT type FROM sqlite_master WHERE name='prompts'"
        ).fetchone()
        dep_type = conn.execute(
            "SELECT type FROM sqlite_master WHERE name='dependencies'"
        ).fetchone()
        relation_type = conn.execute(
            "SELECT type FROM sqlite_master WHERE name='prompt_relations'"
        ).fetchone()
        tag_type = conn.execute(
            "SELECT type FROM sqlite_master WHERE name='prompt_tags'"
        ).fetchone()
        problems: list[str] = []
        if before != after:
            problems.append(
                "legacy_count_mismatch:" + json.dumps(
                    {"before": before, "after": after},
                    sort_keys=True,
                )
            )
        if quick != "ok":
            problems.append(f"quick_check:{quick}")
        if fk:
            problems.append(f"foreign_key_errors:{len(fk)}")
        if any(
            not row or row[0] != "view"
            for row in (prompt_type, dep_type, relation_type, tag_type)
        ):
            problems.append("legacy_surfaces_not_views")
        if problems:
            raise WorkItemsCutoverError(";".join(problems))
        return {
            "ok": True,
            "database": str(path),
            "legacy_counts": after,
            "quick_check": quick,
            "foreign_key_errors": len(fk),
            "cutover_version": CUTOVER_VERSION,
        }
    except Exception:
        try:
            conn.rollback()
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def verify_cutover(db_path: Path) -> dict[str, Any]:
    path = Path(db_path).expanduser().resolve()
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        quick = str(conn.execute("PRAGMA quick_check").fetchone()[0])
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        types = {
            str(row[0]): str(row[1])
            for row in conn.execute(
                """SELECT name,type FROM sqlite_master
                   WHERE name IN (
                     'prompts','dependencies','prompt_relations','prompt_tags',
                     'prompt_metadata','work_items'
                   )"""
            )
        }
        meta = conn.execute(
            "SELECT value FROM meta WHERE key=?",
            (CUTOVER_META_KEY,),
        ).fetchone()
        running = [
            tuple(row)
            for row in conn.execute(
                """SELECT prompt_id,status
                   FROM work_items
                   WHERE prompt_id IS NOT NULL AND status='running'
                   ORDER BY prompt_id"""
            )
        ]
        problems: list[str] = []
        if quick != "ok":
            problems.append(f"quick_check:{quick}")
        if fk:
            problems.append(f"foreign_key_errors:{len(fk)}")
        for name in ("prompts", "dependencies", "prompt_relations", "prompt_tags"):
            if types.get(name) != "view":
                problems.append(f"{name}_not_view")
        for name in ("prompt_metadata", "work_items"):
            if types.get(name) != "table":
                problems.append(f"{name}_not_table")
        if not meta or str(meta[0]) != CUTOVER_VERSION:
            problems.append("cutover_version_missing")
        return {
            "ok": not problems,
            "problems": problems,
            "quick_check": quick,
            "foreign_key_errors": len(fk),
            "types": types,
            "running": running,
            "cutover_version": str(meta[0]) if meta else None,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cut Checklist 2.0 actionable state over to work_items"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    cut = sub.add_parser("cutover")
    cut.add_argument("--db", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--db", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = (
            cutover_database(args.db)
            if args.command == "cutover"
            else verify_cutover(args.db)
        )
    except (OSError, sqlite3.Error, WorkItemsMigrationError, WorkItemsCutoverError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", **payload}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
