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


class RoadmapError(RuntimeError):
    pass


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
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


def first_prompt(repo: Path) -> dict[str, str]:
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
    prompt_path = f"prompts/{first_name}.md"
    prompt = remote_text(repo, prompt_path)
    prompt_id_match = PROMPT_ID_RE.search(prompt)
    if not prompt_id_match:
        raise RoadmapError("prompt_id_missing")
    reasoning_match = REASONING_RE.search(prompt)
    explanation = remote_text(repo, "spiegazioni.md")
    row = next((line for line in explanation.splitlines() if f"[[prompts/{first_name}|" in line or f"[[prompts/{first_name}]]" in line), "")
    type_match = re.search(r"\|\s*(Prompt|Goal)\s*\|\s*$", row) if row else None
    prompt_type = type_match.group(1) if type_match else ""
    return {
        "name": first_name,
        "path": prompt_path,
        "prompt_id": prompt_id_match.group(1),
        "reasoning": reasoning_match.group(1) if reasoning_match else "",
        "type": prompt_type,
        "source": "origin/main",
    }


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


def complete(repo: Path, prompt_id: str, *, dry_run: bool = False) -> dict[str, str]:
    selected = first_prompt(repo)
    if selected["prompt_id"] != prompt_id:
        raise RoadmapError(f"prompt_identity_mismatch:selected={selected['prompt_id']}:requested={prompt_id}")
    if dry_run:
        return {**selected, "status": "ready"}

    parent = Path(tempfile.mkdtemp(prefix="codex-roadmap-"))
    worktree = parent / "worktree"
    keep_on_failure = False
    try:
        run(repo, "worktree", "add", "--detach", str(worktree), "origin/main")
        source = worktree / selected["path"]
        destination = worktree / "completed" / source.name
        if not source.is_file():
            raise RoadmapError("selected_prompt_missing_in_isolated_worktree")
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)

        roadmap_path = worktree / "roadmap.md"
        explanations_path = worktree / "spiegazioni.md"
        roadmap_path.write_text(_renumber_roadmap(roadmap_path.read_text(encoding="utf-8"), selected["name"]), encoding="utf-8")
        explanations_path.write_text(_remove_explanation_row(explanations_path.read_text(encoding="utf-8"), selected["name"]), encoding="utf-8")

        status = run(worktree, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        changed_paths = {line[3:] for line in status if len(line) >= 4}
        allowed = {selected["path"], f"completed/{source.name}", "roadmap.md", "spiegazioni.md"}
        if any(path not in allowed for path in changed_paths):
            raise RoadmapError("unexpected_task_owned_diff:" + ",".join(sorted(changed_paths - allowed)))

        run(worktree, "add", selected["path"], f"completed/{source.name}", "roadmap.md", "spiegazioni.md")
        staged = run(worktree, "diff", "--cached", "--name-only").stdout.splitlines()
        if not staged or any(path not in allowed for path in staged):
            raise RoadmapError("staged_scope_invalid:" + ",".join(staged))
        run(worktree, "commit", "-m", f"Complete roadmap prompt {prompt_id}")
        sha = run(worktree, "rev-parse", "HEAD").stdout.strip()
        push = run(worktree, "push", "origin", "HEAD:main", check=False)
        if push.returncode != 0:
            keep_on_failure = True
            raise RoadmapError(f"push_blocked:{push.stderr.strip()}:isolated_worktree={worktree}")
        return {**selected, "status": "completed", "commit": sha}
    finally:
        if worktree.exists() and not keep_on_failure:
            run(repo, "worktree", "remove", "--force", str(worktree), check=False)
            shutil.rmtree(parent, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read/finalize codex-roadmap without touching local worktree state.")
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("select")
    complete_p = sub.add_parser("complete")
    complete_p.add_argument("--prompt-id", required=True)
    complete_p.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = git_root(Path(args.repo).expanduser())
        if args.cmd == "select":
            payload = first_prompt(repo)
        else:
            payload = complete(repo, args.prompt_id, dry_run=args.dry_run)
    except RoadmapError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
