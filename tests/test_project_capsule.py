import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_capsule', ROOT / 'tools/project_capsule.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CapsuleContractTests(unittest.TestCase):
    def test_schema_rejects_missing_and_unknown_fields(self):
        schema = json.loads((ROOT / 'docs/project-capsule/schema-v1.json').read_text())
        errors = module.schema_errors({'schema_version': 'c2.project-capsule.v1', 'surprise': 1}, schema, schema)
        self.assertTrue(any('identity: required' in e for e in errors))
        self.assertTrue(any('surprise: unknown' in e for e in errors))

    def test_fast_never_runs_full_hook_and_requires_changed_file_mapping(self):
        db = Path('/home/daniele/MegaVault/megavault.sqlite')
        if not db.is_file():
            self.skipTest('MegaVault DB is unavailable')
        report = module.check(ROOT, 'FAST', db, ['tools/project_capsule.py'], 5)
        self.assertEqual('PASS', report['status'], report)
        self.assertFalse(any(c['check'].startswith('hook:') for c in report['checks']))
        missing = module.check(ROOT, 'FAST', db, ['unmapped.file'], 5)
        self.assertEqual('FAIL', missing['status'])
        self.assertTrue(any(c['check'] == 'change_verification:unmapped.file' and c['state'] == 'fail' for c in missing['checks']))


if __name__ == '__main__':
    unittest.main()
