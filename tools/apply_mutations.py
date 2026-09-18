#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from roadmap_db import apply_mutation, connect, reconcile_prompt_file_locations, render

SCHEMA = "codex-roadmap.mutation.v1"

def apply_inbox(repo: Path) -> dict[str, int]:
    repo=Path(repo)
    inbox=repo/"mutations"/"inbox"
    applied=repo/"mutations"/"applied"
    inbox.mkdir(parents=True,exist_ok=True)
    applied.mkdir(parents=True,exist_ok=True)
    files=sorted(inbox.glob("*.json"))
    conn=connect(repo)
    count=0
    try:
        for path in files:
            doc=json.loads(path.read_text(encoding="utf-8"))
            if doc.get("schema") != SCHEMA:
                raise ValueError(f"invalid_mutation_schema:{path.name}")
            actor=str(doc.get("actor") or "chatgpt")
            ops=doc.get("operations")
            if not isinstance(ops,list) or not ops:
                raise ValueError(f"empty_mutation:{path.name}")
            for op in ops:
                if not isinstance(op,dict):
                    raise ValueError(f"invalid_operation:{path.name}")
                apply_mutation(conn,op,default_actor=actor)
                count += 1
            target=applied/path.name
            if target.exists():
                raise ValueError(f"applied_mutation_exists:{target.name}")
            shutil.move(str(path),str(target))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    if files:
        reconcile_prompt_file_locations(repo)
        render(repo)
    return {"files":len(files),"operations":count}

def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    args=p.parse_args(argv)
    print(json.dumps(apply_inbox(Path(args.repo).expanduser().resolve()),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
