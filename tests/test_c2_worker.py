from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake,c2_scheduler,c2_worker
from test_c2_intake import C2IntakeTests


class WorkerTests(unittest.TestCase):
    def test_native_end_to_end_single_run_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path=C2IntakeTests().make_cutover_db(root)
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                marker=root/'marker'
                item=c2_intake.add_work_item(conn,title='Native proof',repo='fixture')
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',
                    command=[sys.executable,'-c',f"from pathlib import Path; Path({str(marker)!r}).write_text('done')"])
                run=c2_scheduler.schedule(conn,event_key='synthetic-intake',now=10)[0]
                c2_scheduler.acknowledge(conn,run['run_id'],worker_ref='c2-run:'+run['run_id'],
                    metadata=run['metadata'],now=11)
                conn.commit()
                calls=[]
                def submit(op,args,key):
                    calls.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    c2_scheduler.complete(conn,**args)
                    conn.commit()
                result=c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',submit=submit)
                self.assertEqual('completed',result['state'])
                self.assertEqual('done',marker.read_text())
                self.assertEqual('completed',conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0])
                with self.assertRaisesRegex(c2_worker.WorkerError,'run_not_claimed'):
                    c2_worker.run_once(path,run['run_id'],state_root=root/'receipts',submit=submit)
                self.assertEqual(1,len(calls))
            finally:
                conn.close()
