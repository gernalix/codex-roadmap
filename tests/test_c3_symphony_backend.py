import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "tools/c3_symphony_backend.py"
spec = importlib.util.spec_from_file_location("c3_symphony_backend", MODULE)
backend = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backend
spec.loader.exec_module(backend)


class BackendTests(unittest.TestCase):
    def test_run_requires_host_credential_and_execs_upstream_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "symphony"
            workflow = root / "WORKFLOW.md"
            binary.write_text("binary")
            workflow.write_text("workflow")
            with self.assertRaisesRegex(backend.BackendError, "systemd_credentials_directory_missing"):
                backend.run(binary, workflow, environ={})
            credential = root / "credentials"
            credential.mkdir()
            (credential / "GITHUB_TOKEN").write_text("test-token\n")
            with patch.object(backend.os, "execve") as execve:
                backend.run(binary, workflow, environ={"CREDENTIALS_DIRECTORY": str(credential)})
            argv = execve.call_args.args
            self.assertEqual(argv[1], [str(binary), str(workflow), "--port", "8765"])
            self.assertEqual(argv[2]["GITHUB_TOKEN"], "test-token")

    def test_status_and_stop_operate_one_unit(self):
        class Result:
            returncode = 0
            stdout = "inactive\n"
        with patch.object(backend.subprocess, "run", return_value=Result()) as command:
            self.assertEqual(backend.status()["active_state"], "inactive")
            self.assertTrue(backend.stop()["stop_requested"])
            self.assertEqual(command.call_args.args[0],
                             ["systemctl", "--user", "stop", backend.UNIT])

    def test_status_returns_only_aggregate_counts(self):
        class Result:
            returncode = 0
            stdout = "active\n"
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, *_):
                return json.dumps({"counts": {"running": 2, "retrying": 1},
                                   "running": [{"secret": "not exposed"}]}).encode()
        with patch.object(backend.subprocess, "run", return_value=Result()), \
             patch.object(backend.urllib.request, "urlopen", return_value=Response()):
            self.assertEqual(backend.status(), {"backend": "symphony",
                             "active_state": "active", "api_healthy": True,
                             "counts": {"running": 2, "retrying": 1}})


if __name__ == "__main__":
    unittest.main()
