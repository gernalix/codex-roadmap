import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from codex_human_tail import colorize, extract_human_message, relative_age, render, select_session, wrap_text, HumanMessage


class CodexHumanTailTests(unittest.TestCase):
    def test_relative_age(self):
        now = datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc)
        self.assertEqual("adesso", relative_age(datetime(2026, 9, 28, 0, 29, 31, tzinfo=timezone.utc), now))
        self.assertEqual("3 min fa", relative_age(datetime(2026, 9, 28, 0, 27, tzinfo=timezone.utc), now))
        self.assertEqual("2 h 5 min fa", relative_age(datetime(2026, 9, 27, 22, 25, tzinfo=timezone.utc), now))
        self.assertEqual("1 g 2 h fa", relative_age(datetime(2026, 9, 26, 22, 30, tzinfo=timezone.utc), now))

    def test_only_assistant_output_text_is_human(self):
        good = {
            "timestamp": "2026-09-27T22:15:57Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Messaggio umano"}],
            },
        }
        self.assertEqual("Messaggio umano", extract_human_message(good).text)
        noisy = [
            {"timestamp": good["timestamp"], "type": "response_item",
             "payload": {"type": "message", "role": "user",
                         "content": [{"type": "input_text", "text": "utente"}]}},
            {"timestamp": good["timestamp"], "type": "response_item",
             "payload": {"type": "agent_message", "content": [{"type": "input_text", "text": "subagent"}]}},
            {"timestamp": good["timestamp"], "type": "response_item",
             "payload": {"type": "function_call", "name": "exec"}},
            {"timestamp": good["timestamp"], "type": "event_msg",
             "payload": {"type": "token_count"}},
        ]
        self.assertTrue(all(extract_human_message(item) is None for item in noisy))

    def test_wrap_never_splits_normal_words(self):
        lines = wrap_text("Questa parola lunghissima_non_va_spezzata e il resto continua", 18)
        self.assertIn("lunghissima_non_va_spezzata", lines)
        self.assertNotIn("lunghissima_non_va_", lines)

    def test_render_wraps_on_words_with_indented_continuations(self):
        message = HumanMessage(
            timestamp=datetime(2026, 9, 28, 0, 27, tzinfo=timezone.utc),
            text="uno due tre quattro cinque sei sette otto nove dieci",
        )
        rendered = render(message, now=datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), width=36, color=False)
        lines = rendered.splitlines()
        self.assertGreater(len(lines), 1)
        self.assertTrue(lines[0].startswith("    3 min fa │ "))
        self.assertTrue(all(line.startswith(" " * 15) for line in lines[1:]))
        self.assertFalse(any(line.rstrip().endswith(("quat", "cin", "sett")) for line in lines))

    def test_colorize_matches_codex_like_inline_emphasis(self):
        styled = colorize("Stato `BLOCKED`, file `roadmap_start.py`, path /root/worker e https://example.test/x")
        self.assertIn("\x1b[32m`BLOCKED`\x1b[0m", styled)
        self.assertIn("\x1b[32m`roadmap_start.py`\x1b[0m", styled)
        self.assertIn("\x1b[36m/root/worker\x1b[0m", styled)
        self.assertIn("\x1b[36mhttps://example.test/x\x1b[0m", styled)

    def test_auto_selection_prefers_latest_root_tui(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / "old.jsonl"
            child = root / "child.jsonl"
            latest = root / "latest.jsonl"

            def write_meta(path, *, originator, thread_source):
                path.write_text(json.dumps({
                    "type": "session_meta",
                    "payload": {"originator": originator, "thread_source": thread_source}
                }) + "\n", encoding="utf-8")
            write_meta(old, originator="codex-tui", thread_source="user")
            write_meta(child, originator="codex-tui", thread_source="subagent")
            write_meta(latest, originator="codex-tui", thread_source="user")

            old.touch()
            child.touch()
            latest.touch()

            import os
            os.utime(old, (10, 10))
            os.utime(child, (30, 30))
            os.utime(latest, (20, 20))

            self.assertEqual(latest.resolve(), select_session(root))


if __name__ == "__main__":
    unittest.main()
