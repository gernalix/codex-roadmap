from __future__ import annotations
import sys, unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import roadmap_finish

class FinishWrapperTests(unittest.TestCase):
    def test_finish_delegates_pass(self):
        original=roadmap_finish.finish_result
        calls=[]
        def fake(repo,prompt_id,result,**kwargs):
            calls.append((str(repo),prompt_id,result,kwargs))
            return {"status":"completed","prompt_id":prompt_id}
        roadmap_finish.finish_result=fake
        try:
            out=roadmap_finish.finish(Path("/tmp/r"),"123456",confirm_executed=True)
        finally:
            roadmap_finish.finish_result=original
        self.assertEqual("PASS",calls[0][2])
        self.assertTrue(calls[0][3]["confirm_executed"])
        self.assertEqual("remote_single_writer",out["finish_mode"])

if __name__=="__main__": unittest.main()
