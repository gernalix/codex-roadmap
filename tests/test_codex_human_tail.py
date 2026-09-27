import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from codex_human_tail import UnreadState, _read_input, colorize, extract_human_message, relative_age, render, select_session, wrap_text, HumanMessage


def _read_input_bytes_for_test(data: bytes):
    import os
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, data)
        os.close(write_fd)
        write_fd = -1
        return _read_input(read_fd, b"")
    finally:
        os.close(read_fd)
        if write_fd >= 0:
            os.close(write_fd)



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

    def test_unread_state_requires_continuous_focus_dwell(self):
        state = UnreadState(focused=True, focus_since=0.0)
        message = HumanMessage(datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), "nuovo")
        state.focus_out()
        state.mark_message(message, now=0.0)
        self.assertIn(message.key, state.unread)
        state.focus_in(10.0)
        self.assertFalse(state.maybe_clear_after_dwell(29.9, 20.0))
        state.focus_out()
        state.focus_in(40.0)
        self.assertFalse(state.maybe_clear_after_dwell(59.9, 20.0))
        self.assertTrue(state.maybe_clear_after_dwell(60.0, 20.0))
        self.assertFalse(state.unread_mode)
        self.assertEqual(set(), state.unread)

    def test_late_unread_message_restarts_read_dwell(self):
        state = UnreadState(focused=True, focus_since=10.0)
        state.unread_mode = True
        message = HumanMessage(datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), "arriva tardi")
        state.mark_message(message, now=29.5)
        self.assertFalse(state.maybe_clear_after_dwell(30.0, 20.0))
        self.assertFalse(state.maybe_clear_after_dwell(49.4, 20.0))
        self.assertTrue(state.maybe_clear_after_dwell(49.5, 20.0))

    def test_messages_arriving_during_short_focus_remain_unread(self):
        state = UnreadState(focused=True, focus_since=0.0)
        first = HumanMessage(datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), "primo")
        second = HumanMessage(datetime(2026, 9, 28, 0, 31, tzinfo=timezone.utc), "secondo")
        state.focus_out()
        state.mark_message(first)
        state.focus_in(10.0)
        state.mark_message(second)
        self.assertEqual({first.key, second.key}, state.unread)

    def test_manual_mark_read_and_future_unfocused_message(self):
        state = UnreadState(focused=False, unread_mode=True)
        first = HumanMessage(datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), "primo")
        second = HumanMessage(datetime(2026, 9, 28, 0, 31, tzinfo=timezone.utc), "secondo")
        state.mark_message(first)
        state.mark_all_read()
        self.assertEqual(set(), state.unread)
        self.assertTrue(state.unread_mode)
        state.mark_message(second)
        self.assertIn(second.key, state.unread)

    def test_focus_input_parser_and_manual_shortcut(self):
        events, pending = _read_input_bytes_for_test(b"\x1b[Or\x1b[Iq")
        self.assertEqual(["focus_out", "mark_read", "focus_in", "quit"], events)
        self.assertEqual(b"", pending)

    def test_unread_render_has_evident_marker(self):
        message = HumanMessage(datetime(2026, 9, 28, 0, 27, tzinfo=timezone.utc), "testo")
        rendered = render(message, now=datetime(2026, 9, 28, 0, 30, tzinfo=timezone.utc), width=80, color=False, unread=True)
        self.assertTrue(rendered.startswith("●      3 min fa │ "))

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
