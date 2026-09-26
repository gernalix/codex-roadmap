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
    def test_read_snapshot_and_submit_fenced_set_clear(self):
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


if __name__ == '__main__':
    unittest.main()
