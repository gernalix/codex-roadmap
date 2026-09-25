#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "work_items.sql"
FEATURE_META_KEY = "work_items_schema_version"
FEATURE_VERSION = "1"


class WorkItemsMigrationError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def prompt_work_item_id(prompt_id: str) -> str:
    return f"prompt:{prompt_id}"


def _connect(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    path = Path(path).expanduser().resolve()
    if read_only:
        if not path.is_file():
            raise WorkItemsMigrationError(f"database_missing:{path}")
        conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _integrity(conn: sqlite3.Connection) -> tuple[str, list[sqlite3.Row]]:
    quick = str(conn.execute("PRAGMA quick_check").fetchone()[0])
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    return quick, fk


def create_backup(db_path: Path, backup_path: Path) -> dict[str, Any]:
    source = Path(db_path).expanduser().resolve()
    target = Path(backup_path).expanduser().resolve()
    if target.exists():
        raise WorkItemsMigrationError(f"backup_exists:{target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(source, read_only=True)) as src, closing(sqlite3.connect(target)) as dst:
        src.backup(dst)
    with closing(_connect(target, read_only=True)) as check:
        quick, fk = _integrity(check)
    if quick != "ok" or fk:
        target.unlink(missing_ok=True)
        raise WorkItemsMigrationError(
            f"backup_validation_failed:quick={quick}:fk={len(fk)}"
        )
    return {
        "path": str(target),
        "size_bytes": target.stat().st_size,
        "sha256": _sha256(target),
        "quick_check": quick,
        "foreign_key_errors": len(fk),
    }


def _assert_parent_acyclic(conn: sqlite3.Connection) -> None:
    parent = {
        str(row["work_item_id"]): (
            str(row["parent_id"]) if row["parent_id"] is not None else None
        )
        for row in conn.execute("SELECT work_item_id,parent_id FROM work_items")
    }
    for start in parent:
        seen: set[str] = set()
        node: str | None = start
        while node is not None:
            if node in seen:
                raise WorkItemsMigrationError(f"work_item_parent_cycle:{start}:{node}")
            seen.add(node)
            node = parent.get(node)


def install_schema(conn: sqlite3.Connection) -> None:
    buffer: list[str] = []
    for line in SCHEMA_PATH.read_text(encoding="utf-8").splitlines():
        buffer.append(line)
        candidate = "\n".join(buffer).strip()
        if not candidate or not sqlite3.complete_statement(candidate):
            continue
        conn.execute(candidate)
        buffer.clear()
    if "\n".join(buffer).strip():
        raise WorkItemsMigrationError("incomplete_work_items_schema_statement")


def backfill_from_legacy(conn: sqlite3.Connection) -> dict[str, int]:
    prompt_rows = conn.execute(
        """SELECT prompt_id,title,prompt_type,status,queue_position,
                  project_id,project_name,repo,created_at,updated_at
           FROM prompts
           ORDER BY created_at,prompt_id"""
    ).fetchall()

    inserted = 0
    for row in prompt_rows:
        work_item_id = prompt_work_item_id(str(row["prompt_id"]))
        kind = "goal" if str(row["prompt_type"]).lower() == "goal" else "task"
        before = conn.total_changes
        conn.execute(
            """INSERT OR IGNORE INTO work_items(
                 work_item_id,parent_id,kind,title,status,executor_policy,sort_order,
                 current_action,next_action,blocker,project_id,project_name,repo,
                 prompt_id,task_id,required,actionable,source_kind,source_ref,
                 created_at,updated_at
               ) VALUES(?,?,?,?,?,'codex',?,NULL,NULL,NULL,?,?,?,?,NULL,1,1,'prompt',?,?,?)""",
            (
                work_item_id,
                None,
                kind,
                row["title"],
                row["status"],
                row["queue_position"],
                row["project_id"],
                row["project_name"],
                row["repo"],
                row["prompt_id"],
                row["prompt_id"],
                row["created_at"],
                row["updated_at"],
            ),
        )
        inserted += int(conn.total_changes > before)

    # Existing explicit parent relations are already single-parent in the live
    # roadmap. Preserve them as hierarchy while retaining the relation edge too.
    for row in conn.execute(
        """SELECT from_prompt_id,to_prompt_id
           FROM prompt_relations
           WHERE relation_type='parent'
           ORDER BY created_at,from_prompt_id,to_prompt_id"""
    ):
        child_id = prompt_work_item_id(str(row["to_prompt_id"]))
        parent_id = prompt_work_item_id(str(row["from_prompt_id"]))
        current = conn.execute(
            "SELECT parent_id FROM work_items WHERE work_item_id=?",
            (child_id,),
        ).fetchone()
        if current is None:
            raise WorkItemsMigrationError(f"missing_child_work_item:{child_id}")
        if current["parent_id"] not in (None, parent_id):
            raise WorkItemsMigrationError(
                f"multiple_work_item_parents:{child_id}:{current['parent_id']}:{parent_id}"
            )
        conn.execute(
            "UPDATE work_items SET parent_id=? WHERE work_item_id=? AND parent_id IS NULL",
            (parent_id, child_id),
        )

    for row in conn.execute(
        "SELECT prompt_id,depends_on_prompt_id,note FROM dependencies"
    ):
        conn.execute(
            """INSERT OR IGNORE INTO work_item_dependencies(
                 work_item_id,depends_on_work_item_id,required,note
               ) VALUES(?,?,1,?)""",
            (
                prompt_work_item_id(str(row["prompt_id"])),
                prompt_work_item_id(str(row["depends_on_prompt_id"])),
                row["note"],
            ),
        )

    for row in conn.execute(
        """SELECT from_prompt_id,to_prompt_id,relation_type,created_at,actor,note
           FROM prompt_relations"""
    ):
        conn.execute(
            """INSERT OR IGNORE INTO work_item_relations(
                 from_work_item_id,to_work_item_id,relation_type,created_at,actor,note
               ) VALUES(?,?,?,?,?,?)""",
            (
                prompt_work_item_id(str(row["from_prompt_id"])),
                prompt_work_item_id(str(row["to_prompt_id"])),
                row["relation_type"],
                row["created_at"],
                row["actor"],
                row["note"],
            ),
        )

    for row in conn.execute("SELECT prompt_id,tag FROM prompt_tags"):
        conn.execute(
            "INSERT OR IGNORE INTO work_item_tags(work_item_id,tag) VALUES(?,?)",
            (prompt_work_item_id(str(row["prompt_id"])), row["tag"]),
        )

    conn.execute(
        """INSERT INTO meta(key,value) VALUES(?,?)
           ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
        (FEATURE_META_KEY, FEATURE_VERSION),
    )
    _assert_parent_acyclic(conn)
    return {
        "legacy_prompts": len(prompt_rows),
        "work_items_inserted": inserted,
    }


def verify_migration(conn: sqlite3.Connection) -> dict[str, Any]:
    quick, fk = _integrity(conn)
    prompt_count = int(conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0])
    mapped_prompt_count = int(
        conn.execute(
            """SELECT COUNT(*)
               FROM prompts p
               JOIN work_items w ON w.prompt_id=p.prompt_id"""
        ).fetchone()[0]
    )
    dependency_count = int(conn.execute("SELECT COUNT(*) FROM dependencies").fetchone()[0])
    mapped_dependency_count = int(
        conn.execute("SELECT COUNT(*) FROM work_item_dependencies").fetchone()[0]
    )
    relation_count = int(conn.execute("SELECT COUNT(*) FROM prompt_relations").fetchone()[0])
    mapped_relation_count = int(
        conn.execute("SELECT COUNT(*) FROM work_item_relations").fetchone()[0]
    )
    tag_count = int(conn.execute("SELECT COUNT(*) FROM prompt_tags").fetchone()[0])
    mapped_tag_count = int(conn.execute("SELECT COUNT(*) FROM work_item_tags").fetchone()[0])
    feature = conn.execute(
        "SELECT value FROM meta WHERE key=?",
        (FEATURE_META_KEY,),
    ).fetchone()
    _assert_parent_acyclic(conn)
    problems: list[str] = []
    if quick != "ok":
        problems.append(f"quick_check:{quick}")
    if fk:
        problems.append(f"foreign_key_errors:{len(fk)}")
    if mapped_prompt_count != prompt_count:
        problems.append(f"prompt_mapping:{mapped_prompt_count}/{prompt_count}")
    if mapped_dependency_count != dependency_count:
        problems.append(
            f"dependency_mapping:{mapped_dependency_count}/{dependency_count}"
        )
    if mapped_relation_count != relation_count:
        problems.append(f"relation_mapping:{mapped_relation_count}/{relation_count}")
    if mapped_tag_count != tag_count:
        problems.append(f"tag_mapping:{mapped_tag_count}/{tag_count}")
    if not feature or str(feature[0]) != FEATURE_VERSION:
        problems.append("feature_version_missing")
    running_mismatch = conn.execute(
        """SELECT p.prompt_id,p.status,w.status
           FROM prompts p
           JOIN work_items w ON w.prompt_id=p.prompt_id
           WHERE p.status='running' AND w.status<>'running'"""
    ).fetchall()
    if running_mismatch:
        problems.append("running_prompt_status_changed")
    return {
        "ok": not problems,
        "problems": problems,
        "quick_check": quick,
        "foreign_key_errors": len(fk),
        "prompts": prompt_count,
        "mapped_prompts": mapped_prompt_count,
        "dependencies": dependency_count,
        "mapped_dependencies": mapped_dependency_count,
        "relations": relation_count,
        "mapped_relations": mapped_relation_count,
        "tags": tag_count,
        "mapped_tags": mapped_tag_count,
        "work_items": int(conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]),
        "feature_version": str(feature[0]) if feature else None,
    }


def migrate_database(db_path: Path) -> dict[str, Any]:
    path = Path(db_path).expanduser().resolve()
    with closing(_connect(path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            install_schema(conn)
            result = backfill_from_legacy(conn)
            verification = verify_migration(conn)
            if not verification["ok"]:
                raise WorkItemsMigrationError(
                    "migration_verification_failed:" + ",".join(verification["problems"])
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {**result, **verification, "database": str(path)}


def restore_backup(backup_path: Path, db_path: Path) -> dict[str, Any]:
    backup = Path(backup_path).expanduser().resolve()
    target = Path(db_path).expanduser().resolve()
    if not backup.is_file():
        raise WorkItemsMigrationError(f"backup_missing:{backup}")
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(target) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise WorkItemsMigrationError(f"target_sidecar_present:{sidecar}")
    with closing(_connect(backup, read_only=True)) as source:
        quick, fk = _integrity(source)
    if quick != "ok" or fk:
        raise WorkItemsMigrationError(
            f"backup_invalid:quick={quick}:fk={len(fk)}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=target.name + ".rollback.",
        suffix=".sqlite",
        dir=target.parent,
    )
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copy2(backup, tmp)
        with closing(_connect(tmp, read_only=True)) as check:
            restored_quick, restored_fk = _integrity(check)
        if restored_quick != "ok" or restored_fk:
            raise WorkItemsMigrationError(
                f"rollback_copy_invalid:quick={restored_quick}:fk={len(restored_fk)}"
            )
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    return {
        "database": str(target),
        "restored_from": str(backup),
        "sha256": _sha256(target),
        "quick_check": "ok",
        "foreign_key_errors": 0,
    }


def _json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explicit, backup-first Checklist 2.0 work_items migration"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup")
    backup.add_argument("--db", type=Path, required=True)
    backup.add_argument("--output", type=Path, required=True)

    migrate = sub.add_parser("migrate")
    migrate.add_argument("--db", type=Path, required=True)
    migrate.add_argument("--backup", type=Path, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--db", type=Path, required=True)

    rollback = sub.add_parser("rollback")
    rollback.add_argument("--db", type=Path, required=True)
    rollback.add_argument("--backup", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "backup":
            payload = create_backup(args.db, args.output)
        elif args.command == "migrate":
            backup_payload = create_backup(args.db, args.backup)
            payload = {
                "backup": backup_payload,
                "migration": migrate_database(args.db),
            }
        elif args.command == "verify":
            with closing(_connect(args.db, read_only=True)) as conn:
                payload = verify_migration(conn)
        elif args.command == "rollback":
            payload = restore_backup(args.backup, args.db)
        else:
            raise AssertionError(args.command)
    except (OSError, sqlite3.Error, WorkItemsMigrationError) as exc:
        _json_print({"status": "blocked", "error": str(exc)})
        return 2
    _json_print({"status": "ok", **payload})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
