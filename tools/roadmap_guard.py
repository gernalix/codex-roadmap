#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PROMPT_LINK_RE = re.compile(r"^\s*\d+\.\s+\[\[prompts/([^|\]]+)(?:\|[^\]]+)?\]\]\s*$")
PROMPT_ID_RE = re.compile(r"\bPROMPT_ID=(\d{6})\b")
REASONING_RE = re.compile(r"\breasoning=([a-z_]+)\b", re.I)

EXECUTION_CONTRACT = (
    "Use prompt_content as the complete selected task. Do not reread roadmap.md, "
    "spiegazioni.md, README.md, or the prompt file unless this pack is inconsistent "
    "or a concrete blocker requires it. Do not read MEMORY/history or run roadmap "
    "preflight pwd/ls/status/pull/fetch: select already fetched canonical origin/main. "
    "Do not inspect later prompts. Reuse verified session evidence, keep exploration "
    "and tests targeted, group independent checks into one tool call when safe, avoid "
    "equivalent retries, and stop at PASS/BLOCKED/FAIL. For long-running commands, "
    "prefer one blocking wait or sparse status checks and do not narrate unchanged "
    "polls. On PASS run dry-run and real complete in one shell invocation when possible. "
    "If implementation was already pushed but complete reports prompt_identity_mismatch "
    "because the roadmap advanced, use reconcile --dry-run and then reconcile "
    "--confirm-executed; never reproduce roadmap bookkeeping manually. A successful "
    "complete or reconcile response with push_verified=git_push_exit_0 is authoritative "
    "proof of roadmap push success; do not run follow-up git status/rev-parse/ls-remote "
    "on the roadmap checkout."
)


class RoadmapError(RuntimeError):
    pass


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RoadmapError(f"git_{args[0]}_failed:{result.stderr.strip()}")
    return result


def git_root(path: Path) -> Path:
    result = run(path, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip())


def fetch_canonical(repo: Path) -> None:
    run(repo, "fetch", "--quiet", "origin", "main")


def remote_text(repo: Path, path: str) -> str:
    result = run(repo, "show", f"origin/main:{path}")
    return result.stdout


def _metadata_value(prompt: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}=([^|`\n]+)", prompt)
    return match.group(1).strip() if match else ""


def _prompt_payload(repo: Path, name: str, path: str, *, include_prompt: bool = False) -> dict[str, str]:
    prompt = remote_text(repo, path)
    prompt_id_match = PROMPT_ID_RE.search(prompt)
    if not prompt_id_match:
        raise RoadmapError(f"prompt_id_missing:{path}")
    reasoning_match = REASONING_RE.search(prompt)
    prompt_type = ""
    if path.startswith("prompts/"):
        explanation = remote_text(repo, "spiegazioni.md")
        row = next(
            (
                line
                for line in explanation.splitlines()
                if f"[[prompts/{name}|" in line or f"[[prompts/{name}]]" in line
            ),
            "",
        )
        type_match = re.search(r"\|\s*(Prompt|Goal)\s*\|\s*$", row) if row else None
        prompt_type = type_match.group(1) if type_match else ""
    payload = {
        "name": name,
        "path": path,
        "prompt_id": prompt_id_match.group(1),
        "project_id": _metadata_value(prompt, "project_id"),
        "model": _metadata_value(prompt, "model"),
        "reasoning": reasoning_match.group(1) if reasoning_match else "",
        "megavault": _metadata_value(prompt, "MegaVault"),
        "campaign_id": _metadata_value(prompt, "campaign_id"),
        "type": prompt_type,
        "source": "origin/main",
    }
    if include_prompt:
        payload["execution_contract"] = EXECUTION_CONTRACT
        payload["prompt_content"] = prompt
    return payload


def first_prompt(repo: Path, *, include_prompt: bool = False, fetch: bool = True) -> dict[str, str]:
    if fetch:
        fetch_canonical(repo)
    roadmap = remote_text(repo, "roadmap.md")
    first_name: str | None = None
    for line in roadmap.splitlines():
        match = PROMPT_LINK_RE.match(line)
        if match:
            first_name = match.group(1)
            break
    if not first_name:
        raise RoadmapError("roadmap_empty_or_invalid")
    return _prompt_payload(repo, first_name, f"prompts/{first_name}.md", include_prompt=include_prompt)


def _prompt_by_id(repo: Path, prompt_id: str, *, fetch: bool = True) -> tuple[dict[str, str], str]:
    if fetch:
        fetch_canonical(repo)
    grep = run(
        repo,
        "grep",
        "-l",
        "-F",
        f"PROMPT_ID={prompt_id}",
        "origin/main",
        "--",
        "prompts",
        "completed",
        check=False,
    )
    if grep.returncode not in (0, 1):
        raise RoadmapError(f"git_grep_failed:{grep.stderr.strip()}")
    candidates: list[tuple[str, str]] = []
    for raw in grep.stdout.splitlines():
        path = raw.split(":", 1)[1] if raw.startswith("origin/main:") else raw
        if not (path.startswith("prompts/") or path.startswith("completed/")):
            continue
        prompt = remote_text(repo, path)
        match = PROMPT_ID_RE.search(prompt)
        if match and match.group(1) == prompt_id:
            candidates.append((path, prompt))
    if not candidates:
        raise RoadmapError(f"prompt_id_not_found:{prompt_id}")
    if len(candidates) != 1:
        raise RoadmapError(
            f"prompt_id_ambiguous:{prompt_id}:" + ",".join(sorted(path for path, _ in candidates))
        )
    path, _ = candidates[0]
    name = Path(path).stem
    location = "completed" if path.startswith("completed/") else "pending"
    payload = _prompt_payload(repo, name, path)
    if payload["prompt_id"] != prompt_id:
        raise RoadmapError(f"prompt_identity_mismatch:requested={prompt_id}:found={payload['prompt_id']}")
    return payload, location


def _renumber_roadmap(text: str, completed_name: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        match = PROMPT_LINK_RE.match(line)
        if match and match.group(1) == completed_name:
            continue
        if match:
            kept.append(match.group(1))
    return "".join(f"{idx}. [[prompts/{name}|{name}]]\n" for idx, name in enumerate(kept, 1))


def _remove_explanation_row(text: str, completed_name: str) -> str:
    output: list[str] = []
    counter = 0
    for line in text.splitlines():
        if f"[[prompts/{completed_name}|" in line or f"[[prompts/{completed_name}]]" in line:
            continue
        if re.match(r"^\|\s*\d+\s*\|", line):
            counter += 1
            line = re.sub(r"^\|\s*\d+\s*\|", f"| {counter} |", line, count=1)
        output.append(line)
    return "\n".join(output).rstrip() + "\n"


def _finalize_prompt(repo: Path, target: dict[str, str], *, commit_message: str) -> dict[str, str]:
    parent = Path(tempfile.mkdtemp(prefix="codex-roadmap-"))
    worktree = parent / "worktree"
    keep_on_failure = False
    try:
        run(repo, "worktree", "add", "--detach", str(worktree), "origin/main")
        source = worktree / target["path"]
        destination = worktree / "completed" / source.name
        if not source.is_file():
            raise RoadmapError("target_prompt_missing_in_isolated_worktree")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise RoadmapError("target_prompt_already_exists_in_completed")
        source.rename(destination)

        roadmap_path = worktree / "roadmap.md"
        explanations_path = worktree / "spiegazioni.md"
        roadmap_path.write_text(
            _renumber_roadmap(roadmap_path.read_text(encoding="utf-8"), target["name"]),
            encoding="utf-8",
        )
        explanations_path.write_text(
            _remove_explanation_row(explanations_path.read_text(encoding="utf-8"), target["name"]),
            encoding="utf-8",
        )

        status = run(worktree, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        changed_paths = {line[3:] for line in status if len(line) >= 4}
        allowed = {target["path"], f"completed/{source.name}", "roadmap.md", "spiegazioni.md"}
        if any(path not in allowed for path in changed_paths):
            raise RoadmapError("unexpected_task_owned_diff:" + ",".join(sorted(changed_paths - allowed)))

        run(worktree, "add", target["path"], f"completed/{source.name}", "roadmap.md", "spiegazioni.md")
        staged = run(worktree, "diff", "--cached", "--name-only").stdout.splitlines()
        if not staged or any(path not in allowed for path in staged):
            raise RoadmapError("staged_scope_invalid:" + ",".join(staged))
        run(worktree, "commit", "-m", commit_message)
        sha = run(worktree, "rev-parse", "HEAD").stdout.strip()
        push = run(worktree, "push", "origin", "HEAD:main", check=False)
        if push.returncode != 0:
            keep_on_failure = True
            raise RoadmapError(f"push_blocked:{push.stderr.strip()}:isolated_worktree={worktree}")
        return {**target, "status": "completed", "commit": sha, "push_verified": "git_push_exit_0"}
    finally:
        if worktree.exists() and not keep_on_failure:
            run(repo, "worktree", "remove", "--force", str(worktree), check=False)
            shutil.rmtree(parent, ignore_errors=True)


def complete(repo: Path, prompt_id: str, *, dry_run: bool = False) -> dict[str, str]:
    selected = first_prompt(repo)
    if selected["prompt_id"] != prompt_id:
        raise RoadmapError(
            f"prompt_identity_mismatch:selected={selected['prompt_id']}:requested={prompt_id}:"
            f"if_requested_task_is_already_executed_use_reconcile"
        )
    if dry_run:
        return {**selected, "status": "ready"}
    return _finalize_prompt(repo, selected, commit_message=f"Complete roadmap prompt {prompt_id}")


def reconcile(
    repo: Path,
    prompt_id: str,
    *,
    dry_run: bool = False,
    confirm_executed: bool = False,
) -> dict[str, str]:
    target, location = _prompt_by_id(repo, prompt_id)
    if location == "completed":
        return {**target, "status": "already_completed", "mode": "reconcile"}

    roadmap = remote_text(repo, "roadmap.md")
    pending_names = [
        match.group(1)
        for line in roadmap.splitlines()
        if (match := PROMPT_LINK_RE.match(line)) is not None
    ]
    if target["name"] not in pending_names:
        raise RoadmapError(f"pending_prompt_missing_from_roadmap:{target['name']}")

    selected = first_prompt(repo, fetch=False)
    if selected["prompt_id"] == prompt_id:
        raise RoadmapError("prompt_is_selected_use_complete")
    context = {
        **target,
        "mode": "reconcile",
        "selected_prompt_id": selected["prompt_id"],
        "selected_prompt_name": selected["name"],
    }
    if dry_run:
        return {**context, "status": "reconcile_ready"}
    if not confirm_executed:
        raise RoadmapError("reconcile_requires_confirm_executed")
    result = _finalize_prompt(repo, target, commit_message=f"Reconcile completed roadmap prompt {prompt_id}")
    return {**result, "mode": "reconcile", "selected_prompt_id": selected["prompt_id"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read/finalize codex-roadmap without touching local worktree state.")
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("select")
    complete_p = sub.add_parser("complete")
    complete_p.add_argument("--prompt-id", required=True)
    complete_p.add_argument("--dry-run", action="store_true")
    reconcile_p = sub.add_parser(
        "reconcile",
        help="Archive an already-executed pending prompt that is no longer selected.",
    )
    reconcile_p.add_argument("--prompt-id", required=True)
    reconcile_p.add_argument("--dry-run", action="store_true")
    reconcile_p.add_argument(
        "--confirm-executed",
        action="store_true",
        help="Required for a mutating reconciliation; confirms implementation already completed elsewhere.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = git_root(Path(args.repo).expanduser())
        if args.cmd == "select":
            payload = first_prompt(repo, include_prompt=True)
        elif args.cmd == "complete":
            payload = complete(repo, args.prompt_id, dry_run=args.dry_run)
        else:
            payload = reconcile(
                repo,
                args.prompt_id,
                dry_run=args.dry_run,
                confirm_executed=args.confirm_executed,
            )
    except RoadmapError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
