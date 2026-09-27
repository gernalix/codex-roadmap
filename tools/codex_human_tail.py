#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import queue
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

from codex_human_companion import AIWorker, ViewerDB, DEFAULT_DB, DEFAULT_MODEL, DEFAULT_REASONING

DEFAULT_ROOT = Path.home() / ".codex" / "sessions"

ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_CYAN = "\033[36m"
ANSI_DIM = "\033[2m"
ANSI_BOLD = "\033[1m"
ANSI_AMBER = "\033[38;5;214m"
ANSI_MAGENTA = "\033[35m"
ANSI_REVERSE = "\033[7m"
ANSI_FOCUS_ON = "\033[?1004h"
ANSI_FOCUS_OFF = "\033[?1004l"
ANSI_CLEAR = "\033[2J\033[H"
ANSI_HOME = "\033[H"
ANSI_ERASE_DOWN = "\033[J"
ANSI_SYNC_ON = "\033[?2026h"
ANSI_SYNC_OFF = "\033[?2026l"
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


@dataclass
class ExplainState:
    active: bool = False
    cursor: int | None = None
    anchor: int | None = None
    selected: set[int] | None = None
    pending_label: str | None = None

    def __post_init__(self) -> None:
        if self.selected is None:
            self.selected = set()

    def enter(self, count: int) -> None:
        self.active = bool(count)
        self.cursor = count - 1 if count else None
        self.anchor = self.cursor
        self.selected.clear()

    def cancel(self) -> None:
        self.active = False
        self.cursor = None
        self.anchor = None
        self.selected.clear()

    def move(self, delta: int, count: int, *, extend: bool = False) -> None:
        if not self.active or not count:
            return
        if self.cursor is None:
            self.cursor = count - 1
        old = self.cursor
        self.cursor = max(0, min(count - 1, self.cursor + delta))
        if extend:
            if self.anchor is None:
                self.anchor = old
            lo, hi = sorted((self.anchor, self.cursor))
            self.selected.update(range(lo, hi + 1))
        else:
            self.anchor = self.cursor

    def toggle_current(self) -> None:
        if self.cursor is None:
            return
        if self.cursor in self.selected:
            self.selected.remove(self.cursor)
        else:
            self.selected.add(self.cursor)

    def targets(self) -> list[int]:
        if self.selected:
            return sorted(self.selected)
        return [self.cursor] if self.cursor is not None else []


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
        if buffer.startswith(b"\x1b[1;2A"):
            events.append("select_extend_up")
            buffer = buffer[6:]
        elif buffer.startswith(b"\x1b[1;2B"):
            events.append("select_extend_down")
            buffer = buffer[6:]
        elif buffer.startswith(b"\x1b[A"):
            events.append("select_up")
            buffer = buffer[3:]
        elif buffer.startswith(b"\x1b[B"):
            events.append("select_down")
            buffer = buffer[3:]
        elif buffer.startswith(b"\x1b[I"):
            events.append("focus_in")
            buffer = buffer[3:]
        elif buffer.startswith(b"\x1b[O"):
            events.append("focus_out")
            buffer = buffer[3:]
        elif buffer[:1] == b"\x1b":
            if len(buffer) == 1:
                events.append("escape")
                buffer = b""
            elif len(buffer) < 3:
                break
            else:
                buffer = buffer[1:]
        elif buffer[:1] in {b"\r", b"\n"}:
            events.append("select_explain")
            buffer = buffer[1:]
        elif buffer[:1] == b" ":
            events.append("select_toggle")
            buffer = buffer[1:]
        elif buffer[:1] == b"e":
            events.append("explain_mode")
            buffer = buffer[1:]
        elif buffer[:1] == b"E":
            events.append("explain_all")
            buffer = buffer[1:]
        elif buffer[:1] in {b"w", b"W"}:
            events.append("companion_toggle")
            buffer = buffer[1:]
        elif buffer[:1] in b"123456789":
            events.append("select_digit:" + buffer[:1].decode())
            buffer = buffer[1:]
        elif buffer[:1] in {b"r", b"R"}:
            events.append("mark_read")
            buffer = buffer[1:]
        elif buffer[:1] in {b"q", b"Q", b"\x03"}:
            events.append("quit")
            buffer = buffer[1:]
        else:
            buffer = buffer[1:]
    return events, buffer


def _session_id(path: Path) -> str:
    meta = session_meta(path)
    return str(meta.get("session_id") or meta.get("id") or path.stem)


def _visible_index_map(messages: list[HumanMessage]) -> dict[int, int]:
    start = max(0, len(messages) - 9)
    return {index: index - start + 1 for index in range(start, len(messages))}


def _row_for_message(message: HumanMessage, message_ids: dict[tuple[str, str], str]) -> dict:
    return {
        "message_id": message_ids[message.key],
        "timestamp": message.timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "text": message.text,
    }


def _nearby_rows(messages: list[HumanMessage], targets: list[int],
                 message_ids: dict[tuple[str, str], str]) -> list[dict]:
    indexes: set[int] = set()
    for idx in targets:
        indexes.update(i for i in range(max(0, idx - 2), min(len(messages), idx + 2)))
    indexes.difference_update(targets)
    return [_row_for_message(messages[i], message_ids) for i in sorted(indexes)]


def _decorate_message(block: str, marker: str) -> str:
    lines = block.splitlines()
    if not lines:
        return marker
    pad = " " * len(marker)
    return "\n".join([marker + lines[0], *(pad + line for line in lines[1:])])


def _render_explanation(text: str, width: int, color: bool) -> str:
    label = "AI · spiegazione"
    head = f"{ANSI_MAGENTA}{ANSI_BOLD}{label}{ANSI_RESET}" if color else label
    body: list[str] = [head]
    for paragraph in text.splitlines():
        if not paragraph.strip():
            body.append("")
            continue
        body.extend(textwrap.wrap(
            paragraph, width=max(30, width - 6),
            break_long_words=False, break_on_hyphens=False,
        ) or [""])
    return "\n".join("    " + line for line in body)


def _status_line(state: UnreadState, read_after: float, color: bool, now: float | None = None,
                 *, companion_enabled: bool = False, ai_pending: str | None = None) -> str:
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
        base = f"● {count} non lett{'o' if count == 1 else 'i'} · {focus}"
        base = f"{ANSI_AMBER}{ANSI_BOLD}{base}{ANSI_RESET}" if color else base
    else:
        focus = "in focus" if state.focused else "fuori focus"
        base = f"○ 0 non letti · {focus} · soglia {read_after:g}s"
        base = f"{ANSI_DIM}{base}{ANSI_RESET}" if color else base
    companion = "ON" if companion_enabled else "off"
    pending = f" · AI: {ai_pending}" if ai_pending else ""
    return f"{base} · e spiega · E tutto · w companion {companion} · r letti · q esci{pending}"


def _frame_text(path: Path, messages: list[HumanMessage], state: UnreadState, read_after: float,
                color: bool, *, now_mono: float | None = None,
                explain: ExplainState | None = None,
                explanations: dict[str, list[str]] | None = None,
                message_ids: dict[tuple[str, str], str] | None = None,
                companion_enabled: bool = False, companion_summary: str = "",
                ai_pending: str | None = None) -> str:
    explain = explain or ExplainState()
    explanations = explanations or {}
    message_ids = message_ids or {}
    columns = shutil.get_terminal_size(fallback=(120, 24)).columns
    header = f"Codex human view · {path.stem}"
    lines = [f"{ANSI_DIM}{header}{ANSI_RESET}" if color else header]
    lines.append(_status_line(
        state, read_after, color, now=now_mono,
        companion_enabled=companion_enabled, ai_pending=ai_pending,
    ))
    if explain.active:
        hint = "EXPLAIN: ↑/↓ muovi · Shift+↑/↓ estendi · Space seleziona · 1-9 toggle · Enter spiega · Esc annulla"
        lines.append(f"{ANSI_MAGENTA}{hint}{ANSI_RESET}" if color else hint)
    lines.append("")

    shortcuts = _visible_index_map(messages) if explain.active else {}
    for idx, message in enumerate(messages):
        unread = message.key in (state.unread or set())
        marker = ""
        if explain.active:
            n = shortcuts.get(idx)
            cursor = idx == explain.cursor
            chosen = idx in (explain.selected or set())
            tag = str(n) if n else " "
            symbol = "▶" if cursor else ("✓" if chosen else " ")
            marker_plain = f"{symbol}[{tag}] "
            marker = (
                f"{ANSI_MAGENTA}{ANSI_BOLD}{marker_plain}{ANSI_RESET}"
                if color and (cursor or chosen) else marker_plain
            )
        block = render(message, color=color, unread=unread)
        lines.append(_decorate_message(block, marker))
        mid = message_ids.get(message.key)
        if mid and mid in explanations:
            for response in explanations[mid]:
                lines.append(_render_explanation(response, columns, color))
        lines.append("")

    if companion_enabled:
        title = "COMPANION LIVE"
        lines.append("─" * min(columns, 80))
        lines.append(f"{ANSI_MAGENTA}{ANSI_BOLD}{title}{ANSI_RESET}" if color else title)
        if companion_summary:
            for paragraph in companion_summary.splitlines():
                if not paragraph.strip():
                    lines.append("")
                else:
                    lines.extend(textwrap.wrap(
                        paragraph, width=max(30, columns - 2),
                        break_long_words=False, break_on_hyphens=False,
                    ) or [""])
        else:
            lines.append("In attesa della prima sintesi…")
    return "\n".join(lines)


def _redraw(path: Path, messages: list[HumanMessage], state: UnreadState, read_after: float,
            color: bool, *, now_mono: float | None = None, initial: bool = False, **kwargs) -> None:
    frame = _frame_text(
        path, messages, state, read_after, color, now_mono=now_mono, **kwargs
    )
    if initial:
        sys.stdout.write(ANSI_CLEAR + frame)
    else:
        sys.stdout.write(ANSI_SYNC_ON + ANSI_HOME + frame + ANSI_ERASE_DOWN + ANSI_SYNC_OFF)
    sys.stdout.flush()


def follow(path: Path, history: int, poll: float, *, color: bool = True,
           read_after: float = 20.0, db_path: Path = DEFAULT_DB,
           ai_model: str = DEFAULT_MODEL, ai_reasoning: str = DEFAULT_REASONING) -> None:
    all_messages = list(iter_messages(path))
    messages = all_messages[-history:] if history else all_messages
    state = UnreadState(focused=True, focus_since=time.monotonic())
    explain = ExplainState()
    session_id = _session_id(path)
    db = ViewerDB(db_path)
    db.ensure_session(session_id, str(path))
    message_ids: dict[tuple[str, str], str] = {}
    for message in all_messages:
        timestamp = message.timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        message_ids[message.key] = db.save_message(session_id, timestamp, message.text)

    companion_enabled, companion_summary, companion_last_id = db.get_companion(session_id)
    worker = AIWorker(db, session_id, model=ai_model, reasoning=ai_reasoning)
    companion_inflight = False
    companion_pending: list[dict] = []
    explanations: dict[str, list[str]] = {}
    ai_pending: str | None = None
    request_counter = 0

    def submit_explanation(targets: list[int], mode: str) -> None:
        nonlocal ai_pending, request_counter
        if not targets:
            return
        selected = [_row_for_message(messages[i], message_ids) for i in targets]
        nearby = [] if mode == "all" else _nearby_rows(messages, targets, message_ids)
        request_counter += 1
        label = f"explain-{request_counter}"
        worker.submit_explain(
            request_id=label, mode=mode, selected=selected, nearby=nearby
        )
        ai_pending = "spiegazione in corso…"
        explain.pending_label = label

    def submit_all() -> None:
        nonlocal ai_pending, request_counter
        rows = [dict(row) for row in db.messages(session_id)]
        if not rows:
            return
        request_counter += 1
        label = f"all-{request_counter}"
        worker.submit_explain(
            request_id=label, mode="all", selected=rows, nearby=[]
        )
        ai_pending = "analisi completa in corso…"
        explain.pending_label = label

    def rows_after(last_id: str | None) -> list[dict]:
        rows = [dict(row) for row in db.messages(session_id)]
        if not last_id:
            return rows
        for index, row in enumerate(rows):
            if row["message_id"] == last_id:
                return rows[index + 1:]
        return rows

    def schedule_companion(rows: list[dict]) -> None:
        nonlocal companion_inflight, ai_pending, request_counter
        if not companion_enabled or not rows:
            return
        companion_pending.extend(rows)
        if companion_inflight:
            return
        batch = list(companion_pending)
        companion_pending.clear()
        request_counter += 1
        label = f"companion-{request_counter}"
        worker.submit_companion(
            request_id=label, previous_summary=companion_summary,
            new_messages=batch,
        )
        companion_inflight = True
        ai_pending = "companion in aggiornamento…"

    if companion_enabled:
        schedule_companion(rows_after(companion_last_id))

    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    fd = sys.stdin.fileno() if interactive else -1
    old_termios = termios.tcgetattr(fd) if interactive else None
    input_buffer = b""

    if interactive:
        tty.setcbreak(fd)
        os.set_blocking(fd, False)
        print(ANSI_FOCUS_ON, end="")
    _redraw(
        path, messages, state, read_after, color, initial=True,
        explain=explain, explanations=explanations, message_ids=message_ids,
        companion_enabled=companion_enabled, companion_summary=companion_summary,
        ai_pending=ai_pending,
    )
    age_signature = tuple(relative_age(message.timestamp) for message in messages)
    last_status_tick = int(time.monotonic()) if state.unread else None
    last_columns = shutil.get_terminal_size(fallback=(120, 24)).columns

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
                        elif event == "explain_mode":
                            explain.enter(len(messages))
                        elif event == "escape":
                            explain.cancel()
                        elif event == "select_up":
                            explain.move(-1, len(messages))
                        elif event == "select_down":
                            explain.move(1, len(messages))
                        elif event == "select_extend_up":
                            explain.move(-1, len(messages), extend=True)
                        elif event == "select_extend_down":
                            explain.move(1, len(messages), extend=True)
                        elif event == "select_toggle" and explain.active:
                            explain.toggle_current()
                        elif event.startswith("select_digit:") and explain.active:
                            digit = int(event.split(":", 1)[1])
                            reverse = {n: idx for idx, n in _visible_index_map(messages).items()}
                            if digit in reverse:
                                explain.cursor = reverse[digit]
                                explain.toggle_current()
                        elif event == "select_explain" and explain.active:
                            targets = explain.targets()
                            submit_explanation(
                                targets, "single" if len(targets) == 1 else "multi"
                            )
                        elif event == "explain_all":
                            submit_all()
                        elif event == "companion_toggle":
                            companion_enabled = not companion_enabled
                            db.set_companion(session_id, enabled=companion_enabled)
                            if companion_enabled:
                                schedule_companion(rows_after(companion_last_id))
                        elif event == "quit":
                            return
                        redraw = True

            if state.maybe_clear_after_dwell(now_mono, read_after):
                redraw = True

            while True:
                try:
                    result = worker.results.get_nowait()
                except queue.Empty:
                    break
                ai_pending = None
                if result.error:
                    anchor = result.selected_ids[-1] if result.selected_ids else None
                    if anchor:
                        explanations.setdefault(anchor, []).append(
                            f"Errore AI: {result.error}"
                        )
                elif result.mode == "companion" and result.response:
                    companion_summary = result.response
                    companion_inflight = False
                    last_id = result.selected_ids[-1] if result.selected_ids else companion_last_id
                    companion_last_id = last_id
                    db.set_companion(
                        session_id, summary=companion_summary,
                        last_message_id=companion_last_id, enabled=companion_enabled,
                    )
                    if companion_pending:
                        batch = list(companion_pending)
                        companion_pending.clear()
                        schedule_companion(batch)
                elif result.response:
                    anchor = result.selected_ids[-1] if result.selected_ids else None
                    if anchor:
                        prefix = "[cache] " if result.from_cache else ""
                        explanations.setdefault(anchor, []).append(prefix + result.response)
                    explain.cancel()
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
                        timestamp = message.timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                        mid = db.save_message(session_id, timestamp, message.text)
                        message_ids[message.key] = mid
                        messages.append(message)
                        if history:
                            messages = messages[-max(history, 9):]
                        if companion_enabled:
                            schedule_companion([{
                                "message_id": mid, "timestamp": timestamp, "text": message.text
                            }])
                        redraw = True

            current_age_signature = tuple(relative_age(message.timestamp) for message in messages)
            if current_age_signature != age_signature:
                age_signature = current_age_signature
                redraw = True

            columns = shutil.get_terminal_size(fallback=(120, 24)).columns
            if columns != last_columns:
                last_columns = columns
                redraw = True

            status_tick = int(now_mono) if state.focused and state.unread else None
            if status_tick != last_status_tick:
                last_status_tick = status_tick
                redraw = True

            if redraw:
                _redraw(
                    path, messages, state, read_after, color, now_mono=now_mono,
                    explain=explain, explanations=explanations, message_ids=message_ids,
                    companion_enabled=companion_enabled, companion_summary=companion_summary,
                    ai_pending=ai_pending,
                )
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
    parser.add_argument("--history", type=int, default=12, help="Messaggi recenti mostrati nel viewer.")
    parser.add_argument("--poll", type=float, default=0.25, help="Intervallo di polling in secondi.")
    parser.add_argument("--read-after", type=float, default=20.0, metavar="SECONDS",
                        help="Secondi continui in focus prima di segnare i non letti come letti.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite unico per transcript Codex e AI.")
    parser.add_argument("--ai-model", default=DEFAULT_MODEL, help="Modello per explain/companion.")
    parser.add_argument("--ai-reasoning", default=DEFAULT_REASONING,
                        choices=["low", "medium", "high"], help="Reasoning per explain/companion.")
    parser.add_argument("--once", action="store_true", help="Stampa lo storico e termina.")
    args = parser.parse_args(argv)

    root = Path(args.source_root).expanduser()
    path = select_session(root, args.session)
    use_color = os.isatty(sys.stdout.fileno()) and os.environ.get("NO_COLOR") is None
    if args.once:
        for message in list(iter_messages(path))[-args.history:]:
            print(render(message, color=use_color))
            print()
        return 0
    follow(
        path, max(0, args.history), max(0.05, args.poll),
        color=use_color, read_after=max(0.0, args.read_after),
        db_path=Path(args.db).expanduser(),
        ai_model=args.ai_model, ai_reasoning=args.ai_reasoning,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
