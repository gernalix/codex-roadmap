"""Post-cutover runtime → persistent socket writer → native execution/recovery.

Only temporary fixture DBs/files are touched; no GitHub, real unit, canonical
lifecycle item, browser or notification is created by this gate.
"""
from contextlib import closing, ExitStack
import json
import multiprocessing
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_runtime
import c2_worker
import c3_local_writer
import c3_runtime
import test_c2_intake as fixtures


class C3EndToEndTests(unittest.TestCase):
    def test_socket_runtime_native_crash_recovery_and_restart(self):
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary)
            path = fixtures.C2IntakeTests().make_cutover_db(root)
            socket = root / 'writer.sock'
            lease = root / 'runtime-lease.sqlite3'
            marker = root / 'retired.json'
            marker.write_text('{}')
            launched = []
            for module, name, value in (
                (c3_runtime, 'DEFAULT_DB', lease),
                (c2_runtime, 'SUPERVISOR_DB', lease),
                (c3_runtime, 'LOCK', root / 'runtime.lock'),
                (c3_runtime, 'MARKER', marker),
                (c3_runtime, 'publish_runtime_identity', lambda row: None),
                (c3_runtime, '_launch', lambda run, db: launched.append(run)),
                (c3_runtime, '_notify', lambda event: None),
                (c3_runtime, '_worker_active', lambda run: False),
                (c2_runtime, '_coding_route', lambda: {'mode':'production', 'healthy':True,
                    'tracker_repo':'fixture/tracker', 'source_repos':['fixture/native']}),
                (c2_runtime, 'KILL_SWITCH', root / 'absent-switch'),
            ):
                stack.enter_context(patch.object(module, name, value))
            stack.enter_context(patch.dict(os.environ, {'C3_MUTATION_TRANSPORT':'local',
                                                       'C3_WRITER_SOCKET':str(socket)}))
            stack.enter_context(patch('submit_mutation._gh', side_effect=AssertionError('no GitHub')))

            def start_writer():
                process = multiprocessing.Process(target=c3_local_writer.serve,
                                                  args=(path.parent, socket))
                process.start()
                deadline = time.monotonic() + 5
                while not socket.exists() and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(socket.exists())
                return process

            def stop_writer(process):
                process.terminate()
                process.join(5)
                socket.unlink(missing_ok=True)

            process = start_writer()
            try:
                # The actual C3 runtime establishes its own fence through the
                # actual local writer; intake then uses the same authority.
                first = c3_runtime.run(path)
                self.assertIn('claim_supervisor', [event[0] for event in first['events']])
                output = root / 'native-effects'
                command = [sys.executable, '-c',
                    f"from pathlib import Path; p=Path({str(output)!r}); "
                    "p.write_text((p.read_text() if p.exists() else '')+'once\\n')"]
                arguments = {'title':'Isolated native acceptance', 'repo':'fixture/native',
                             'execution':{'activity':'native', 'command':command, 'worktree':str(root),
                                          'resources':['fixture:device']}}
                with closing(c3_runtime.connect(lease)) as coordination:
                    owner = c3_runtime.snapshot(coordination)
                arguments['supervisor_authority'] = {key:owner[key] for key in
                    ('supervisor_id','fencing_token','lease_expires_at')}
                c3_local_writer.submit_local({'schema':'codex-roadmap.mutation.v1',
                    'actor':'fixture-external-intake',
                    'operations':[{'op':'c2_intake','arguments':arguments}]},
                    request_key='fixture-intake',socket_path=socket)
                changed_file = path.parent / 'state.changed'
                external_event = changed_file.stat().st_mtime_ns
                cycles = [c3_runtime.run(path)]
                self.assertEqual(external_event, changed_file.stat().st_mtime_ns)
                with closing(sqlite3.connect(path)) as db:
                    observed = db.execute('SELECT title,status,blocker FROM work_items').fetchall()
                self.assertEqual(1, len(launched), (cycles, observed))
                run_id = launched[0]
                with closing(sqlite3.connect(path)) as db:
                    before = db.execute('SELECT work_item_id,state,lease_until FROM work_item_runs WHERE run_id=?',
                                        (run_id,)).fetchone()
                    self.assertEqual('running', before[1])
                    self.assertEqual(1, db.execute('SELECT COUNT(*) FROM work_item_executor_starts WHERE run_id=?',
                                                  (run_id,)).fetchone()[0])

                # Crash after native side-effect and durable execution receipt,
                # before terminal publication. Recovery must not repeat argv.
                def interrupted_submit(*args):
                    raise RuntimeError('fixture lost terminal publication')
                with self.assertRaisesRegex(RuntimeError, 'lost terminal'):
                    c2_worker.run_once(path, run_id, state_root=root/'runs',
                        submit=interrupted_submit, worker_prefix='c3-run:', legacy_codex_allowed=False)
                self.assertEqual('once\n', output.read_text())
                c2_runtime._writer_submit('recover', {'now':before[2]+1}, 'fixture-recover')
                c3_runtime.run(path)  # Same run, reacknowledged; no new executor.
                result = c2_worker.run_once(path, run_id, state_root=root/'runs',
                    submit=c2_runtime._writer_submit, worker_prefix='c3-run:', legacy_codex_allowed=False)
                self.assertEqual('completed', result['state'])
                self.assertGreater(changed_file.stat().st_mtime_ns, external_event)
                self.assertEqual('once\n', output.read_text())
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual('completed', db.execute('SELECT status FROM work_items WHERE work_item_id=?',
                                                             (before[0],)).fetchone()[0])
                    self.assertEqual(1, db.execute('SELECT COUNT(*) FROM work_item_runs WHERE work_item_id=?',
                                                   (before[0],)).fetchone()[0])
                    self.assertEqual(0, db.execute('SELECT COUNT(*) FROM work_item_resource_leases WHERE run_id=?',
                                                   (run_id,)).fetchone()[0])
                    self.assertEqual('ok', db.execute('PRAGMA integrity_check').fetchone()[0])
                    self.assertEqual([], db.execute('PRAGMA foreign_key_check').fetchall())
                stop_writer(process)
                process = start_writer()
                replay = c2_runtime._writer_submit('complete',
                    {'run_id':run_id, 'succeeded':True, 'worker_ref':'c3-run:'+run_id},
                    'c2-complete-'+run_id)
                self.assertTrue(replay['idempotent'])
                self.assertEqual('once\n', output.read_text())
            finally:
                stop_writer(process)


if __name__ == '__main__':
    unittest.main()
