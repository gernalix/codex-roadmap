from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import roadmap_db as db
import work_items_cutover as cutover
import work_items_migration as migration


class WorkItemsCutoverTests(unittest.TestCase):
    def prepare(self, root: Path, *, terminal_history: bool = False) -> Path:
        repo = root / "repo"
        repo.mkdir()
        (repo / "prompts").mkdir()
        for prompt_id, slug in (
            ("111111", "one"),
            ("222222", "two"),
            ("333333", "three"),
        ):
            (repo / "prompts" / f"{slug}.md").write_text(
                f"PROMPT_ID={prompt_id}\n",
                encoding="utf-8",
            )
        conn = db.connect(repo)
        db.register_prompt(
            conn,
            prompt_id="111111",
            slug="one",
            title="One",
            current_path="prompts/one.md",
            model="GPT-5.6 Terra",
            reasoning="medium",
            queue_position=1,
        )
        db.register_prompt(
            conn,
            prompt_id="222222",
            slug="two",
            title="Two",
            current_path="prompts/two.md",
            queue_position=2,
        )
        db.register_prompt(
            conn,
            prompt_id="333333",
            slug="three",
            title="Three",
            current_path="prompts/three.md",
            queue_position=3,
        )
        db.add_dependency(conn, "222222", "111111")
        db.add_tag(conn, "222222", "before")
        db.add_relation(conn, "111111", "333333", "parent", actor="test")
        if terminal_history:
            conn.execute("""INSERT INTO terminal_request_history(
                prompt_id,requested_status,actor,note,requested_at,running_history_id,
                archived_at,replaced_by_running_history_id
            ) VALUES('111111','blocked','test','prior generation',
                     '2026-09-25T10:01:00Z',42,'2026-09-26T10:00:00Z',73)""")
        db.refresh_materialization_hashes(conn, repo)
        conn.commit()
        conn.close()
        migration.migrate_database(repo / "roadmap.sqlite")
        cutover.cutover_database(repo / "roadmap.sqlite")
        return repo


    def test_legacy_surfaces_are_views_and_direct_writes_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp))
            conn = sqlite3.connect(repo / "roadmap.sqlite")
            types = dict(
                conn.execute(
                    """SELECT name,type FROM sqlite_master
                       WHERE name IN ('prompts','dependencies','prompt_relations','prompt_tags')"""
                )
            )
            self.assertEqual(
                {
                    "prompts": "view",
                    "dependencies": "view",
                    "prompt_relations": "view",
                    "prompt_tags": "view",
                },
                types,
            )
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute(
                    "UPDATE prompts SET status='completed' WHERE prompt_id='111111'"
                )
            conn.close()

    def test_terminal_request_history_survives_work_item_cutover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp), terminal_history=True)
            conn = sqlite3.connect(repo / "roadmap.sqlite")
            row = conn.execute(
                "SELECT prompt_id,requested_status,running_history_id,replaced_by_running_history_id "
                "FROM terminal_request_history"
            ).fetchone()
            self.assertEqual(("111111", "blocked", 42, 73), row)
            conn.close()

    def test_canonical_api_writes_new_authority_after_cutover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp))
            conn = db.connect(repo)
            self.assertTrue(db.work_items_cutover_active(conn))

            db.set_model(conn, "111111", "GPT-5.6 Sol", actor="test")
            db.set_reasoning(conn, "111111", "low", actor="test")
            db.set_explanation(conn, "111111", "Updated explanation", actor="test")
            db.reorder_prompt(conn, "111111", 4, actor="test")
            db.add_tag(conn, "111111", "new-tag")
            db.remove_tag(conn, "222222", "before", actor="test")
            db.replace_dependency(
                conn, "222222", "111111", "333333", actor="test"
            )
            db.add_relation(conn, "222222", "333333", "related", actor="test")
            with self.assertRaisesRegex(
                db.RoadmapDBError, "work_item_parent_conflict"
            ):
                db.add_relation(conn, "222222", "333333", "parent", actor="test")
            conn.commit()

            prompt = db.prompt_row(conn, "111111")
            self.assertEqual("GPT-5.6 Sol", prompt["model"])
            self.assertEqual("low", prompt["reasoning"])
            self.assertEqual("Updated explanation", prompt["explanation"])
            self.assertEqual(4, prompt["queue_position"])
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM prompt_tags WHERE prompt_id='111111' AND tag='new-tag'"
                ).fetchone()[0],
            )
            self.assertEqual(
                0,
                conn.execute(
                    "SELECT COUNT(*) FROM prompt_tags WHERE prompt_id='222222' AND tag='before'"
                ).fetchone()[0],
            )
            self.assertEqual(
                [("333333",)],
                [
                    tuple(row)
                    for row in conn.execute(
                        "SELECT depends_on_prompt_id FROM dependencies WHERE prompt_id='222222'"
                    ).fetchall()
                ],
            )
            parent = conn.execute(
                "SELECT parent_id FROM work_items WHERE prompt_id='333333'"
            ).fetchone()[0]
            self.assertEqual("prompt:111111", parent)
            self.assertEqual(
                1,
                conn.execute(
                    """SELECT COUNT(*) FROM prompt_relations
                       WHERE from_prompt_id='222222'
                         AND to_prompt_id='333333'
                         AND relation_type='related'"""
                ).fetchone()[0],
            )
            conn.close()

    def test_existing_wi_ids_are_used_for_prompt_relations_dependencies_and_tags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp))
            conn = db.connect(repo)
            work_item_ids = {
                "444444": "wi:44444444-4444-4444-8444-444444444444",
                "555555": "wi:55555555-5555-4555-8555-555555555555",
                "666666": "wi:66666666-6666-4666-8666-666666666666",
            }
            for prompt_id in ("444444", "555555", "666666"):
                db.register_prompt(
                    conn,
                    prompt_id=prompt_id,
                    slug=f"prompt-{prompt_id}",
                    title=prompt_id,
                    current_path=f"prompts/{prompt_id}.md",
                )
                conn.execute(
                    "UPDATE work_items SET work_item_id=? WHERE prompt_id=?",
                    (work_item_ids[prompt_id], prompt_id),
                )
            db.set_status(conn, "444444", "blocked", actor="test")
            db.set_status(conn, "555555", "completed", actor="test")

            db.add_relation(conn, "444444", "555555", "resolved_by", actor="test")
            db.add_dependency(conn, "666666", "555555")
            db.add_tag(conn, "666666", "mapped")
            self.assertEqual(
                (work_item_ids["444444"], work_item_ids["555555"]),
                tuple(conn.execute(
                    "SELECT from_work_item_id,to_work_item_id FROM work_item_relations "
                    "WHERE relation_type='resolved_by'"
                ).fetchone()),
            )
            self.assertEqual(
                (work_item_ids["666666"], work_item_ids["555555"]),
                tuple(conn.execute(
                    "SELECT work_item_id,depends_on_work_item_id FROM work_item_dependencies "
                    "WHERE work_item_id=?", (work_item_ids["666666"],)
                ).fetchone()),
            )
            self.assertEqual(
                (work_item_ids["666666"], "mapped"),
                tuple(conn.execute(
                    "SELECT work_item_id,tag FROM work_item_tags WHERE tag='mapped'"
                ).fetchone()),
            )
            self.assertEqual(
                "resolved",
                conn.execute(
                    "SELECT pbf_disposition FROM v_pbf_dispositions WHERE prompt_id='444444'"
                ).fetchone()[0],
            )
            db.add_relation(conn, "444444", "666666", "parent", actor="test")
            self.assertEqual(
                work_item_ids["444444"],
                conn.execute(
                    "SELECT parent_id FROM work_items WHERE prompt_id='666666'"
                ).fetchone()[0],
            )
            db.replace_dependency(conn, "666666", "555555", "444444")
            db.remove_dependency(conn, "666666", "444444")
            db.remove_tag(conn, "666666", "mapped")
            self.assertEqual(
                0,
                conn.execute(
                    "SELECT COUNT(*) FROM work_item_dependencies WHERE work_item_id=?",
                    (work_item_ids["666666"],),
                ).fetchone()[0],
            )
            self.assertEqual(
                0,
                conn.execute(
                    "SELECT COUNT(*) FROM work_item_tags WHERE work_item_id=?",
                    (work_item_ids["666666"],),
                ).fetchone()[0],
            )
            conn.close()

    def test_executor_policy_mutation_updates_pending_and_rejects_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp))
            conn = db.connect(repo)
            db.apply_mutation(conn, {
                "op": "executor_policy",
                "prompt_id": "111111",
                "executor_policy": "chatgpt",
                "note": "user override",
            })
            self.assertEqual("chatgpt", conn.execute("SELECT executor_policy FROM work_items WHERE prompt_id=\'111111\'").fetchone()[0])
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE event_type='prompt_executor_policy_updated'"
                ).fetchone()[0],
            )
            db.set_status(conn, "111111", "running", actor="chatgpt", note="launch")
            with self.assertRaisesRegex(db.RoadmapDBError, "running_prompt_locked"):
                db.apply_mutation(conn, {
                    "op": "executor_policy",
                    "prompt_id": "111111",
                    "executor_policy": "rdc",
                })
            conn.close()

    def test_register_and_status_transition_work_after_cutover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.prepare(Path(tmp))
            conn = db.connect(repo)
            db.register_prompt(
                conn,
                prompt_id="444444",
                slug="four",
                title="Four",
                current_path="prompts/four.md",
                prompt_type="Goal",
                model="GPT-5.6 Luna",
                reasoning="low",
                queue_position=5,
                prompt_text="PROMPT_ID=444444\n",
            )
            db.set_status(conn, "111111", "completed", actor="test")
            db.set_status(conn, "444444", "running", actor="codex", note="launch")
            conn.commit()

            row = db.prompt_row(conn, "444444")
            self.assertEqual("running", row["status"])
            self.assertEqual("Goal", row["prompt_type"])
            self.assertEqual("GPT-5.6 Luna", row["model"])
            self.assertEqual(
                "running",
                conn.execute(
                    "SELECT status FROM work_items WHERE prompt_id='444444'"
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM prompt_metadata WHERE prompt_id='444444'"
                ).fetchone()[0],
            )
            conn.close()


if __name__ == "__main__":
    unittest.main()
