from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import import_codex_usage as importer


class ImportTests(unittest.TestCase):
    def test_legacy_importer_delegates_to_remote_single_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            source = base / "usage"
            repo.mkdir()
            source.mkdir()
            sentinel = repo / "sentinel.txt"
            sentinel.write_text("unchanged", encoding="utf-8")

            with patch.object(
                importer,
                "sync",
                return_value={"status": "ok", "queued": 1},
            ) as sync:
                out = importer.import_metrics(repo, source, render_after=False)

            self.assertEqual({"status": "ok", "queued": 1}, out)
            sync.assert_called_once_with(
                repo,
                source,
                repository=importer.DEFAULT_REMOTE_REPO,
                branch=importer.DEFAULT_REMOTE_BRANCH,
            )
            self.assertEqual("unchanged", sentinel.read_text(encoding="utf-8"))
            self.assertFalse((repo / "roadmap.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
