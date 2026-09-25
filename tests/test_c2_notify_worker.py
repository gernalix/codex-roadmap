from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_intake,c2_scheduler,c2_notify_worker
from test_c2_intake import C2IntakeTests

class NotifyTests(unittest.TestCase):
    def test_milestone_delivery_once_across_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=C2IntakeTests().make_cutover_db(Path(tmp))
            conn=c2_intake._connect(path)
            try:
                c2_scheduler.install_schema(conn);conn.execute('BEGIN IMMEDIATE')
                item=c2_intake.add_work_item(conn,title='Gate completed',kind='gate')
                conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",(item['work_item_id'],))
                c2_scheduler.enqueue_milestone(conn,item['work_item_id'])
                key='work-item:'+item['work_item_id']+':completed'
                c2_scheduler.claim_milestone(conn,key)
                conn.commit()
                sent=[]; posted=[]
                def send(title,message):
                    sent.append((title,message));return True
                def submit(op,args,request_key):
                    posted.append(request_key)
                    conn.execute('BEGIN IMMEDIATE');c2_scheduler.mark_milestone(conn,**args);conn.commit()
                for _ in range(2):
                    self.assertEqual('sent',c2_notify_worker.deliver(path,key,root=Path(tmp)/'notices',
                        send=send,submit=submit))
                self.assertEqual(1,len(sent))
                self.assertEqual(1,len(set(posted)))
                self.assertEqual('sent',conn.execute('SELECT state FROM c2_notification_outbox').fetchone()[0])
            finally:
                conn.close()
