#!/usr/bin/env python3
"""Publish one eligible C2 coding item to Symphony's supported GitHub tracker.

The roadmap is read-only here. GitHub Issues is the handoff boundary; Symphony
owns execution state after publication. This pilot deliberately supports one
source repository and one local publisher host.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import fcntl
import json
import os
import re
import shlex
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path


LABEL = "c3-symphony-ready"
SOURCE_REPO = "gernalix/codex-roadmap"
TRACKER_REPO = "gernalix/symphony-canary"
SAFE_VALUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
SAFE_ITEM = re.compile(r"wi:[a-f0-9]{32}\Z")


class BridgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class CodingItem:
    work_item_id: str
    title: str
    objective: str
    acceptance: str
    repo: str
    model: str
    reasoning: str


def load_item(db: Path, work_item_id: str) -> CodingItem:
    if not SAFE_ITEM.fullmatch(work_item_id):
        raise BridgeError("invalid_work_item_id")
    uri = f"file:{db.resolve()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT w.work_item_id,w.title,w.objective,w.acceptance_json,w.repo,
                   w.status,w.actionable,w.executor_policy,s.activity,
                   s.model,s.reasoning
            FROM work_items w
            JOIN work_item_execution_specs s USING(work_item_id)
            WHERE w.work_item_id=?
        """, (work_item_id,)).fetchone()
        runnable = conn.execute(
            "SELECT 1 FROM v_work_item_runnable WHERE work_item_id=?",
            (work_item_id,),
        ).fetchone()
    if row is None or runnable is None or row["status"] != "pending" or not row["actionable"]:
        raise BridgeError("item_not_runnable")
    if row["executor_policy"] != "codex" or row["activity"] != "coding":
        raise BridgeError("item_not_autonomous_coding")
    if row["repo"] != SOURCE_REPO:
        raise BridgeError("source_repo_not_in_pilot")
    model, reasoning = row["model"], row["reasoning"]
    if not model or not reasoning or not SAFE_VALUE.fullmatch(model) or not SAFE_VALUE.fullmatch(reasoning):
        raise BridgeError("missing_or_invalid_model_reasoning")
    return CodingItem(work_item_id, row["title"], row["objective"] or "",
                      row["acceptance_json"] or "[]", row["repo"], model, reasoning)


def issue_title(item: CodingItem) -> str:
    return f"[C3 {item.work_item_id}] {item.title}"[:250]


def issue_body(item: CodingItem) -> str:
    return (f"C3 source: {item.work_item_id}\n"
            f"Source repository: {item.repo}\n\n"
            f"Objective:\n{item.objective}\n\n"
            f"Acceptance (canonical JSON):\n{item.acceptance}\n")


class GitHubIssues:
    def __init__(self, tracker_repo: str = TRACKER_REPO):
        if tracker_repo != TRACKER_REPO:
            raise BridgeError("tracker_repo_not_in_pilot")
        self.repo = tracker_repo

    def api(self, method: str, path: str, payload: dict | None = None) -> object:
        command = ["gh", "api", "--method", method, path]
        if payload is not None:
            command += ["--input", "-"]
        result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True, check=False)
        if result.returncode:
            raise BridgeError(f"github_api_failed:{method}:{path}:{result.returncode}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise BridgeError("github_api_invalid_json") from exc

    def matching(self, title: str) -> list[dict]:
        matches = []
        page = 1
        while True:
            rows = self.api("GET", f"repos/{self.repo}/issues?state=all&per_page=100&page={page}")
            if not isinstance(rows, list):
                raise BridgeError("github_issues_invalid_response")
            matches.extend(row for row in rows if isinstance(row, dict)
                           and "pull_request" not in row and row.get("title") == title)
            if len(rows) < 100:
                return matches
            page += 1

    def create(self, title: str, body: str) -> dict:
        result = self.api("POST", f"repos/{self.repo}/issues",
                          {"title": title, "body": body, "labels": [LABEL]})
        if not isinstance(result, dict) or not isinstance(result.get("number"), int):
            raise BridgeError("github_issue_create_invalid_response")
        return result


def publish(item: CodingItem, github: GitHubIssues, lock_path: Path) -> dict:
    """Local-host serialization plus readback makes replay after a crash safe."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        title, body = issue_title(item), issue_body(item)
        matches = github.matching(title)
        if len(matches) > 1:
            raise BridgeError("duplicate_tracker_identity")
        if matches:
            issue = matches[0]
            if issue.get("body") != body:
                raise BridgeError("tracker_identity_conflict")
            if issue.get("state") != "open":
                raise BridgeError("tracker_issue_already_terminal")
            if LABEL not in {str(x.get("name", "")).lower() for x in issue.get("labels", [])}:
                raise BridgeError("tracker_issue_missing_ready_label")
            return {"issue_number": issue["number"], "created": False}
        issue = github.create(title, body)
        # The response is not dispatch proof; read back the unique identity.
        matches = github.matching(title)
        if (len(matches) != 1 or matches[0].get("number") != issue["number"]
                or matches[0].get("body") != body
                or matches[0].get("state") != "open"
                or LABEL not in {str(x.get("name", "")).lower()
                                 for x in matches[0].get("labels", [])}):
            raise BridgeError("tracker_create_readback_failed")
        return {"issue_number": issue["number"], "created": True}


def workflow_text(item: CodingItem, workspace_root: Path, tracker_repo: str = TRACKER_REPO) -> str:
    if tracker_repo != TRACKER_REPO:
        raise BridgeError("tracker_repo_not_in_pilot")
    if not workspace_root.is_absolute():
        raise BridgeError("workspace_root_must_be_absolute")
    command = (f"codex -c {shlex.quote('model=' + item.model)} "
               f"-c {shlex.quote('model_reasoning_effort=' + item.reasoning)} app-server")
    config = {
        "tracker": {"kind": "github", "provider": {"repo": tracker_repo, "token": "$GITHUB_TOKEN"},
                    "required_labels": [LABEL], "active_states": ["open"], "terminal_states": ["closed"]},
        "workspace": {"root": str(workspace_root)},
        "hooks": {"after_create": f"git clone https://github.com/{item.repo}.git ."},
        "agent": {"max_concurrent_agents": 1, "max_turns": 3},
        "codex": {"command": command, "approval_policy": "never", "thread_sandbox": "workspace-write"},
    }
    prompt = ("You are working on the GitHub pilot issue {{ issue.identifier }}.\n"
              "Work only in this isolated repository copy. Do not push or merge.\n"
              "The issue description defines the task and acceptance checks.\n"
              "After verifying the change, use github_api to comment with concise evidence and close the issue.\n"
              "If blocked, comment with the blocker and leave the issue open.\n\n"
              "{{ issue.description }}\n")
    return "---\n" + json.dumps(config, indent=2) + "\n---\n\n" + prompt


def write_workflow(item: CodingItem, workspace_root: Path, output: Path) -> None:
    root = workspace_root.resolve()
    target = output.resolve()
    if target == root or root in target.parents:
        raise BridgeError("workflow_inside_codex_workspace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(workflow_text(item, root), encoding="utf-8")
    target.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["publish", "workflow"])
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--lock", type=Path, default=Path.home()/".local/share/c3-symphony/publish.lock")
    args = parser.parse_args()
    try:
        item = load_item(args.db, args.work_item_id)
        if args.action == "publish":
            result = publish(item, GitHubIssues(), args.lock)
        else:
            if args.workspace_root is None or args.output is None:
                raise BridgeError("workflow_paths_required")
            write_workflow(item, args.workspace_root, args.output)
            result = {"workflow": str(args.output)}
    except (BridgeError, sqlite3.Error, OSError) as exc:
        parser.exit(2, f"c3_symphony_bridge: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
