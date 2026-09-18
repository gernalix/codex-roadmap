from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import apply_mutations
import bootstrap_roadmap
import roadmap_db


class SingleWriterEnforcementTests(unittest.TestCase):
    def test_mutating_roadmap_db_cli_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc = roadmap_db.main(
                [
                    "--repo",
                    tmp,
                    "status",
                    "--prompt-id",
                    "123456",
                    "--status",
                    "completed",
                ]
            )
        self.assertEqual(2, rc)

    def test_render_cli_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc = roadmap_db.main(["--repo", tmp, "render"])
        self.assertEqual(2, rc)

    def test_legacy_inbox_writer_requires_explicit_test_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "legacy_direct_inbox_writer_disabled"):
                apply_mutations.apply_inbox(Path(tmp))

    def test_bootstrap_requires_explicit_writer_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "bootstrap_single_writer_only"):
                bootstrap_roadmap.bootstrap(Path(tmp))


if __name__ == "__main__":
    unittest.main()
