#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from roadmap_db import FINAL_STATUS, materialization_hash
from submit_mutation import MutationSubmitError, SCHEMA, submit_document

DEFAULT_REMOTE_REPO = "gernalix/codex-roadmap"
DEFAULT_REMOTE_BRANCH = "main"


class SyncError(RuntimeError):
    pass


def _download_remote_db(repository: str, branch: str) -> tuple[set[str], set[str]]:
    try:
        proc = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repository}/contents/roadmap.sqlite?ref={branch}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise SyncError("gh_cli_missing") from exc
    if proc.returncode:
        raise SyncError(f"remote_db_download_failed:{proc.stderr.decode(errors='replace').strip()}")
    try:
        payload = json.loads(proc.stdout.decode("utf-8"))
        raw_db = base64.b64decode(str(payload["content"]).replace("\n", ""), validate=True)
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
        raise SyncError("remote_db_invalid") from exc

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
        handle.write(raw_db)
        handle.flush()
        try:
            conn = sqlite3.connect(f"file:{handle.name}?mode=ro", uri=True)
            prompt_ids = {str(row[0]) for row in conn.execute("SELECT prompt_id FROM prompts")}
            cycle_keys = {
                str(row[0])
                for row in conn.execute(
                    "SELECT cycle_key FROM executions WHERE cycle_key IS NOT NULL AND cycle_key<>''"
                )
            }
        except sqlite3.DatabaseError as exc:
            raise SyncError("remote_db_invalid") from exc
        finally:
            try:
                conn.close()
            except UnboundLocalError:
                pass
    return prompt_ids, cycle_keys


def _execution_operation(data: dict[str, Any], prompt_id: str, cycle_key: str) -> dict[str, Any]:
    status = str(data.get("status") or "").upper()
    if status not in FINAL_STATUS:
        raise SyncError(f"execution_not_terminal:{prompt_id}:{status or 'missing'}")
    outcome = status
    prompt_text = str(data.get("prompt_text_redacted") or "")
    observed_hash = materialization_hash(prompt_text) if prompt_text else None

    operation: dict[str, Any] = {
        "op": "usage_execution",
        "prompt_id": prompt_id,
        "cycle_key": cycle_key,
        "outcome": outcome,
        "source": "codex-usage",
    }
    optional = {
        "materialization_sha256": observed_hash,
        "started_at": data.get("timestamp_start_utc"),
        "ended_at": data.get("timestamp_end_utc"),
        "duration_seconds": data.get("duration_seconds"),
        "model": data.get("model"),
        "reasoning": data.get("reasoning_effort"),
        "codex_project": data.get("repo_project"),
        "chat_title": data.get("chat_title"),
        "branch": data.get("branch"),
        "commit_before": data.get("commit_before"),
        "commit_after": data.get("commit_after"),
        "tool_call_count": data.get("tool_call_count"),
        "input_tokens": data.get("input_tokens"),
        "cached_input_tokens": data.get("cached_input_tokens"),
        "uncached_input_tokens": data.get("uncached_input_tokens"),
        "output_tokens": data.get("output_tokens"),
        "reasoning_output_tokens": data.get("reasoning_output_tokens"),
        "total_tokens": data.get("total_tokens"),
    }
    operation.update({key: value for key, value in optional.items() if value is not None})
    return operation


def sync(
    repo: Path,
    source: Path,
    *,
    repository: str = DEFAULT_REMOTE_REPO,
    branch: str = DEFAULT_REMOTE_BRANCH,
) -> dict[str, object]:
    # repo remains a compatibility argument for the systemd unit/old callers.
    # It is intentionally never fetched, modified, committed or pushed.
    _ = Path(repo)
    source = Path(source).expanduser().resolve()
    known_prompts, remote_cycles = _download_remote_db(repository, branch)

    stats: dict[str, object] = {
        "files": 0,
        "already_applied": 0,
        "queued": 0,
        "pending": 0,
        "applied_race": 0,
        "skipped_invalid": 0,
        "skipped_unregistered": 0,
        "skipped_no_cycle_key": 0,
        "skipped_nonterminal": 0,
    }

    for path in sorted(source.glob("prompts/*/metrics.json")):
        stats["files"] = int(stats["files"]) + 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stats["skipped_invalid"] = int(stats["skipped_invalid"]) + 1
            continue

        prompt_id = str(data.get("prompt_id") or path.parent.name)
        if not re.fullmatch(r"\d{6}", prompt_id):
            stats["skipped_invalid"] = int(stats["skipped_invalid"]) + 1
            continue
        cycle_key = str(data.get("cycle_key") or "")
        if not cycle_key:
            # Historical rows without a stable cycle key were already handled by
            # the legacy importer. Re-sending them could create duplicate executions.
            stats["skipped_no_cycle_key"] = int(stats["skipped_no_cycle_key"]) + 1
            continue
        if cycle_key in remote_cycles:
            stats["already_applied"] = int(stats["already_applied"]) + 1
            continue
        if prompt_id not in known_prompts:
            # Registration may still be queued. Leave it for the next timer tick;
            # never invent a competing historical stub from the local writer.
            stats["skipped_unregistered"] = int(stats["skipped_unregistered"]) + 1
            continue

        try:
            operation = _execution_operation(data, prompt_id, cycle_key)
        except SyncError as exc:
            if str(exc).startswith("execution_not_terminal:"):
                stats["skipped_nonterminal"] = int(stats["skipped_nonterminal"]) + 1
                continue
            raise
        document = {"schema": SCHEMA, "actor": "codex-usage", "operations": [operation]}
        key_hash = hashlib.sha256(cycle_key.encode("utf-8")).hexdigest()[:20]
        request_key = f"usage-{prompt_id}-{key_hash}"
        try:
            result = submit_document(
                document,
                request_key=request_key,
                repository=repository,
                branch=branch,
            )
        except MutationSubmitError as exc:
            raise SyncError(f"mutation_submit_failed:{prompt_id}:{exc}") from exc

        submission = result["submission"]
        if submission == "queued":
            stats["queued"] = int(stats["queued"]) + 1
        elif submission == "pending":
            stats["pending"] = int(stats["pending"]) + 1
        elif submission == "applied":
            stats["applied_race"] = int(stats["applied_race"]) + 1

    return {"status": "ok", **stats}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Queue codex-usage execution metadata for the remote roadmap single writer."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source", required=True)
    parser.add_argument("--repository", default=DEFAULT_REMOTE_REPO)
    parser.add_argument("--branch", default=DEFAULT_REMOTE_BRANCH)
    args = parser.parse_args(argv)
    try:
        result = sync(
            Path(args.repo).expanduser(),
            Path(args.source).expanduser(),
            repository=args.repository,
            branch=args.branch,
        )
    except SyncError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
