from pathlib import Path
from contextlib import closing
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake
import c2_scheduler
import c2_runtime
from test_c2_intake import C2IntakeTests


class RuntimeTests(unittest.TestCase):
    def test_snapshot_to_writer_then_worker_without_duplicate_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn)
                conn.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(conn,title='Native',repo='repo',sort_order=1)
                c2_scheduler.configure(conn,item['work_item_id'],activity='native',command=['true'])
                conn.commit()
                submitted=[]; launched=[]
                def submit(op,args,key):
                    submitted.append((op,key))
                    conn.execute('BEGIN IMMEDIATE')
                    if op=='schedule': c2_scheduler.schedule(conn,now=10,**args)
                    elif op=='acknowledge': c2_scheduler.acknowledge(conn,now=11,**args)
                    conn.commit()
                # Read connection is independent of the writer connection to
                # model accepted remote snapshots between events.
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=10)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=11)
                with closing(c2_runtime._open_snapshot(path)) as snapshot:
                    c2_runtime.advance(snapshot,submit=submit,launch=launched.append,now=12)
                self.assertEqual(['schedule','acknowledge'],[op for op,_ in submitted])
                self.assertEqual(1,len(launched))
                self.assertEqual('running',conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0])
            finally:
                conn.close()
