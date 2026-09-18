#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from roadmap_db import connect, db_path, refresh_materialization_hashes, render

def bootstrap(repo: Path) -> dict[str, object]:
    repo=Path(repo)
    created=not db_path(repo).exists()
    seed=None
    if created:
        seed=json.loads((repo/"seed"/"initial-roadmap.json").read_text(encoding="utf-8"))
        if seed.get("schema")!="codex-roadmap.seed.v1":
            raise ValueError("invalid_seed_schema")
    conn=connect(repo)
    try:
        if created:
            for p in seed["prompts"]:
                cols=list(p)
                conn.execute(
                    f"INSERT INTO prompts({','.join(cols)}) VALUES({','.join('?' for _ in cols)})",
                    [p[c] for c in cols],
                )
            for dep in seed.get("dependencies",[]):
                conn.execute("INSERT INTO dependencies(prompt_id,depends_on_prompt_id,note) VALUES(?,?,?)",
                             (dep["prompt_id"],dep["depends_on_prompt_id"],dep.get("note")))
            for rel in seed.get("relations",[]):
                conn.execute(
                    "INSERT INTO prompt_relations(from_prompt_id,to_prompt_id,relation_type,created_at,actor,note) VALUES(?,?,?,?,?,?)",
                    (rel["from_prompt_id"],rel["to_prompt_id"],rel["relation_type"],rel["created_at"],rel["actor"],rel.get("note")),
                )
            for tag in seed.get("tags",[]):
                conn.execute("INSERT INTO prompt_tags(prompt_id,tag) VALUES(?,?)",(tag["prompt_id"],tag["tag"]))
        hashes=refresh_materialization_hashes(conn,repo)
        conn.commit()
    except Exception:
        conn.rollback()
        if created:
            db_path(repo).unlink(missing_ok=True)
        raise
    finally:
        conn.close()
    if created or hashes:
        render(repo)
    return {
        "status":"created" if created else "exists",
        "database":str(db_path(repo)),
        "prompts":len(seed["prompts"]) if created else None,
        "materialization_hashes_added":hashes,
    }

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo",default="."); a=p.parse_args(argv)
    print(json.dumps(bootstrap(Path(a.repo).expanduser().resolve()),sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
