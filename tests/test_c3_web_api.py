from contextlib import closing
from pathlib import Path
import json
import sys
import tempfile
import threading
import unittest
from unittest import mock
import urllib.request
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import c2_intake
import c2_scheduler
import c3_api
import c3_override
import apply_issue_mutation
import test_c2_intake


class WebApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.path = test_c2_intake.C2IntakeTests().make_cutover_db(self.root)
        with closing(c2_intake._connect(self.path)) as conn:
            c2_scheduler.install_schema(conn)
            c3_override.install_schema(conn)
            conn.commit()
            conn.execute('BEGIN IMMEDIATE')
            self.a = c2_intake.add_work_item(conn, title='Web batch', kind='goal')['work_item_id']
            self.b = c2_intake.add_work_item(conn, title='Dependent task', parent_id=self.a)['work_item_id']
            conn.execute('INSERT INTO work_item_dependencies VALUES(?,?,1,NULL)', (self.b, self.a))
            conn.commit()
        self.control = c3_api.Control(self.root, self.path)
        self.server = c3_api.serve(self.control, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)
        self.issue = 0

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def request(self, path, body=None, *, intent=True):
        headers = {'Origin': self.base, 'Content-Type': 'application/json'}
        if intent:
            headers['X-C3-Intent'] = 'explicit-user'
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.load(response)

    def writer(self, document, *, request_key):
        self.issue += 1
        event = self.root / 'event.json'
        event.write_text(json.dumps({'issue': {'number': self.issue, 'title': '[roadmap-mutation] ' + request_key, 'body': json.dumps(document)}}))
        apply_issue_mutation.apply_issue(self.path.parent, event, render_views=False)
        return {'issue_number': str(self.issue), 'request_key': request_key}

    def action(self, wid, action, **extra):
        _, preview = self.request('/api/preview', {'work_item_id': wid, 'action': action})
        args = {**preview, 'request_id': 'web-' + action, **extra}
        with mock.patch.object(c3_api, 'submit_document', side_effect=self.writer), mock.patch.object(c3_api, '_wait_issue_applied'):
            return self.request('/api/override', args)[1]

    def test_http_real_writer_pause_resume_and_live_refresh(self):
        result = self.action(self.a, 'pause')
        self.assertTrue(next(i for i in result['state']['items'] if i['work_item_id'] == self.b)['paused'])
        self.action(self.a, 'resume')
        state = self.request('/api/state')[1]
        self.assertFalse(next(i for i in state['items'] if i['work_item_id'] == self.a)['paused'])
        self.assertEqual(2, len(state['events']))

    def test_delete_confirmation_and_history_preservation(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.action(self.a, 'delete', confirmed_affected=[self.a])
        self.assertEqual(409, error.exception.code)
        error.exception.close()
        result = self.action(self.a, 'delete', confirmed_affected=sorted([self.a, self.b]))
        self.assertFalse(any(i['work_item_id'] in (self.a, self.b) for i in result['state']['items']))
        with closing(self.control.connect()) as conn:
            self.assertEqual(2, conn.execute('SELECT COUNT(*) FROM work_items WHERE work_item_id IN (?,?)', (self.a, self.b)).fetchone()[0])

    def test_http_reorder_warning_and_stale_preview(self):
        # Root dependency constrains the protocol move, not merely UI rendering.
        with closing(c2_intake._connect(self.path)) as conn:
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('UPDATE work_items SET parent_id=NULL WHERE work_item_id=?', (self.b,))
            conn.commit()
        result = self.action(self.b, 'move', position=0)
        self.assertIn(self.a, result['result']['blocking_prerequisites'])
        self.assertGreater(result['result']['applied_position'], 0)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/api/override', {'work_item_id': self.a, 'action': 'pause', 'precondition': 'stale', 'request_id': 'stale'})
        self.assertEqual(409, error.exception.code)
        error.exception.close()

    def test_same_origin_intent_required_and_unknown_route(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/api/preview', {'work_item_id': self.a, 'action': 'pause'}, intent=False)
        self.assertEqual(403, error.exception.code)
        error.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/missing')
        self.assertEqual(404, error.exception.code)
        error.exception.close()

    def test_writer_failure_is_error_not_optimistic_success(self):
        _, plan = self.request('/api/preview', {'work_item_id': self.a, 'action': 'pause'})
        with mock.patch.object(c3_api, 'submit_document', side_effect=RuntimeError('writer unavailable')):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.request('/api/override', {**plan, 'request_id': 'failure'})
        self.assertEqual(503, error.exception.code)
        self.assertIn('writer unavailable', error.exception.read().decode())
        error.exception.close()
        self.assertFalse(next(i for i in self.request('/api/state')[1]['items'] if i['work_item_id'] == self.a)['paused'])

    def test_static_production_ui(self):
        with urllib.request.urlopen(self.base) as response:
            self.assertEqual(200, response.status)
            self.assertIn(b'C3 Control', response.read())
            self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])


if __name__ == '__main__':
    unittest.main()
