#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
import time
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
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
ROOT_PATH_RE = re.compile(r"(?<![\w`])(/root/[A-Za-z0-9_./-]+)")
URL_RE = re.compile(r"(?<![\w`])(https?://\S+)")


@dataclass(frozen=True)
class HumanMessage:
    timestamp: datetime
    text: str


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
) -> str:
    label = relative_age(message.timestamp, now=now)
    prefix = f"{label:>12} │ "
    continuation = " " * len(prefix)
    terminal_width = width or shutil.get_terminal_size(fallback=(120, 24)).columns
    content_width = max(20, terminal_width - len(prefix) - 1)
    lines = wrap_text(message.text, content_width)
    if color:
        lines = [colorize(line) for line in lines]
    return "\n".join(
        (prefix if index == 0 else continuation) + line
        for index, line in enumerate(lines)
    )


def follow(path: Path, history: int, poll: float, *, color: bool = True) -> None:
    messages = list(iter_messages(path))
    for message in messages[-history:]:
        print(render(message, color=color))
        print()
    sys.stdout.flush()

    offset = path.stat().st_size
    pending = ""
    while True:
        try:
            size = path.stat().st_size
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
                        print(render(message, color=color))
                        print()
                        sys.stdout.flush()
            time.sleep(poll)
        except KeyboardInterrupt:
            return
        except FileNotFoundError:
            time.sleep(poll)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vista live read-only dei soli messaggi umani di Codex CLI."
    )
    parser.add_argument("--source-root", default=str(DEFAULT_ROOT))
    parser.add_argument("--session", help="Path o UUID/parziale della sessione da seguire.")
    parser.add_argument("--history", type=int, default=8, help="Messaggi precedenti da mostrare.")
    parser.add_argument("--poll", type=float, default=0.25, help="Intervallo di polling in secondi.")
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
    follow(path, max(0, args.history), max(0.05, args.poll), color=use_color)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
