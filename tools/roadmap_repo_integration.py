#!/usr/bin/env python3
"""Dedicated GitHub PR writer for isolated codex-roadmap task branches."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

REPOSITORY = "gernalix/codex-roadmap"
SHA = re.compile(r"[0-9a-f]{40}\Z")
PROMPT = re.compile(r"[0-9]{6}\Z")
WORK_ITEM = re.compile(r"wi:([0-9a-f]{32})\Z")


class IntegrationError(RuntimeError):
    pass


def _run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise IntegrationError(f"command_failed:{args[0]}:{proc.stderr.strip() or proc.stdout.strip() or proc.returncode}")
    return proc.stdout.strip()


def _git(repo: Path, *args: str) -> str:
    return _run("git", "-C", str(repo), *args)


def _branch_name(task_id: str) -> str:
    match = WORK_ITEM.fullmatch(task_id)
    return "wi-" + match.group(1) if match else task_id


def _state_path(task_id: str) -> str:
    return f"operations/task-state/{_branch_name(task_id)}.md"


def _pr(prompt_id: str) -> dict | None:
    branch = "task/" + _branch_name(prompt_id)
    rows = json.loads(_run("gh", "pr", "list", "--repo", REPOSITORY,
        "--head", branch, "--state", "all", "--limit", "100",
        "--json", "number,state,headRefName,headRefOid,baseRefName,mergeCommit,body,isDraft,mergeable,statusCheckRollup,url"))
    matches = [row for row in rows if row.get("headRefName") == branch
               and row.get("baseRefName") == "main"]
    open_prs = [row for row in matches if row.get("state") == "OPEN"]
    if len(open_prs) > 1:
        raise IntegrationError("multiple_open_task_prs")
    return max(open_prs or matches, key=lambda row: int(row["number"])) if matches else None


def _marker(pr: dict) -> str | None:
    match = re.search(r"(?m)^C2-tested-head: ([0-9a-f]{40})$", str(pr.get("body") or ""))
    return match.group(1) if match else None


def _valid(prompt_id: str) -> None:
    if not PROMPT.fullmatch(prompt_id) and not WORK_ITEM.fullmatch(prompt_id):
        raise IntegrationError("invalid_prompt_id")


def _identity(repo: Path, prompt_id: str) -> str:
    if Path(_git(repo, "rev-parse", "--show-toplevel")).resolve() != repo.resolve():
        raise IntegrationError("worktree_root_mismatch")
    branch = "task/" + _branch_name(prompt_id)
    if _git(repo, "branch", "--show-current") != branch:
        raise IntegrationError("task_branch_mismatch")
    remote = _git(repo, "remote", "get-url", "origin")
    if not re.fullmatch(r"(?:https://github\.com/|git@github\.com:)gernalix/codex-roadmap(?:\.git)?", remote):
        raise IntegrationError("repository_mismatch")
    if _git(repo, "status", "--porcelain"):
        raise IntegrationError("task_worktree_dirty")
    head = _git(repo, "rev-parse", "HEAD")
    if not SHA.fullmatch(head):
        raise IntegrationError("invalid_task_head")
    return head


def status(prompt_id: str) -> dict:
    _valid(prompt_id)
    pr = _pr(prompt_id)
    if pr is None:
        return {"status": "no-task-record", "integration_state": "missing"}
    head = str(pr.get("headRefOid") or "")
    if not SHA.fullmatch(head):
        raise IntegrationError("pr_head_missing")
    marker = _marker(pr)
    if marker and marker != head:
        raise IntegrationError("tested_head_drift")
    if pr.get("state") == "MERGED":
        merge = str((pr.get("mergeCommit") or {}).get("oid") or "")
        if not SHA.fullmatch(merge):
            raise IntegrationError("merge_commit_missing")
        comparison = json.loads(_run("gh", "api", f"repos/{REPOSITORY}/compare/{merge}...main"))
        if comparison.get("status") not in ("ahead", "identical"):
            raise IntegrationError("merge_not_on_main")
        return {"status": "merged", "integration_state": "merged", "head_sha": head,
                "merge_sha": merge, "pr_number": pr["number"]}
    if pr.get("state") != "OPEN" or marker is None:
        raise IntegrationError("unmanaged_or_closed_task_pr")
    return {"status": "queued", "integration_state": "queued", "head_sha": head,
            "pr_number": pr["number"]}


def queue(repo: Path, prompt_id: str, *, expected_head: str | None = None) -> dict:
    _valid(prompt_id)
    repo = repo.expanduser().resolve()
    head = _identity(repo, prompt_id)
    if expected_head is not None and head != expected_head:
        raise IntegrationError("tested_head_drift")
    existing = _pr(prompt_id)
    update_existing = False
    if existing:
        result = status(prompt_id)
        prior = result.get("head_sha")
        if prior == head:
            return result
        if result.get("status") == "queued" and expected_head == head:
            # A caller that names the exact tested local HEAD may update an
            # existing managed PR; CI will rerun for that new head.
            update_existing = True
        elif result.get("status") != "merged":
            raise IntegrationError("task_pr_head_drift")
        if not update_existing:
            _git(repo, "merge-base", "--is-ancestor", str(prior), head)
            changed = set(_git(repo, "diff", "--name-only", str(prior), head).splitlines())
            if changed and changed <= {_state_path(prompt_id)}:
                return result
    branch = "task/" + _branch_name(prompt_id)
    remote = _git(repo, "ls-remote", "origin", "refs/heads/" + branch)
    remote_head = remote.split()[0] if remote else "0" * 40
    if remote_head != "0" * 40 and remote_head != head:
        _git(repo, "merge-base", "--is-ancestor", remote_head, head)
    _git(repo, "push", f"--force-with-lease=refs/heads/{branch}:{remote_head}",
         "origin", f"{head}:refs/heads/{branch}")
    is_work_item = WORK_ITEM.fullmatch(prompt_id) is not None
    pr_title = ("[single-writer] " if is_work_item else "[c2-roadmap] ") + prompt_id
    body = f"C2 codex-roadmap task {prompt_id}\n\nC2-tested-head: {head}\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md") as doc:
        doc.write(body)
        doc.flush()
        if update_existing:
            _run("gh", "pr", "edit", str(existing["number"]), "--repo", REPOSITORY,
                 "--title", pr_title, "--body-file", doc.name)
        else:
            _run("gh", "pr", "create", "--repo", REPOSITORY, "--base", "main",
                 "--head", branch, "--title", pr_title,
                 "--body-file", doc.name)
    result = status(prompt_id)
    if result.get("head_sha") != head:
        raise IntegrationError("queued_head_mismatch")
    return result


def integrate(prompt_id: str) -> dict:
    _valid(prompt_id)
    current = status(prompt_id)
    if current["status"] == "merged":
        return current
    if current["status"] != "queued":
        raise IntegrationError("task_pr_missing")
    pr = _pr(prompt_id)
    assert pr is not None
    if pr.get("isDraft") or pr.get("mergeable") != "MERGEABLE":
        raise IntegrationError("task_pr_not_mergeable")
    checks = pr.get("statusCheckRollup") or []
    if not checks or any(c.get("conclusion") not in ("SUCCESS", "NEUTRAL", "SKIPPED") for c in checks):
        raise IntegrationError("task_pr_checks_not_green")
    head = current["head_sha"]
    merged = json.loads(_run("gh", "api", "--method", "PUT",
        f"repos/{REPOSITORY}/pulls/{pr['number']}/merge", "-f", f"sha={head}",
        "-f", "merge_method=merge"))
    if not merged.get("merged"):
        raise IntegrationError("task_pr_merge_rejected")
    result = status(prompt_id)
    if result.get("head_sha") != head or result.get("merge_sha") != merged.get("sha"):
        raise IntegrationError("merged_head_mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("queue", "status", "integrate"))
    identity = parser.add_mutually_exclusive_group(required=True)
    identity.add_argument("--prompt-id")
    identity.add_argument("--work-item-id")
    parser.add_argument("--worktree", type=Path)
    parser.add_argument("--expected-head")
    args = parser.parse_args()
    try:
        if args.command == "queue":
            if args.worktree is None:
                raise IntegrationError("worktree_required")
            result = queue(args.worktree, args.prompt_id or args.work_item_id,
                           expected_head=args.expected_head)
        elif args.command == "integrate":
            result = integrate(args.prompt_id or args.work_item_id)
        else:
            result = status(args.prompt_id or args.work_item_id)
    except (IntegrationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
