from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c2_supervisor_lease import acquire, connect, snapshot
import c2_supervisor_recovery_controller as controller
from c2_supervisor_watchdog import watch_once


class Page:
    def close(self):
        pass


class RecoveryControllerTests(unittest.TestCase):
    def test_watchdog_never_launches_and_controller_reuses_one_recovery_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state'
            state.mkdir()
            db_path = Path(tmp) / 'lease.sqlite3'
            with connect(db_path) as db:
                acquire(db, owner='first', pointer='/tmp/pointer', supervisor_id='first', now=100, ttl=10)
                self.assertEqual('recovery_required', watch_once(db, now=111)['state'])
                launches = []
                def prepare(row):
                    return controller.prepare_successor(row,
                        open_tab=lambda: (launches.append('tab') or ('target-1', Page())),
                        send=lambda page, message: (
                            self.assertIn('SUPERVISOR_RECOVERY_ID=first:1', message)
                            or 'https://chatgpt.com/c/recovered'),
                        find=lambda _: 'https://chatgpt.com/c/recovered')
                with patch.object(controller, 'STATE_DIR', state), \
                     patch.object(controller, 'KILL_SWITCH', Path(tmp) / 'kill'):
                    first = controller.recover_once(db, prepare=prepare, browser=lambda: 'healthy', supervisor=lambda: 'healthy')
                    again = controller.recover_once(db, prepare=prepare, browser=lambda: 'healthy', supervisor=lambda: 'healthy')
                self.assertEqual('prepared', first['state'])
                self.assertEqual('successor_prepared', again['state'])
                self.assertEqual(['tab'], launches)
                self.assertEqual('https://chatgpt.com/c/recovered', snapshot(db)['successor_session_id'])

    def test_ambiguous_send_never_creates_second_tab(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state'
            state.mkdir()
            db_path = Path(tmp) / 'lease.sqlite3'
            with connect(db_path) as db:
                acquire(db, owner='first', pointer='/tmp/pointer', supervisor_id='first', now=100, ttl=10)
                watch_once(db, now=111)
                launches = []
                with patch.object(controller, 'STATE_DIR', state), \
                     patch.object(controller, 'KILL_SWITCH', Path(tmp) / 'kill'):
                    def ambiguous(row):
                        return controller.prepare_successor(row,
                            open_tab=lambda: (launches.append('tab') or ('target-1', Page())),
                            send=lambda *_: (_ for _ in ()).throw(TimeoutError('lost ack')),
                            find=lambda _: None)
                    with self.assertRaises(TimeoutError):
                        controller.recover_once(db, prepare=ambiguous, browser=lambda: 'healthy', supervisor=lambda: 'healthy')
                    self.assertEqual('starting', controller.recover_once(
                        db, prepare=ambiguous, browser=lambda: 'healthy', supervisor=lambda: 'healthy')['state'])
                self.assertEqual(['tab'], launches)

    def test_kill_switch_blocks_controller_before_browser(self):
        with tempfile.TemporaryDirectory() as tmp:
            kill = Path(tmp) / 'kill'
            kill.touch()
            with connect(Path(tmp) / 'lease.sqlite3') as db:
                with patch.object(controller, 'KILL_SWITCH', kill):
                    result = controller.recover_once(db, browser=lambda: self.fail('browser called'))
                self.assertEqual('kill_switch_active', result['state'])

    def test_controller_never_starts_missing_browser(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(returncode=3)
        with patch.object(controller, '_json', side_effect=OSError('cdp down')), \
             patch.object(controller, 'KILL_SWITCH', Path('/definitely/missing')):
            self.assertEqual('browser_manual_start_required',
                             controller.ensure_browser(run=run))
        self.assertEqual(1, len(calls))
        self.assertEqual(['systemctl', '--user', 'is-active', '--quiet',
                          'chatgpt-rdc-browser.service'], calls[0])

    def test_controller_never_restarts_active_supervisor(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(returncode=0)
        self.assertEqual('healthy', controller.ensure_supervisor(run=run))
        self.assertEqual(1, len(calls))
        self.assertEqual('is-active', calls[0][2])


if __name__ == '__main__':
    unittest.main()
