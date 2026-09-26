"""One synthetic C2 migration-to-delivery path with real SQLite and native execution."""
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_identity,c2_intake,c2_runtime,c2_worker,c2_notify_worker,c2_mutations
import roadmap_db as db
import work_items_migration as migration
import work_items_state_import as state_import
import work_items_cutover as cutover
from test_c2_identity import C2IdentityTests


class C2EndToEnd(unittest.TestCase):
    def test_backup_import_schedule_execute_notify_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            repo=root/'roadmap';repo.mkdir()
            source=db.connect(repo)
            for prompt_id in ('175908','707603'):
                db.register_prompt(source,prompt_id=prompt_id,slug='p'+prompt_id,
                    title='Already running '+prompt_id,current_path='prompts/'+prompt_id+'.md',
                    project_id='51')
                db.set_status(source,prompt_id,'running',actor='fixture')
            source.commit();source.close()
            path=repo/'roadmap.sqlite'
            backup=root/'original.sqlite'
            migration.create_backup(path,backup)
            migration.migrate_database(path)
            state_root=root/'state';state_root.mkdir()
            (state_root/'175908.md').write_text('''PROMPT_ID: 175908
## Objective
Preserve running goal.
## Plan / checklist
- [x] Old check
- [ ] New check
## Current step
Keep working.
## Completed
- Old check
## Remaining
- New check
## Blockers
None.
## Evidence
- Verified.
## Next action
Continue.
''')
            with closing(c2_intake._connect(path)) as conn:
                before=state_import.import_state_tree(conn,state_root,source_commit='fixture')
                self.assertEqual(1,before['imported'])
                again=state_import.import_state_tree(conn,state_root,source_commit='fixture')
                self.assertEqual(1,again['idempotent'])
                conn.commit()
            vault=C2IdentityTests().make_megavault(root)
            c2_identity.import_megavault_subset(path,vault)
            self.assertTrue(c2_identity.import_megavault_subset(path,vault)['idempotent'])
            cutover.cutover_database(path)
            marker=root/'executed'
            with closing(c2_intake._connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(writer,title='Native milestone',kind='gate',
                    project='51',repo='fixture:native',sort_order=0)
                import c2_scheduler
                c2_scheduler.configure(writer,item['work_item_id'],activity='native',
                    command=[sys.executable,'-c',f"from pathlib import Path; Path({str(marker)!r}).write_text('once')"])
                authority={'supervisor_id':'fixture-supervisor','fencing_token':1,
                           'lease_expires_at':time.time()+120}
                db.apply_mutation(writer,{'op':'c2_claim_supervisor',
                                          'arguments':{'supervisor_authority':authority}})
                writer.commit()
                def submit(operation,args,key):
                    writer.execute('BEGIN IMMEDIATE')
                    try:
                        args=dict(args)
                        if operation in c2_mutations.SUPERVISOR_OPERATIONS:
                            args['supervisor_authority']=authority
                        db.apply_mutation(writer,{'op':'c2_'+operation,'arguments':args})
                        writer.commit()
                    except Exception:
                        writer.rollback();raise
                launched=[]
                for now in (10,11,12):
                    with closing(c2_runtime._open_snapshot(path)) as snapshot:
                        c2_runtime.advance(snapshot,submit=submit,launch=launched.append,
                            launch_notify=lambda key: None,now=now,max_parallel=4)
                self.assertEqual(1,len(launched))
                run_id=launched[0]
                result=c2_worker.run_once(path,run_id,state_root=root/'runs',
                    submit=lambda op,args,key:submit(op,args,key))
                self.assertEqual('completed',result['state'])
                self.assertEqual('once',marker.read_text())
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=lambda _:None,
                        launch_notify=lambda _:None,now=13,max_parallel=4)
                delivered=[]
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=lambda _:None,
                        launch_notify=delivered.append,now=14,max_parallel=4)
                self.assertEqual(1,len(delivered))
                notifications=[]
                for _ in range(2):
                    c2_notify_worker.deliver(path,delivered[0],root=root/'notices',
                        send=lambda title,message:notifications.append(message) or True,
                        submit=lambda op,args,key:submit(op,args,key))
                self.assertEqual(1,len(notifications))
                self.assertIn('Native milestone',notifications[0])
                self.assertEqual('sent',writer.execute('SELECT state FROM c2_notification_outbox').fetchone()[0])
                self.assertEqual('ok',writer.execute('PRAGMA integrity_check').fetchone()[0])
                self.assertEqual([],writer.execute('PRAGMA foreign_key_check').fetchall())
                self.assertEqual([('175908','running'),('707603','running')],
                    [tuple(row) for row in writer.execute("SELECT prompt_id,status FROM prompts WHERE prompt_id IN ('175908','707603') ORDER BY prompt_id")])
            migration.restore_backup(backup,path)
            with closing(sqlite3.connect(path)) as restored:
                self.assertIsNone(restored.execute("SELECT 1 FROM sqlite_master WHERE name='work_items'").fetchone())
                self.assertEqual('ok',restored.execute('PRAGMA quick_check').fetchone()[0])
