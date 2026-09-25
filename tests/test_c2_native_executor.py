from pathlib import Path
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_native_executor import execute,NativeExecutionError

class NativeTests(unittest.TestCase):
    def test_real_native_run_and_receipt_replay_execute_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'count'
            metadata={'activity':'native','worktree':tmp,'command_json':json.dumps([
                sys.executable,'-c',"from pathlib import Path; p=Path('count'); p.write_text(p.read_text()+'x' if p.exists() else 'x')"])}
            receipt=Path(tmp)/'receipt.json'
            first=execute(run_id='run',metadata=metadata,receipt=receipt)
            self.assertEqual('completed',first['state'])
            self.assertEqual(first,execute(run_id='run',metadata=metadata,receipt=receipt))
            self.assertEqual('x',target.read_text())
            with self.assertRaisesRegex(NativeExecutionError,'identity_conflict'):
                execute(run_id='other',metadata=metadata,receipt=receipt)

    def test_ambiguous_receipt_is_not_reexecuted(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'receipt.json'
            metadata={'activity':'native','command_json':json.dumps([sys.executable,'-c','pass'])}
            state=execute(run_id='run',metadata=metadata,receipt=receipt)
            state['state']='executing'; receipt.write_text(json.dumps(state))
            self.assertEqual('executing',execute(run_id='run',metadata=metadata,receipt=receipt)['state'])
