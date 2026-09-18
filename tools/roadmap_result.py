#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

MAX_PUSH_RACE_RETRIES=3
RESULT_STATUS={"PASS":"completed","FAIL":"failed","BLOCKED":"blocked","CANCELLED":"cancelled","UNKNOWN":"unknown"}

class RoadmapResultError(RuntimeError): pass

def run(repo: Path,*args:str,check:bool=True):
    p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RoadmapResultError(f"git_{args[0]}_failed:{p.stderr.strip()}")
    return p

def git_root(path: Path) -> Path:
    return Path(run(path,"rev-parse","--show-toplevel").stdout.strip())

def _prompt_state(repo: Path,prompt_id:str):
    conn=sqlite3.connect(repo/"roadmap.sqlite"); conn.row_factory=sqlite3.Row
    try:
        row=conn.execute("SELECT * FROM prompts WHERE prompt_id=?",(prompt_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def _apply_in_worktree(wt: Path,prompt_id:str,result:str) -> dict[str,str]:
    row=_prompt_state(wt,prompt_id)
    if not row:
        raise RoadmapResultError(f"prompt_not_found:{prompt_id}")
    wanted=RESULT_STATUS[result]
    if row["status"]==wanted and row["current_path"].startswith(("completed/","falliti/")):
        return {"status":wanted,"prompt_id":prompt_id,"idempotent":"true"}
    if row["status"] not in ("pending","running",wanted):
        raise RoadmapResultError(f"terminal_transition_refused:{row['status']}->{wanted}")

    src=wt/row["current_path"]
    if not src.is_file():
        raise RoadmapResultError(f"prompt_file_missing:{row['current_path']}")
    dest_dir="completed" if result=="PASS" else "falliti"
    dest_rel=f"{dest_dir}/{src.name}"
    dest=wt/dest_rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.resolve()!=src.resolve():
        raise RoadmapResultError(f"archive_destination_exists:{dest_rel}")
    if src.resolve()!=dest.resolve():
        src.rename(dest)

    # Record the terminal execution/status and then point the prompt at its archived file.
    script=wt/"tools"/"roadmap_db.py"
    cmd=[
        "python3",str(script),"--repo",str(wt),"terminal",
        "--prompt-id",prompt_id,"--result",result,"--actor","codex",
    ]
    p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:
        raise RoadmapResultError(f"db_terminal_failed:{p.stderr.strip()}")
    conn=sqlite3.connect(wt/"roadmap.sqlite")
    try:
        conn.execute("UPDATE prompts SET current_path=? WHERE prompt_id=?",(dest_rel,prompt_id))
        conn.commit()
    finally:
        conn.close()
    p=subprocess.run(["python3",str(script),"--repo",str(wt),"render"],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:
        raise RoadmapResultError(f"render_failed:{p.stderr.strip()}")
    return {"status":wanted,"prompt_id":prompt_id,"path":dest_rel}

def finish_result(
    repo: Path,prompt_id:str,result:str,*,confirm_executed:bool=False,dry_run:bool=False
) -> dict[str,str]:
    if result not in RESULT_STATUS:
        raise RoadmapResultError(f"invalid_result:{result}")
    if not dry_run and not confirm_executed:
        raise RoadmapResultError("mutation_requires_confirm_executed")
    repo=git_root(repo)
    for attempt in range(MAX_PUSH_RACE_RETRIES+1):
        run(repo,"fetch","--quiet","origin","main")
        parent=Path(tempfile.mkdtemp(prefix="codex-roadmap-result-"))
        wt=parent/"worktree"
        try:
            run(repo,"worktree","add","--detach",str(wt),"origin/main")
            state=_prompt_state(wt,prompt_id)
            if not state:
                raise RoadmapResultError(f"prompt_not_found:{prompt_id}")
            if dry_run:
                return {"status":"ready","prompt_id":prompt_id,"result":result,"current_status":state["status"]}
            payload=_apply_in_worktree(wt,prompt_id,result)
            status=[line for line in run(wt,"status","--porcelain=v1","-z","--untracked-files=all").stdout.split("\0") if line]
            changed=[line[3:] for line in status if len(line)>=4]
            allowed_prefixes=(
                "roadmap.sqlite","roadmap.md","spiegazioni.md","prompt-registry.md","obsidian/",
                "prompts/","completed/","falliti/",
            )
            bad=[p for p in changed if not any(p==a or p.startswith(a) for a in allowed_prefixes)]
            if bad:
                raise RoadmapResultError("unexpected_changes:"+",".join(sorted(bad)))
            if not changed:
                return {**payload,"push_race_retries":str(attempt),"push_verified":"no_change"}
            run(wt,"add","-A","roadmap.sqlite","roadmap.md","spiegazioni.md","prompt-registry.md","obsidian","prompts","completed","falliti")
            run(wt,"commit","-m",f"Record roadmap prompt {prompt_id} {result}")
            sha=run(wt,"rev-parse","HEAD").stdout.strip()
            push=run(wt,"push","origin","HEAD:main",check=False)
            if push.returncode==0:
                return {**payload,"commit":sha,"push_race_retries":str(attempt),"push_verified":"git_push_exit_0"}
            msg=(push.stderr or "").lower()
            if attempt<MAX_PUSH_RACE_RETRIES and ("fetch first" in msg or "non-fast-forward" in msg):
                continue
            raise RoadmapResultError(f"push_blocked:{push.stderr.strip()}")
        finally:
            if wt.exists():
                run(repo,"worktree","remove","--force",str(wt),check=False)
            shutil.rmtree(parent,ignore_errors=True)
    raise RoadmapResultError("push_race_retry_exhausted")

def build_parser():
    p=argparse.ArgumentParser(description="Record a terminal Codex result in roadmap.sqlite and archive the prompt.")
    p.add_argument("--repo",default=".")
    p.add_argument("--prompt-id",required=True)
    p.add_argument("--result",required=True,choices=tuple(RESULT_STATUS))
    p.add_argument("--confirm-executed",action="store_true")
    p.add_argument("--dry-run",action="store_true")
    return p

def main(argv=None):
    a=build_parser().parse_args(argv)
    try:
        payload=finish_result(Path(a.repo).expanduser(),a.prompt_id,a.result,confirm_executed=a.confirm_executed,dry_run=a.dry_run)
    except RoadmapResultError as e:
        print(json.dumps({"status":"blocked","error":str(e)},sort_keys=True)); return 2
    print(json.dumps(payload,sort_keys=True)); return 0

if __name__=="__main__":
    raise SystemExit(main())
