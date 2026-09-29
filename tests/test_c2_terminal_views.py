from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import c2_master_executor_view as executor_view
import c2_master_watcher_view as watcher_view
import c2_roadmap_status as dashboard


class TerminalViewTests(unittest.TestCase):
    def test_dashboard_live_mode_uses_alternate_screen(self):
        out = StringIO()
        with patch.object(dashboard.sys, "stdout", out):
            dashboard._live_screen_enter()
            dashboard._live_screen_exit()
        value = out.getvalue()
        self.assertIn("\033[?1049h", value)
        self.assertIn("\033[3J", value)
        self.assertIn("\033[?1049l", value)

    def test_executor_shows_only_current_raw_codex_batch(self):
        stream = StringIO(
            "old\n=== C2 Inbox Codex fallback old ===\nold-batch\n"
            "=== C2 Inbox Codex fallback new ===\nnew-batch\n"
        )
        out = StringIO()
        with redirect_stdout(out):
            executor_view.show_current_batch(stream)
        value = out.getvalue()
        self.assertNotIn("old-batch", value)
        self.assertIn("new-batch", value)
        self.assertEqual(stream.tell(), len(stream.getvalue()))

    def test_watchdog_delegated_state_is_plain_language(self):
        state = {"status": "working", "phase": "delegated", "intervention": ""}
        heartbeat = {
            "delegated_worker_alive": True,
            "delegated_worker_progressing": True,
            "delegated_progress_age_s": 30,
        }
        alert = {"active": False}

        def fake_load(path, default):
            if path == watcher_view.STATE:
                return state
            if path == watcher_view.HEARTBEAT:
                return heartbeat
            if path == watcher_view.ALERT:
                return alert
            return default

        with patch.object(watcher_view, "load", side_effect=fake_load), \
             patch.object(watcher_view, "service", side_effect=lambda name: "active" if "watcher" in name else "inactive"), \
             patch.object(watcher_view, "inbox_count", return_value=272):
            text = watcher_view.render()
        self.assertIn("C2 È SANO", text)
        self.assertIn("Master Goal è in pausa intenzionalmente", text)
        self.assertIn("Nessuno.", text)
        self.assertNotIn("WAKE RESULT", text)
        self.assertNotIn("CONFIDENCE", text)


if __name__ == "__main__":
    unittest.main()
