from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from roadmap_render import _effective_outcome


class EffectiveOutcomeTests(unittest.TestCase):
    def test_terminal_status_wins_over_stale_execution(self) -> None:
        self.assertEqual(
            "PASS",
            _effective_outcome({"status": "completed", "last_outcome": "BLOCKED"}),
        )
        self.assertEqual(
            "BLOCKED",
            _effective_outcome({"status": "blocked", "last_outcome": "PASS"}),
        )

    def test_active_prompt_uses_execution_outcome(self) -> None:
        self.assertEqual(
            "BLOCKED",
            _effective_outcome({"status": "running", "last_outcome": "BLOCKED"}),
        )


if __name__ == "__main__":
    unittest.main()
