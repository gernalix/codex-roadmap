#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "codex-roadmap.mutation.v1"
DEFAULT_REMOTE_REPO = os.environ.get("CODEX_ROADMAP_REMOTE_REPO", "gernalix/codex-roadmap")
DEFAULT_REMOTE_BRANCH = os.environ.get("CODEX_ROADMAP_REMOTE_BRANCH", "main")


class MutationSubmitError(RuntimeError):
    pass


def _canonical_bytes(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _validate_request_key(request_key: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", request_key):
        raise MutationSubmitError(f"invalid_request_key:{request_key}")
    return request_key


def _gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(
            ["gh", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise MutationSubmitError("gh_cli_missing") from exc
    if check and proc.returncode:
        raise MutationSubmitError(f"gh_failed:{proc.stderr.strip()}")
    return proc


def _read_remote_document(
    *,
    repository: str,
    branch: str,
    path: str,
) -> dict[str, Any] | None:
    proc = _gh("api", f"repos/{repository}/contents/{path}?ref={branch}", check=False)
    if proc.returncode:
        if "404" in proc.stderr or "Not Found" in proc.stderr:
            return None
        raise MutationSubmitError(f"gh_read_failed:{proc.stderr.strip()}")
    try:
        payload = json.loads(proc.stdout)
        raw = base64.b64decode(str(payload["content"]).replace("\n", ""))
        doc = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError) as exc:
        raise MutationSubmitError(f"invalid_remote_mutation:{path}") from exc
    if not isinstance(doc, dict):
        raise MutationSubmitError(f"invalid_remote_mutation:{path}")
    return doc


def submit_document(
    document: dict[str, Any],
    *,
    request_key: str,
    repository: str = DEFAULT_REMOTE_REPO,
    branch: str = DEFAULT_REMOTE_BRANCH,
) -> dict[str, str]:
    if document.get("schema") != SCHEMA:
        raise MutationSubmitError("invalid_mutation_schema")
    operations = document.get("operations")
    if not isinstance(operations, list) or not operations:
        raise MutationSubmitError("empty_mutation")
    request_key = _validate_request_key(request_key)
    inbox_path = f"mutations/inbox/{request_key}.json"
    applied_path = f"mutations/applied/{request_key}.json"

    for path, state in ((applied_path, "applied"), (inbox_path, "pending")):
        existing = _read_remote_document(repository=repository, branch=branch, path=path)
        if existing is None:
            continue
        if _canonical_bytes(existing) != _canonical_bytes(document):
            raise MutationSubmitError(f"request_key_conflict:{request_key}:{state}")
        return {"submission": state, "path": path, "request_key": request_key}

    encoded = base64.b64encode(_canonical_bytes(document)).decode("ascii")
    proc = _gh(
        "api",
        "--method",
        "PUT",
        f"repos/{repository}/contents/{inbox_path}",
        "-f",
        f"message=Queue roadmap mutation {request_key}",
        "-f",
        f"content={encoded}",
        "-f",
        f"branch={branch}",
        check=False,
    )
    if proc.returncode:
        # A simultaneous identical submit can win the create race. Re-read once;
        # never retry a blind write or touch the local git checkout.
        for path, state in ((applied_path, "applied"), (inbox_path, "pending")):
            existing = _read_remote_document(repository=repository, branch=branch, path=path)
            if existing is not None and _canonical_bytes(existing) == _canonical_bytes(document):
                return {"submission": state, "path": path, "request_key": request_key}
        raise MutationSubmitError(f"gh_submit_failed:{proc.stderr.strip()}")

    return {"submission": "queued", "path": inbox_path, "request_key": request_key}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Submit one immutable roadmap mutation directly to the remote inbox without modifying the local git checkout."
    )
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--request-key", required=True)
    parser.add_argument("--repository", default=DEFAULT_REMOTE_REPO)
    parser.add_argument("--branch", default=DEFAULT_REMOTE_BRANCH)
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.file.read_text(encoding="utf-8"))
        result = submit_document(
            document,
            request_key=args.request_key,
            repository=args.repository,
            branch=args.branch,
        )
    except (OSError, ValueError, MutationSubmitError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps({"status": "ok", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
