#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import select
import shutil
import sys
import termios
import textwrap
import time
import tty
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT = Path.home() / ".codex" / "sessions"

ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_CYAN = "\033[36m"
ANSI_DIM = "\033[2m"
ANSI_BOLD = "\033[1m"
ANSI_AMBER = "\033[38;5;214m"
ANSI_FOCUS_ON = "\033[?1004h"
ANSI_FOCUS_OFF = "\033[?1004l"
ANSI_CLEAR = "\033[2J\033[H"
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
ROOT_PATH_RE = re.compile(r"(?<![\w`])(/root/[A-Za-z0-9_./-]+)")
URL_RE = re.compile(r"(?<![\w`])(https?://\S+)")


@dataclass(frozen=True)
class HumanMessage:
    timestamp: datetime
    text: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.timestamp.isoformat(), self.text)


@dataclass
class UnreadState:
    focused: bool = True
    unread_mode: bool = False
    focus_since: float | None = None
    last_unread_at: float | None = None
    unread: set[tuple[str, str]] | None = None

    def __post_init__(self) -> None:
        if self.unread is None:
            self.unread = set()

    def focus_out(self) -> None:
        self.focused = False
        self.focus_since = None
        self.unread_mode = True

    def focus_in(self, now: float) -> None:
        self.focused = True
        self.focus_since = now

    def mark_message(self, message: HumanMessage, now: float | None = None) -> None:
        if self.unread_mode:
            self.unread.add(message.key)
            self.last_unread_at = time.monotonic() if now is None else now

    def maybe_clear_after_dwell(self, now: float, threshold: float) -> bool:
        if not self.focused or not self.unread_mode or self.focus_since is None:
            return False
        dwell_start = self.focus_since
        if self.last_unread_at is not None:
            dwell_start = max(dwell_start, self.last_unread_at)
        if now - dwell_start < threshold:
            return False
        self.unread.clear()
        self.unread_mode = False
        self.focus_since = now
        self.last_unread_at = None
        return True

    def mark_all_read(self) -> None:
        self.unread.clear()
        self.unread_mode = not self.focused
        self.last_unread_at = None
        if self.focused:
            self.focus_since = time.monotonic()


def parse_timestamp(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def relative_age(then: datetime, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    seconds = max(0, int((now - then.astimezone(timezone.utc)).total_seconds()))
    if seconds < 60:
        return "adesso"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min fa"
    hours, rem_minutes = divmod(minutes, 60)
    if hours < 24:
        if rem_minutes:
            return f"{hours} h {rem_minutes} min fa"
        return f"{hours} h fa"
    days, rem_hours = divmod(hours, 24)
    if rem_hours:
        return f"{days} g {rem_hours} h fa"
    return f"{days} g fa"


def extract_human_message(obj: dict) -> HumanMessage | None:
    if obj.get("type") != "response_item":
        return None
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return None
    if payload.get("type") != "message" or payload.get("role") != "assistant":
        return None
    content = payload.get("content")
    if not isinstance(content, list):
        return None
    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "output_text":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    if not parts:
        return None
    stamp = obj.get("timestamp")
    if not isinstance(stamp, str):
        return None
    try:
        timestamp = parse_timestamp(stamp)
    except ValueError:
        return None
    return HumanMessage(timestamp=timestamp, text="\n".join(parts))


def session_meta(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "session_meta" and isinstance(obj.get("payload"), dict):
                    return obj["payload"]
                if obj.get("type") not in {"session_meta", "response_item"}:
                    break
    except OSError:
        pass
    return {}


def root_tui_candidate(path: Path) -> bool:
    meta = session_meta(path)
    return meta.get("originator") == "codex-tui" and meta.get("thread_source") == "user"
def select_session(root: Path, explicit: str | None = None) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file():
            return candidate.resolve()
        matches = list(root.rglob(f"*{explicit}*.jsonl"))
        if len(matches) == 1:
            return matches[0].resolve()
        if not matches:
            raise SystemExit(f"Sessione Codex non trovata: {explicit}")
        raise SystemExit(f"Sessione ambigua: {explicit} ({len(matches)} match)")

    paths = [p for p in root.rglob("*.jsonl") if root_tui_candidate(p)]
    if not paths:
        raise SystemExit(f"Nessuna sessione Codex TUI trovata in {root}")
    paths.sort(key=lambda p: (p.stat().st_mtime_ns, str(p)), reverse=True)
    return paths[0].resolve()


def iter_messages(path: Path) -> Iterable[HumanMessage]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = extract_human_message(obj)
            if message:
                yield message
def colorize(text: str) -> str:
    # Codex TUI-like emphasis: inline code/state names green, paths/URLs cyan.
    protected: list[str] = []

    def protect_code(match: re.Match[str]) -> str:
        token = f"\x00CODE{len(protected)}\x00"
        protected.append(f"{ANSI_GREEN}`{match.group(1)}`{ANSI_RESET}")
        return token

    text = INLINE_CODE_RE.sub(protect_code, text)
    text = URL_RE.sub(lambda m: f"{ANSI_CYAN}{m.group(1)}{ANSI_RESET}", text)
    text = ROOT_PATH_RE.sub(lambda m: f"{ANSI_CYAN}{m.group(1)}{ANSI_RESET}", text)
    for index, styled in enumerate(protected):
        text = text.replace(f"\x00CODE{index}\x00", styled)
    return text


def wrap_text(text: str, width: int) -> list[str]:
    output: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph.strip():
            output.append("")
            continue
        wrapped = textwrap.wrap(
            paragraph,
            width=max(1, width),
            break_long_words=False,
            break_on_hyphens=False,
            replace_whitespace=False,
            drop_whitespace=True,
        )
        output.extend(wrapped or [""])
    return output


def render(
    message: HumanMessage,
    now: datetime | None = None,
    *,
    width: int | None = None,
    color: bool = True,
    unread: bool = False,
) -> str:
    label = relative_age(message.timestamp, now=now)
    plain_prefix = f"{'●  ' if unread else ''}{label:>12} │ "
    prefix = plain_prefix
    if unread and color:
        prefix = f"{ANSI_AMBER}{ANSI_BOLD}●  {label:>12} │{ANSI_RESET} "
    if unread:
        gutter_plain = " " * (len(plain_prefix) - 2) + "┃ "
        continuation = (
            " " * (len(plain_prefix) - 2) + f"{ANSI_AMBER}{ANSI_BOLD}┃{ANSI_RESET} "
            if color else gutter_plain
        )
    else:
        continuation = " " * len(plain_prefix)
    terminal_width = width or shutil.get_terminal_size(fallback=(120, 24)).columns
    content_width = max(20, terminal_width - len(plain_prefix) - 1)
    lines = wrap_text(message.text, content_width)
    if color:
        lines = [colorize(line) for line in lines]
    return "\n".join(
        (prefix if index == 0 else continuation) + line
        for index, line in enumerate(lines)
    )


def _read_input(fd: int, buffer: bytes) -> tuple[list[str], bytes]:
    events: list[str] = []
    try:
        chunk = os.read(fd, 1024)
    except BlockingIOError:
        return events, buffer
    buffer += chunk
    while buffer:
        if buffer.startswith(b"\x1b[I"):
            events.append("focus_in")
            buffer = buffer[3:]
        elif buffer.startswith(b"\x1b[O"):
            events.append("focus_out")
            buffer = buffer[3:]
        elif buffer[:1] in {b"r", b"R"}:
            events.append("mark_read")
            buffer = buffer[1:]
        elif buffer[:1] in {b"q", b"Q", b"\x03"}:
            events.append("quit")
            buffer = buffer[1:]
        elif buffer.startswith(b"\x1b") and len(buffer) < 3:
            break
        else:
            buffer = buffer[1:]
    return events, buffer


def _status_line(state: UnreadState, read_after: float, color: bool, now: float | None = None) -> str:
    count = len(state.unread or ())
    if count:
        if state.focused and state.focus_since is not None:
            now = time.monotonic() if now is None else now
            dwell_start = state.focus_since
            if state.last_unread_at is not None:
                dwell_start = max(dwell_start, state.last_unread_at)
            remaining = max(0, int(read_after - (now - dwell_start) + 0.999))
            focus = f"letti tra {remaining}s se resti qui"
        else:
            focus = "fuori focus"
        text = f"● {count} non lett{'o' if count == 1 else 'i'} · {focus} · r segna letti · q esci"
        return f"{ANSI_AMBER}{ANSI_BOLD}{text}{ANSI_RESET}" if color else text
    return "r segna letti · q esci"


def _redraw(path: Path, messages: list[HumanMessage], state: UnreadState, read_after: float, color: bool, *, now_mono: float | None = None) -> None:
    print(ANSI_CLEAR, end="")
    header = f"Codex human view · {path.stem}"
    print(f"{ANSI_DIM}{header}{ANSI_RESET}" if color else header)
    print(_status_line(state, read_after, color, now=now_mono))
    print()
    for message in messages:
        print(render(message, color=color, unread=message.key in (state.unread or set())))
        print()
    sys.stdout.flush()


def follow(path: Path, history: int, poll: float, *, color: bool = True, read_after: float = 20.0) -> None:
    messages = list(iter_messages(path))[-history:]
    state = UnreadState(focused=True, focus_since=time.monotonic())
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    fd = sys.stdin.fileno() if interactive else -1
    old_termios = termios.tcgetattr(fd) if interactive else None
    input_buffer = b""

    if interactive:
        tty.setcbreak(fd)
        os.set_blocking(fd, False)
        print(ANSI_FOCUS_ON, end="")
    _redraw(path, messages, state, read_after, color)
    age_signature = tuple(relative_age(message.timestamp) for message in messages)
    last_status_tick = int(time.monotonic()) if state.unread else None

    offset = path.stat().st_size
    pending = ""
    try:
        while True:
            now_mono = time.monotonic()
            redraw = False
            if interactive:
                ready, _, _ = select.select([fd], [], [], 0)
                if ready:
                    events, input_buffer = _read_input(fd, input_buffer)
                    for event in events:
                        if event == "focus_out":
                            state.focus_out()
                        elif event == "focus_in":
                            state.focus_in(now_mono)
                        elif event == "mark_read":
                            state.mark_all_read()
                        elif event == "quit":
                            return
                        redraw = True

            if state.maybe_clear_after_dwell(now_mono, read_after):
                redraw = True

            try:
                size = path.stat().st_size
            except FileNotFoundError:
                time.sleep(poll)
                continue
            if size < offset:
                offset = 0
                pending = ""
            if size > offset:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    handle.seek(offset)
                    chunk = handle.read()
                    offset = handle.tell()
                pending += chunk
                lines = pending.split("\n")
                pending = lines.pop()
                for line in lines:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    message = extract_human_message(obj)
                    if message:
                        state.mark_message(message, now=now_mono)
                        messages.append(message)
                        messages = messages[-200:]
                        redraw = True
            current_age_signature = tuple(relative_age(message.timestamp) for message in messages)
            if current_age_signature != age_signature:
                age_signature = current_age_signature
                redraw = True

            status_tick = int(now_mono) if state.focused and state.unread else None
            if status_tick != last_status_tick:
                last_status_tick = status_tick
                redraw = True
            if redraw:
                _redraw(path, messages, state, read_after, color, now_mono=now_mono)
            time.sleep(poll)
    except KeyboardInterrupt:
        return
    finally:
        if interactive:
            print(ANSI_FOCUS_OFF, end="", flush=True)
            if old_termios is not None:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_termios)
            os.set_blocking(fd, True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vista live read-only dei soli messaggi umani di Codex CLI."
    )
    parser.add_argument("--source-root", default=str(DEFAULT_ROOT))
    parser.add_argument("--session", help="Path o UUID/parziale della sessione da seguire.")
    parser.add_argument("--history", type=int, default=8, help="Messaggi precedenti da mostrare.")
    parser.add_argument("--poll", type=float, default=0.25, help="Intervallo di polling in secondi.")
    parser.add_argument("--read-after", type=float, default=20.0, metavar="SECONDS", help="Secondi continui in focus prima di segnare i non letti come letti (default: 20).")
    parser.add_argument("--once", action="store_true", help="Stampa lo storico e termina.")
    args = parser.parse_args(argv)

    root = Path(args.source_root).expanduser()
    path = select_session(root, args.session)
    use_color = os.isatty(sys.stdout.fileno()) and os.environ.get("NO_COLOR") is None
    if os.isatty(sys.stdout.fileno()):
        header = f"Codex human view · {path.stem}"
        print(f"{ANSI_DIM}{header}{ANSI_RESET}\n" if use_color else f"{header}\n")
    if args.once:
        for message in list(iter_messages(path))[-args.history:]:
            print(render(message, color=use_color))
            print()
        return 0
    follow(path, max(0, args.history), max(0.05, args.poll), color=use_color, read_after=max(0.0, args.read_after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
