from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_execution_override as cli
import c2_intake
import c2_scheduler
import test_c2_intake


class ExecutionOverrideCliTests(unittest.TestCase):
    def test_default_read_syncs_and_reads_verified_snapshot(self):
        output=StringIO()
        with patch.object(cli,'sync') as sync, \
             patch.object(cli,'_open_snapshot') as open_snapshot, \
             patch.object(cli,'read_override',return_value=None), \
             redirect_stdout(output):
            open_snapshot.return_value.__enter__.return_value = object()
            self.assertEqual(0,cli.main(['read']))
        sync.assert_called_once_with(cli.DEFAULT_REPO,cli.DEFAULT_OUTPUT)
        open_snapshot.assert_called_once_with(cli.DEFAULT_OUTPUT)
        self.assertEqual({'execution_override':None},json.loads(output.getvalue()))

    def test_explicit_snapshot_read_and_fenced_set_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=test_c2_intake.C2IntakeTests().make_cutover_db(Path(tmp))
            with c2_intake._connect(path) as conn:
                conn.execute('BEGIN IMMEDIATE')
                c2_scheduler.set_override(conn,selector='repo',value='gernalix/PersonalHub',now=1)
            output=StringIO()
            with redirect_stdout(output):
                self.assertEqual(0,cli.main(['--db',str(path),'read']))
            self.assertEqual('gernalix/PersonalHub',json.loads(output.getvalue())['execution_override']['value'])
            authority={'supervisor_id':'test','fencing_token':1,'lease_expires_at':9999999999}
            with patch.object(cli,'_current_authority',return_value=authority), \
                 patch.object(cli,'submit_document',return_value={'issue_number':1}) as submit, \
                 redirect_stdout(StringIO()):
                self.assertEqual(0,cli.main(['set','--selector','tag','--value','focus:ph']))
                self.assertEqual('c2_set_execution_override',submit.call_args.args[0]['operations'][0]['op'])
                self.assertEqual(authority,submit.call_args.args[0]['operations'][0]['arguments']['supervisor_authority'])
                self.assertEqual(0,cli.main(['clear']))
                self.assertEqual('c2_clear_execution_override',submit.call_args.args[0]['operations'][0]['op'])

    def test_identical_set_replay_uses_same_request_key_without_random_uuid(self):
        authority={'supervisor_id':'test','fencing_token':1,'lease_expires_at':9999999999}
        with patch.object(cli,'_current_authority',return_value=authority), \
             patch.object(cli,'submit_document',return_value={'issue_number':1}) as submit, \
             redirect_stdout(StringIO()):
            self.assertEqual(0,cli.main(['set','--selector','tag','--value','focus:ph']))
            first=submit.call_args.kwargs['request_key']
            self.assertEqual(0,cli.main(['set','--selector','tag','--value','focus:ph']))
            second=submit.call_args.kwargs['request_key']
        self.assertEqual(first,second)
        self.assertEqual(first,cli._request_key(submit.call_args.args[0]))
        self.assertNotIn('uuid',cli.__dict__)

    def test_identical_clear_replay_uses_same_request_key(self):
        authority={'supervisor_id':'test','fencing_token':1,'lease_expires_at':9999999999}
        with patch.object(cli,'_current_authority',return_value=authority), \
             patch.object(cli,'submit_document',return_value={'issue_number':1}) as submit, \
             redirect_stdout(StringIO()):
            self.assertEqual(0,cli.main(['clear']))
            first=submit.call_args.kwargs['request_key']
            self.assertEqual(0,cli.main(['clear']))
            second=submit.call_args.kwargs['request_key']
        self.assertEqual(first,second)

    def test_different_operation_value_or_authority_document_uses_different_key(self):
        authority={'supervisor_id':'test','fencing_token':1,'lease_expires_at':9999999999}
        changed_authority={**authority,'fencing_token':2}
        def key_for(argv, current_authority):
            with patch.object(cli,'_current_authority',return_value=current_authority), \
                 patch.object(cli,'submit_document',return_value={'issue_number':1}) as submit, \
                 redirect_stdout(StringIO()):
                self.assertEqual(0,cli.main(argv))
            return submit.call_args.kwargs['request_key']
        set_key=key_for(['set','--selector','tag','--value','focus:ph'],authority)
        self.assertNotEqual(set_key,key_for(['clear'],authority))
        self.assertNotEqual(set_key,key_for(['set','--selector','tag','--value','focus:other'],authority))
        self.assertNotEqual(set_key,key_for(['set','--selector','tag','--value','focus:ph'],changed_authority))


if __name__ == '__main__':
    unittest.main()
