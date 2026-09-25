#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
from typing import Any

IDENTITY_IMPORT_META = "c2_identity_import_version"
IDENTITY_IMPORT_VERSION = "1"
PROMPT_ID_MIN = 100000
PROMPT_ID_MAX = 999999


class C2IdentityError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect_db(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    resolved = Path(path).expanduser().resolve()
    if read_only:
        if not resolved.is_file():
            raise C2IdentityError(f"database_missing:{resolved}")
        conn = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(resolved)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


IMPORT_TABLES = (
    "projects",
    "project_aliases",
    "repositories",
    "project_components",
    "project_operations",
    "prompt_id_registry",
    "prompt_id_events",
)

def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row["name"]) for row in conn.execute(f'PRAGMA table_info("{table}")')]


def _assert_tables(conn: sqlite3.Connection) -> None:
    names = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    missing = [name for name in IMPORT_TABLES if name not in names]
    if missing:
        raise C2IdentityError("missing_tables:" + ",".join(missing))


def _copy_table(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
    table: str,
) -> tuple[int, int]:
    source_cols = _table_columns(source, table)
    target_cols = _table_columns(target, table)
    common = [col for col in source_cols if col in target_cols]
    if not common:
        raise C2IdentityError(f"no_common_columns:{table}")
    rows = source.execute(
        f'SELECT {",".join(common)} FROM "{table}"'
    ).fetchall()
    inserted = 0
    matched = 0
    placeholders = ",".join("?" for _ in common)
    sql = (
        f'INSERT OR IGNORE INTO "{table}"({",".join(common)}) '
        f"VALUES({placeholders})"
    )
    for row in rows:
        before = target.total_changes
        target.execute(sql, tuple(row[col] for col in common))
        if target.total_changes > before:
            inserted += 1
            continue
        pk_cols = [
            str(r["name"])
            for r in target.execute(f'PRAGMA table_info("{table}")')
            if int(r["pk"]) > 0
        ]
        if not pk_cols:
            matched += 1
            continue
        where = " AND ".join(f'"{col}" IS ?' for col in pk_cols)
        existing = target.execute(
            f'SELECT {",".join(common)} FROM "{table}" WHERE {where}',
            tuple(row[col] for col in pk_cols),
        ).fetchone()
        if existing is None:
            raise C2IdentityError(f"identity_collision_missing:{table}")
        for col in common:
            if existing[col] != row[col]:
                raise C2IdentityError(
                    f"identity_collision:{table}:{','.join(pk_cols)}:{col}"
                )
        matched += 1
    return inserted, matched

def import_megavault_subset(
    target_db: Path,
    megavault_db: Path,
) -> dict[str, Any]:
    source_path = Path(megavault_db).expanduser().resolve()
    with closing(connect_db(source_path, read_only=True)) as source, closing(
        connect_db(target_db)
    ) as target:
        _assert_tables(source)
        _assert_tables(target)
        source_quick = str(source.execute("PRAGMA quick_check").fetchone()[0])
        source_fk = source.execute("PRAGMA foreign_key_check").fetchall()
        if source_quick != "ok" or source_fk:
            raise C2IdentityError(
                f"megavault_invalid:quick={source_quick}:fk={len(source_fk)}"
            )

        existing = target.execute(
            "SELECT value FROM meta WHERE key=?",
            (IDENTITY_IMPORT_META,),
        ).fetchone()
        if existing and str(existing[0]) == IDENTITY_IMPORT_VERSION:
            return {
                "idempotent": True,
                "source_sha256": file_sha256(source_path),
                "tables": {},
            }

        target.execute("BEGIN IMMEDIATE")
        # Random PROMPT_ID order is not parent order. Validate the complete
        # imported graph before commit rather than rejecting forward edges.
        target.execute("PRAGMA defer_foreign_keys=ON")
        results: dict[str, dict[str, int]] = {}
        try:
            for table in IMPORT_TABLES:
                inserted, matched = _copy_table(source, target, table)
                results[table] = {"inserted": inserted, "matched": matched}
            historical_reserved = reserve_existing_roadmap_prompt_ids(target)
            target.execute(
                """INSERT INTO meta(key,value) VALUES(?,?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                (IDENTITY_IMPORT_META, IDENTITY_IMPORT_VERSION),
            )
            target.execute(
                """INSERT INTO meta(key,value) VALUES('c2_identity_source_sha256',?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                (file_sha256(source_path),),
            )
            quick = str(target.execute("PRAGMA quick_check").fetchone()[0])
            fk = target.execute("PRAGMA foreign_key_check").fetchall()
            if quick != "ok" or fk:
                raise C2IdentityError(
                    f"identity_import_invalid:quick={quick}:fk={len(fk)}"
                )
            target.commit()
        except Exception:
            target.rollback()
            raise
        return {
            "idempotent": False,
            "source_sha256": file_sha256(source_path),
            "tables": results,
            "historical_roadmap_prompt_ids_reserved": historical_reserved,
        }

def reserve_existing_roadmap_prompt_ids(conn: sqlite3.Connection) -> int:
    surface = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name='prompts'"
    ).fetchone()
    if not surface:
        return 0
    rows = conn.execute(
        "SELECT prompt_id,created_at FROM prompts ORDER BY prompt_id"
    ).fetchall()
    inserted = 0
    for row in rows:
        try:
            prompt_id = int(str(row["prompt_id"]))
        except ValueError:
            continue
        if not (PROMPT_ID_MIN <= prompt_id <= PROMPT_ID_MAX):
            continue
        exists = conn.execute(
            "SELECT 1 FROM prompt_id_registry WHERE prompt_id=?",
            (prompt_id,),
        ).fetchone()
        if exists:
            continue
        created = str(row["created_at"] or utc_now())
        conn.execute(
            """INSERT INTO prompt_id_registry(
                 prompt_id,parent_prompt_id,project_id,source,status,
                 content_sha256,created_at_utc,materialized_at_utc,
                 used_at_utc,cancelled_at_utc
               ) VALUES(?,NULL,NULL,'historical-roadmap','allocated',NULL,?,NULL,NULL,NULL)""",
            (prompt_id, created),
        )
        conn.execute(
            """INSERT INTO prompt_id_events(
                 prompt_id,event_type,event_at_utc,detail
               ) VALUES(?,'allocated',?,'reserved during C2 migration from existing roadmap')""",
            (prompt_id, created),
        )
        inserted += 1
    return inserted

def _occupied_prompt_ids(conn: sqlite3.Connection) -> set[int]:
    occupied = {
        int(row[0])
        for row in conn.execute("SELECT prompt_id FROM prompt_id_registry")
    }
    for query in (
        "SELECT prompt_id FROM work_items WHERE prompt_id IS NOT NULL",
        "SELECT prompt_id FROM prompts",
    ):
        try:
            rows = conn.execute(query).fetchall()
        except sqlite3.OperationalError:
            continue
        for row in rows:
            try:
                occupied.add(int(str(row[0])))
            except (TypeError, ValueError):
                continue
    return occupied


def resolve_project_id(conn: sqlite3.Connection, value: str | int) -> int:
    try:
        project_id = int(value)
    except (TypeError, ValueError):
        row = conn.execute(
            """SELECT p.project_id
               FROM project_aliases a
               JOIN projects p ON p.project_id=a.project_id
               WHERE lower(a.alias)=lower(?)
               UNION
               SELECT project_id FROM projects WHERE lower(slug)=lower(?)
               UNION
               SELECT project_id FROM projects WHERE lower(name)=lower(?)
               LIMIT 1""",
            (str(value), str(value), str(value)),
        ).fetchone()
        if not row:
            raise C2IdentityError(f"project_not_found:{value}")
        return int(row[0])
    row = conn.execute(
        "SELECT 1 FROM projects WHERE project_id=?",
        (project_id,),
    ).fetchone()
    if not row:
        raise C2IdentityError(f"project_not_found:{project_id}")
    return project_id

def allocate_prompt_id(
    conn: sqlite3.Connection,
    *,
    source: str,
    project_id: int | None = None,
    parent_prompt_id: int | None = None,
) -> int:
    source = str(source).strip()
    if not source or source.startswith("historical-"):
        raise C2IdentityError("invalid_prompt_id_source")
    if project_id is not None:
        resolve_project_id(conn, project_id)
    if parent_prompt_id is not None:
        parent = conn.execute(
            "SELECT 1 FROM prompt_id_registry WHERE prompt_id=?",
            (int(parent_prompt_id),),
        ).fetchone()
        if not parent:
            raise C2IdentityError(f"parent_prompt_id_not_found:{parent_prompt_id}")
    occupied = _occupied_prompt_ids(conn)
    space = PROMPT_ID_MAX - PROMPT_ID_MIN + 1
    if len(occupied) >= space:
        raise C2IdentityError("prompt_id_space_exhausted")
    prompt_id: int | None = None
    for _ in range(256):
        candidate = PROMPT_ID_MIN + secrets.randbelow(space)
        if candidate not in occupied:
            prompt_id = candidate
            break
    if prompt_id is None:
        for candidate in range(PROMPT_ID_MIN, PROMPT_ID_MAX + 1):
            if candidate not in occupied:
                prompt_id = candidate
                break
    assert prompt_id is not None
    now = utc_now()
    conn.execute(
        """INSERT INTO prompt_id_registry(
             prompt_id,parent_prompt_id,project_id,source,status,
             content_sha256,created_at_utc,materialized_at_utc,
             used_at_utc,cancelled_at_utc
           ) VALUES(?,?,?,?, 'allocated',NULL,?,NULL,NULL,NULL)""",
        (prompt_id, parent_prompt_id, project_id, source, now),
    )
    conn.execute(
        """INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail)
           VALUES(?,'allocated',?,?)""",
        (prompt_id, now, source),
    )
    return prompt_id

def _registry_row(conn: sqlite3.Connection, prompt_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM prompt_id_registry WHERE prompt_id=?",
        (int(prompt_id),),
    ).fetchone()
    if not row:
        raise C2IdentityError(f"prompt_id_not_found:{prompt_id}")
    return row


def materialize_prompt_id(
    conn: sqlite3.Connection,
    prompt_id: int,
    *,
    content_sha256: str,
) -> None:
    digest = str(content_sha256).strip().lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise C2IdentityError("invalid_content_sha256")
    row = _registry_row(conn, prompt_id)
    if str(row["source"]).startswith("historical-"):
        raise C2IdentityError(f"historical_prompt_id_terminal:{prompt_id}")
    if row["status"] == "materialized" and row["content_sha256"] == digest:
        return
    if row["status"] != "allocated":
        raise C2IdentityError(
            f"prompt_id_not_allocated:{prompt_id}:{row['status']}"
        )
    now = utc_now()
    conn.execute(
        """UPDATE prompt_id_registry
           SET status='materialized',
               content_sha256=?,
               materialized_at_utc=?
           WHERE prompt_id=?""",
        (digest, now, int(prompt_id)),
    )
    conn.execute(
        """INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail)
           VALUES(?,'materialized',?,?)""",
        (int(prompt_id), now, digest),
    )


def mark_prompt_id_used(conn: sqlite3.Connection, prompt_id: int) -> None:
    row = _registry_row(conn, prompt_id)
    if str(row["source"]).startswith("historical-"):
        raise C2IdentityError(f"historical_prompt_id_terminal:{prompt_id}")
    if row["status"] == "used":
        return
    if row["status"] != "materialized":
        raise C2IdentityError(
            f"prompt_id_not_materialized:{prompt_id}:{row['status']}"
        )
    now = utc_now()
    conn.execute(
        "UPDATE prompt_id_registry SET status='used',used_at_utc=? WHERE prompt_id=?",
        (now, int(prompt_id)),
    )
    conn.execute(
        """INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail)
           VALUES(?,'used',?,NULL)""",
        (int(prompt_id), now),
    )


def cancel_prompt_id(conn: sqlite3.Connection, prompt_id: int) -> None:
    row = _registry_row(conn, prompt_id)
    if str(row["source"]).startswith("historical-"):
        raise C2IdentityError(f"historical_prompt_id_terminal:{prompt_id}")
    if row["status"] == "cancelled":
        return
    if row["status"] not in {"allocated", "materialized"}:
        raise C2IdentityError(
            f"prompt_id_cannot_cancel:{prompt_id}:{row['status']}"
        )
    now = utc_now()
    conn.execute(
        "UPDATE prompt_id_registry SET status='cancelled',cancelled_at_utc=? WHERE prompt_id=?",
        (now, int(prompt_id)),
    )
    conn.execute(
        """INSERT INTO prompt_id_events(prompt_id,event_type,event_at_utc,detail)
           VALUES(?,'cancelled',?,NULL)""",
        (int(prompt_id), now),
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="C2 project/repository identity and PROMPT_ID registry")
    parser.add_argument("--db", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    imp = sub.add_parser("import-megavault")
    imp.add_argument("--megavault-db", type=Path, required=True)

    project = sub.add_parser("project-resolve")
    project.add_argument("value")

    alloc = sub.add_parser("allocate")
    alloc.add_argument("--source", required=True)
    alloc.add_argument("--project-id")
    alloc.add_argument("--parent-prompt-id", type=int)

    materialize = sub.add_parser("materialize")
    materialize.add_argument("prompt_id", type=int)
    materialize.add_argument("--sha256", required=True)

    used = sub.add_parser("used")
    used.add_argument("prompt_id", type=int)

    cancel = sub.add_parser("cancel")
    cancel.add_argument("prompt_id", type=int)

    show = sub.add_parser("show")
    show.add_argument("prompt_id", type=int)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "import-megavault":
            payload = import_megavault_subset(args.db, args.megavault_db)
        else:
            with closing(connect_db(args.db)) as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    if args.command == "project-resolve":
                        payload = {"project_id": resolve_project_id(conn, args.value)}
                    elif args.command == "allocate":
                        project_id = (
                            resolve_project_id(conn, args.project_id)
                            if args.project_id is not None
                            else None
                        )
                        prompt_id = allocate_prompt_id(
                            conn,
                            source=args.source,
                            project_id=project_id,
                            parent_prompt_id=args.parent_prompt_id,
                        )
                        payload = {"prompt_id": prompt_id, "status": "allocated"}
                    elif args.command == "materialize":
                        materialize_prompt_id(
                            conn, args.prompt_id, content_sha256=args.sha256
                        )
                        payload = {"prompt_id": args.prompt_id, "status": "materialized"}
                    elif args.command == "used":
                        mark_prompt_id_used(conn, args.prompt_id)
                        payload = {"prompt_id": args.prompt_id, "status": "used"}
                    elif args.command == "cancel":
                        cancel_prompt_id(conn, args.prompt_id)
                        payload = {"prompt_id": args.prompt_id, "status": "cancelled"}
                    elif args.command == "show":
                        payload = dict(_registry_row(conn, args.prompt_id))
                    else:
                        raise AssertionError(args.command)
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
    except (OSError, sqlite3.Error, C2IdentityError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", **payload}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
