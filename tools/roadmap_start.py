#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from submit_mutation import MutationSubmitError, SCHEMA, submit_document

DEFAULT_REMOTE_REPO = "gernalix/codex-roadmap"
DEFAULT_REMOTE_HOST = os.environ.get("CODEX_ROADMAP_REMOTE_HOST", "github.com")
DEFAULT_REMOTE_BRANCH = "main"
DEFAULT_REPO_TASK = Path.home() / "projects" / "github-autosync" / "repo_single_writer.py"


class RoadmapStartError(RuntimeError):
    pass


def _gh_json(*args: str) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["gh", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "GH_HOST": DEFAULT_REMOTE_HOST},
        )
    except FileNotFoundError as exc:
        raise RoadmapStartError("gh_cli_missing") from exc
    if proc.returncode:
        raise RoadmapStartError(f"gh_failed:{proc.stderr.strip()}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RoadmapStartError("invalid_gh_response") from exc
    if not isinstance(data, dict):
        raise RoadmapStartError("invalid_gh_response")
    return data


def _wait_issue_applied(repository: str, issue_number: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while True:
        issue = _gh_json("api", f"repos/{repository}/issues/{issue_number}")
        state = str(issue.get("state") or "")
        reason = str(issue.get("state_reason") or "")
        if state == "closed":
            if reason == "completed":
                return
            raise RoadmapStartError(f"start_claim_rejected:{issue_number}:{reason or 'closed'}")
        if time.monotonic() >= deadline:
            raise RoadmapStartError(f"start_claim_timeout:{issue_number}")
        time.sleep(1.0)


def _remote_prompt_record(repository: str, branch: str, prompt_id: str) -> dict[str, Any]:
    payload = _gh_json(
        "api",
        f"repos/{repository}/contents/roadmap.sqlite?ref={branch}",
    )
    try:
        raw = base64.b64decode(str(payload["content"]).replace("\n", ""), validate=True)
    except (KeyError, ValueError) as exc:
        raise RoadmapStartError("remote_db_invalid") from exc

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
        handle.write(raw)
        handle.flush()
        try:
            conn = sqlite3.connect(f"file:{handle.name}?mode=ro", uri=True)
            row = conn.execute(
                "SELECT status,repo,project_id FROM prompts WHERE prompt_id=?",
                (prompt_id,),
            ).fetchone()
        except sqlite3.DatabaseError as exc:
            raise RoadmapStartError("remote_db_invalid") from exc
        finally:
            try:
                conn.close()
            except UnboundLocalError:
                pass
    if not row:
        raise RoadmapStartError(f"prompt_not_found:{prompt_id}")
    return {
        "status": str(row[0]),
        "repo": str(row[1] or ""),
        "project_id": str(row[2] or ""),
    }


def _remote_prompt_status(repository: str, branch: str, prompt_id: str) -> str:
    return str(_remote_prompt_record(repository, branch, prompt_id)["status"])


def _repo_task_worktree(record: dict[str, Any], prompt_id: str) -> str | None:
    repo_slug = str(record.get("repo") or "").strip()
    if not repo_slug or repo_slug.lower() == DEFAULT_REMOTE_REPO.lower():
        return None
    if not DEFAULT_REPO_TASK.is_file():
        raise RoadmapStartError("repo_task_helper_missing")
    cmd = [
        "python3",
        str(DEFAULT_REPO_TASK),
        "start-roadmap",
        "--repo-slug",
        repo_slug,
        "--task-id",
        prompt_id,
        "--actor",
        "codex",
    ]
    project_id = str(record.get("project_id") or "").strip()
    if project_id:
        cmd.extend(["--project-id", project_id])
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RoadmapStartError(f"repo_task_start_failed:{detail}")
    worktree = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    if not worktree:
        raise RoadmapStartError("repo_task_start_missing_worktree")
    return worktree


def _request_start_failure_block(
    prompt_id: str,
    *,
    repository: str,
    branch: str,
    timeout: float,
) -> None:
    document = {
        "schema": SCHEMA,
        "actor": "codex",
        "operations": [
            {
                "op": "terminal_request",
                "prompt_id": prompt_id,
                "status": "blocked",
                "actor": "codex",
                "note": "repo-task isolation could not be established after launch claim",
            }
        ],
    }
    try:
        submitted = submit_document(
            document,
            request_key=f"terminal-{prompt_id}",
            repository=repository,
            branch=branch,
        )
        _wait_issue_applied(repository, submitted["issue_number"], timeout)
    except Exception:
        # Preserve the original isolation failure as the primary diagnostic.
        pass


def claim_start(
    repo: Path,
    prompt_id: str,
    *,
    repository: str = DEFAULT_REMOTE_REPO,
    branch: str = DEFAULT_REMOTE_BRANCH,
    timeout: float = 120.0,
) -> dict[str, str]:
    # Local roadmap checkout is deliberately not read or modified.
    _ = repo
    if not re.fullmatch(r"\d{6}", prompt_id):
        raise RoadmapStartError(f"invalid_prompt_id:{prompt_id}")

    # Reject an unregistered ID before creating an immutable Issue that the
    # single writer can only reject later.  The post-write readback below is
    # retained: a registered prompt can still become non-runnable meanwhile.
    try:
        prompt_record = _remote_prompt_record(repository, branch, prompt_id)
    except RoadmapStartError as exc:
        if str(exc) == f"prompt_not_found:{prompt_id}":
            raise RoadmapStartError(f"prompt_not_registered:{prompt_id}") from exc
        raise

    document = {
        "schema": SCHEMA,
        "actor": "codex",
        "operations": [
            {
                "op": "status",
                "prompt_id": prompt_id,
                "status": "running",
                "actor": "codex",
                "note": "launch-claim:roadmap_start",
            }
        ],
    }
    try:
        submitted = submit_document(
            document,
            request_key=f"start-{prompt_id}",
            repository=repository,
            branch=branch,
        )
    except MutationSubmitError as exc:
        raise RoadmapStartError(str(exc)) from exc

    _wait_issue_applied(repository, submitted["issue_number"], timeout)
    status = _remote_prompt_status(repository, branch, prompt_id)
    if status != "running":
        raise RoadmapStartError(f"prompt_not_claimed:{prompt_id}:{status}")

    try:
        worktree = _repo_task_worktree(prompt_record, prompt_id)
    except RoadmapStartError:
        _request_start_failure_block(
            prompt_id,
            repository=repository,
            branch=branch,
            timeout=timeout,
        )
        raise

    result = {
        "status": "ok",
        "prompt_id": prompt_id,
        "roadmap_status": status,
        "issue_number": submitted["issue_number"],
        "issue_url": submitted.get("issue_url", ""),
    }
    if worktree:
        result.update(
            {
                "worktree_path": worktree,
                "task_branch": f"task/{prompt_id}",
                "repo_single_writer": "enabled",
            }
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Atomically claim a roadmap prompt before Codex begins project work."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--repository", default=DEFAULT_REMOTE_REPO)
    parser.add_argument("--branch", default=DEFAULT_REMOTE_BRANCH)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args(argv)

    try:
        result = claim_start(
            Path(args.repo).expanduser(),
            args.prompt_id,
            repository=args.repository,
            branch=args.branch,
            timeout=args.timeout,
        )
    except RoadmapStartError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
