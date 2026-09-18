#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from roadmap_db import connect, db_path, render

def bootstrap(repo: Path) -> dict[str, object]:
    repo=Path(repo)
    if db_path(repo).exists():
        return {"status":"exists","database":str(db_path(repo))}
    seed=json.loads((repo/"seed"/"initial-roadmap.json").read_text(encoding="utf-8"))
    if seed.get("schema")!="codex-roadmap.seed.v1":
        raise ValueError("invalid_seed_schema")
    conn=connect(repo)
    try:
        for p in seed["prompts"]:
            cols=list(p)
            conn.execute(
                f"INSERT INTO prompts({','.join(cols)}) VALUES({','.join('?' for _ in cols)})",
                [p[c] for c in cols],
            )
        for d in seed.get("dependencies",[]):
            conn.execute("INSERT INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
                         (d["prompt_id"],d["depends_on_prompt_id"],d.get("note")))
        for r in seed.get("relations",[]):
            conn.execute(
                "INSERT INTO prompt_relations(from_prompt_id,to_prompt_id,relation_type,created_at,actor,note) VALUES(?,?,?,?,?,?)",
                (r["from_prompt_id"],r["to_prompt_id"],r["relation_type"],r["created_at"],r["actor"],r.get("note")),
            )
        for t in seed.get("tags",[]):
            conn.execute("INSERT INTO prompt_tags(prompt_id,tag) VALUES(?,?)",(t["prompt_id"],t["tag"]))
        conn.commit()
    except Exception:
        conn.rollback()
        db_path(repo).unlink(missing_ok=True)
        raise
    finally:
        conn.close()
    render(repo)
    return {"status":"created","prompts":len(seed["prompts"])}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo",default="."); a=p.parse_args(argv)
    print(json.dumps(bootstrap(Path(a.repo).expanduser().resolve()),sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
