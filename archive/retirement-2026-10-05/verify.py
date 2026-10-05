"""Read-only archive and source-to-project reconciliation verification."""
import json, pathlib, sqlite3, hashlib
A = pathlib.Path(__file__).resolve().parent
x = json.loads((A / 'export.json').read_text())
c = sqlite3.connect('file:' + str(A / 'canonical.sqlite') + '?mode=ro', uri=True)
c.row_factory = sqlite3.Row
assert c.execute('pragma integrity_check').fetchone()[0] == 'ok'
manifest = json.loads((A / 'manifest.json').read_text())
for name, digest in manifest['sha256'].items():
    assert hashlib.sha256((A / name).read_bytes()).hexdigest() == digest, name
for table, rows in x.items():
    assert rows == [dict(r) for r in c.execute('select * from "' + table + '"')], table
plan = json.loads((A / 'migration-plan.json').read_text())
dest = json.loads((A / 'destinations.json').read_text())
expected = {r['work_item_id'] for r in x['work_items'] if r['status'] not in ('completed', 'cancelled', 'superseded', 'waived')}
expected |= {r['issue_id'] for r in x['issue_inbox'] if r['state'] == 'pending'}
actual = [s for t in plan['tasks'] for s in t['sources']]
assert expected <= set(actual) and len(actual) == len(set(actual))
assert set(dest) == {t['key'] for t in plan['tasks']}
for task in plan['tasks']:
    assert set(dest[task['key']]['sources']) == set(task['sources'])
    assert task['sources'] and len(task['sources_data']) == len(task['sources'])
    assert dest[task['key']]['destination']
print('PASS: complete archive, unique lossless source coverage, provenance and destinations')
