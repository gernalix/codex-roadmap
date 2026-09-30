"""Bounded Codex fallback for the canonical C2 issue-triage run."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

REPO = Path.home() / "projects/codex-roadmap"
RUNTIME_ENV = Path.home() / ".config/c2-supervisor/runtime.env"
SYNC = Path.home() / ".local/share/c2-supervisor/worktree/tools/c2_snapshot_sync.py"
CODEX = Path.home() / ".local/bin/codex"
LOG = Path.home() / ".local/state/c2/inbox-drain-codex.log"
DEFAULT_BATCH = 25

PROMPT = """You are the semantic executor for the existing C2 issue-triage work item.
Do not create a supervisor, run, Goal or task. Reuse the current fenced authority from
/home/daniele/.config/c2-supervisor/runtime.env.

Process up to {batch} rows from v_issue_inbox_pending_ordered, strictly in displayed order.
For each row, read only minimum canonical context and decide promote/discard plus complete
human-facing copy. Active match => promote into it with evidence. Completed match =>
create/promote a regression successor. Discard only irrelevant/obsolete/duplicate captures
with a concrete reason. Ambiguous input => leave it pending; never guess. Do not implement
roadmap work or dispatch workers.

Minimize writer round-trips. Build ordered operation batches shaped as
{{"operation":"promote_issue|discard_issue","arguments":{{...}}}} and use
c2_control.submit_controls(..., canonical_renew=True) for independent dispositions,
especially discards and promotions into already-known work-item IDs. If a later row depends
on the new work-item ID created by an earlier row in this same batch, flush the current batch,
verify its writer receipt, refresh the snapshot, then continue; never guess a generated ID.
Use single submit_control only at such dependency boundaries. Preserve one human-facing
copy/evidence disposition per row. If a bulk writer receipt is rejected, split that batch
and retry only its unchanged dispositions until the invalid/conflicting row is isolated;
do not reprocess rows whose writer receipt already applied. Stop after {batch} rows or an empty Inbox.
If the Inbox is empty at the start or becomes empty in this batch, perform the canonical
post-drain reconciliation required by this work item's objective and acceptance criteria.
Then submit c2_record_checkpoint through the fenced control path with the exact acceptance
criteria in completed, remaining=[], blocker=null, concrete evidence, and one next_action.
Do not claim completion until that checkpoint is writer-applied.
C2_RUN_ID={run_id}
C2_WORK_ITEM_ID={work_item_id}
"""


def _env() -> dict[str, str]:
    env = os.environ.copy()
    for raw in RUNTIME_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            env[key] = value
    return env


def _sync(env: dict[str, str]) -> None:
    proc = subprocess.run(
        ["python3", str(SYNC)], cwd=REPO, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90,
    )
    if proc.returncode:
        raise RuntimeError("snapshot_sync_failed")


def _pending(db_path: Path) -> int:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return int(conn.execute(
            "SELECT COUNT(*) FROM v_issue_inbox_pending_ordered"
        ).fetchone()[0])
    finally:
        conn.close()


def _completion_ready(db_path: Path, work_item_id: str) -> bool:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        item = conn.execute(
            "SELECT acceptance_json FROM work_items WHERE work_item_id=?", (work_item_id,)
        ).fetchone()
        cp = conn.execute("""SELECT completed_json,remaining_json,evidence_json,blocker
            FROM work_item_checkpoints WHERE work_item_id=? AND source_file='c2-writer'
            ORDER BY checkpoint_id DESC LIMIT 1""", (work_item_id,)).fetchone()
        if not item or not cp or cp["blocker"]:
            return False
        acceptance = set(json.loads(item["acceptance_json"] or "[]"))
        completed = set(json.loads(cp["completed_json"] or "[]"))
        remaining = json.loads(cp["remaining_json"] or "[]")
        evidence = json.loads(cp["evidence_json"] or "[]")
        return bool(acceptance) and acceptance.issubset(completed) and not remaining and bool(evidence)
    finally:
        conn.close()


def execute(*, run_id: str, work_item_id: str, db_path: Path,
            batch: int = DEFAULT_BATCH) -> dict:
    env = _env()
    _sync(env)
    before = _pending(db_path)
    if before == 0 and _completion_ready(db_path, work_item_id):
        return {"state": "complete", "before": 0, "after": 0, "returncode": 0}
    prompt = PROMPT.format(batch=batch, run_id=run_id, work_item_id=work_item_id)
    cmd = [
        str(CODEX), "exec", "-m", "gpt-6-luna",
        "-c", 'model_reasoning_effort="medium"',
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check", "--ephemeral", "-C", str(REPO), "-",
    ]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8", buffering=1) as stream:
        stream.write("\n\n=== C2 Inbox Codex fallback " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\n")
        proc = subprocess.run(
            cmd, input=prompt, text=True, env=env, cwd=REPO,
            stdout=stream, stderr=subprocess.STDOUT, timeout=3000,
        )
    _sync(env)
    after = _pending(db_path)
    ready = after == 0 and _completion_ready(db_path, work_item_id)
    if ready:
        state = "complete"
    elif after == 0:
        state = "finalizing"
    elif after < before:
        state = "progress"
    else:
        state = "blocked"
    return {
        "state": state,
        "before": before,
        "after": after,
        "returncode": int(proc.returncode),
    }
