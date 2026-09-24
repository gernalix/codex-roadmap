#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from roadmap_start import RoadmapStartError, claim_start

SCHEMA = 2
DEFAULT_SOURCE_ROOT = Path.home() / ".codex" / "sessions"
DEFAULT_STATE = Path.home() / ".local" / "state" / "codex-roadmap" / "live-status.json"
DEFAULT_USAGE_PUBLISHER = Path.home() / ".local" / "lib" / "codex-usage-monitor" / "current" / "codex_usage_publisher.py"
DEFAULT_USAGE_SOURCE = Path.home() / "projects" / "codex-usage"
DEFAULT_REPO = Path.home() / "projects" / "codex-roadmap"
PROMPT_ID_RE = re.compile(r"\bPROMPT_ID\s*[:=]\s*[`*_~]*([0-9]{6})\b", re.I)
TERMINAL_TYPES = {"task_complete", "turn_aborted"}


class LiveStatusError(RuntimeError):
    pass


def _extract_text(payload: dict[str, Any]) -> str:
    content = payload.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            value = item.get("text")
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts)


def _prompt_id(text: str) -> str | None:
    match = PROMPT_ID_RE.search((text or "").replace(r"\_", "_"))
    return match.group(1) if match else None


def _scan_bytes(
    data: bytes,
    active_prompt_id: str | None,
) -> tuple[str | None, set[str], bool]:
    observed: set[str] = set()
    terminal_seen = False
    active = active_prompt_id
    for raw in data.splitlines():
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw.decode("utf-8", errors="replace"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(obj, dict):
            continue
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
        top = str(obj.get("type") or "")
        ptype = str(payload.get("type") or "")
        if ptype == "message" and payload.get("role") == "user":
            prompt_id = _prompt_id(_extract_text(payload))
            if prompt_id:
                active = prompt_id
                observed.add(prompt_id)
        if top == "event_msg" and ptype in TERMINAL_TYPES:
            terminal_seen = True
            active = None
    return active, observed, terminal_seen


def _load_state(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": SCHEMA, "initialized": False, "files": {}, "claimed": {}}
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        return {"schema": SCHEMA, "initialized": False, "files": {}, "claimed": {}}
    state.setdefault("initialized", False)
    state.setdefault("files", {})
    state.setdefault("claimed", {})
    return state


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _scan_file(
    path: Path,
    file_state: dict[str, Any],
    *,
    bootstrap: bool,
) -> tuple[dict[str, Any], set[str], bool]:
    try:
        size = path.stat().st_size
    except OSError:
        return file_state, set(), False

    try:
        offset = int(file_state.get("offset") or 0)
    except (TypeError, ValueError):
        offset = 0
    active = file_state.get("active_prompt_id")
    if active is not None:
        active = str(active)
    if size < offset:
        offset = 0
        active = None

    try:
        with path.open("rb") as handle:
            handle.seek(offset)
            data = handle.read()
    except OSError:
        return file_state, set(), False

    if not data:
        return {"offset": size, "active_prompt_id": active}, set(), False

    last_newline = data.rfind(b"\n")
    if last_newline < 0:
        return {"offset": offset, "active_prompt_id": active}, set(), False
    complete = data[: last_newline + 1]
    new_offset = offset + len(complete)
    active, observed, terminal_seen = _scan_bytes(complete, active)

    if bootstrap:
        # Do not replay old terminal events on first install. Still expose a
        # genuinely active prompt at EOF so an already-running Codex task is protected.
        terminal_seen = False
        if active:
            observed = {active}
        else:
            observed = set()

    return {"offset": new_offset, "active_prompt_id": active}, observed, terminal_seen


def _claim_prompt(repo: Path, prompt_id: str) -> tuple[bool, str]:
    try:
        result = claim_start(repo, prompt_id, timeout=120.0)
    except RoadmapStartError as exc:
        text = str(exc)
        permanent = (
            "start_claim_rejected:" in text
            or "prompt_not_claimed:" in text
            or "prompt_not_found:" in text
            or "terminal_prompt_cannot_reactivate:" in text
        )
        return permanent, text
    return True, str(result.get("roadmap_status") or "running")


def watch_once(
    *,
    repo: Path,
    source_root: Path,
    state_path: Path,
    usage_publisher: Path | None = None,
    usage_source: Path | None = None,
) -> dict[str, Any]:
    state = _load_state(state_path)
    bootstrap = not bool(state.get("initialized"))
    files_state = state["files"] if isinstance(state.get("files"), dict) else {}
    claimed = state["claimed"] if isinstance(state.get("claimed"), dict) else {}

    source_paths = sorted(source_root.rglob("*.jsonl")) if source_root.is_dir() else []
    observed: set[str] = set()
    terminal_seen = False
    active_ids: set[str] = set()

    for path in source_paths:
        key = str(path)
        previous = files_state.get(key) if isinstance(files_state.get(key), dict) else {}
        new_state, new_ids, saw_terminal = _scan_file(path, previous, bootstrap=bootstrap)
        files_state[key] = new_state
        observed.update(new_ids)
        terminal_seen = terminal_seen or saw_terminal
        if new_state.get("active_prompt_id"):
            active_ids.add(str(new_state["active_prompt_id"]))

    attempts: dict[str, str] = {}
    for prompt_id in sorted(observed | (active_ids if bootstrap else set())):
        if prompt_id in claimed:
            continue
        permanent, detail = _claim_prompt(repo, prompt_id)
        attempts[prompt_id] = detail
        if permanent:
            claimed[prompt_id] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    if len(claimed) > 500:
        for key in sorted(claimed, key=lambda k: str(claimed[k]))[:-500]:
            claimed.pop(key, None)

    # This watcher is a start-claim safety net only. Terminal events are observed
    # for diagnostics but never trigger publisher/sync/finalization side effects.
    # Telemetry has its own timer and roadmap state has one explicit finalizer.
    _ = usage_publisher, usage_source
    state["schema"] = SCHEMA
    state["initialized"] = True
    state["files"] = files_state
    state["claimed"] = claimed

    _write_state(state_path, state)
    return {
        "status": "ok",
        "bootstrap": bootstrap,
        "files": len(source_paths),
        "active_prompt_ids": sorted(active_ids),
        "claim_attempts": attempts,
        "terminal_event_observed": terminal_seen,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fast local bridge from native Codex rollout activity to the roadmap single writer."
    )
    parser.add_argument("--repo", default=str(DEFAULT_REPO))
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--usage-publisher", default=str(DEFAULT_USAGE_PUBLISHER), help=argparse.SUPPRESS)
    parser.add_argument("--usage-source", default=str(DEFAULT_USAGE_SOURCE), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    state_path = Path(args.state).expanduser()
    lock_path = state_path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "locked"}, sort_keys=True))
            return 0
        try:
            result = watch_once(
                repo=Path(args.repo).expanduser().resolve(),
                source_root=Path(args.source_root).expanduser(),
                state_path=state_path,
                usage_publisher=Path(args.usage_publisher).expanduser(),
                usage_source=Path(args.usage_source).expanduser(),
            )
        except Exception as exc:
            print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
            return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
