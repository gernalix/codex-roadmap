#!/usr/bin/env python3
"""Guarded fast-forward pull for codex-roadmap.

Fetches first, compares the local and fetched remote roadmap, and refuses to
advance local main unless every running prompt is preserved or has an authoritative
terminal request / matching terminal Codex-usage execution proving it finished.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any

TERMINAL_OUTCOME = {
    "completed": "PASS",
    "failed": "FAIL",
    "blocked": "BLOCKED",
    "cancelled": "CANCELLED",
    "unknown": "UNKNOWN",
}
PROTECTED_COLUMNS = (
    "prompt_id",
    "slug",
    "title",
    "project_id",
    "project_name",
    "repo",
    "chat_guidance",
    "prompt_type",
    "model",
    "reasoning",
    "megavault_mode",
    "campaign_id",
    # explanation is presentation-only and may change while a prompt runs.
    # The canonical prompt body/materialization and execution metadata remain protected.
    "queue_position",
    "current_path",
    "materialization_sha256",
)


GENERATED_VIEW_ROOTS = (
    "roadmap.md",
    "spiegazioni.md",
    "prompt-registry.md",
)


class RoadmapPullBlocked(RuntimeError):
    pass


def _git(repo: Path, *args: str, binary: bool = False) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=not binary,
        check=False,
    )


def _git_ok(repo: Path, *args: str) -> str:
    proc = _git(repo, *args)
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise RoadmapPullBlocked(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    proc = _git(repo, *args, binary=True)
    if proc.returncode:
        detail = proc.stderr.decode(errors="replace").strip() or f"exit={proc.returncode}"
        raise RoadmapPullBlocked(f"git {' '.join(args)} failed: {detail}")
    return bytes(proc.stdout)


def _git_dir(repo: Path) -> Path:
    raw = _git_ok(repo, "rev-parse", "--git-dir")
    path = Path(raw)
    return path if path.is_absolute() else (repo / path).resolve()


def _nul_paths(raw: str) -> set[str]:
    return {part for part in raw.split("\0") if part}


def _tracked_dirty_paths(repo: Path) -> set[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
    ):
        paths.update(_nul_paths(_git_ok(repo, *args)))
    return paths


def _untracked_paths(repo: Path) -> set[str]:
    return _nul_paths(_git_ok(repo, "ls-files", "--others", "--exclude-standard", "-z"))


def _safe_c2_scratch(repo: Path, relative: str) -> bool:
    """Recognize only bounded, root-level C2 argument documents; preserve them."""
    if not re.fullmatch(r"\.c2-[a-z0-9][a-z0-9-]*-args\.json", relative):
        return False
    path = repo / relative
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        return False
    try:
        return isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
    except (OSError, UnicodeError, ValueError):
        return False


def _unsafe_untracked_paths(repo: Path) -> set[str]:
    return {path for path in _untracked_paths(repo) if not _safe_c2_scratch(repo, path)}


def _is_generated_view(path: str) -> bool:
    return path in GENERATED_VIEW_ROOTS or path.startswith("obsidian/")


def _restore_generated_view_dirt(repo: Path) -> list[str]:
    tracked = _tracked_dirty_paths(repo)
    untracked = _unsafe_untracked_paths(repo)
    non_generated = sorted(path for path in tracked if not _is_generated_view(path))
    if non_generated or untracked:
        details = non_generated + sorted(untracked)
        raise RoadmapPullBlocked(
            "local_worktree_dirty_non_generated:" + ",".join(details[:20])
        )

    generated = sorted(path for path in tracked if _is_generated_view(path))
    if generated:
        _git_ok(repo, "restore", "--staged", "--worktree", "--", *generated)
    return generated


def _require_clean_main(repo: Path, branch: str) -> tuple[str, list[str]]:
    current = _git_ok(repo, "branch", "--show-current")
    if current != branch:
        raise RoadmapPullBlocked(f"branch_mismatch:expected={branch}:actual={current or 'DETACHED'}")
    restored = _restore_generated_view_dirt(repo)
    if _tracked_dirty_paths(repo) or _unsafe_untracked_paths(repo):
        raise RoadmapPullBlocked("local_worktree_dirty_after_generated_restore")
    return _git_ok(repo, "rev-parse", "HEAD"), restored


def _recover_interrupted_fast_forward(repo: Path, before: str, remote_head: str) -> str | None:
    """Undo only an index/worktree that exactly matches a fetched remote commit.

    A rejected ref update can leave Git's fast-forward files staged while HEAD
    still points at `before`. A later worktree-only restore of roadmap.sqlite
    produces MM. Never discard an independent local DB edit or untracked file.
    """
    if _unsafe_untracked_paths(repo):
        return None
    if _git(repo, "merge-base", "--is-ancestor", before, remote_head).returncode:
        return None
    try:
        index_tree = _git_ok(repo, "write-tree")
        candidates = _git_ok(repo, "rev-list", f"{before}..{remote_head}").splitlines()
        candidate = next(
            (commit for commit in candidates if _git_ok(repo, "rev-parse", f"{commit}^{{tree}}") == index_tree),
            None,
        )
        if candidate is None:
            return None
        unstaged = _nul_paths(_git_ok(repo, "diff", "--name-only", "-z"))
        if unstaged - {"roadmap.sqlite"}:
            return None
        if "roadmap.sqlite" in unstaged:
            local_db = (repo / "roadmap.sqlite").read_bytes()
            if local_db not in (
                _git_bytes(repo, "show", f"{before}:roadmap.sqlite"),
                _git_bytes(repo, "show", ":roadmap.sqlite"),
            ):
                return None
        changed = sorted(_tracked_dirty_paths(repo))
        if "roadmap.sqlite" not in changed:
            return None
        _git_ok(repo, "restore", "--source=HEAD", "--staged", "--worktree", "--", *changed)
        return candidate
    except (OSError, RoadmapPullBlocked):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hook_paths(repo: Path) -> tuple[Path, Path]:
    source = repo / ".githooks" / "reference-transaction"
    target = (_git_dir(repo) / "roadmap-hooks" / "reference-transaction").resolve()
    return source, target


def _ensure_installed_hook(repo: Path) -> None:
    source, hook = _hook_paths(repo)
    expected = hook.parent
    configured = _git_ok(repo, "config", "--get", "core.hooksPath")
    if not configured:
        raise RoadmapPullBlocked("pull_guard_not_installed:run tools/install_roadmap_pull_guard.py")
    actual = Path(configured)
    if not actual.is_absolute():
        actual = (repo / actual).resolve()
    if (
        actual != expected
        or not source.is_file()
        or not hook.is_file()
        or not os.access(hook, os.X_OK)
        or _sha256(source) != _sha256(hook)
    ):
        raise RoadmapPullBlocked("pull_guard_stale_or_missing:run tools/install_roadmap_pull_guard.py")


def _install_hook_from_ref(repo: Path, ref: str) -> None:
    target = (_git_dir(repo) / "roadmap-hooks" / "reference-transaction").resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = _git_bytes(repo, "show", f"{ref}:.githooks/reference-transaction")
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(raw)
    os.chmod(tmp, 0o700)
    tmp.replace(target)
    _git_ok(repo, "config", "--local", "core.hooksPath", str(target.parent))
    _git_ok(repo, "config", "--local", "pull.ff", "only")


def _refresh_installed_hook(repo: Path) -> None:
    source, target = _hook_paths(repo)
    if not source.is_file():
        raise RoadmapPullBlocked("tracked_pull_guard_missing_after_merge")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    shutil.copyfile(source, tmp)
    os.chmod(tmp, 0o700)
    tmp.replace(target)


def _db_from_bytes(raw: bytes) -> tuple[tempfile.NamedTemporaryFile, sqlite3.Connection]:
    handle = tempfile.NamedTemporaryFile(suffix=".sqlite")
    handle.write(raw)
    handle.flush()
    try:
        conn = sqlite3.connect(f"file:{handle.name}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT 1 FROM prompts LIMIT 1").fetchall()
    except Exception:
        handle.close()
        raise
    return handle, conn


def _open_local_db(repo: Path) -> sqlite3.Connection:
    path = repo / "roadmap.sqlite"
    if not path.is_file():
        raise RoadmapPullBlocked("local_roadmap_db_missing")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row(conn: sqlite3.Connection, prompt_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone()


def _running_ids(conn: sqlite3.Connection) -> set[str]:
    return {str(r[0]) for r in conn.execute("SELECT prompt_id FROM prompts WHERE status='running'")}


def _protected_snapshot(conn: sqlite3.Connection, prompt_id: str) -> dict[str, Any]:
    row = _row(conn, prompt_id)
    if row is None:
        raise RoadmapPullBlocked(f"prompt_missing:{prompt_id}")
    snapshot: dict[str, Any] = {key: row[key] for key in PROTECTED_COLUMNS}
    snapshot["dependencies"] = [
        tuple(r)
        for r in conn.execute(
            "SELECT depends_on_prompt_id,note FROM dependencies WHERE prompt_id=? ORDER BY depends_on_prompt_id",
            (prompt_id,),
        )
    ]
    snapshot["tags"] = [
        str(r[0])
        for r in conn.execute("SELECT tag FROM prompt_tags WHERE prompt_id=? ORDER BY tag", (prompt_id,))
    ]
    snapshot["relations_from"] = [
        tuple(r)
        for r in conn.execute(
            "SELECT to_prompt_id,relation_type,note FROM prompt_relations WHERE from_prompt_id=? "
            "ORDER BY to_prompt_id,relation_type",
            (prompt_id,),
        )
    ]
    snapshot["relations_to"] = [
        tuple(r)
        for r in conn.execute(
            "SELECT from_prompt_id,relation_type,note FROM prompt_relations WHERE to_prompt_id=? "
            "ORDER BY from_prompt_id,relation_type",
            (prompt_id,),
        )
    ]
    return snapshot


def _terminal_confirmed(conn: sqlite3.Connection, prompt_id: str, remote_status: str) -> bool:
    if TERMINAL_OUTCOME.get(remote_status) is None:
        return False

    # Only the explicit roadmap finalizer can authorize a local running prompt
    # to advance to a remote terminal state. codex-usage is telemetry only.
    try:
        request = conn.execute(
            "SELECT requested_status FROM terminal_requests WHERE prompt_id=?",
            (prompt_id,),
        ).fetchone()
    except sqlite3.OperationalError:
        request = None
    return request is not None and str(request["requested_status"]) == remote_status


def _show_exists(repo: Path, ref: str, path: str) -> bool:
    return _git(repo, "cat-file", "-e", f"{ref}:{path}").returncode == 0


def _prompt_materialization(
    conn: sqlite3.Connection,
    prompt_id: str,
) -> sqlite3.Row | None:
    try:
        return conn.execute(
            "SELECT body,sha256 FROM prompt_materializations WHERE prompt_id=?",
            (prompt_id,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None


def _verify_remote_running_materialization(
    repo: Path,
    ref: str,
    conn: sqlite3.Connection,
    prompt_id: str,
) -> None:
    row = _row(conn, prompt_id)
    if row is None or row["status"] != "running":
        raise RoadmapPullBlocked(f"remote_running_row_invalid:{prompt_id}")
    materialization = _prompt_materialization(conn, prompt_id)
    if materialization is not None:
        expected = str(row["materialization_sha256"] or "")
        observed = str(materialization["sha256"] or "")
        if expected and observed != expected:
            raise RoadmapPullBlocked(
                f"remote_running_materialization_hash_mismatch:{prompt_id}"
            )
        if not str(materialization["body"] or "").strip():
            raise RoadmapPullBlocked(f"remote_running_materialization_empty:{prompt_id}")
        return

    # Transitional compatibility for roadmap DBs created before prompt bodies
    # became canonical SQLite data. No Markdown dashboard is consulted.
    path = str(row["current_path"] or "")
    if not path.startswith("prompts/") or not path.endswith(".md"):
        raise RoadmapPullBlocked(f"remote_running_path_invalid:{prompt_id}:{path}")
    if not _show_exists(repo, ref, path):
        raise RoadmapPullBlocked(f"remote_running_prompt_file_missing:{prompt_id}:{path}")


def _authorize_merge(repo: Path, old: str, new: str, branch: str) -> Path:
    path = _git_dir(repo) / "roadmap-pull-authorization.json"
    payload = {
        "ref": f"refs/heads/{branch}",
        "old": old,
        "new": new,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    return path


def guarded_pull(
    repo: Path,
    *,
    remote: str = "origin",
    branch: str = "main",
    bootstrap_guard: bool = False,
) -> dict[str, Any]:
    repo = repo.expanduser().resolve()
    fetched_head: str | None = None
    recovered_interrupted_fast_forward: str | None = None
    try:
        before, restored_generated_views = _require_clean_main(repo, branch)
    except RoadmapPullBlocked as exc:
        if not str(exc).startswith("local_worktree_dirty_non_generated:"):
            raise
        before = _git_ok(repo, "rev-parse", "HEAD")
        refspec = f"refs/heads/{branch}:refs/remotes/{remote}/{branch}"
        _git_ok(repo, "fetch", remote, refspec)
        fetched_head = _git_ok(repo, "rev-parse", f"{remote}/{branch}")
        recovered_interrupted_fast_forward = _recover_interrupted_fast_forward(
            repo, before, fetched_head
        )
        if recovered_interrupted_fast_forward is None:
            raise exc
        before, restored_generated_views = _require_clean_main(repo, branch)

    # Fetch is safe: it does not update the local main/worktree. Bootstrap mode
    # may install the guard from this exact fetched commit before any merge.
    if fetched_head is None:
        refspec = f"refs/heads/{branch}:refs/remotes/{remote}/{branch}"
        _git_ok(repo, "fetch", remote, refspec)
    remote_ref = f"{remote}/{branch}"
    remote_head = _git_ok(repo, "rev-parse", remote_ref)
    if bootstrap_guard:
        _install_hook_from_ref(repo, remote_head)
    else:
        _ensure_installed_hook(repo)

    ancestor = _git(repo, "merge-base", "--is-ancestor", before, remote_head)
    if ancestor.returncode:
        raise RoadmapPullBlocked(f"non_fast_forward:local={before}:remote={remote_head}")

    local_conn = _open_local_db(repo)
    remote_db = _git_bytes(repo, "show", f"{remote_head}:roadmap.sqlite")
    handle, remote_conn = _db_from_bytes(remote_db)
    try:
        local_running = _running_ids(local_conn)
        remote_running = _running_ids(remote_conn)
        preserved: list[str] = []
        terminal_confirmed: list[str] = []

        for prompt_id in sorted(remote_running):
            _verify_remote_running_materialization(
                repo, remote_head, remote_conn, prompt_id
            )

        for prompt_id in sorted(local_running):
            remote_row = _row(remote_conn, prompt_id)
            if remote_row is None:
                raise RoadmapPullBlocked(f"running_prompt_deleted_remote:{prompt_id}")
            if remote_row["status"] == "running":
                if _protected_snapshot(local_conn, prompt_id) != _protected_snapshot(remote_conn, prompt_id):
                    raise RoadmapPullBlocked(f"running_prompt_modified_remote:{prompt_id}")
                local_materialization = _prompt_materialization(local_conn, prompt_id)
                remote_materialization = _prompt_materialization(remote_conn, prompt_id)
                if local_materialization is not None and remote_materialization is not None:
                    if (
                        local_materialization["sha256"] != remote_materialization["sha256"]
                        or local_materialization["body"] != remote_materialization["body"]
                    ):
                        raise RoadmapPullBlocked(
                            f"running_prompt_content_modified_remote:{prompt_id}"
                        )
                else:
                    # Transitional compatibility until the first writer mutation
                    # backfills prompt_materializations in the canonical DB.
                    local_path = str(_row(local_conn, prompt_id)["current_path"])
                    local_blob = _git_bytes(repo, "show", f"{before}:{local_path}")
                    remote_blob = _git_bytes(repo, "show", f"{remote_head}:{local_path}")
                    if local_blob != remote_blob:
                        raise RoadmapPullBlocked(
                            f"running_prompt_content_modified_remote:{prompt_id}"
                        )
                preserved.append(prompt_id)
            elif _terminal_confirmed(remote_conn, prompt_id, str(remote_row["status"])):
                terminal_confirmed.append(prompt_id)
            else:
                raise RoadmapPullBlocked(
                    f"running_prompt_not_preserved:{prompt_id}:remote_status={remote_row['status']}"
                )

        # A locally terminal prompt must never reappear as running remotely.
        for prompt_id in sorted(remote_running - local_running):
            local_row = _row(local_conn, prompt_id)
            if local_row is not None and local_row["status"] not in ("pending", "running"):
                raise RoadmapPullBlocked(
                    f"terminal_prompt_reactivated_remote:{prompt_id}:{local_row['status']}"
                )

        auth = _authorize_merge(repo, before, remote_head, branch)
        try:
            merge = _git(repo, "merge", "--ff-only", remote_head)
            if merge.returncode:
                detail = merge.stderr.strip() or merge.stdout.strip() or f"exit={merge.returncode}"
                raise RoadmapPullBlocked(f"guarded_merge_failed:{detail}")
        finally:
            auth.unlink(missing_ok=True)

        after = _git_ok(repo, "rev-parse", "HEAD")
        if after != remote_head:
            raise RoadmapPullBlocked(f"post_pull_head_mismatch:{after}:{remote_head}")
        if _tracked_dirty_paths(repo) or _unsafe_untracked_paths(repo):
            raise RoadmapPullBlocked("post_pull_worktree_dirty")

        # Keep the non-worktree hook copy synchronized if the tracked hook changed.
        _refresh_installed_hook(repo)

        post_conn = _open_local_db(repo)
        try:
            for prompt_id in sorted(remote_running):
                row = _row(post_conn, prompt_id)
                if row is None or row["status"] != "running":
                    raise RoadmapPullBlocked(f"post_pull_running_lost:{prompt_id}")
        finally:
            post_conn.close()

        return {
            "status": "PASS",
            "before_head": before,
            "head": after,
            "preserved_running": preserved,
            "remote_running": sorted(remote_running),
            "terminal_confirmed": terminal_confirmed,
            "restored_generated_views": restored_generated_views,
            "recovered_interrupted_fast_forward": recovered_interrupted_fast_forward,
        }
    finally:
        local_conn.close()
        remote_conn.close()
        handle.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("~/projects/codex-roadmap"))
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument(
        "--bootstrap-guard",
        action="store_true",
        help="One-time bootstrap: install the guard from the fetched remote commit before merging.",
    )
    args = parser.parse_args(argv)
    try:
        result = guarded_pull(
            args.repo,
            remote=args.remote,
            branch=args.branch,
            bootstrap_guard=args.bootstrap_guard,
        )
    except RoadmapPullBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
