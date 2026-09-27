from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_supervisor_source as source


class SupervisorSourceTests(unittest.TestCase):
    def test_requires_safety_layer_in_clean_runtime_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'src'
            with patch.object(source, 'SUPERVISOR_SRC', root):
                with self.assertRaisesRegex(RuntimeError, 'supervisor_safety_runtime_missing'):
                    source.require_supervisor_source()
                safety = root / 'chatgpt_rdc_supervisor/safety.py'
                safety.parent.mkdir(parents=True)
                safety.write_text('# fixture\n')
                self.assertEqual(root, source.require_supervisor_source())


if __name__ == '__main__':
    unittest.main()
