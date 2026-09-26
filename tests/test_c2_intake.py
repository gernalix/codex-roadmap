from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import c2_intake
import c2_scheduler
import roadmap_db as db
import roadmap_render
import work_items_cutover as cutover
import work_items_migration as migration


class C2IntakeTests(unittest.TestCase):
    def test_auto_intake_creates_native_spec_from_complete_structured_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,title="Run exact helper",executor_policy="auto",
                    execution={"command":["/usr/bin/true"]},
                )
                self.assertEqual({"state":"ready"},item["execution_readiness"])
                spec = conn.execute("SELECT activity,command_json FROM work_item_execution_specs WHERE work_item_id=?",
                                    (item["work_item_id"],)).fetchone()
                self.assertEqual(("native",'["/usr/bin/true"]'),tuple(spec))
                self.assertEqual("rdc",c2_scheduler.schedule(conn,event_key="auto-native",now=1)[0]["executor"])
            finally:
                conn.close()

    def test_incomplete_auto_intake_waits_without_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(conn,title="Needs context",executor_policy="auto")
                self.assertEqual({"state":"waiting","reason":"execution_context_missing"},
                                 item["execution_readiness"])
                partial = c2_intake.add_work_item(conn,title="Needs exact argv",executor_policy="auto",
                                                  execution={"activity":"native"})
                self.assertEqual("native_command_missing",partial["execution_readiness"]["reason"])
                self.assertEqual(0,conn.execute("SELECT COUNT(*) FROM work_item_execution_specs WHERE work_item_id IN (?,?)",
                    (item["work_item_id"],partial["work_item_id"])).fetchone()[0])
                self.assertEqual([],c2_scheduler.schedule(conn,event_key="incomplete",now=1))
            finally:
                conn.close()

    def test_auto_intake_never_guesses_from_title_or_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(conn,title="Run tests",repo="fixture",executor_policy="auto",
                                                  execution={"command":["/usr/bin/true"]})
                self.assertEqual("execution_worktree_missing",item["execution_readiness"]["reason"])
                self.assertEqual(0,conn.execute("SELECT COUNT(*) FROM work_item_execution_specs WHERE work_item_id=?",
                    (item["work_item_id"],)).fetchone()[0])
            finally:
                conn.close()

    def test_personalhub_auto_item_stays_with_external_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(conn,title="PH work",repo="https://github.com/gernalix/PersonalHub.git",
                    executor_policy="auto",execution={"command":["/usr/bin/true"],"worktree":"/tmp/ph"})
                self.assertEqual({"state":"waiting","reason":"external_personalhub_worker"},
                                 item["execution_readiness"])
                self.assertEqual(0,conn.execute("SELECT COUNT(*) FROM work_item_execution_specs WHERE work_item_id=?",
                    (item["work_item_id"],)).fetchone()[0])
                self.assertEqual([],c2_scheduler.schedule(conn,event_key="ph-external",now=1))
            finally:
                conn.close()

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
                    execution={"worktree":"/tmp/isolated-codex-worktree"},
                )
                conn.commit()

                prompt_id = result["prompt_id"]
                self.assertEqual(
                    f"prompts/implement-scheduler-{prompt_id}.md",
                    result["current_path"],
                )
                row = conn.execute(
                    "SELECT * FROM work_items WHERE work_item_id=?",
                    (item["work_item_id"],),
                ).fetchone()
                self.assertEqual(prompt_id, row["prompt_id"])
                self.assertEqual("codex", row["executor_policy"])
                self.assertEqual({"state":"ready"},result["execution_readiness"])
                spec=conn.execute("SELECT activity,model,reasoning,worktree FROM work_item_execution_specs WHERE work_item_id=?",
                                  (item["work_item_id"],)).fetchone()
                self.assertEqual(("coding","GPT-5.6 Sol","medium","/tmp/isolated-codex-worktree"),tuple(spec))
                meta = conn.execute(
                    "SELECT slug,current_path,model,reasoning,prompt_type FROM prompt_metadata WHERE prompt_id=?",
                    (prompt_id,),
                ).fetchone()
                self.assertEqual(f"implement-scheduler-{prompt_id}", meta["slug"])
                self.assertEqual(f"prompts/{meta['slug']}.md", meta["current_path"])
                self.assertEqual(("GPT-5.6 Sol", "medium", "Goal"), tuple(meta)[2:])
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
                body = conn.execute(
                    "SELECT body FROM prompt_materializations WHERE prompt_id=?",
                    (prompt_id,),
                ).fetchone()[0]
                self.assertTrue(body.startswith(f"PROMPT_ID={prompt_id}\n\n"))
            finally:
                conn.close()

    def test_reconcile_prompt_file_locations_repairs_legacy_active_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.make_cutover_db(root)
            repo = path.parent
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Canonical prompt path",
                    project="51",
                )
                result = c2_intake.prepare_codex(
                    conn,
                    item["work_item_id"],
                    prompt_text="# Goal\nPath repair.\n",
                    source="c2-intake:path-repair",
                    model="GPT-5.6 Sol",
                    reasoning="medium",
                )
                prompt_id = result["prompt_id"]
                canonical = result["current_path"]
                legacy = f"prompts/{prompt_id}-canonical-prompt-path.md"
                conn.execute(
                    "UPDATE prompt_metadata SET current_path=? WHERE prompt_id=?",
                    (legacy, prompt_id),
                )
                conn.commit()
                legacy_path = repo / legacy
                legacy_path.parent.mkdir(parents=True, exist_ok=True)
                legacy_path.write_text(
                    f"PROMPT_ID={prompt_id}\n\n# Goal\nPath repair.\n",
                    encoding="utf-8",
                )
            finally:
                conn.close()

            self.assertEqual(1, roadmap_render.reconcile_prompt_file_locations(repo))
            self.assertFalse((repo / legacy).exists())
            self.assertTrue((repo / canonical).is_file())
            verify = c2_intake._connect(path)
            try:
                self.assertEqual(
                    canonical,
                    verify.execute(
                        "SELECT current_path FROM prompts WHERE prompt_id=?",
                        (prompt_id,),
                    ).fetchone()[0],
                )
            finally:
                verify.close()

    def test_repair_prompt_materialization_is_sha_guarded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_cutover_db(Path(tmp))
            conn = c2_intake._connect(path)
            try:
                item = c2_intake.add_work_item(
                    conn,
                    title="Repair body",
                    project="51",
                )
                result = c2_intake.prepare_codex(
                    conn,
                    item["work_item_id"],
                    prompt_text="# Goal\nRepair me.\n",
                    source="c2-intake:repair-body",
                    model="GPT-5.6 Sol",
                    reasoning="medium",
                )
                prompt_id = result["prompt_id"]
                malformed = "C2_WORK_ITEM_ID=" + item["work_item_id"] + "\n\n# Goal\nRepair me.\n"
                db.set_prompt_text(
                    conn,
                    prompt_id,
                    malformed,
                    actor="test",
                    note="legacy malformed C2 prompt",
                )
                old_sha = conn.execute(
                    "SELECT materialization_sha256 FROM prompts WHERE prompt_id=?",
                    (prompt_id,),
                ).fetchone()[0]
                repaired_text = f"PROMPT_ID={prompt_id}\n\n{malformed}"
                repaired = c2_intake.repair_prompt_materialization(
                    conn,
                    item["work_item_id"],
                    expected_sha256=old_sha,
                    prompt_text=repaired_text,
                )
                conn.commit()
                self.assertEqual(prompt_id, repaired["prompt_id"])
                self.assertEqual(
                    repaired_text,
                    conn.execute(
                        "SELECT body FROM prompt_materializations WHERE prompt_id=?",
                        (prompt_id,),
                    ).fetchone()[0],
                )
                with self.assertRaisesRegex(
                    c2_intake.C2IntakeError,
                    "materialization_sha256_mismatch",
                ):
                    c2_intake.repair_prompt_materialization(
                        conn,
                        item["work_item_id"],
                        expected_sha256=old_sha,
                        prompt_text=repaired_text,
                    )
            finally:
                conn.rollback()
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
