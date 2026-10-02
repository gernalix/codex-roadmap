import sys
import tempfile
import unittest
import multiprocessing
import time
import socket
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c3_local_writer import LocalWriter, serve, submit_local
from roadmap_db import RoadmapDBError
from submit_mutation import submit_document, MutationSubmitError


class LocalWriterTests(unittest.TestCase):
    def test_systemd_ready_follows_lock_and_socket_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            mutation_socket = repo / 'writer.sock'
            notification_socket = repo / 'notify.sock'
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as notification:
                notification.bind(str(notification_socket))
                notification.settimeout(5)
                with patch.dict('os.environ', {'NOTIFY_SOCKET':str(notification_socket)}):
                    # Python 3.14's already-running forkserver retains its old
                    # environment; spawn models a fresh systemd process here.
                    process = multiprocessing.get_context('spawn').Process(
                        target=serve, args=(repo, mutation_socket))
                    process.start()
                    try:
                        self.assertEqual(b'READY=1', notification.recv(128))
                        self.assertTrue(mutation_socket.exists())
                        self.assertTrue((repo/'roadmap.sqlite').exists())
                        with self.assertRaises(BlockingIOError):
                            serve(repo, repo/'duplicate.sock')
                    finally:
                        process.terminate()
                        process.join(5)

    def document(self, prompt_id='123456'):
        return {'schema': 'codex-roadmap.mutation.v1', 'actor': 'test', 'operations': [
            {'op': 'register', 'prompt_id': prompt_id, 'slug': 'test-' + prompt_id,
             'title': 'Test', 'current_path': 'prompts/test-' + prompt_id + '.md',
             'prompt_text': 'PROMPT_ID=' + prompt_id + '\nTest'}]}

    def test_replay_collision_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = LocalWriter(Path(directory))
            try:
                first = writer.apply(self.document(), 'first')
                self.assertEqual(first['submission'], 'applied')
                self.assertTrue(writer.apply(self.document(), 'first')['idempotent'])
                with self.assertRaisesRegex(ValueError, 'request_key_conflict'):
                    writer.apply(self.document('123457'), 'first')
                document = self.document('123458')
                document['operations'].append({'op': 'invalid'})
                with self.assertRaises(RoadmapDBError):
                    writer.apply(document, 'rollback')
                self.assertIsNone(writer.conn.execute("SELECT prompt_id FROM prompts WHERE prompt_id='123458'").fetchone())
                self.assertEqual(writer.conn.execute('SELECT COUNT(*) FROM mutation_receipts').fetchone()[0], 1)
                self.assertEqual(writer.conn.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
                self.assertLess(int(first['issue_number']), 0)
            finally:
                writer.close()

    def test_socket_transport_and_single_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            socket_path = repo / 'writer.sock'
            process = multiprocessing.Process(target=serve, args=(repo, socket_path))
            process.start()
            try:
                deadline = time.monotonic() + 5
                while not socket_path.exists() and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(socket_path.exists())
                result = submit_local(self.document(), request_key='socket-test', socket_path=socket_path)
                self.assertEqual(result['submission'], 'applied')
                self.assertTrue(submit_local(self.document(), request_key='socket-test', socket_path=socket_path)['idempotent'])
                with patch.dict('os.environ', {'C3_MUTATION_TRANSPORT': 'local', 'C3_WRITER_SOCKET': str(socket_path)}), patch('submit_mutation._gh', side_effect=AssertionError('GitHub must not be contacted')):
                    self.assertTrue(submit_document(self.document(), request_key='socket-test')['idempotent'])
                    with self.assertRaises(MutationSubmitError):
                        submit_document(self.document('123457'), request_key='socket-test')
                with self.assertRaisesRegex(ValueError, 'request_key_conflict'):
                    submit_local(self.document('123457'), request_key='socket-test', socket_path=socket_path)
                with self.assertRaises(BlockingIOError):
                    serve(repo, repo / 'second.sock')
            finally:
                process.terminate()
                process.join(5)

    def test_receipt_survives_restart_and_local_ids_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = LocalWriter(Path(directory))
            first = writer.apply(self.document(), 'first')
            writer.close()
            writer = LocalWriter(Path(directory))
            try:
                self.assertTrue(writer.apply(self.document(), 'first')['idempotent'])
                second = writer.apply(self.document('123457'), 'second')
                self.assertNotEqual(first['issue_number'], second['issue_number'])
            finally:
                writer.close()
