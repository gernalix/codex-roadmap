from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_browser_recovery as recovery


class BrowserRecoveryTests(unittest.TestCase):
    def test_cdp_preflight_reserves_capacity_before_target_creation(self):
        events = []
        safety = ModuleType('chatgpt_rdc_supervisor.safety')
        safety.reserve_launch = lambda *, open_tabs: events.append(('reserve', open_tabs))
        class FakeCDP:
            def __init__(self, url):
                events.append(('connect', url))
            def call(self, method, params):
                events.append(('call', method))
                return {'targetId': 'new-target'}
            def close(self):
                pass
        lists = iter([
            [{'id': 'existing', 'type': 'page'}],
            [{'id': 'new-target', 'type': 'page', 'webSocketDebuggerUrl': 'ws://target'}],
        ])
        def data(path):
            return next(lists) if path == '/json/list' else {'webSocketDebuggerUrl': 'ws://browser'}
        with patch.dict(sys.modules, {'chatgpt_rdc_supervisor.safety': safety}), \
             patch.object(recovery, '_json', side_effect=data), \
             patch.object(recovery, 'CDP', FakeCDP):
            target, page = recovery.open_successor_tab()
        self.assertEqual('new-target', target)
        self.assertIsInstance(page, FakeCDP)
        self.assertEqual(('reserve', 1), events[0])
        self.assertEqual(('call', 'Target.createTarget'), events[2])

    def test_circuit_breaker_denies_before_creating_target(self):
        safety = ModuleType('chatgpt_rdc_supervisor.safety')
        def reject(**_):
            raise RuntimeError('circuit_breaker')
        safety.reserve_launch = reject
        with patch.dict(sys.modules, {'chatgpt_rdc_supervisor.safety': safety}), \
             patch.object(recovery, '_json', return_value=[{'type': 'page'}]), \
             patch.object(recovery, 'CDP') as cdp:
            with self.assertRaisesRegex(RuntimeError, 'circuit_breaker'):
                recovery.open_successor_tab()
        cdp.assert_not_called()


if __name__ == '__main__':
    unittest.main()
