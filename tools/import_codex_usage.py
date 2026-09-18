#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from roadmap_db import (
    RoadmapDBError,
    connect,
    ensure_historical_stub,
    FINAL_STATUS,
    materialization_hash,
    now_utc,
    prompt_row,
    record_execution,
    reconcile_prompt_file_locations,
    render,
)

def normalized_prompt_hash(text: str) -> str:
    return materialization_hash(text)

def import_metrics(repo: Path, source: Path, *, render_after: bool = True) -> dict[str, int]:
    source = Path(source)
    files = sorted(source.glob("prompts/*/metrics.json"))
    conn = connect(repo)
    stats = {"files":0,"inserted":0,"existing":0,"stubs":0,"conflicts":0,"updated_status":0,"skipped":0}
    try:
        for path in files:
            stats["files"] += 1
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                stats["skipped"] += 1
                continue
            prompt_id = str(data.get("prompt_id") or path.parent.name)
            if not re.fullmatch(r"\d{6}", prompt_id):
                stats["skipped"] += 1
                continue
            existing_prompt = conn.execute("SELECT * FROM prompts WHERE prompt_id=?", (prompt_id,)).fetchone()
            if not existing_prompt:
                ensure_historical_stub(
                    conn, prompt_id,
                    title=f"Historical prompt {prompt_id}",
                    status="unknown",
                    actor="codex-usage-import",
                )
                stats["stubs"] += 1
                existing_prompt = prompt_row(conn, prompt_id)

            observed_hash = normalized_prompt_hash(str(data.get("prompt_text_redacted") or ""))
            expected_hash = existing_prompt["materialization_sha256"]
            cycle_key = str(data.get("cycle_key") or "") or None
            # A strict mismatch is recorded but does not overwrite the prompt's state.
            conflict = bool(expected_hash and data.get("prompt_text_redacted") and expected_hash != observed_hash)
            if conflict:
                conn.execute(
                    """INSERT OR IGNORE INTO identity_conflicts(
                         prompt_id,observed_cycle_key,expected_sha256,observed_sha256,detected_at,source
                       ) VALUES(?,?,?,?,?,?)""",
                    (prompt_id, cycle_key, expected_hash, observed_hash, now_utc(), str(path)),
                )
                stats["conflicts"] += 1

            if cycle_key and conn.execute("SELECT 1 FROM executions WHERE cycle_key=?", (cycle_key,)).fetchone():
                stats["existing"] += 1
                continue

            status = str(data.get("status") or "UNKNOWN").upper()
            outcome = status if status in FINAL_STATUS else "UNKNOWN"
            before = prompt_row(conn,prompt_id)["status"]
            record_execution(
                conn,
                prompt_id,
                cycle_key=cycle_key,
                materialization_sha256=observed_hash if data.get("prompt_text_redacted") else None,
                started_at=data.get("timestamp_start_utc"),
                ended_at=data.get("timestamp_end_utc"),
                outcome=outcome,
                duration_seconds=data.get("duration_seconds"),
                model=data.get("model"),
                reasoning=data.get("reasoning_effort"),
                codex_project=data.get("repo_project"),
                tool_call_count=data.get("tool_call_count"),
                input_tokens=data.get("input_tokens"),
                cached_input_tokens=data.get("cached_input_tokens"),
                uncached_input_tokens=data.get("uncached_input_tokens"),
                output_tokens=data.get("output_tokens"),
                reasoning_output_tokens=data.get("reasoning_output_tokens"),
                total_tokens=data.get("total_tokens"),
                source="codex-usage",
                actor="codex",
                update_status=not conflict,
            )
            after = prompt_row(conn,prompt_id)["status"]
            if before != after:
                stats["updated_status"] += 1
            stats["inserted"] += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    stats["archived_files"] = reconcile_prompt_file_locations(repo)
    if render_after:
        render(repo)
    return stats


def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Backfill/reconcile roadmap.sqlite from codex-usage prompt metrics.")
    p.add_argument("--repo",default=".")
    p.add_argument("--source",required=True)
    p.add_argument("--no-render",action="store_true")
    return p

def main(argv: list[str] | None=None) -> int:
    args=build_parser().parse_args(argv)
    stats=import_metrics(Path(args.repo).expanduser().resolve(),Path(args.source).expanduser().resolve(),render_after=not args.no_render)
    print(json.dumps(stats,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
