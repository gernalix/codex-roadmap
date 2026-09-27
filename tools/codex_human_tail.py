#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT = Path.home() / ".codex" / "sessions"


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
def render(message: HumanMessage, now: datetime | None = None) -> str:
    label = relative_age(message.timestamp, now=now)
    lines = message.text.splitlines() or [""]
    prefix = f"{label:>12} │ "
    continuation = " " * 15
    return "\n".join([prefix + lines[0], *(continuation + line for line in lines[1:])])


def follow(path: Path, history: int, poll: float) -> None:
    messages = list(iter_messages(path))
    for message in messages[-history:]:
        print(render(message))
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
                        print(render(message))
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
    if os.isatty(sys.stdout.fileno()):
        print(f"Codex human view · {path.stem}\n")
    if args.once:
        for message in list(iter_messages(path))[-args.history:]:
            print(render(message))
            print()
        return 0
    follow(path, max(0, args.history), max(0.05, args.poll))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
