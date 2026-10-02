"""Route C2 repository integration through the owning repository writer."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import subprocess

REPO_SINGLE_WRITER = Path.home() / "projects/github-autosync/repo_single_writer.py"


class RepositoryIntegrationError(RuntimeError):
    pass


def prompt_repository(db_path: Path, prompt_id: str) -> str:
    try:
        with sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True) as db:
            row = db.execute("SELECT repo FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone()
    except sqlite3.Error as exc:
        raise RepositoryIntegrationError("prompt_repository_unavailable") from exc
    if not row or not row[0]:
        raise RepositoryIntegrationError("prompt_repository_missing")
    return str(row[0])


def _external(prompt_id: str, command: str, repository: str) -> dict:
    if not REPO_SINGLE_WRITER.is_file():
        raise RepositoryIntegrationError("repo_task_helper_missing")
    proc = subprocess.run(["python3", str(REPO_SINGLE_WRITER), command,
        "--task-id", prompt_id, "--repo", repository], text=True, capture_output=True, check=False)
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RepositoryIntegrationError(f"repo_integration_{command}_failed:{detail}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RepositoryIntegrationError("repo_integration_invalid_response") from exc


def queue_integration(prompt_id: str, repository: str, worktree: Path) -> tuple[str, bool]:
    payload = _external(prompt_id, "finish-any", repository)
    state = str(payload.get("status") or "")
    if state == "merged":
        return state, True
    if state == "no-task-record":
        raise RepositoryIntegrationError("repo_integration_task_record_missing")
    if state in ("queued", "ready"):
        return "queued", False
    raise RepositoryIntegrationError(f"repo_integration_unexpected_status:{state or 'missing'}")


def integration_status(prompt_id: str, repository: str) -> dict:
    return _external(prompt_id, "status-any", repository)
