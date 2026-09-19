#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import re
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from submit_mutation import MutationSubmitError, SCHEMA, submit_document

DEFAULT_REMOTE_REPO = "gernalix/codex-roadmap"
DEFAULT_REMOTE_BRANCH = "main"


class RoadmapStartError(RuntimeError):
    pass


def _gh_json(*args: str) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["gh", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
        time.sleep(2.0)


def _remote_prompt_status(repository: str, branch: str, prompt_id: str) -> str:
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
                "SELECT status FROM prompts WHERE prompt_id=?",
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
    return str(row[0])


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

    return {
        "status": "ok",
        "prompt_id": prompt_id,
        "roadmap_status": status,
        "issue_number": submitted["issue_number"],
        "issue_url": submitted.get("issue_url", ""),
    }


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
