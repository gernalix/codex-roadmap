from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_appserver_rpc import resolve_model,AppServerError

class ResolverTests(unittest.TestCase):
    def test_catalog_label_maps_only_same_model_and_reasoning(self):
        def rpc(method,params):
            return {'data':[{'id':'gpt-6-luna','model':'gpt-6-luna','displayName':'GPT-6-Luna',
                'supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}]}
        self.assertEqual('gpt-6-luna',resolve_model(rpc,'GPT-6 Luna','medium'))
        with self.assertRaisesRegex(AppServerError,'exact_model_not_available'):
            resolve_model(rpc,'GPT-6 Sol','medium')
        with self.assertRaisesRegex(AppServerError,'exact_reasoning_not_available'):
            resolve_model(rpc,'GPT-6 Luna','ultra')
