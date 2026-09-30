#!/usr/bin/env python3
"""Publish one eligible C2 coding item to Symphony's supported GitHub tracker.

The roadmap is read-only here. GitHub Issues is the handoff boundary; Symphony
owns execution state after publication. Host configuration fences the tracker
and source repositories; issue prose never supplies either authority.
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
import time
from dataclasses import dataclass
from pathlib import Path


LABEL = "c3-symphony-ready"
CANARY_TRACKER = "gernalix/symphony-canary"
DEFAULT_CONFIG = Path.home()/".config/c3-symphony/config.json"
REPO_ID = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
MODEL_ID = re.compile(r"gpt-[0-9][0-9a-z.]*-[a-z0-9-]+\Z")
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
SAFE_ITEM = re.compile(r"wi:[a-f0-9]{32}\Z")


class BridgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class HostConfig:
    mode: str
    tracker_repo: str | None
    source_repos: frozenset[str]


def load_config(path: Path = DEFAULT_CONFIG) -> HostConfig:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BridgeError("host_config_missing_or_invalid") from exc
    if not isinstance(data, dict) or data.get("mode") not in {"legacy", "canary", "production"}:
        raise BridgeError("routing_mode_invalid")
    mode = data["mode"]
    tracker = data.get("tracker_repo")
    repos = data.get("source_repos")
    if mode == "legacy":
        return HostConfig(mode, None, frozenset())
    if (not isinstance(tracker, str) or not REPO_ID.fullmatch(tracker)
            or not isinstance(repos, list) or not repos
            or any(not isinstance(repo, str) or not REPO_ID.fullmatch(repo) for repo in repos)
            or len(set(repos)) != len(repos)):
        raise BridgeError("tracker_or_source_allowlist_required")
    if mode == "canary" and tracker != CANARY_TRACKER:
        raise BridgeError("canary_tracker_mismatch")
    if mode == "production" and tracker == CANARY_TRACKER:
        raise BridgeError("production_tracker_is_canary")
    return HostConfig(mode, tracker, frozenset(repos))


@dataclass(frozen=True)
class CodingItem:
    work_item_id: str
    title: str
    objective: str
    acceptance: str
    repo: str
    model: str
    reasoning: str
    worktree: str | None = None
    prompt_id: str | None = None


def resolve_model(value: str | None) -> str:
    label = re.sub(r"\s+", "-", (value or "").strip().lower())
    if not MODEL_ID.fullmatch(label):
        raise BridgeError("missing_or_invalid_model")
    return label


def resolve_reasoning(value: str | None) -> str:
    effort = (value or "").strip().lower()
    if effort not in REASONING_EFFORTS:
        raise BridgeError("missing_or_invalid_reasoning")
    return effort


def load_item(db: Path, work_item_id: str, config: HostConfig,
              run_id: str | None = None) -> CodingItem:
    if not SAFE_ITEM.fullmatch(work_item_id):
        raise BridgeError("invalid_work_item_id")
    uri = f"file:{db.resolve()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT w.work_item_id,w.title,w.objective,w.acceptance_json,w.repo,w.prompt_id,
                   w.status,w.actionable,w.executor_policy,s.activity,
                   s.model,s.reasoning,s.worktree
            FROM work_items w
            JOIN work_item_execution_specs s USING(work_item_id)
            WHERE w.work_item_id=?
        """, (work_item_id,)).fetchone()
        if run_id:
            runnable = conn.execute("""SELECT 1 FROM work_item_runs
                WHERE run_id=? AND work_item_id=? AND executor='symphony'
                  AND state IN ('running','recovering') AND worker_ref=?""",
                (run_id, work_item_id, "c2-run:"+run_id)).fetchone()
        else:
            runnable = conn.execute(
                "SELECT 1 FROM v_work_item_runnable WHERE work_item_id=?",
                (work_item_id,),
            ).fetchone()
    expected_status = "running" if run_id else "pending"
    if row is None or runnable is None or row["status"] != expected_status or not row["actionable"]:
        raise BridgeError("item_not_runnable")
    if row["executor_policy"] not in {"auto", "codex"} or row["activity"] != "coding":
        raise BridgeError("item_not_autonomous_coding")
    if row["repo"] not in config.source_repos:
        raise BridgeError("source_repo_not_allowlisted")
    model, reasoning = resolve_model(row["model"]), resolve_reasoning(row["reasoning"])
    return CodingItem(work_item_id, row["title"], row["objective"] or "",
                      row["acceptance_json"] or "[]", row["repo"], model, reasoning,
                      row["worktree"], row["prompt_id"])


def issue_title(item: CodingItem) -> str:
    return f"[C3 {item.work_item_id}] {item.title}"[:250]


def issue_body(item: CodingItem) -> str:
    return (f"C3 source: {item.work_item_id}\n"
            f"Source repository: {item.repo}\n\n"
            f"Objective:\n{item.objective}\n\n"
            f"Acceptance (canonical JSON):\n{item.acceptance}\n")


class GitHubIssues:
    def __init__(self, tracker_repo: str):
        if not REPO_ID.fullmatch(tracker_repo):
            raise BridgeError("tracker_repo_invalid")
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
            if issue.get("state") == "closed":
                return {"issue_number": issue["number"], "created": False}
            if issue.get("state") != "open":
                raise BridgeError("tracker_issue_invalid_state")
            if LABEL not in {str(x.get("name", "")).lower() for x in issue.get("labels", [])}:
                raise BridgeError("tracker_issue_missing_ready_label")
            return {"issue_number": issue["number"], "created": False}
        issue = github.create(title, body)
        # The response is not dispatch proof; read back the unique identity.
        for attempt in range(5):
            matches = github.matching(title)
            if len(matches) > 1:
                raise BridgeError("duplicate_tracker_identity")
            if matches:
                if (matches[0].get("number") != issue["number"]
                        or matches[0].get("body") != body
                        or matches[0].get("state") != "open"
                        or LABEL not in {str(x.get("name", "")).lower()
                                         for x in matches[0].get("labels", [])}):
                    raise BridgeError("tracker_create_readback_failed")
                break
            if attempt < 4:
                time.sleep(0.5)
        else:
            raise BridgeError("tracker_create_readback_failed")
        return {"issue_number": issue["number"], "created": True}


def inspect(item: CodingItem, github: GitHubIssues) -> dict:
    matches = github.matching(issue_title(item))
    if len(matches) != 1 or matches[0].get("body") != issue_body(item):
        raise BridgeError("tracker_identity_missing_or_conflicted")
    issue = matches[0]
    if issue.get("state") not in {"open", "closed"} or not isinstance(issue.get("number"), int):
        raise BridgeError("tracker_issue_invalid_state")
    result = {"issue_number": issue["number"], "state": issue["state"]}
    if issue["state"] == "closed":
        comments = github.api("GET", f"repos/{github.repo}/issues/{issue['number']}/comments?per_page=100")
        if not isinstance(comments, list) or len(comments) == 100:
            raise BridgeError("tracker_terminal_comments_unbounded")
        contracts = [str(row.get("body", ""))[10:] for row in comments
                     if isinstance(row, dict) and str(row.get("body", "")).startswith("C3_RESULT=")]
        if len(contracts) != 1:
            raise BridgeError("tracker_terminal_contract_missing_or_duplicate")
        try:
            result["terminal"] = json.loads(contracts[0])
        except ValueError as exc:
            raise BridgeError("tracker_terminal_contract_invalid") from exc
    return result


def verify_worktree(item: CodingItem) -> Path:
    if not item.prompt_id or not re.fullmatch(r"[0-9]{6}", item.prompt_id):
        raise BridgeError("production_prompt_id_required")
    if not item.worktree or not Path(item.worktree).is_absolute():
        raise BridgeError("production_worktree_required")
    tree = Path(item.worktree).resolve(strict=True)
    checks = (("rev-parse", "--show-toplevel"), ("branch", "--show-current"),
              ("remote", "get-url", "origin"))
    values = []
    for args in checks:
        result = subprocess.run(["git", "-C", str(tree), *args], text=True,
                                capture_output=True, check=False)
        if result.returncode:
            raise BridgeError("production_worktree_invalid")
        values.append(result.stdout.strip())
    if (Path(values[0]).resolve() != tree or values[1] != "task/"+item.prompt_id
            or not re.fullmatch(r"(?:https://github\.com/|git@github\.com:)"+
                                re.escape(item.repo)+r"(?:\.git)?", values[2])):
        raise BridgeError("production_worktree_identity_mismatch")
    return tree


def workflow_text(item: CodingItem, workspace_root: Path, config: HostConfig) -> str:
    if item.repo not in config.source_repos or not config.tracker_repo:
        raise BridgeError("source_or_tracker_not_configured")
    tracker_repo = config.tracker_repo
    if not workspace_root.is_absolute():
        raise BridgeError("workspace_root_must_be_absolute")
    command = (f"codex -c {shlex.quote('model=' + item.model)} "
               f"-c {shlex.quote('model_reasoning_effort=' + item.reasoning)}")
    if config.mode == "production":
        tree = verify_worktree(item)
        branch = "task/" + str(item.prompt_id)
        clone = (
            f"git clone --no-hardlinks --branch {shlex.quote(branch)} "
            f"{shlex.quote(str(tree))} source && "
            "git -C source rev-parse HEAD > .c3-source-base"
        )
    else:
        clone = f"gh repo clone {item.repo} source -- --depth 1"
    command += " app-server"
    config = {
        "server": {"host": "127.0.0.1"},
        "tracker": {"kind": "github", "provider": {"repo": tracker_repo, "token": "$GITHUB_TOKEN"},
                    "required_labels": [LABEL], "active_states": ["open"], "terminal_states": ["closed"]},
        "workspace": {"root": str(workspace_root)},
        "hooks": {"after_create": clone},
        "agent": {"max_concurrent_agents": 1, "max_turns": 3},
        "codex": {"command": command, "approval_policy": "never", "thread_sandbox": "workspace-write"},
    }
    prompt = ("You are working on the GitHub tracker issue {{ issue.identifier }}.\n"
              "This issue is the Symphony execution handoff for one canonical C2 work item. "
              "Symphony has already dispatched it. Do not call roadmap_start.py, "
              "c2_executor_start.py, c2_executor_result.py, or roadmap_finish.py.\n"
              "The isolated writable task clone is available as source/. Work only there. "
              "Run git commands with `git -C source`. Commit tested changes on the task branch. "
              "Do not push or merge; the existing repository writer owns integration.\n"
              "The issue description defines the task and acceptance checks.\n"
              "For every github_api read/comment/close call, the canonical tracker repository is "
              f"{tracker_repo} and the tracker issue is {{{{ issue.identifier }}}}; the Source repository "
              "in the issue body is never the tracker target.\n"
              "After verifying and committing the change, comment on the exact tracker issue with "
              "one line C3_RESULT=<JSON object> containing outcome=PASS, completed (list), "
              "remaining=[], evidence (nonempty list), blocker=null, next_action=null. "
              "Close that exact tracker issue, "
              "then read back that same tracker repository/issue and require state=closed.\n"
              "If blocked, comment with the blocker on that exact tracker issue and leave it open.\n\n"
              "{{ issue.description }}\n")
    return "---\n" + json.dumps(config, indent=2) + "\n---\n\n" + prompt


def write_workflow(item: CodingItem, workspace_root: Path, output: Path, config: HostConfig) -> None:
    root = workspace_root.resolve()
    target = output.resolve()
    if target == root or root in target.parents:
        raise BridgeError("workflow_inside_codex_workspace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(workflow_text(item, root, config), encoding="utf-8")
    target.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["publish", "workflow", "inspect"])
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--lock", type=Path, default=Path.home()/".local/share/c3-symphony/publish.lock")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if config.mode == "legacy":
            raise BridgeError("symphony_disabled_in_legacy_mode")
        item = load_item(args.db, args.work_item_id, config, args.run_id)
        if config.mode == "production" and args.action in {"publish", "inspect"}:
            if not args.run_id:
                raise BridgeError("production_run_identity_required")
            owner = Path.home()/".local/state/c3-symphony/ownership"/(args.work_item_id[3:]+".json")
            try:
                recorded = json.loads(owner.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise BridgeError("production_ownership_missing") from exc
            if recorded != {"work_item_id": args.work_item_id, "run_id": args.run_id,
                            "tracker_repo": config.tracker_repo, "mode": config.mode}:
                raise BridgeError("production_ownership_mismatch")
        if args.action == "publish":
            result = publish(item, GitHubIssues(config.tracker_repo), args.lock)
        elif args.action == "inspect":
            result = inspect(item, GitHubIssues(config.tracker_repo))
        else:
            if args.workspace_root is None or args.output is None:
                raise BridgeError("workflow_paths_required")
            write_workflow(item, args.workspace_root, args.output, config)
            result = {"workflow": str(args.output)}
    except (BridgeError, sqlite3.Error, OSError) as exc:
        parser.exit(2, f"c3_symphony_bridge: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
