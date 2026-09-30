import importlib.util
import hashlib
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
            workflow.write_text('---\n{"tracker":{"provider":{"repo":"gernalix/symphony-canary"}},"server":{"host":"127.0.0.1"}}\n---\n')
            with patch.object(backend, "load_config", return_value=backend.load_config.__globals__["HostConfig"](
                    "canary", "gernalix/symphony-canary", frozenset({"gernalix/codex-roadmap"}))):
                with self.assertRaisesRegex(backend.BackendError, "systemd_credentials_directory_missing"):
                    backend.run(binary, workflow, environ={})
            credential = root / "credentials"
            credential.mkdir()
            (credential / "GITHUB_TOKEN").write_text("test-token\n")
            with patch.object(backend, "load_config", return_value=backend.load_config.__globals__["HostConfig"](
                    "canary", "gernalix/symphony-canary", frozenset({"gernalix/codex-roadmap"}))), \
                 patch.object(backend.os, "execve") as execve:
                backend.run(binary, workflow, environ={"CREDENTIALS_DIRECTORY": str(credential)})
            argv = execve.call_args.args
            self.assertEqual(argv[1], [str(binary),
                             "--i-understand-that-this-will-be-running-without-the-usual-guardrails",
                             str(workflow), "--port", backend.PORT])
            self.assertEqual(argv[2]["GITHUB_TOKEN"], "test-token")

    def test_status_and_stop_operate_one_unit(self):
        class Result:
            returncode = 0
            stdout = "inactive\n"
        with patch.object(backend, "load_config", return_value=backend.load_config.__globals__["HostConfig"](
                "canary", "gernalix/symphony-canary", frozenset({"gernalix/codex-roadmap"}))), \
             patch.object(backend, "DEFAULT_CONFIG", MODULE), \
             patch.object(backend, "user_bus_environment", return_value={}), \
             patch.object(backend.subprocess, "run", return_value=Result()) as command:
            self.assertEqual(backend.status()["active_state"], "inactive")
            self.assertTrue(backend.stop()["stop_requested"])
            self.assertEqual(command.call_args.args[0],
                             ["systemctl", "--user", "stop", backend.UNIT])

    def test_publish_passes_decrypted_credential_only_to_host_bridge(self):
        with tempfile.TemporaryDirectory() as directory:
            credential = Path(directory) / "credentials"
            credential.mkdir()
            (credential / "GITHUB_TOKEN").write_text("test-token\n")
            db = Path(directory) / "roadmap.sqlite"
            with patch.object(backend.os, "execve") as execve:
                backend.publish(db, "wi:" + "a" * 32,
                                environ={"CREDENTIALS_DIRECTORY": str(credential)})
            argv = execve.call_args.args
            self.assertIn("c3_symphony_bridge.py", argv[1][1])
            self.assertEqual(argv[2]["GITHUB_TOKEN"], "test-token")

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
        with patch.object(backend, "load_config", return_value=backend.load_config.__globals__["HostConfig"](
                "canary", "gernalix/symphony-canary", frozenset({"gernalix/codex-roadmap"}))), \
             patch.object(backend, "DEFAULT_CONFIG", MODULE), \
             patch.object(backend, "user_bus_environment", return_value={}), \
             patch.object(backend.subprocess, "run", return_value=Result()), \
             patch.object(backend.urllib.request, "urlopen", return_value=Response()):
            self.assertEqual(backend.status(), {"backend": "symphony",
                             "mode": "canary", "active_state": "active", "api_healthy": True,
                             "counts": {"running": 2, "retrying": 1}})

    def test_user_bus_fallback_and_missing_bus_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            with patch.object(backend.os, "getuid", return_value=1000), \
                 patch.object(backend.Path, "is_socket", return_value=True):
                env = backend.user_bus_environment({"XDG_RUNTIME_DIR": str(runtime)})
            self.assertEqual(env["DBUS_SESSION_BUS_ADDRESS"], f"unix:path={runtime}/bus")
            with patch.object(backend.os, "getuid", return_value=1000), \
                 patch.object(backend.Path, "is_dir", return_value=True), \
                 patch.object(backend.Path, "is_socket", return_value=True):
                fallback = backend.user_bus_environment({})
            self.assertEqual(fallback["XDG_RUNTIME_DIR"], "/run/user/1000")
            self.assertEqual(fallback["DBUS_SESSION_BUS_ADDRESS"], "unix:path=/run/user/1000/bus")
            with self.assertRaisesRegex(backend.BackendError, "user_runtime_directory_missing"):
                backend.user_bus_environment({"XDG_RUNTIME_DIR": str(runtime/"missing")})

    def test_production_artifact_path_and_hash_are_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory)/"symphony"
            binary.write_bytes(b"approved artifact")
            binary.chmod(0o755)
            with patch.object(backend, "PRODUCTION_BINARY", binary), \
                 patch.object(backend, "PRODUCTION_SHA256", hashlib.sha256(binary.read_bytes()).hexdigest()):
                backend.verify_artifact(binary)
                with self.assertRaisesRegex(backend.BackendError, "production_artifact_path_invalid"):
                    backend.verify_artifact(Path(directory)/"pilot")
                binary.write_bytes(b"drift")
                with self.assertRaisesRegex(backend.BackendError, "production_artifact_hash_mismatch"):
                    backend.verify_artifact(binary)


if __name__ == "__main__":
    unittest.main()
