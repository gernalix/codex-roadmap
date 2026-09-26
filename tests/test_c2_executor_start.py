from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import c2_executor_start as start


class ExecutorStartTests(unittest.TestCase):
    @patch('c2_executor_start.submit_document')
    def test_run_identity_is_minimal_and_idempotent(self, submit):
        submit.return_value={'submission':'queued','request_key':'x'}
        start.submit_start(run_id='run-1')
        doc=submit.call_args.args[0]
        args=doc['operations'][0]['arguments']
        self.assertEqual({'run_id':'run-1'},args)
        self.assertTrue(submit.call_args.kwargs['request_key'].startswith('c2-executor-start-'))

    @patch('c2_executor_start.submit_document')
    @patch.dict(os.environ,{'CODEX_THREAD_ID':'thread-1'},clear=True)
    def test_manual_codex_uses_thread_identity_when_available(self, submit):
        submit.return_value={'submission':'queued'}
        start.submit_start(prompt_id='123456')
        args=submit.call_args.args[0]['operations'][0]['arguments']
        self.assertEqual('codex',args['executor'])
        self.assertEqual('thread-1',args['executor_ref'])
        self.assertEqual('codex://threads/thread-1',args['chat_url'])

    def test_manual_start_requires_executor_without_run(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,'executor required'):
                start.submit_start(work_item_id='wi:test')


if __name__=='__main__':
    unittest.main()
