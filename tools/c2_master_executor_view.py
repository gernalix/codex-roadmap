#!/usr/bin/env python3
"""Expose the canonical headless Codex executor's raw stdout without redraws."""
from __future__ import annotations

import os
import time
from pathlib import Path

LOG = Path.home() / ".local/state/c2/inbox-drain-codex.log"
MARKER = "=== C2 Inbox Codex fallback "


def wait_for_log() -> None:
    while not LOG.exists():
        print("Codex Executor — in attesa del primo output del worker C2...", flush=True)
        time.sleep(2)


def show_current_batch(stream) -> None:
    stream.seek(0)
    lines = stream.readlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith(MARKER):
            start = i
    for line in lines[start:]:
        print(line, end="", flush=True)
    stream.seek(0, os.SEEK_END)
def main() -> int:
    wait_for_log()
    print("Codex Executor — output RAW di codex exec (worker C2 headless)", flush=True)
    print("Ctrl+C chiude solo questa vista, non il worker C2.\n", flush=True)
    with LOG.open("r", encoding="utf-8", errors="replace") as stream:
        show_current_batch(stream)
        while True:
            line = stream.readline()
            if line:
                print(line, end="", flush=True)
                continue
            time.sleep(0.2)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        pass
