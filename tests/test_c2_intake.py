from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import c2_intake
import roadmap_db as db
import work_items_cutover as cutover
import work_items_migration as migration


class C2IntakeTests(unittest.TestCase):
    def test_prepare_codex_reuses_only_unique_proven_model_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path=self.make_cutover_db(Path(tmp))
            conn=c2_intake._connect(path)
            try:
                conn.execute("UPDATE work_items SET repo='https://example.test/roadmap' WHERE prompt_id='123456'")
                for cycle in ('one','two'):
                    db.record_execution(conn,'123456',cycle_key=cycle,outcome='PASS',
                        model='GPT-5.6 Sol',reasoning='medium',update_status=False)
                item=c2_intake.add_work_item(conn,title='Follow-up',project='51')
                result=c2_intake.prepare_codex(conn,item['work_item_id'],
                    prompt_text='# Follow-up\n',source='c2-intake:test')
                self.assertEqual(('GPT-5.6 Sol','medium'),(result['model'],result['reasoning']))
            finally:
                conn.close()

    def make_cutover_db(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        conn = db.connect(repo)
        db.register_prompt(
            conn,
            prompt_id="123456",
            slug="existing",
            title="Existing",
            current_path="prompts/existing.md",
            project_id="51",
            queue_position=1,
        )
        conn.commit()
        conn.close()
        path = repo / "roadmap.sqlite"
        migration.migrate_database(path)
        conn = sqlite3.connect(path)
        conn.execute(
            "INSERT INTO projects VALUES(51,'roadmap','Roadmap','active',0,'test',NULL)"
        )
        conn.execute(
            "INSERT INTO project_aliases VALUES('c2',51)"
        )
        conn.execute(
            """INSERT INTO repositories(
                 repository_id,project_id,location,kind,branch,head,status,canonical,
                 repository_kind,host_id,worktree_path,remote_url,runtime_path
               ) VALUES('R1',51,'local','git','main','abc','active',1,
                        'remote_repo',NULL,NULL,'https://example.test/roadmap',NULL)"""
        )
        conn.execute(
            """INSERT INTO meta(key,value) VALUES('c2_identity_import_version','1')
               ON CONFLICT(key) DO UPDATE SET value=excluded.value"""
        )
        conn.commit()
        conn.close()
        cutover.cutover_database(path)
        return path

    def test_add_creates_work_item_without_prompt_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Do mechanical task",
                    project="c2",
                    executor_policy="auto",
                    next_action="Run helper.",
                    tags=["mechanical", "repeatable"],
                )
                conn.commit()
                self.assertIsNone(item["prompt_id"])
                self.assertEqual("pending", item["status"])
                self.assertEqual("51", item["project_id"])
                self.assertEqual(
                    "https://example.test/roadmap",
                    item["repo"],
                )
                self.assertEqual(
                    0,
                    conn.execute(
                        "SELECT COUNT(*) FROM prompt_id_registry"
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_prepare_codex_allocates_prompt_and_links_same_work_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Implement scheduler",
                    kind="goal",
                    project="51",
                    executor_policy="auto",
                    next_action="Implement it.",
                )
                result = c2_intake.prepare_codex(
                    conn,
                    item["work_item_id"],
                    prompt_text="# Goal\nImplement scheduler.\n",
                    source="c2-intake:test",
                    model="GPT-5.6 Sol",
                    reasoning="medium",
                    megavault_mode="STANDARD",
                )
                conn.commit()

                prompt_id = result["prompt_id"]
                row = conn.execute(
                    "SELECT * FROM work_items WHERE work_item_id=?",
                    (item["work_item_id"],),
                ).fetchone()
                self.assertEqual(prompt_id, row["prompt_id"])
                self.assertEqual("codex", row["executor_policy"])
                meta = conn.execute(
                    "SELECT model,reasoning,prompt_type FROM prompt_metadata WHERE prompt_id=?",
                    (prompt_id,),
                ).fetchone()
                self.assertEqual(("GPT-5.6 Sol", "medium", "Goal"), tuple(meta))
                registry = conn.execute(
                    "SELECT status,project_id FROM prompt_id_registry WHERE prompt_id=?",
                    (int(prompt_id),),
                ).fetchone()
                self.assertEqual(("materialized", 51), tuple(registry))
                self.assertEqual(
                    1,
                    conn.execute(
                        "SELECT COUNT(*) FROM prompt_materializations WHERE prompt_id=?",
                        (prompt_id,),
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_prepare_codex_rejects_execution_metadata_in_prompt_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Bad prompt",
                    project="51",
                )
                with self.assertRaisesRegex(
                    c2_intake.C2IntakeError,
                    "prompt_text_contains_execution_metadata",
                ):
                    c2_intake.prepare_codex(
                        conn,
                        item["work_item_id"],
                        prompt_text="MODEL=GPT-5.6 Sol\n# Goal\nBad.\n",
                        source="c2-intake:test",
                    )
            finally:
                conn.rollback()
                conn.close()

    def test_human_work_item_is_not_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Need human approval",
                    project="51",
                    executor_policy="human",
                )
                conn.commit()
                runnable = {
                    row["work_item_id"]
                    for row in c2_intake.runnable_work_items(conn)
                }
                self.assertNotIn(item["work_item_id"], runnable)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
