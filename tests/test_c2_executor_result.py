from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_executor_result


class ExecutorResultCliTests(unittest.TestCase):
    def test_request_key_is_stable_for_replay_and_changes_for_new_result(self):
        base={'work_item_id':'wi:one','outcome':'BLOCKED','completed':[],
              'remaining':['wait'],'evidence':['report'],'blocker':'wait',
              'next_action':'resume','strict_contract':True}
        self.assertEqual(c2_executor_result.build_request_key(base),
                         c2_executor_result.build_request_key(dict(base)))
        changed={**base,'outcome':'PASS','remaining':[],'blocker':None,'next_action':None}
        self.assertNotEqual(c2_executor_result.build_request_key(base),
                            c2_executor_result.build_request_key(changed))
