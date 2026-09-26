from pathlib import Path
import sys
import tempfile
import unittest
from textwrap import dedent
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_appserver_rpc import AppServerRPC,resolve_model,AppServerError

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


class TransportTests(unittest.TestCase):
    def test_completion_before_start_response_is_retained(self):
        server=dedent('''\
            import json,sys
            def send(value):
                print(json.dumps(value),flush=True)
            for line in sys.stdin:
                request=json.loads(line)
                if 'id' not in request: continue
                method=request['method']
                if method=='turn/start':
                    send({'method':'turn/completed','params':{
                          'turn':{'id':'turn-1','status':'completed'}}})
                    send({'id':request['id'],'result':{'turn':{'id':'turn-1','status':'inProgress'}}})
                else:
                    send({'id':request['id'],'result':{}})
            ''')
        with tempfile.TemporaryDirectory() as tmp:
            script=Path(tmp)/'server.py'
            script.write_text(server)
            with AppServerRPC(command=[sys.executable,str(script)],timeout=2) as rpc:
                result=rpc('turn/start',{'threadId':'thread-1','input':[]})
                self.assertEqual('turn-1',result['turn']['id'])
                terminal=rpc.wait_for_turn('thread-1','turn-1',idle_check=0.1)
                self.assertEqual('completed',terminal['status'])

    def test_stale_in_progress_turn_without_active_server_fails_closed(self):
        server=dedent('''\
            import json,sys
            for line in sys.stdin:
                request=json.loads(line)
                if 'id' not in request: continue
                result={'thread':{'status':{'type':'idle'},
                        'turns':[{'id':'turn-1','status':'inProgress'}]}} if request['method']=='thread/read' else {}
                print(json.dumps({'id':request['id'],'result':result}),flush=True)
            ''')
        with tempfile.TemporaryDirectory() as tmp:
            script=Path(tmp)/'server.py'
            script.write_text(server)
            with AppServerRPC(command=[sys.executable,str(script)],timeout=2) as rpc:
                with self.assertRaisesRegex(AppServerError,'orphaned_turn_requires_recovery'):
                    rpc.wait_for_turn('thread-1','turn-1',idle_check=0.01)
